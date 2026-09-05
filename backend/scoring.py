from __future__ import annotations

import hashlib
import math


QUESTIONS = [
    {"id": "dob", "section": "Personal Info", "text": "What is your date of birth?", "type": "date"},
    {"id": "gender", "section": "Personal Info", "text": "Which gender best describes you?", "type": "choice", "options": ["Female", "Male", "Non-binary", "Prefer not to say"]},
    {"id": "marital_status", "section": "Personal Info", "text": "What is your marital status?", "type": "choice", "options": ["Single", "Married", "Partnered", "Widowed", "Divorced"]},
    {"id": "living_arrangement", "section": "Home Life", "text": "How do you usually live?", "type": "choice", "options": ["Alone", "Couple", "With extended family", "Care home", "Assisted living"]},
    {"id": "care_support", "section": "Home Life", "text": "Does someone help care for you?", "type": "choice", "options": ["No", "Yes - partner", "Yes - children", "Yes - other relatives", "Yes - paid carer"]},
    {"id": "education_level", "section": "Background", "text": "What is your highest education level?", "type": "choice", "options": ["No formal education", "Primary", "Secondary", "University", "Higher postgraduate degree"]},
    {"id": "employment_status", "section": "Background", "text": "What is your current employment status?", "type": "choice", "options": ["Retired", "Employed - full time", "Employed - part time", "Self-employed", "Volunteering"]},
    {"id": "employment_sector", "section": "Background", "text": "Which work sector best describes your main career?", "type": "choice", "options": ["Healthcare", "Education", "Public sector", "Retail", "Manufacturing", "Finance", "Homemaker", "Other", "Not applicable"]},
    {"id": "postcode", "section": "Contact", "text": "What postcode area should we use for nearby ideas?", "type": "text", "placeholder": "Example: SW1A"},
    {"id": "vision_problem", "section": "Staying Healthy", "text": "Do you have a problem with your vision?", "type": "yesno"},
    {"id": "hearing_problem", "section": "Staying Healthy", "text": "Do you have a problem with your hearing?", "type": "yesno"},
    {"id": "teeth_problem", "section": "Staying Healthy", "text": "Do you have a problem with your teeth?", "type": "yesno"},
    {"id": "falls_3_months", "section": "Staying Healthy", "text": "Have you had any falls in the last 3 months?", "type": "yesno"},
    {"id": "diet_concern", "section": "Staying Healthy", "text": "Do you have any concerns about your diet or nutrition?", "type": "yesno"},
    {"id": "lost_3kg", "section": "Staying Healthy", "text": "Have you unintentionally lost 3kg in the last three months?", "type": "yesno"},
    {"id": "regular_exercise", "section": "Staying Healthy", "text": "Do you take regular exercise?", "type": "yesno"},
    {"id": "vaccinations", "section": "Staying Healthy", "text": "Are you up to date with your vaccinations?", "type": "choice", "options": ["Yes", "No", "Not sure"]},
    {"id": "bp_checked", "section": "Staying Healthy", "text": "Has your blood pressure been checked in the last year?", "type": "choice", "options": ["Yes", "No", "Not sure"]},
    {"id": "sleep_hours", "section": "Sleep", "text": "On most nights, how many hours do you sleep?", "type": "choice", "options": ["Less than 5", "5-6", "6-7", "7-8", "8-9", "More than 9"]},
    {"id": "sleep_quality", "section": "Sleep", "text": "How rested do you usually feel in the morning?", "type": "choice", "options": ["Refreshed", "Mostly rested", "Mixed", "Usually tired", "Exhausted"]},
    {"id": "protein_veg", "section": "Nutrition", "text": "How often do you eat protein foods and vegetables in the same day?", "type": "choice", "options": ["Rarely", "A few days a week", "Most days", "Every day"]},
    {"id": "shopping", "section": "Independence", "text": "Are you able to do your shopping?", "type": "ability"},
    {"id": "dressing", "section": "Independence", "text": "Can you dress yourself?", "type": "ability"},
    {"id": "bathing", "section": "Independence", "text": "Can you use a bath or shower by yourself?", "type": "ability"},
    {"id": "toileting", "section": "Independence", "text": "Can you use the toilet or commode?", "type": "ability"},
    {"id": "transfers", "section": "Independence", "text": "Can you move yourself from bed to chair?", "type": "ability"},
    {"id": "indoors", "section": "Independence", "text": "Can you get around indoors?", "type": "ability"},
    {"id": "home_problems", "section": "Wellbeing", "text": "Do you have problems with the place where you live?", "type": "yesno"},
    {"id": "finance_problems", "section": "Wellbeing", "text": "Do you have problems with your finances?", "type": "yesno"},
    {"id": "activities", "section": "Wellbeing", "text": "Can you pursue leisure interests, hobbies, work or learning activities important to you?", "type": "yesno"},
    {"id": "lonely", "section": "Wellbeing", "text": "Do you often feel lonely?", "type": "yesno"},
    {"id": "sleep_trouble", "section": "Wellbeing", "text": "Have you had any trouble sleeping in the last month?", "type": "yesno"},
    {"id": "moderate_pain", "section": "Wellbeing", "text": "Do you suffer from moderate or severe pain most days?", "type": "yesno"},
    {"id": "down_depressed", "section": "Wellbeing", "text": "Have you often been bothered by feeling down, depressed or hopeless?", "type": "yesno"},
    {"id": "life_satisfied", "section": "Wellbeing", "text": "Are you basically satisfied with your life?", "type": "yesno"},
    {"id": "often_bored", "section": "Wellbeing", "text": "Do you often get bored?", "type": "yesno"},
    {"id": "memory_more", "section": "Cognition", "text": "Do you feel you have more problems with memory than most?", "type": "yesno"},
    {"id": "forgetting", "section": "Cognition", "text": "In the past year, have you noticed forgetting things more than usual?", "type": "yesno"},
    {"id": "confused_day_place", "section": "Cognition", "text": "Do you sometimes feel confused about what day it is or where you are?", "type": "yesno"},
    {"id": "memory_concern_other", "section": "Cognition", "text": "Has anyone close to you raised concerns about your memory or thinking?", "type": "yesno"},
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


def score_answers(answers: dict) -> dict:
    independence_ids = ["shopping", "dressing", "bathing", "toileting", "transfers", "indoors"]
    independence = round(sum(ability_score(answers.get(k, "")) for k in independence_ids) / len(independence_ids))
    sleep_hours = {"Less than 5": 25, "5-6": 48, "6-7": 66, "7-8": 92, "8-9": 82, "More than 9": 56}.get(answers.get("sleep_hours"), 62)
    sleep_quality = {"Refreshed": 96, "Mostly rested": 84, "Mixed": 64, "Usually tired": 40, "Exhausted": 22}.get(answers.get("sleep_quality"), 60)
    nutrition = round(sum([
        yes_good(answers.get("diet_concern", ""), False),
        yes_good(answers.get("lost_3kg", ""), False),
        {"Rarely": 30, "A few days a week": 55, "Most days": 78, "Every day": 92}.get(answers.get("protein_veg"), 55),
    ]) / 3)
    mental = round(sum([
        yes_good(answers.get("down_depressed", ""), False),
        yes_good(answers.get("life_satisfied", ""), True),
        yes_good(answers.get("often_bored", ""), False),
    ]) / 3)
    cognition = round(sum([
        yes_good(answers.get("memory_more", ""), False),
        yes_good(answers.get("forgetting", ""), False),
        yes_good(answers.get("confused_day_place", ""), False),
        yes_good(answers.get("memory_concern_other", ""), False),
        yes_good(answers.get("vision_problem", ""), False),
        yes_good(answers.get("hearing_problem", ""), False),
    ]) / 6)
    social = round(sum([
        yes_good(answers.get("lonely", ""), False),
        yes_good(answers.get("activities", ""), True),
        yes_good(answers.get("often_bored", ""), False),
    ]) / 3)
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
    wellbeing = round(sum([
        mental,
        social,
        round((sleep_hours + sleep_quality + yes_good(answers.get("sleep_trouble", ""), False)) / 3),
        yes_good(answers.get("moderate_pain", ""), False),
    ]) / 4)
    accommodation = yes_good(answers.get("home_problems", ""), False)
    financial = yes_good(answers.get("finance_problems", ""), False)
    return {
        "staying_healthy": staying_healthy,
        "independence": independence,
        "wellbeing": wellbeing,
        "accommodation": accommodation,
        "financial_wellbeing": financial,
        "nutrition_vitality": nutrition,
        "sleep_recovery": round((sleep_hours + sleep_quality + yes_good(answers.get("sleep_trouble", ""), False)) / 3),
        "social_connection": social,
        "cognition_sensory": cognition,
        "preventive_care": preventive,
    }


def persona_and_recommendations(profile: dict, answers: dict, scores: dict) -> dict:
    public_scores = {key: scores[key] for key in ["staying_healthy", "independence", "wellbeing", "accommodation", "financial_wellbeing"]}
    low = sorted(public_scores.items(), key=lambda x: x[1])[:3]
    high = sorted(public_scores.items(), key=lambda x: x[1], reverse=True)[:2]
    name = profile.get("name") or "This member"
    outcode = (profile.get("postcode") or answers.get("postcode") or "local").split()[0]
    persona = (
        f"{name} has completed the ACT Assess taster for a Healthy Longevity Profile. "
        f"The strongest areas are {high[0][0].replace('_', ' ')} and {high[1][0].replace('_', ' ')}. "
        f"The main opportunity areas are {low[0][0].replace('_', ' ')}, {low[1][0].replace('_', ' ')}, "
        f"and {low[2][0].replace('_', ' ')}. The summary is intended to support prevention, confidence and the next conversation with a clinician or trusted supporter."
    )
    support_priorities = support_priorities_for(answers, scores, outcode)
    prevention_opportunities = prevention_opportunities_for(answers, scores)
    clinical_risks = clinical_risks_for(answers, scores)
    recommendations = [
        {"title": item["title"], "body": item["body"], "type": item["type"]}
        for item in (support_priorities + prevention_opportunities)[:6]
    ]
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
    if scores["nutrition_vitality"] < 75:
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
    }


