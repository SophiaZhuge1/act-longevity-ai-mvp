from __future__ import annotations

import json
import mimetypes
import os
import hashlib
import secrets
import time
from collections import defaultdict, deque
from json import JSONDecodeError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlparse

from env_loader import load_env_file

load_env_file()

from email_service import send_report_email
from ai_chat import ChatUnavailable, ai_available, answer_question
from local_resources import resources_for
from report_pdf import create_pdf_report
from scoring import (
    ABILITY_OPTIONS, QUESTIONS, identified_concerns, persona_and_recommendations,
    sanitise_answers, score_answers,
)
from store import InvalidMemberAccess, MemberAccessRequired, Store


store = Store()
APP_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = APP_ROOT / "dist"
RATE_LIMITS = defaultdict(deque)
RATE_LIMIT_LOCK = Lock()


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.send_response(200 if parsed.path == "/api/health" else 404)
            self.send_header("Content-Type", "application/json")
            self._send_security_headers()
            self.end_headers()
            return
        self._send_static(parsed.path, head_only=True)

    def do_OPTIONS(self):
        self._send({}, status=204)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send({"ok": True, "database": store.storage_backend()})
            return
        if parsed.path == "/api/questions":
            self._send({"questions": enrich_questions(QUESTIONS)})
            return
        if parsed.path == "/api/chat/status":
            self._send({"available": ai_available()})
            return
        if parsed.path == "/api/users":
            if not self._admin_authorised():
                self._send({"error": "Admin access required"}, status=403)
                return
            self._send({"users": store.list_users()})
            return
        if parsed.path.startswith("/api/users/"):
            if not self._admin_authorised():
                self._send({"error": "Admin access required"}, status=403)
                return
            user_id = parsed.path.split("/")[-1]
            user = store.get_user(user_id)
            self._send(user or {"error": "User not found"}, status=200 if user else 404)
            return
        if parsed.path == "/api/local-resources":
            query = parse_qs(parsed.query)
            user_id = query.get("user_id", [""])[0]
            user = store.get_user(user_id)
            token = self.headers.get("X-Chat-Token", "")
            expected = user.get("chat_token_hash", "") if user else ""
            authorised = bool(expected and secrets.compare_digest(hashlib.sha256(token.encode("utf-8")).hexdigest(), expected))
            if not authorised:
                self._send({"resources": resources_for({}, query.get("postcode", [""])[0], {})})
                return
            self._send({"resources": resources_for(user["scores"], user["profile"].get("postcode", ""), user.get("answers", {}))})
            return
        self._send_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
        except (JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            self._send({"error": str(exc) or "Invalid JSON request."}, status=400)
            return
        if parsed.path == "/api/concerns":
            answers = sanitise_answers(payload.get("answers", {}))
            scores = score_answers(answers)
            self._send({"concerns": identified_concerns(answers, scores)})
            return
        if parsed.path == "/api/members/login":
            if not allow_request(f"login:{self.client_address[0]}", limit=10, window_seconds=900):
                self._send({"error": "Too many sign-in attempts. Please wait 15 minutes and try again."}, status=429)
                return
            try:
                result = store.authenticate_member(payload.get("email", ""), payload.get("access_code", ""))
            except InvalidMemberAccess as exc:
                self._send({"error": str(exc)}, status=401)
                return
            self._send(result)
            return
        if parsed.path == "/api/assessments":
            profile = payload.get("profile", {})
            answers = sanitise_answers(payload.get("answers", {}))
            consent = payload.get("consent", {})
            waitlist = payload.get("waitlist", {})
            selected_priorities = payload.get("selected_priorities", [])[:3]
            scores = score_answers(answers)
            ai_result = persona_and_recommendations(profile, answers, scores, selected_priorities)
            try:
                record = store.create_user_record(profile, answers, scores, ai_result, consent, waitlist, payload.get("member_access"))
            except MemberAccessRequired as exc:
                self._send({"error": str(exc)}, status=409)
                return
            record["resources"] = resources_for(scores, profile.get("postcode") or answers.get("postcode", ""), answers)
            delivery = prepare_report_delivery(record)
            record["delivery"] = delivery
            store.update_user_delivery(record["user_id"], delivery)
            record.pop("chat_token_hash", None)
            self._send(record, status=201)
            return
        if parsed.path == "/api/chat":
            user_id = payload.get("user_id", "")
            if not allow_request(f"chat:{user_id or self.client_address[0]}", limit=30, window_seconds=3600):
                self._send({"error": "You have reached the Ask ACT hourly limit. Please try again later."}, status=429)
                return
            message = payload.get("message", "")
            if not isinstance(message, str) or not message.strip() or len(message) > 600:
                self._send({"error": "Please enter a question of up to 600 characters."}, status=400)
                return
            if payload.get("ai_consent") is not True:
                self._send({"error": "Please agree to share relevant assessment details with the AI service first."}, status=400)
                return
            user = store.get_user(user_id)
            if not user:
                self._send({"error": "User not found"}, status=404)
                return
            expected = user.get("chat_token_hash", "")
            supplied = payload.get("chat_token", "")
            if not isinstance(supplied, str) or not expected or not secrets.compare_digest(hashlib.sha256(supplied.encode("utf-8")).hexdigest(), expected):
                self._send({"error": "This chat session is not authorised. Please complete a new assessment."}, status=403)
                return
            try:
                answer = answer_question(user, message.strip(), store.recent_chat(user_id))
            except ChatUnavailable as exc:
                self._send({"error": str(exc)}, status=503)
                return
            store.save_chat(user_id, message.strip(), answer)
            self._send({"answer": answer})
            return
        self._send({"error": "Not found"}, status=404)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValueError("Request is too large.")
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        payload = json.loads(raw or "{}")
        if not isinstance(payload, dict):
            raise ValueError("Request must be a JSON object.")
        return payload

    def _admin_authorised(self) -> bool:
        expected = os.getenv("ACT_ADMIN_API_KEY", "")
        supplied = self.headers.get("X-Admin-Key", "")
        return bool(expected and secrets.compare_digest(supplied, expected))

    def _send(self, data: dict, status: int = 200):
        body = b"" if status == 204 else json.dumps(data).encode("utf-8")
        self.send_response(status)
        allowed_origin = os.getenv("CORS_ORIGIN", "").strip()
        if allowed_origin:
            self.send_header("Access-Control-Allow-Origin", allowed_origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Chat-Token, X-Admin-Key")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._send_security_headers()
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
        self._send_security_headers()
        if file_path.name == "index.html":
            self.send_header("Cache-Control", "no-cache")
        else:
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _send_security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' https://img.youtube.com data:; "
            "style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
        )


def enrich_questions(questions: list[dict]) -> list[dict]:
    out = []
    for item in questions:
        if item["type"] in {"yesno", "positive_yesno"}:
            out.append({**item, "options": ["Yes", "No"]})
        elif item["type"] == "ability":
            out.append({**item, "options": ABILITY_OPTIONS})
        else:
            out.append(item)
    return out


def allow_request(key: str, limit: int, window_seconds: int) -> bool:
    now = time.monotonic()
    with RATE_LIMIT_LOCK:
        attempts = RATE_LIMITS[key]
        while attempts and attempts[0] <= now - window_seconds:
            attempts.popleft()
        if len(attempts) >= limit:
            return False
        attempts.append(now)
        return True


def prepare_report_delivery(record: dict) -> dict:
    try:
        pdf_path = create_pdf_report(record)
        email_result = send_report_email(record, pdf_path)
        return {
            "pdf_created": True,
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
