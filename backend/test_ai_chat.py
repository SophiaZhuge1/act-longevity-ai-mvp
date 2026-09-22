import json
import os
import tempfile
import unittest
from io import BytesIO
from urllib.error import HTTPError
from pathlib import Path
from unittest.mock import patch

from ai_chat import ChatUnavailable, answer_question, profile_context
from store import Store


USER = {
    "profile": {"name": "Private Name", "dob": "1948-05-01", "postcode": "SW1A 1AA", "phone": "07700000000", "living_arrangement": "Alone"},
    "answers": {"falls_3_months": "Yes", "falls_frequency": "Once", "bp_checked": "No"},
    "scores": {"staying_healthy": 65, "independence": 80, "wellbeing": 75, "social_resources": 70, "clinical_risk": 60},
    "recommendations": [{"title": "Arrange a falls review", "body": "Speak with a GP or falls service.", "type": "clinical"}],
    "selected_priorities": [{"title": "Falls"}],
    "clinical_risks": [{"title": "Risk related to falls", "significant": True}],
}


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, *_args):
        return json.dumps({"output": [{"type": "message", "content": [{"type": "output_text", "text": "A falls review is a sensible first step."}]}]}).encode()


class AskActTests(unittest.TestCase):
    def test_chat_access_token_is_not_stored_in_plain_text(self):
        ai_result = {
            "persona": "A wellness summary.", "recommendations": [], "videos": [],
            "lowest_categories": [], "support_priorities": [], "prevention_opportunities": [],
            "clinical_risks": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            with patch("store.LOCAL_DB", Path(directory) / "store.json"), patch.dict(os.environ, {"MONGODB_URI": ""}):
                store = Store()
                result = store.create_user_record(USER["profile"], USER["answers"], USER["scores"], ai_result, waitlist={"email": "private@example.com"})
                saved = store.get_user(result["user_id"])
                self.assertNotIn("chat_token", saved)
                self.assertNotEqual(saved["chat_token_hash"], result["chat_token"])
                store.save_chat(result["user_id"], "First question", "First answer")
                store.save_chat("someone-else", "Private question", "Private answer")
                self.assertEqual(len(store.recent_chat(result["user_id"])), 1)

    def test_context_omits_direct_identifiers(self):
        context = json.dumps(profile_context(USER))
        self.assertIn("falls", context.lower())
        for private in ["Private Name", "SW1A 1AA", "07700000000", "1948-05-01"]:
            self.assertNotIn(private, context)

    def test_missing_key_is_explicit(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with self.assertRaises(ChatUnavailable):
                answer_question(USER, "Why a falls review?", [])

    def test_quota_error_has_actionable_message(self):
        error = HTTPError("https://api.openai.com/v1/responses", 429, "Too Many Requests", {}, BytesIO(b'{"error":{"type":"insufficient_quota","code":"credit_balance_exhausted"}}'))
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}), patch("ai_chat.urlopen", side_effect=error):
            with self.assertRaisesRegex(ChatUnavailable, "no available API credit"):
                answer_question(USER, "Why a falls review?", [])

    def test_request_uses_profile_history_and_no_provider_storage(self):
        captured = {}

        def fake_urlopen(request, timeout):
            captured["payload"] = json.loads(request.data)
            captured["timeout"] = timeout
            return FakeResponse()

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_CHAT_MODEL": "gpt-5-mini"}):
            with patch("ai_chat.urlopen", side_effect=fake_urlopen):
                result = answer_question(USER, "What about that?", [{"message": "Why a falls review?", "answer": "It can help prevent another fall."}])
        self.assertIn("falls review", result)
        self.assertIs(captured["payload"]["store"], False)
        self.assertEqual(captured["payload"]["input"][-1]["content"], "What about that?")
        self.assertEqual(captured["payload"]["input"][-3]["content"], "Why a falls review?")
        self.assertNotIn("Private Name", json.dumps(captured["payload"]))


if __name__ == "__main__":
    unittest.main()