def support_priorities_for(answers: dict, scores: dict, outcode: str) -> list[dict]:
    priorities = []
    if scores["independence"] < 72:
        priorities.append({"title": "Daily independence support", "body": "A few practical adjustments around shopping, bathing or moving around indoors could make daily routines easier and safer.", "type": "service"})
    if answers.get("falls_3_months") == "Yes":
        priorities.append({"title": "Falls prevention support", "body": "A recent fall is worth discussing with a GP, pharmacist or falls service, especially if confidence with movement has changed.", "type": "movement"})
    if scores["wellbeing"] < 72:
        priorities.append({"title": "Wellbeing check-in", "body": "Mood, sleep, pain or loneliness may be affecting day-to-day life. A small support plan can help restore confidence.", "type": "local"})
    if scores["accommodation"] < 70:
        priorities.append({"title": "Home environment", "body": "Problems with the home can affect safety, comfort and confidence. Local housing or occupational therapy advice may help.", "type": "home"})
    if scores["financial_wellbeing"] < 70:
        priorities.append({"title": "Money and benefits advice", "body": "Financial worries can affect wellbeing. Local advice services can help check benefits, bills and support options.", "type": "finance"})
    if scores["social_connection"] < 70:
        priorities.append({"title": "Connection nearby", "body": f"Coffee mornings, library groups, walking groups or older-adult activities around {outcode} could help rebuild regular contact.", "type": "social"})
    return priorities


