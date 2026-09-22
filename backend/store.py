from __future__ import annotations

import json
import os
import hashlib
import secrets
import uuid
from pathlib import Path
from datetime import datetime, timezone

from scoring import embedding


DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
LOCAL_DB = DATA_DIR / "local_store.json"
SCORE_KEYS = ["staying_healthy", "independence", "wellbeing", "social_resources", "clinical_risk"]


class MemberAccessRequired(Exception):
    pass


class InvalidMemberAccess(Exception):
    pass


class Store:
    def __init__(self) -> None:
        self.mongo = None
        self.db = None
        uri = os.getenv("MONGODB_URI")
        require_mongodb = os.getenv("REQUIRE_MONGODB", "false").lower() == "true"
        if uri:
            try:
                from pymongo import MongoClient

                client = MongoClient(uri, serverSelectionTimeoutMS=2500)
                client.admin.command("ping")
                self.mongo = client
                self.db = client[os.getenv("MONGODB_DB", "longevity_app")]
                self.db.members.create_index("email_hash", unique=True)
                self.db.users.create_index([("member_id", 1), ("created_at", 1)])
            except Exception as exc:
                if require_mongodb:
                    raise RuntimeError("MongoDB is required but the connection failed.") from exc
                print(f"MongoDB unavailable, using local JSON store: {exc}")
        elif require_mongodb:
            raise RuntimeError("MONGODB_URI must be configured when REQUIRE_MONGODB=true.")
        if not LOCAL_DB.exists():
            LOCAL_DB.write_text(json.dumps({"users": [], "vectors": [], "chat": [], "waitlist": [], "analytics": [], "members": []}, indent=2), encoding="utf-8")

    def storage_backend(self) -> str:
        return "mongodb" if self.db is not None else "local"

    def create_user_record(self, profile: dict, answers: dict, scores: dict, ai_result: dict, consent: dict | None = None, waitlist: dict | None = None, member_access: dict | None = None) -> dict:
        user_id = f"U-{uuid.uuid4().hex[:8]}"
        chat_token = secrets.token_urlsafe(32)
        profile = {**profile, "user_id": user_id}
        consent = consent or {}
        waitlist = waitlist or {}
        member_access = member_access or {}
        now = datetime.now(timezone.utc).isoformat()
        email = normalise_email(waitlist.get("email", ""))
        if not email or "@" not in email:
            raise MemberAccessRequired("A valid email address is required to create a private progress record.")
        access_email = normalise_email(member_access.get("email", ""))
        member = self._member_by_email(access_email) if member_access.get("access_code") else self._member_by_email(email)
        access_code = None
        if member_access.get("access_code"):
            if email != access_email or not member or not verify_member_code(member, member_access.get("access_code", "")):
                raise MemberAccessRequired("Your report email must match the email used to open this ACT progress record.")
        elif member:
            if not verify_member_code(member, member_access.get("access_code", "")):
                raise MemberAccessRequired("An ACT progress record already exists for this email. Sign in with its private access code before adding another assessment.")
        else:
            access_code = create_access_code()
            member = {
                "member_id": f"M-{uuid.uuid4().hex[:12]}",
                "email_hash": email_hash(email),
                "access_code_hash": secret_hash(access_code),
                "created_at": now,
                "latest_profile": profile,
            }
            self._save_member(member)
        member_id = member["member_id"]
        vector_text = " ".join([
            ai_result["persona"],
            json.dumps(scores, sort_keys=True),
            " ".join(f"{k}:{v}" for k, v in answers.items()),
            " ".join(item["body"] for item in ai_result["recommendations"]),
        ])
        record = {
            "user_id": user_id,
            "member_id": member_id,
            "profile": profile,
            "answers": answers,
            "scores": scores,
            "persona": ai_result["persona"],
            "recommendations": ai_result["recommendations"],
            "videos": ai_result["videos"],
            "lowest_categories": ai_result["lowest_categories"],
            "support_priorities": ai_result["support_priorities"],
            "prevention_opportunities": ai_result["prevention_opportunities"],
            "clinical_risks": ai_result["clinical_risks"],
            "identified_concerns": ai_result.get("identified_concerns", []),
            "selected_priorities": ai_result.get("selected_priorities", []),
            "consent": {**consent, "captured_at": now},
            "waitlist": {**waitlist, "captured_at": now} if waitlist.get("join") else {"join": False},
            "created_at": now,
            "chat_token_hash": hashlib.sha256(chat_token.encode("utf-8")).hexdigest(),
        }
        vector_record = {
            "vector_id": f"persona-{user_id}",
            "user_id": user_id,
            "doc_type": "persona_health_features",
            "text": vector_text,
            "embedding": embedding(vector_text),
            "metadata": {
                "member_id": member_id,
                "postcode": profile.get("postcode") or answers.get("postcode"),
                "lowest_categories": ai_result["lowest_categories"],
                "scores": scores,
                "selected_priority_ids": [item.get("id") for item in ai_result.get("selected_priorities", [])],
                "significant_clinical_risks": [item.get("title") for item in ai_result.get("clinical_risks", []) if item.get("significant")],
            },
        }
        analytics_record = anonymised_analytics_record(user_id, profile, answers, scores, ai_result, now)
        if self.db is not None:
            self.db.users.replace_one({"user_id": user_id}, record, upsert=True)
            self.db.vector_documents.replace_one({"vector_id": vector_record["vector_id"]}, vector_record, upsert=True)
            if consent.get("analytics") is True:
                self.db.population_analytics.replace_one({"analytics_id": analytics_record["analytics_id"]}, analytics_record, upsert=True)
            if waitlist.get("join") is True:
                self.db.waitlist.replace_one({"user_id": user_id}, waitlist_record(user_id, profile, waitlist, now), upsert=True)
        else:
            data = self._read_local()
            data.setdefault("users", [])
            data.setdefault("vectors", [])
            data.setdefault("chat", [])
            data.setdefault("waitlist", [])
            data.setdefault("analytics", [])
            data.setdefault("members", [])
            data["users"] = [x for x in data["users"] if x["user_id"] != user_id] + [record]
            data["vectors"] = [x for x in data["vectors"] if x["vector_id"] != vector_record["vector_id"]] + [vector_record]
            if consent.get("analytics") is True:
                data["analytics"] = [x for x in data["analytics"] if x["analytics_id"] != analytics_record["analytics_id"]] + [analytics_record]
            if waitlist.get("join") is True:
                data["waitlist"] = [x for x in data["waitlist"] if x["user_id"] != user_id] + [waitlist_record(user_id, profile, waitlist, now)]
            self._write_local(data)
        self._update_member_profile(member_id, profile)
        result = {**record, "chat_token": chat_token}
        if access_code:
            result["member_access_code"] = access_code
        result["history"] = self.member_history(member_id)
        return result

    def authenticate_member(self, email: str, access_code: str) -> dict:
        member = self._member_by_email(normalise_email(email))
        if not member or not verify_member_code(member, access_code):
            raise InvalidMemberAccess("We could not match that email and ACT access code.")
        return {
            "member_id": member["member_id"],
            "latest_profile": member.get("latest_profile", {}),
            "history": self.member_history(member["member_id"]),
        }

    def member_history(self, member_id: str) -> list[dict]:
        if self.db is not None:
            records = list(self.db.users.find({"member_id": member_id}, {"_id": 0}).sort("created_at", 1))
        else:
            records = sorted((item for item in self._read_local().get("users", []) if item.get("member_id") == member_id), key=lambda item: item.get("created_at", ""))
        return [history_item(record) for record in records]

    def _member_by_email(self, email: str) -> dict | None:
        if not email:
            return None
        hashed = email_hash(email)
        if self.db is not None:
            return self.db.members.find_one({"email_hash": hashed}, {"_id": 0})
        return next((item for item in self._read_local().get("members", []) if item.get("email_hash") == hashed), None)

    def _save_member(self, member: dict) -> None:
        if self.db is not None:
            self.db.members.replace_one({"member_id": member["member_id"]}, member, upsert=True)
            return
        data = self._read_local()
        data.setdefault("members", [])
        data["members"] = [item for item in data["members"] if item.get("member_id") != member["member_id"]] + [member]
        self._write_local(data)

    def _update_member_profile(self, member_id: str, profile: dict) -> None:
        if self.db is not None:
            self.db.members.update_one({"member_id": member_id}, {"$set": {"latest_profile": profile}})
            return
        data = self._read_local()
        for member in data.get("members", []):
            if member.get("member_id") == member_id:
                member["latest_profile"] = profile
                break
        self._write_local(data)

    def list_users(self) -> list[dict]:
        if self.db is not None:
            return list(self.db.users.find({}, {"_id": 0}))
        return self._read_local()["users"]

    def get_user(self, user_id: str) -> dict | None:
        if self.db is not None:
            return self.db.users.find_one({"user_id": user_id}, {"_id": 0})
        return next((x for x in self._read_local()["users"] if x["user_id"] == user_id), None)

    def update_user_delivery(self, user_id: str, delivery: dict) -> None:
        if self.db is not None:
            self.db.users.update_one({"user_id": user_id}, {"$set": {"delivery": delivery}})
            return
        data = self._read_local()
        for user in data.get("users", []):
            if user.get("user_id") == user_id:
                user["delivery"] = delivery
                break
        self._write_local(data)

    def vector_search(self, query: str, limit: int = 3) -> list[dict]:
        query_vec = embedding(query)
        vectors = list(self.db.vector_documents.find({}, {"_id": 0})) if self.db is not None else self._read_local()["vectors"]
        ranked = sorted(vectors, key=lambda v: cosine(query_vec, v["embedding"]), reverse=True)
        return ranked[:limit]

    def save_chat(self, user_id: str, message: str, answer: str) -> None:
        chat = {"user_id": user_id, "message": message, "answer": answer}
        if self.db is not None:
            self.db.chat.insert_one(chat)
        else:
            data = self._read_local()
            data["chat"].append(chat)
            self._write_local(data)

    def recent_chat(self, user_id: str, limit: int = 6) -> list[dict]:
        if self.db is not None:
            return list(reversed(list(self.db.chat.find({"user_id": user_id}, {"_id": 0}).sort("_id", -1).limit(limit))))
        return [turn for turn in self._read_local().get("chat", []) if turn.get("user_id") == user_id][-limit:]

    def _read_local(self) -> dict:
        return json.loads(LOCAL_DB.read_text(encoding="utf-8"))

    def _write_local(self, data: dict) -> None:
        LOCAL_DB.write_text(json.dumps(data, indent=2), encoding="utf-8")


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def normalise_email(value: str) -> str:
    return (value or "").strip().lower()


