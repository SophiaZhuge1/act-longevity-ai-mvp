from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from scoring import embedding


DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
LOCAL_DB = DATA_DIR / "local_store.json"


class Store:
    def __init__(self) -> None:
        self.mongo = None
        self.db = None
        uri = os.getenv("MONGODB_URI")
        if uri:
            try:
                from pymongo import MongoClient

                client = MongoClient(uri, serverSelectionTimeoutMS=2500)
                client.admin.command("ping")
                self.mongo = client
                self.db = client[os.getenv("MONGODB_DB", "longevity_app")]
            except Exception as exc:
                print(f"MongoDB unavailable, using local JSON store: {exc}")
        if not LOCAL_DB.exists():
            LOCAL_DB.write_text(json.dumps({"users": [], "vectors": [], "chat": []}, indent=2), encoding="utf-8")

    def create_user_record(self, profile: dict, answers: dict, scores: dict, ai_result: dict) -> dict:
        user_id = profile.get("user_id") or f"U-{uuid.uuid4().hex[:8]}"
        profile = {**profile, "user_id": user_id}
        vector_text = " ".join([
            ai_result["persona"],
            json.dumps(scores, sort_keys=True),
            " ".join(f"{k}:{v}" for k, v in answers.items()),
            " ".join(item["body"] for item in ai_result["recommendations"]),
        ])
        record = {
            "user_id": user_id,
            "profile": profile,
            "answers": answers,
            "scores": scores,
            "persona": ai_result["persona"],
            "recommendations": ai_result["recommendations"],
            "videos": ai_result["videos"],
            "lowest_categories": ai_result["lowest_categories"],
        }
        vector_record = {
            "vector_id": f"persona-{user_id}",
            "user_id": user_id,
            "doc_type": "persona_health_features",
            "text": vector_text,
            "embedding": embedding(vector_text),
            "metadata": {
                "postcode": profile.get("postcode") or answers.get("postcode"),
                "lowest_categories": ai_result["lowest_categories"],
                "scores": scores,
            },
        }
        if self.db is not None:
            self.db.users.replace_one({"user_id": user_id}, record, upsert=True)
            self.db.vector_documents.replace_one({"vector_id": vector_record["vector_id"]}, vector_record, upsert=True)
        else:
            data = self._read_local()
            data["users"] = [x for x in data["users"] if x["user_id"] != user_id] + [record]
            data["vectors"] = [x for x in data["vectors"] if x["vector_id"] != vector_record["vector_id"]] + [vector_record]
            self._write_local(data)
        return record

    def list_users(self) -> list[dict]:
        if self.db is not None:
            return list(self.db.users.find({}, {"_id": 0}))
        return self._read_local()["users"]

    def get_user(self, user_id: str) -> dict | None:
        if self.db is not None:
            return self.db.users.find_one({"user_id": user_id}, {"_id": 0})
        return next((x for x in self._read_local()["users"] if x["user_id"] == user_id), None)

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

    def _read_local(self) -> dict:
        return json.loads(LOCAL_DB.read_text(encoding="utf-8"))

    def _write_local(self, data: dict) -> None:
        LOCAL_DB.write_text(json.dumps(data, indent=2), encoding="utf-8")


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))