def prevention_opportunities_for(answers: dict, scores: dict) -> list[dict]:
    opportunities = []
    if answers.get("regular_exercise") == "No":
        opportunities.append({"title": "WHO prevention opportunity: movement", "body": "Gentle activity, balance practice and strength work can support independence and reduce preventable decline.", "type": "movement"})
    if answers.get("vaccinations") in {"No", "Not sure"}:
        opportunities.append({"title": "Vaccination review", "body": "Checking recommended vaccinations with a pharmacist or GP can reduce avoidable illness risk.", "type": "prevention"})
    if answers.get("bp_checked") in {"No", "Not sure"}:
        opportunities.append({"title": "Blood pressure check", "body": "A recent blood pressure reading is a simple prevention step and can highlight risks early.", "type": "prevention"})
    if scores["nutrition_vitality"] < 72:
        opportunities.append({"title": "Nutrition opportunity", "body": "Protein-rich meals, vegetables and regular eating can support muscle, immunity and energy.", "type": "nutrition"})
    if scores["sleep_recovery"] < 68:
        opportunities.append({"title": "Sleep routine", "body": "A consistent wake time, morning daylight and calmer evenings can support recovery and daytime energy.", "type": "sleep"})
    return opportunities


def clinical_risks_for(answers: dict, scores: dict) -> list[dict]:
    risks = []
    if answers.get("falls_3_months") == "Yes":
        risks.append({"title": "Falls", "body": "A fall in the last three months should be discussed with a doctor or local falls service."})
    if answers.get("lost_3kg") == "Yes":
        risks.append({"title": "Unplanned weight loss", "body": "Unintentional weight loss may need a clinical review, especially if appetite or energy has changed."})
    if answers.get("moderate_pain") == "Yes":
        risks.append({"title": "Persistent pain", "body": "Moderate or severe pain most days is worth reviewing so it does not limit sleep, movement or mood."})
    if answers.get("down_depressed") == "Yes":
        risks.append({"title": "Low mood", "body": "Feeling down, depressed or hopeless is important to discuss with a GP or trusted professional."})
    if any(answers.get(key) == "Yes" for key in ["memory_more", "forgetting", "confused_day_place", "memory_concern_other"]):
        risks.append({"title": "Memory or thinking", "body": "Changes in memory or confusion should be discussed with a clinician, especially if others have noticed it too."})
    if answers.get("vision_problem") == "Yes" or answers.get("hearing_problem") == "Yes":
        risks.append({"title": "Senses", "body": "Vision or hearing changes can affect independence and falls risk, so an eye or hearing check may help."})
    if answers.get("bp_checked") in {"No", "Not sure"}:
        risks.append({"title": "Unknown blood pressure", "body": "Without a recent blood pressure check, an important cardiovascular risk may be missed."})
    if not risks:
        risks.append({"title": "No urgent flags from this taster", "body": "No major clinical discussion points were identified from the current answers, but this is not a diagnosis."})
    return risks[:6]