def email_hash(email: str) -> str:
    return hashlib.sha256(normalise_email(email).encode("utf-8")).hexdigest()


def secret_hash(value: str) -> str:
    return hashlib.sha256((value or "").strip().upper().encode("utf-8")).hexdigest()


def verify_member_code(member: dict, access_code: str) -> bool:
    expected = member.get("access_code_hash", "")
    return bool(expected and access_code and secrets.compare_digest(secret_hash(access_code), expected))


def create_access_code() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    raw = "".join(secrets.choice(alphabet) for _ in range(8))
    return f"ACT-{raw[:4]}-{raw[4:]}"


def history_item(record: dict) -> dict:
    return {
        "assessment_id": record.get("user_id"),
        "created_at": record.get("created_at"),
        "scores": {key: record.get("scores", {}).get(key, 0) for key in SCORE_KEYS},
        "summary": record.get("persona", ""),
        "selected_priorities": record.get("selected_priorities", []),
        "clinical_risks": record.get("clinical_risks", []),
    }


def age_band_from_dob(dob: str) -> str:
    try:
        year = int(dob.split("-")[0])
    except Exception:
        return "unknown"
    age = datetime.now().year - year
    if age < 70:
        return "under_70"
    if age < 80:
        return "70_79"
    if age < 90:
        return "80_89"
    return "90_plus"


