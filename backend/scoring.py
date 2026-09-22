from __future__ import annotations

import hashlib
import math
from datetime import date


QUESTIONS = [
    {"id": "vision_problem", "section": "Staying Healthy", "text": "Do you have a problem with your vision?", "type": "yesno", "concern": "Vision"},
    {"id": "hearing_problem", "section": "Staying Healthy", "text": "Do you have a problem with your hearing?", "type": "yesno", "concern": "Hearing"},
    {"id": "teeth_problem", "section": "Staying Healthy", "text": "Do you have a problem with your teeth, mouth or dentures?", "type": "yesno", "concern": "Teeth and mouth"},
    {"id": "falls_3_months", "section": "Staying Healthy", "text": "Have you had any falls in the last three months?", "type": "yesno", "concern": "Falls", "trigger": True},
    {"id": "falls_frequency", "section": "Staying Healthy", "text": "How many times have you fallen in the last three months?", "type": "choice", "options": ["Once", "Twice", "Three or more times"], "show_if": [{"id": "falls_3_months", "value": "Yes"}], "follow_up": "Falls"},
    {"id": "falls_get_up", "section": "Staying Healthy", "text": "After a fall, would you have difficulty getting up from the floor without help?", "type": "yesno", "show_if": [{"id": "falls_3_months", "value": "Yes"}], "follow_up": "Falls"},
    {"id": "diet_concern", "section": "Staying Healthy", "text": "Do you have any concerns about your diet or nutrition?", "type": "yesno", "concern": "Diet and nutrition"},
    {"id": "lost_3kg", "section": "Staying Healthy", "text": "Have you unintentionally lost 3 kg in weight over the last three months?", "type": "yesno", "concern": "Unintentional weight loss"},
    {"id": "regular_exercise", "section": "Staying Healthy", "text": "Do you take regular exercise?", "type": "positive_yesno", "concern": "Exercise and movement"},
    {"id": "vaccinations", "section": "Staying Healthy", "text": "Are you up to date with your vaccinations?", "type": "positive_yesno", "concern": "Vaccinations"},
    {"id": "bp_checked", "section": "Staying Healthy", "text": "Has your blood pressure been checked in the last year?", "type": "positive_yesno", "concern": "Blood pressure"},

    {"id": "shopping", "section": "Independence", "text": "Are you able to do your shopping?", "type": "positive_yesno", "concern": "Shopping"},
    {"id": "dressing", "section": "Independence", "text": "Can you dress yourself?", "type": "positive_yesno", "concern": "Dressing"},
    {"id": "bathing", "section": "Independence", "text": "Are you able to use a bath or shower by yourself?", "type": "positive_yesno", "concern": "Bathing or showering"},
    {"id": "toileting", "section": "Independence", "text": "Can you use the toilet or commode?", "type": "positive_yesno", "concern": "Using the toilet"},
    {"id": "transfers", "section": "Independence", "text": "Can you move yourself from bed to chair, if they are next to each other?", "type": "positive_yesno", "concern": "Moving between bed and chair"},
    {"id": "indoors", "section": "Independence", "text": "Can you get around indoors?", "type": "positive_yesno", "concern": "Getting around indoors"},

    {"id": "accommodation_problem", "section": "Wellbeing", "text": "Do you have problems with the place where you live?", "type": "yesno", "concern": "Your home", "trigger": True},
    {"id": "accommodation_safe", "section": "Wellbeing", "text": "Do you feel unsafe where you live?", "type": "yesno", "show_if": [{"id": "accommodation_problem", "value": "Yes"}], "follow_up": "Your home"},
    {"id": "accommodation_suitable", "section": "Wellbeing", "text": "Does your home make everyday activities difficult?", "type": "yesno", "show_if": [{"id": "accommodation_problem", "value": "Yes"}], "follow_up": "Your home"},
    {"id": "accommodation_access", "section": "Wellbeing", "text": "Is it difficult to move around or get in and out of your home?", "type": "yesno", "show_if": [{"id": "accommodation_problem", "value": "Yes"}], "follow_up": "Your home"},
    {"id": "accommodation_warmth", "section": "Wellbeing", "text": "Is it difficult to keep your home comfortably warm?", "type": "yesno", "show_if": [{"id": "accommodation_problem", "value": "Yes"}], "follow_up": "Your home"},
    {"id": "accommodation_maintenance", "section": "Wellbeing", "text": "Are repairs or home maintenance becoming difficult to manage?", "type": "yesno", "show_if": [{"id": "accommodation_problem", "value": "Yes"}], "follow_up": "Your home"},
    {"id": "accommodation_stability", "section": "Wellbeing", "text": "Are you worried about being able to remain in your current home?", "type": "yesno", "show_if": [{"id": "accommodation_problem", "value": "Yes"}], "follow_up": "Your home"},
    {"id": "finance_problem", "section": "Wellbeing", "text": "Do you have problems with your finances?", "type": "yesno", "concern": "Finances", "trigger": True},
    {"id": "finance_essentials", "section": "Wellbeing", "text": "Do you have difficulty meeting essential costs such as food, heating or bills?", "type": "yesno", "show_if": [{"id": "finance_problem", "value": "Yes"}], "follow_up": "Finances"},
    {"id": "finance_unexpected", "section": "Wellbeing", "text": "Would an unexpected expense be difficult for you to manage?", "type": "yesno", "show_if": [{"id": "finance_problem", "value": "Yes"}], "follow_up": "Finances"},
    {"id": "participation_ok", "section": "Wellbeing", "text": "Are you able to pursue leisure interests, hobbies, work and learning activities which are important to you?", "type": "positive_yesno", "concern": "Activities and interests"},
    {"id": "lonely", "section": "Wellbeing", "text": "Do you often feel lonely?", "type": "yesno", "concern": "Loneliness"},
    {"id": "sleep_trouble", "section": "Wellbeing", "text": "Have you had any trouble sleeping in the last month?", "type": "yesno", "concern": "Sleep"},
    {"id": "moderate_pain", "section": "Wellbeing", "text": "Do you suffer from moderate or severe pain most days?", "type": "yesno", "concern": "Pain"},
    {"id": "down_depressed", "section": "Wellbeing", "text": "During the last month, have you often been bothered by feeling down, depressed or hopeless?", "type": "yesno", "concern": "Low mood", "trigger": True},
    {"id": "little_interest", "section": "Wellbeing", "text": "During the last month, have you often been bothered by having little interest or pleasure in doing things?", "type": "yesno", "concern": "Loss of interest", "trigger": True},
    {"id": "gds_satisfied", "section": "Wellbeing", "text": "Thinking about the past week, are you basically satisfied with your life?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_dropped_activities", "section": "Wellbeing", "text": "Have you dropped many of your activities and interests?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_empty", "section": "Wellbeing", "text": "Do you feel that your life is empty?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_bored", "section": "Wellbeing", "text": "Do you often get bored?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_good_spirits", "section": "Wellbeing", "text": "Are you in good spirits most of the time?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_afraid", "section": "Wellbeing", "text": "Are you afraid that something bad is going to happen to you?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_happy", "section": "Wellbeing", "text": "Do you feel happy most of the time?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_helpless", "section": "Wellbeing", "text": "Do you often feel helpless?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_stay_home", "section": "Wellbeing", "text": "Do you prefer to stay at home, rather than going out and doing new things?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_memory", "section": "Wellbeing", "text": "Do you feel you have more problems with memory than most people?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_wonderful_alive", "section": "Wellbeing", "text": "Do you think it is wonderful to be alive now?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_worthless", "section": "Wellbeing", "text": "Do you feel pretty worthless the way you are now?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_energy", "section": "Wellbeing", "text": "Do you feel full of energy?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_hopeless", "section": "Wellbeing", "text": "Do you feel that your situation is hopeless?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "gds_better_off", "section": "Wellbeing", "text": "Do you think that most people are better off than you are?", "type": "yesno", "show_if": [{"id": "down_depressed", "value": "Yes"}, {"id": "little_interest", "value": "Yes"}], "show_if_mode": "any", "follow_up": "Mood"},
    {"id": "forgetting", "section": "Wellbeing", "text": "In the past year, have you noticed forgetting things more than usual?", "type": "yesno", "concern": "Memory"},
    {"id": "confused_day_place", "section": "Wellbeing", "text": "Do you sometimes feel confused about what day it is or where you are?", "type": "yesno", "concern": "Confusion"},
    {"id": "memory_concern_other", "section": "Wellbeing", "text": "Has anyone close to you raised concerns about your memory or thinking?", "type": "yesno", "concern": "Memory or thinking"},
]

ABILITY_OPTIONS = ["Yes, without help", "Yes, with some difficulty", "Only with help", "No"]


def embedding(text: str, dims: int = 64) -> list[float]:
    values = [0.0] * dims
    for raw in text.lower().split():
        token = raw.strip(".,:;!?()")
        if not token:
            continue
        digest = hashlib.sha256(token.encode()).digest()
        idx = int.from_bytes(digest[:2], "big") % dims
        values[idx] += 1 if digest[2] % 2 == 0 else -1
    norm = math.sqrt(sum(v * v for v in values)) or 1
    return [round(v / norm, 6) for v in values]


def yes_good(value: str, yes_is_good: bool) -> int:
    if value not in {"Yes", "No"}:
        return 55
    return 100 if (value == "Yes") == yes_is_good else 35


def ability_score(value: str) -> int:
    return {"Yes, without help": 100, "Yes, with some difficulty": 70, "Only with help": 38, "No": 15}.get(value, 55)


def question_is_visible(question: dict, answers: dict) -> bool:
    conditions = question.get("show_if", [])
    if not conditions:
        return True
    matches = [answers.get(item["id"]) == item["value"] for item in conditions]
    return any(matches) if question.get("show_if_mode") == "any" else all(matches)


def sanitise_answers(answers: dict) -> dict:
    allowed = {question["id"] for question in QUESTIONS if question_is_visible(question, answers)}
    return {key: value for key, value in answers.items() if key in allowed}


def gds_score(answers: dict) -> int:
    yes_scores = {
        "gds_dropped_activities", "gds_empty", "gds_bored", "gds_afraid", "gds_helpless",
        "gds_stay_home", "gds_memory", "gds_worthless", "gds_hopeless", "gds_better_off",
    }
    no_scores = {"gds_satisfied", "gds_good_spirits", "gds_happy", "gds_wonderful_alive", "gds_energy"}
    return sum(answers.get(key) == "Yes" for key in yes_scores) + sum(answers.get(key) == "No" for key in no_scores)


def score_answers(answers: dict) -> dict:
    answers = sanitise_answers(answers)
    independence_ids = ["shopping", "dressing", "bathing", "toileting", "transfers", "indoors"]
    independence = round(sum(yes_good(answers.get(k, ""), True) for k in independence_ids) / len(independence_ids))
    nutrition = round(sum([
        yes_good(answers.get("diet_concern", ""), False),
        yes_good(answers.get("lost_3kg", ""), False),
        yes_good(answers.get("teeth_problem", ""), False),
    ]) / 3)
    mood_follow_up_shown = answers.get("down_depressed") == "Yes" or answers.get("little_interest") == "Yes"
    mental = max(20, round(100 - (gds_score(answers) / 15 * 80))) if mood_follow_up_shown else 100
    cognition_core = round(sum([
        yes_good(answers.get("forgetting", ""), False),
        yes_good(answers.get("confused_day_place", ""), False),
        yes_good(answers.get("memory_concern_other", ""), False),
    ]) / 3)
    sensory = round(sum([
        yes_good(answers.get("vision_problem", ""), False),
        yes_good(answers.get("hearing_problem", ""), False),
    ]) / 2)
    cognition = round((cognition_core + sensory) / 2)
    social = round(sum([
        yes_good(answers.get("lonely", ""), False),
        yes_good(answers.get("participation_ok", ""), True),
    ]) / 2)
    preventive = round(sum([
        100 if answers.get("vaccinations") == "Yes" else 55 if answers.get("vaccinations") == "Not sure" else 30,
        100 if answers.get("bp_checked") == "Yes" else 55 if answers.get("bp_checked") == "Not sure" else 30,
        yes_good(answers.get("teeth_problem", ""), False),
    ]) / 3)
    staying_healthy = round(sum([
        yes_good(answers.get("vision_problem", ""), False),
        yes_good(answers.get("hearing_problem", ""), False),
        yes_good(answers.get("teeth_problem", ""), False),
        yes_good(answers.get("falls_3_months", ""), False),
        yes_good(answers.get("regular_exercise", ""), True),
        nutrition,
        preventive,
    ]) / 7)
    sleep = yes_good(answers.get("sleep_trouble", ""), False)
    pain = yes_good(answers.get("moderate_pain", ""), False)
    wellbeing = round(sum([
        mental,
        sleep,
        pain,
    ]) / 3)
    accommodation_ids = [
        "accommodation_safe", "accommodation_suitable", "accommodation_access",
        "accommodation_warmth", "accommodation_maintenance", "accommodation_stability",
    ]
    accommodation = 100 if answers.get("accommodation_problem") == "No" else round(sum(yes_good(answers.get(k, ""), False) for k in accommodation_ids) / len(accommodation_ids))
    financial = 100 if answers.get("finance_problem") == "No" else round(sum(yes_good(answers.get(k, ""), False) for k in ["finance_essentials", "finance_unexpected"]) / 2)
    social_resources = round((social + accommodation + financial) / 3)
    falls_safety = 100
    if answers.get("falls_3_months") == "Yes":
        falls_safety = 15 if answers.get("falls_frequency") in {"Twice", "Three or more times"} or answers.get("falls_get_up") == "Yes" else 35
    weight_safety = 20 if answers.get("lost_3kg") == "Yes" else 100
    mood_significant = gds_score(answers) > 5 or (answers.get("down_depressed") == "Yes" and answers.get("little_interest") == "Yes")
    mood_safety = min(mental, 35) if mood_significant else 65 if answers.get("down_depressed") == "Yes" or answers.get("little_interest") == "Yes" else 100
    cognitive_flags = sum(answers.get(key) == "Yes" for key in ["forgetting", "confused_day_place", "memory_concern_other"])
    cognition_significant = cognitive_flags >= 2 or answers.get("confused_day_place") == "Yes" or answers.get("memory_concern_other") == "Yes"
    cognition_safety = 25 if cognition_significant else 65 if cognitive_flags else 100
    pain_safety = yes_good(answers.get("moderate_pain", ""), False)
    sensory_safety = sensory
    blood_pressure_safety = 100 if answers.get("bp_checked") == "Yes" else 55 if answers.get("bp_checked") == "Not sure" else 30
    clinical_risk = round(sum([
        falls_safety,
        weight_safety,
        mood_safety,
        cognition_safety,
        pain_safety,
        sensory_safety,
        blood_pressure_safety,
    ]) / 7)
    return {
        "staying_healthy": staying_healthy,
        "independence": independence,
        "wellbeing": wellbeing,
        "social_resources": social_resources,
        "clinical_risk": clinical_risk,
        "accommodation": accommodation,
        "financial_wellbeing": financial,
        "nutrition_vitality": nutrition,
        "sleep_recovery": sleep,
        "social_connection": social,
        "cognition_sensory": cognition,
        "preventive_care": preventive,
        "gds_15": gds_score(answers) if mood_follow_up_shown else 0,
    }


def persona_and_recommendations(profile: dict, answers: dict, scores: dict, selected_priority_ids: list[str] | None = None) -> dict:
    answers = sanitise_answers(answers)
    selected_priority_ids = selected_priority_ids or []
    public_scores = {key: scores[key] for key in ["staying_healthy", "independence", "wellbeing", "social_resources", "clinical_risk"]}
    low = sorted(public_scores.items(), key=lambda x: x[1])[:3]
    high = sorted(public_scores.items(), key=lambda x: x[1], reverse=True)[:2]
    name = profile.get("name") or "This member"
    outcode = (profile.get("postcode") or answers.get("postcode") or "local").split()[0]
    labels = {
        "staying_healthy": "staying healthy", "independence": "independence",
        "wellbeing": "wellbeing", "social_resources": "social resources",
        "clinical_risk": "clinical risk",
    }
    concerns = identified_concerns(answers, scores)
    selected_priorities = [item for item in concerns if item["id"] in selected_priority_ids][:3]
    clinical_risks = clinical_risks_for(answers, scores)
    significant_risks = [item for item in clinical_risks if item.get("significant")]
    actions = []
    if scores["social_connection"] < 70:
        actions.append(f"choose one welcoming older-adult group, workshop or wellbeing walk near {outcode} for regular connection")
    if scores["independence"] < 72:
        actions.append("make daily routines easier with grocery delivery, prepared meals or a local care-needs assessment")
    if answers.get("bp_checked") in {"No", "Not sure"}:
        actions.append("arrange a blood-pressure check and use the NHS or WHO information below to prepare any questions")
    if answers.get("regular_exercise") == "No" or answers.get("falls_3_months") == "Yes":
        actions.append("build movement gently through seated exercise or a supervised strength-and-balance class")
    if scores["nutrition_vitality"] < 72 or answers.get("diet_concern") == "Yes":
        actions.append("protect energy with regular, simple meals that include protein and vegetables")
    if scores["sleep_recovery"] < 68:
        actions.append("use a steady wake time and a calmer evening routine to support sleep")
    if not actions:
        actions.append("maintain the routines that are working, including regular movement, social contact and preventive health checks")
    age = age_from_dob(profile.get("dob", ""))
    context = []
    if age:
        context.append(f"age {age}")
    if profile.get("living_arrangement"):
        context.append(f"living {profile['living_arrangement'].lower()}")
    plan_lead = f" Taking account of {' and '.join(context)}, a practical" if context else " A practical"
    risk_intro = ""
    if significant_risks:
        risk_names = ", ".join(item["title"].lower() for item in significant_risks)
        risk_intro = f"The assessment has flagged {risk_names} as important clinical points to discuss with a GP or suitable health professional. These come before the general wellness suggestions. "
    priority_intro = ""
    if selected_priorities:
        priority_intro = f"{name} chose {', '.join(item['title'].lower() for item in selected_priorities)} as the main priorities. "
    persona = (
        f"{risk_intro}{priority_intro}{name}'s strongest areas are {labels[high[0][0]]} and {labels[high[1][0]]}, while the clearest opportunities are "
        f"{labels[low[0][0]]}, {labels[low[1][0]]} and {labels[low[2][0]]}.{plan_lead} whole-person plan is to "
        f"{'; then '.join(actions[:4])}. This is a wellness summary rather than a diagnosis; seek prompt professional advice for new, worsening or worrying symptoms."
    )
    support_priorities = support_priorities_for(answers, scores, outcode)
    prevention_opportunities = prevention_opportunities_for(answers, scores)
    all_advice = support_priorities + prevention_opportunities
    priority_advice = []
    clinically_covered = {item.get("concern_id") for item in significant_risks}
    for priority in selected_priorities:
        if priority["id"] in clinically_covered:
            continue
        matched = next((item for item in all_advice if item.get("concern_id") == priority["id"]), None)
        priority_advice.append(matched or recommendation_for_concern(priority, outcode))
    clinical_advice = [{**item, "type": "clinical"} for item in significant_risks]
    recommendations = unique_items(clinical_advice + priority_advice + all_advice, "title")[:6]
    if not recommendations:
        recommendations.append({"title": "Keep the rhythm", "body": "Keep up regular movement, social contact, vaccinations, blood pressure checks, and a steady sleep routine.", "type": "maintenance"})
    videos = []
    if scores["independence"] < 75 or answers.get("falls_3_months") == "Yes":
        videos.extend([
            {
                "title": "Seated senior exercise",
                "category": "Movement",
                "url": "https://www.youtube.com/results?search_query=senior+seated+exercise+follow+along",
                "thumbnail": "https://img.youtube.com/vi/8BcPHWGQO44/hqdefault.jpg",
                "why": "A chair-based routine can feel safer when balance or confidence is lower.",
            },
            {
                "title": "Balance exercises for seniors",
                "category": "Movement",
                "url": "https://www.youtube.com/results?search_query=safe+balance+exercises+for+seniors",
                "thumbnail": "https://img.youtube.com/vi/z-tUHuNPStw/hqdefault.jpg",
                "why": "Balance practice helps reduce fall risk and supports everyday movement.",
            },
            {
                "title": "Gentle yoga for seniors",
                "category": "Movement",
                "url": "https://www.youtube.com/results?search_query=gentle+yoga+for+seniors+follow+along",
                "thumbnail": "https://img.youtube.com/vi/kFhG-ZzLNN4/hqdefault.jpg",
                "why": "Gentle yoga can support flexibility, breathing and calm.",
            },
        ])
    if scores["nutrition_vitality"] < 80 or answers.get("diet_concern") == "Yes":
        videos.extend([
            {
                "title": "Tuna egg salad, 27g protein",
                "category": "Food",
                "url": "https://www.youtube.com/watch?v=e2VUemyscvQ",
                "thumbnail": "https://img.youtube.com/vi/e2VUemyscvQ/hqdefault.jpg",
                "why": "Simple protein-rich meals can help preserve muscle and steady energy.",
            },
            {
                "title": "Mediterranean chickpea salad",
                "category": "Food",
                "url": "https://www.youtube.com/watch?v=jWCrEAvSZ8g",
                "thumbnail": "https://img.youtube.com/vi/jWCrEAvSZ8g/hqdefault.jpg",
                "why": "Low-salt, fibre-rich dinners can support blood pressure and cholesterol goals.",
            },
            {
                "title": "Peanut butter overnight oats",
                "category": "Food",
                "url": "https://www.youtube.com/watch?v=XemsXWiJ-eM",
                "thumbnail": "https://img.youtube.com/vi/XemsXWiJ-eM/hqdefault.jpg",
                "why": "Make-ahead oats are low effort and can support regular meals on tired mornings.",
            },
        ])
    if not videos:
        videos = [
            {
                "title": "Gentle daily movement",
                "category": "Movement",
                "url": "https://www.youtube.com/results?search_query=gentle+daily+exercise+for+seniors",
                "thumbnail": "https://img.youtube.com/vi/kFhG-ZzLNN4/hqdefault.jpg",
                "why": "A light daily routine can help maintain confidence, flexibility and mood.",
            },
            {
                "title": "Healthy simple meals",
                "category": "Food",
                "url": "https://www.youtube.com/watch?v=jWCrEAvSZ8g",
                "thumbnail": "https://img.youtube.com/vi/jWCrEAvSZ8g/hqdefault.jpg",
                "why": "Quick meal ideas make it easier to keep nutrition steady without much effort.",
            },
        ]
    return {
        "persona": persona,
        "recommendations": recommendations[:6],
        "videos": videos,
        "lowest_categories": [x[0] for x in low],
        "support_priorities": support_priorities,
        "prevention_opportunities": prevention_opportunities,
        "clinical_risks": clinical_risks,
        "identified_concerns": concerns,
        "selected_priorities": selected_priorities,
    }


def identified_concerns(answers: dict, scores: dict | None = None) -> list[dict]:
    scores = scores or score_answers(answers)
    concerns = []

    def add(identifier: str, title: str, detail: str, clinical: bool = False) -> None:
        concerns.append({"id": identifier, "title": title, "detail": detail, "clinical": clinical})

    simple = [
        ("vision", "Vision", "Seeing clearly or managing vision in everyday life", answers.get("vision_problem") == "Yes"),
        ("hearing", "Hearing", "Hearing conversations and sounds clearly", answers.get("hearing_problem") == "Yes"),
        ("teeth", "Teeth and mouth", "Comfort with teeth, mouth or dentures", answers.get("teeth_problem") == "Yes"),
        ("falls", "Falls", "Reducing the chance and consequences of another fall", answers.get("falls_3_months") == "Yes"),
        ("nutrition", "Diet and nutrition", "Making regular, nourishing meals easier", answers.get("diet_concern") == "Yes"),
        ("weight_loss", "Unintentional weight loss", "Reviewing recent weight loss and protecting nutrition", answers.get("lost_3kg") == "Yes"),
        ("movement", "Exercise and movement", "Building safe, regular movement", answers.get("regular_exercise") == "No"),
        ("vaccinations", "Vaccinations", "Checking which vaccinations are recommended", answers.get("vaccinations") in {"No", "Not sure"}),
        ("blood_pressure", "Blood pressure", "Arranging a recent blood-pressure check", answers.get("bp_checked") in {"No", "Not sure"}),
        ("independence", "Everyday independence", "Making shopping and personal routines easier", any(answers.get(key) == "No" for key in ["shopping", "dressing", "bathing", "toileting", "transfers", "indoors"])),
        ("home", "Your home", "Improving safety, comfort or suitability at home", answers.get("accommodation_problem") == "Yes"),
        ("finances", "Finances", "Getting help with essential costs or money worries", answers.get("finance_problem") == "Yes"),
        ("activities", "Activities and interests", "Doing more of the activities that matter to you", answers.get("participation_ok") == "No"),
        ("loneliness", "Loneliness and connection", "Finding comfortable ways to connect with other people", answers.get("lonely") == "Yes"),
        ("sleep", "Sleep", "Improving rest and daytime energy", answers.get("sleep_trouble") == "Yes"),
        ("pain", "Pain", "Reducing the effect of pain on daily life", answers.get("moderate_pain") == "Yes"),
        ("mood", "Mood and emotional wellbeing", "Getting the right support for low mood or loss of interest", answers.get("down_depressed") == "Yes" or answers.get("little_interest") == "Yes"),
        ("cognition", "Memory or thinking", "Reviewing changes in memory, orientation or thinking", any(answers.get(key) == "Yes" for key in ["forgetting", "confused_day_place", "memory_concern_other"])),
    ]
    significant_ids = {"falls", "weight_loss", "mood", "cognition"}
    for identifier, title, detail, flagged in simple:
        if flagged:
            add(identifier, title, detail, identifier in significant_ids)
    return concerns


def recommendation_for_concern(concern: dict, outcode: str) -> dict:
    suggestions = {
        "vision": ("Arrange an eye-health check", "An optician or GP can help review changes in vision and how they affect daily life.", "prevention"),
        "hearing": ("Arrange a hearing check", "A hearing assessment can identify practical aids and make conversations easier.", "prevention"),
        "teeth": ("Make eating more comfortable", "A dentist can review pain, chewing problems or denture fit; choose softer nourishing foods while waiting.", "nutrition"),
        "nutrition": ("Make nourishing meals easier", "Try regular simple meals with a protein food, vegetables and enough fluids; use delivery or prepared meals when helpful.", "nutrition"),
        "weight_loss": ("Ask for a prompt weight-loss review", "Unplanned weight loss of about 3 kg in three months should be discussed with a GP or suitable clinician.", "clinical"),
        "movement": ("Begin with gentle movement", "Start with short walks, chair-based movement or a supervised strength-and-balance class suited to your ability.", "movement"),
        "vaccinations": ("Check your vaccinations", "Ask a pharmacist or GP which vaccinations are currently recommended for you.", "prevention"),
        "blood_pressure": ("Arrange a blood-pressure check", "A pharmacy or GP can check your blood pressure and explain whether any follow-up is needed.", "prevention"),
        "independence": ("Make daily routines easier", "Compare grocery delivery, prepared meals and local care support; a council care-needs assessment may identify useful help.", "service"),
        "home": ("Improve comfort and safety at home", "Ask the council or an occupational therapy service about repairs, equipment, adaptations or housing advice.", "home"),
        "finances": ("Get a benefits and bills check", "A local advice service can review benefits, heating help, bills and other support.", "finance"),
        "activities": ("Return to something that matters", f"Choose one manageable hobby, class or interest group around {outcode} and plan a first visit.", "social"),
        "loneliness": ("Find a comfortable local connection", f"Look for an older-adult coffee morning, u3a group or wellbeing walk around {outcode}.", "social"),
        "sleep": ("Create a steadier sleep rhythm", "Keep a regular wake time, seek morning daylight and use a calmer wind-down routine.", "sleep"),
        "pain": ("Review persistent pain", "Discuss pain on most days with a GP or pharmacist so it does not unnecessarily limit sleep, movement or mood.", "clinical"),
        "mood": ("Talk about changes in mood", "Arrange a conversation with a GP or trusted health professional about persistent low mood or loss of interest.", "clinical"),
        "cognition": ("Discuss memory or thinking changes", "Ask a GP for a review, particularly when confusion occurs or someone close has noticed a change.", "clinical"),
        "falls": ("Arrange a falls review", "A GP or local falls service can review balance, medicines, vision and home risks after a recent fall.", "clinical"),
    }
    title, body, kind = suggestions.get(concern["id"], (concern["title"], concern["detail"], "maintenance"))
    return {"title": title, "body": body, "type": kind, "concern_id": concern["id"]}


def unique_items(items: list[dict], key: str) -> list[dict]:
    seen = set()
    result = []
    for item in items:
        value = item.get(key)
        if value not in seen:
            seen.add(value)
            result.append(item)
    return result


def support_priorities_for(answers: dict, scores: dict, outcode: str) -> list[dict]:
    priorities = []
    if scores["independence"] < 95:
        priorities.append({"title": "Make daily routines easier", "body": "Compare grocery delivery, prepared-meal services and local care support. A council care-needs assessment can also identify equipment or help at home.", "type": "service", "concern_id": "independence"})
    if answers.get("falls_3_months") == "Yes":
        priorities.append({"title": "Falls prevention support", "body": "A recent fall is worth discussing with a GP or falls service, especially after repeated falls or difficulty getting up from the floor.", "type": "movement", "concern_id": "falls"})
    if scores["wellbeing"] < 72:
        priorities.append({"title": "Wellbeing check-in", "body": "Mood, sleep, pain or loneliness may be affecting day-to-day life. A small support plan can help restore confidence.", "type": "local"})
    if scores["accommodation"] < 70:
        priorities.append({"title": "Home environment", "body": "Problems with the home can affect safety, comfort and confidence. Local housing or occupational therapy advice may help.", "type": "home", "concern_id": "home"})
    if scores["financial_wellbeing"] < 70:
        priorities.append({"title": "Money and benefits advice", "body": "Financial worries can affect wellbeing. Local advice services can help check benefits, bills and support options.", "type": "finance", "concern_id": "finances"})
    if scores["social_connection"] < 70:
        priorities.append({"title": "Find your local community", "body": f"Older-adult coffee mornings, u3a workshops, friendship groups and wellbeing walks around {outcode} can turn social contact into a regular part of the week.", "type": "social", "concern_id": "loneliness"})
    return priorities


def prevention_opportunities_for(answers: dict, scores: dict) -> list[dict]:
    opportunities = []
    if answers.get("regular_exercise") == "No":
        opportunities.append({"title": "WHO prevention opportunity: movement", "body": "Gentle activity, balance practice and strength work can support independence and reduce preventable decline.", "type": "movement", "concern_id": "movement"})
    if answers.get("vaccinations") in {"No", "Not sure"}:
        opportunities.append({"title": "Vaccination review", "body": "Checking recommended vaccinations with a pharmacist or GP can reduce avoidable illness risk.", "type": "prevention", "concern_id": "vaccinations"})
    if answers.get("bp_checked") in {"No", "Not sure"}:
        opportunities.append({"title": "Blood pressure check", "body": "Arrange a blood-pressure check with a pharmacy or GP. The NHS and WHO links below explain why checks matter and what to discuss with a clinician.", "type": "prevention", "concern_id": "blood_pressure"})
    if scores["nutrition_vitality"] < 72:
        opportunities.append({"title": "Nutrition opportunity", "body": "Protein-rich meals, vegetables and regular eating can support muscle, immunity and energy.", "type": "nutrition", "concern_id": "nutrition"})
    if scores["sleep_recovery"] < 68:
        opportunities.append({"title": "Sleep routine", "body": "A consistent wake time, morning daylight and calmer evenings can support recovery and daytime energy.", "type": "sleep", "concern_id": "sleep"})
    return opportunities


def clinical_risks_for(answers: dict, scores: dict) -> list[dict]:
    risks = []
    if answers.get("falls_3_months") == "Yes":
        detail = "Repeated falls or difficulty getting up from the floor increase the importance of a prompt review." if answers.get("falls_frequency") in {"Twice", "Three or more times"} or answers.get("falls_get_up") == "Yes" else "Even one recent fall is worth reviewing to reduce the chance of injury or another fall."
        risks.append({"title": "Risk related to falls", "body": f"{detail} Discuss this with a GP or local falls service. Call 999 after a fall if there may be a head, back, neck or hip injury, or if the person cannot get up.", "significant": True, "concern_id": "falls"})
    if answers.get("lost_3kg") == "Yes":
        risks.append({"title": "Unintentional weight loss", "body": "Losing around 3 kg without trying in three months should be discussed promptly with a GP or suitable clinician, particularly if appetite, swallowing or energy has changed.", "significant": True, "concern_id": "weight_loss"})
    mood_significant = scores.get("gds_15", 0) > 5 or (answers.get("down_depressed") == "Yes" and answers.get("little_interest") == "Yes")
    if mood_significant:
        risks.append({"title": "Possible depression", "body": "The answers suggest that a fuller assessment of mood would be helpful. Arrange an appointment with a GP or suitable mental-health professional; this screening result is not a diagnosis.", "significant": True, "concern_id": "mood"})
    cognitive_flags = sum(answers.get(key) == "Yes" for key in ["forgetting", "confused_day_place", "memory_concern_other"])
    cognition_significant = cognitive_flags >= 2 or answers.get("confused_day_place") == "Yes" or answers.get("memory_concern_other") == "Yes"
    if cognition_significant:
        risks.append({"title": "Possible cognitive impairment", "body": "Changes in memory, orientation or thinking should be discussed with a GP, especially when confusion occurs or someone close has noticed a change.", "significant": True, "concern_id": "cognition"})
    if answers.get("moderate_pain") == "Yes":
        risks.append({"title": "Persistent pain", "body": "Moderate or severe pain most days is worth reviewing so it does not unnecessarily limit sleep, movement or mood.", "significant": False})
    if not mood_significant and (answers.get("down_depressed") == "Yes" or answers.get("little_interest") == "Yes"):
        risks.append({"title": "Low mood or loss of interest", "body": "Persistent changes in mood or interest are important to discuss with a GP or trusted professional, even when the follow-up score is below the screening threshold.", "significant": False})
    if not cognition_significant and cognitive_flags:
        risks.append({"title": "Memory change", "body": "A change in memory is worth monitoring and discussing with a GP if it persists, worsens or affects daily life.", "significant": False})
    if answers.get("vision_problem") == "Yes" or answers.get("hearing_problem") == "Yes":
        risks.append({"title": "Vision or hearing", "body": "Vision or hearing changes can affect independence and falls risk, so an eye or hearing check may help.", "significant": False})
    if answers.get("bp_checked") in {"No", "Not sure"}:
        risks.append({"title": "Unknown blood pressure", "body": "Without a recent blood-pressure check, an important cardiovascular risk may be missed. Arrange a check with a pharmacy or GP.", "significant": False})
    return risks[:6]


def age_from_dob(dob: str) -> int | None:
    try:
        born = date.fromisoformat(dob)
    except (TypeError, ValueError):
        return None
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
