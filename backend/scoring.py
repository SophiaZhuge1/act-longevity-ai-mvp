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
    mobility = round(sum([
        yes_good(answers.get("falls_3_months", ""), False),
        yes_good(answers.get("regular_exercise", ""), True),
        ability_score(answers.get("indoors", "")),
        ability_score(answers.get("transfers", "")),
        yes_good(answers.get("moderate_pain", ""), False),
        independence,
    ]) / 6)
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
    cardiometabolic = round(sum([
        yes_good(answers.get("regular_exercise", ""), True),
        100 if answers.get("bp_checked") == "Yes" else 50,
        nutrition,
        round((sleep_hours + sleep_quality + yes_good(answers.get("sleep_trouble", ""), False)) / 3),
    ]) / 4)
    return {
        "cardiometabolic": cardiometabolic,
        "mobility_independence": mobility,
        "sleep_recovery": round((sleep_hours + sleep_quality + yes_good(answers.get("sleep_trouble", ""), False)) / 3),
        "nutrition_vitality": nutrition,
        "mental_wellbeing": mental,
        "cognition_sensory": cognition,
        "social_connection": social,
        "preventive_care": preventive,
    }


def persona_and_recommendations(profile: dict, answers: dict, scores: dict) -> dict:
    low = sorted(scores.items(), key=lambda x: x[1])[:3]
    high = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
    name = profile.get("name") or "This member"
    outcode = (profile.get("postcode") or answers.get("postcode") or "local").split()[0]
    persona = (
        f"{name} is an older adult in the {profile.get('age_band', '70-90')} age range. "
        f"The strongest areas are {high[0][0].replace('_', ' ')} and {high[1][0].replace('_', ' ')}. "
        f"The main opportunity areas are {low[0][0].replace('_', ' ')}, {low[1][0].replace('_', ' ')}, "
        f"and {low[2][0].replace('_', ' ')}. Recommendations should be gentle, local, practical, and easy to start."
    )
    recommendations = []
    if scores["mobility_independence"] < 68:
        recommendations += [
            {"title": "Gentle movement", "body": "Take a short walk, do light stretching, or follow a senior yoga video to maintain flexibility and heart health.", "type": "movement"},
            {"title": "Balance and strength", "body": "Try heel-to-toe raises, wall push-ups, and sit-to-stand movements from a sturdy chair to help prevent falls.", "type": "movement"},
        ]
    if ability_score(answers.get("shopping", "")) < 80:
        recommendations.append({"title": "Shopping support", "body": "Grocery delivery or meal-prep services can reduce fatigue and make regular nutritious meals easier.", "type": "service"})
    if scores["sleep_recovery"] < 68:
        recommendations.append({"title": "Sleep rhythm", "body": "Keep a consistent wake-up time, get morning daylight, and avoid late caffeine to support deeper sleep.", "type": "sleep"})
    if scores["nutrition_vitality"] < 68:
        recommendations.append({"title": "Protein and plants", "body": "Add one protein food and one vegetable to lunch or dinner to support muscle, immunity, and steady energy.", "type": "nutrition"})
    if scores["social_connection"] < 70:
        recommendations.append({"title": "Local connection", "body": f"Look for older-adult coffee mornings, library groups, walking groups, or gentle classes around {outcode}.", "type": "local"})
    if scores["preventive_care"] < 75 or scores["cardiometabolic"] < 68:
        recommendations.append({"title": "Blood pressure basics", "body": "Book a blood pressure check and consider fibre-rich foods, oily fish, and pharmacist guidance before trying supplements.", "type": "prevention"})
    if not recommendations:
        recommendations.append({"title": "Keep the rhythm", "body": "Maintain regular movement, social contact, vaccinations, blood pressure checks, and a steady sleep routine.", "type": "maintenance"})
    videos = []
    if scores["mobility_independence"] < 75:
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
    return {"persona": persona, "recommendations": recommendations[:6], "videos": videos, "lowest_categories": [x[0] for x in low]}