def anonymised_analytics_record(user_id: str, profile: dict, answers: dict, scores: dict, ai_result: dict, created_at: str) -> dict:
    source = f"{user_id}:{profile.get('postcode') or answers.get('postcode') or ''}"
    outcode = (profile.get("postcode") or answers.get("postcode") or "").split()[0].upper()
    return {
        "analytics_id": f"A-{uuid.uuid5(uuid.NAMESPACE_URL, source).hex[:12]}",
        "age_band": age_band_from_dob(profile.get("dob") or answers.get("dob", "")),
        "gender": profile.get("gender") or answers.get("gender", "Prefer not to say"),
        "outcode": outcode,
        "living_arrangement": profile.get("living_arrangement") or answers.get("living_arrangement"),
        "scores": {key: scores[key] for key in SCORE_KEYS},
        "lowest_categories": ai_result.get("lowest_categories", []),
        "priority_count": len(ai_result.get("support_priorities", [])),
        "selected_priority_ids": [item.get("id") for item in ai_result.get("selected_priorities", [])],
        "clinical_risk_count": len(ai_result.get("clinical_risks", [])),
        "significant_clinical_risk_count": sum(item.get("significant") is True for item in ai_result.get("clinical_risks", [])),
        "created_at": created_at,
    }


def waitlist_record(user_id: str, profile: dict, waitlist: dict, created_at: str) -> dict:
    return {
        "user_id": user_id,
        "name": profile.get("name", ""),
        "email": waitlist.get("email", ""),
        "organisation": waitlist.get("organisation", ""),
        "interest_type": waitlist.get("interest_type", "Individual"),
        "created_at": created_at,
    }
