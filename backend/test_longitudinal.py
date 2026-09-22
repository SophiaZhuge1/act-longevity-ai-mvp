import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from store import InvalidMemberAccess, MemberAccessRequired, Store


SCORES = {
    "staying_healthy": 70,
    "independence": 80,
    "wellbeing": 65,
    "social_resources": 75,
    "clinical_risk": 60,
}
AI_RESULT = {
    "persona": "A concise assessment summary.",
    "recommendations": [],
    "videos": [],
    "lowest_categories": ["clinical_risk"],
    "support_priorities": [],
    "prevention_opportunities": [],
    "clinical_risks": [],
    "selected_priorities": [{"id": "movement", "title": "Exercise and movement"}],
}
PROFILE = {"name": "Jane", "dob": "1948-05-01", "postcode": "SW1A 1AA"}
WAITLIST = {"email": "jane@example.com", "join": False}


class LongitudinalStoreTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.local_db = Path(self.directory.name) / "store.json"
        self.patches = [patch("store.LOCAL_DB", self.local_db), patch.dict(os.environ, {"MONGODB_URI": ""})]
        for item in self.patches:
            item.start()
        self.store = Store()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.directory.cleanup()

    def test_first_and_returning_assessments_share_one_timeline(self):
        first = self.store.create_user_record(PROFILE, {}, SCORES, AI_RESULT, waitlist=WAITLIST)
        code = first["member_access_code"]
        self.assertTrue(code.startswith("ACT-"))
        self.assertEqual(len(first["history"]), 1)

        login = self.store.authenticate_member(" JANE@example.com ", code.lower())
        self.assertEqual(len(login["history"]), 1)
        self.assertEqual(login["member_id"], first["member_id"])

        improved = {**SCORES, "wellbeing": 78, "clinical_risk": 72}
        second = self.store.create_user_record(
            PROFILE, {}, improved, AI_RESULT, waitlist=WAITLIST,
            member_access={"email": "jane@example.com", "access_code": code},
        )
        self.assertEqual(second["member_id"], first["member_id"])
        self.assertEqual(len(second["history"]), 2)
        self.assertEqual(second["history"][-1]["scores"]["wellbeing"], 78)
        self.assertNotIn("member_access_code", second)

    def test_existing_email_requires_private_code(self):
        self.store.create_user_record(PROFILE, {}, SCORES, AI_RESULT, waitlist=WAITLIST)
        with self.assertRaises(MemberAccessRequired):
            self.store.create_user_record(PROFILE, {}, SCORES, AI_RESULT, waitlist=WAITLIST)
        with self.assertRaises(InvalidMemberAccess):
            self.store.authenticate_member("jane@example.com", "ACT-WRONG-0000")

    def test_authenticated_timeline_email_cannot_be_changed(self):
        first = self.store.create_user_record(PROFILE, {}, SCORES, AI_RESULT, waitlist=WAITLIST)
        with self.assertRaises(MemberAccessRequired):
            self.store.create_user_record(
                PROFILE, {}, SCORES, AI_RESULT,
                waitlist={"email": "different@example.com"},
                member_access={"email": "jane@example.com", "access_code": first["member_access_code"]},
            )


if __name__ == "__main__":
    unittest.main()
