import unittest

from scoring import QUESTIONS, score_answers


class QuestionnaireTests(unittest.TestCase):
    def test_reference_questions_and_follow_ups_are_present(self):
        text_by_id = {item["id"]: item["text"] for item in QUESTIONS}
        self.assertEqual(len(QUESTIONS), 53)
        self.assertEqual(text_by_id["foot_problem"], "Do you have a problem with your feet?")
        self.assertEqual(text_by_id["falls_frequency"], "Have you had 2 or more falls in the last 3 months?")
        self.assertEqual(text_by_id["incontinence"], "Do you have problems with your bladder, such as accidental leakage of urine, most days?")
        self.assertEqual(text_by_id["finance_essentials"], "In general, do your finances work out at the end of the month?")
        self.assertEqual(text_by_id["gds_satisfied"], "Are you basically satisfied with your life?")

    def test_new_health_and_independence_questions_affect_scores(self):
        baseline = score_answers({"foot_problem": "No", "incontinence": "No"})
        concerns = score_answers({"foot_problem": "Yes", "incontinence": "Yes"})
        self.assertLess(concerns["staying_healthy"], baseline["staying_healthy"])
        self.assertLess(concerns["independence"], baseline["independence"])

    def test_positive_finance_follow_ups_are_scored_in_the_right_direction(self):
        stable = score_answers({
            "finance_problem": "Yes",
            "finance_essentials": "Yes",
            "finance_unexpected": "Yes",
        })
        struggling = score_answers({
            "finance_problem": "Yes",
            "finance_essentials": "No",
            "finance_unexpected": "No",
        })
        self.assertGreater(stable["financial_wellbeing"], struggling["financial_wellbeing"])


if __name__ == "__main__":
    unittest.main()
