from __future__ import annotations

import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from email_service import send_report_email
from local_resources import resources_for
from report_pdf import create_pdf_report
from scoring import ABILITY_OPTIONS, QUESTIONS, persona_and_recommendations, score_answers
from store import Store


store = Store()
APP_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = APP_ROOT / "dist"


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.send_response(200 if parsed.path == "/api/health" else 404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            return
        self._send_static(parsed.path, head_only=True)

    def do_OPTIONS(self):
        self._send({}, status=204)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send({"ok": True})
            return
        if parsed.path == "/api/questions":
            self._send({"questions": enrich_questions(QUESTIONS)})
            return
        if parsed.path == "/api/users":
            self._send({"users": store.list_users()})
            return
        if parsed.path.startswith("/api/users/"):
            user_id = parsed.path.split("/")[-1]
            user = store.get_user(user_id)
            self._send(user or {"error": "User not found"}, status=200 if user else 404)
            return
        if parsed.path == "/api/local-resources":
            query = parse_qs(parsed.query)
            user_id = query.get("user_id", [""])[0]
            user = store.get_user(user_id)
            if not user:
                self._send({"resources": resources_for({}, query.get("postcode", [""])[0])})
                return
            self._send({"resources": resources_for(user["scores"], user["profile"].get("postcode", ""))})
            return
        self._send_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/assessments":
            payload = self._read_json()
            profile = payload.get("profile", {})
            answers = payload.get("answers", {})
            consent = payload.get("consent", {})
            waitlist = payload.get("waitlist", {})
            scores = score_answers(answers)
            ai_result = persona_and_recommendations(profile, answers, scores)
            record = store.create_user_record(profile, answers, scores, ai_result, consent, waitlist)
            record["resources"] = resources_for(scores, profile.get("postcode") or answers.get("postcode", ""))
            delivery = prepare_report_delivery(record)
            record["delivery"] = delivery
            store.update_user_delivery(record["user_id"], delivery)
            self._send(record, status=201)
            return
        if parsed.path == "/api/chat":
            payload = self._read_json()
            user_id = payload.get("user_id", "")
            message = payload.get("message", "")
            user = store.get_user(user_id)
            if not user:
                self._send({"error": "User not found"}, status=404)
                return
            matches = store.vector_search(message, 2)
            answer = chat_answer(user, message, matches)
            store.save_chat(user_id, message, answer)
            self._send({"answer": answer, "retrieved": matches})
            return
        self._send({"error": "Not found"}, status=404)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def _send(self, data: dict, status: int = 200):
        body = b"" if status == 204 else json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _send_static(self, path: str, head_only: bool = False):
        if not DIST_DIR.exists():
            self._send({"error": "Frontend build not found. Run npm run build first."}, status=404)
            return
        requested = path.lstrip("/") or "index.html"
        file_path = (DIST_DIR / requested).resolve()
        try:
            file_path.relative_to(DIST_DIR.resolve())
        except ValueError:
            self._send({"error": "Not found"}, status=404)
            return
        if not file_path.exists() or not file_path.is_file():
            file_path = DIST_DIR / "index.html"
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)


def enrich_questions(questions: list[dict]) -> list[dict]:
    out = []
    for item in questions:
        if item["type"] == "yesno":
            out.append({**item, "options": ["Yes", "No"]})
        elif item["type"] == "ability":
            out.append({**item, "options": ABILITY_OPTIONS})
        else:
            out.append(item)
    return out


def chat_answer(user: dict, message: str, matches: list[dict]) -> str:
    lowered = message.lower()
    recs = user.get("recommendations", [])
    if "exercise" in lowered or "movement" in lowered or "yoga" in lowered:
        movement = [r for r in recs if r["type"] in {"movement", "local"}]
        if movement:
            return "A gentle place to start: " + " ".join(r["body"] for r in movement[:2])
        return "Your profile looks reasonably strong for movement. Keep a steady routine with walking, light strength, and balance practice."
    if "shop" in lowered or "food" in lowered or "meal" in lowered:
        return "For food support, the goal is to make good meals easier rather than perfect. Grocery delivery, prepared meals, or a simple protein-plus-vegetable lunch can help maintain energy."
    if "blood pressure" in lowered or "cholesterol" in lowered or "supplement" in lowered:
        return "For blood pressure or cholesterol, start with a recent check, fibre-rich foods, regular movement, and speaking with a pharmacist or clinician before supplements, especially if you take medicines."
    if "why" in lowered:
        return f"This recommendation comes from your profile: {user['persona']}"
    context = matches[0]["text"][:240] if matches else user["persona"]
    return f"Based on your profile, I would keep the next step small and practical. {context}"


def prepare_report_delivery(record: dict) -> dict:
    try:
        pdf_path = create_pdf_report(record)
        email_result = send_report_email(record, pdf_path)
        return {
            "pdf_created": True,
            "pdf_path": str(pdf_path),
            "email": email_result,
        }
    except Exception as exc:
        return {
            "pdf_created": False,
            "email": {"sent": False, "reason": f"Report delivery failed: {exc}"},
        }


def run():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"App running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
