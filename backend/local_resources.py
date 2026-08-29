from __future__ import annotations


LOCAL_RESOURCES = [
    {"name": "Age UK local activities", "kind": "social", "icon": "users", "why": "Good first stop for coffee mornings, advice and older-adult social groups.", "url": "https://www.ageuk.org.uk/services/in-your-area/"},
    {"name": "u3a groups", "kind": "learning", "icon": "book", "why": "Local learning and interest groups can support purpose, memory and social connection.", "url": "https://www.u3a.org.uk/find"},
    {"name": "Ramblers Wellbeing Walks", "kind": "movement", "icon": "walking", "why": "Short group walks can be a friendly way to add gentle movement safely.", "url": "https://www.ramblers.org.uk/go-walking/wellbeing-walks"},
    {"name": "NHS Better Health - exercise", "kind": "movement", "icon": "heart", "why": "Reliable public-health guidance for building movement gradually.", "url": "https://www.nhs.uk/better-health/get-active/"},
    {"name": "Iceland Food Club", "kind": "shopping", "icon": "shopping", "why": "A grocery option that may help people who struggle with regular shopping.", "url": "https://www.iceland.co.uk/food-club"},
    {"name": "Wiltshire Farm Foods", "kind": "meal_delivery", "icon": "meal", "why": "Prepared frozen meals can help maintain nutrition when cooking or shopping is tiring.", "url": "https://www.wiltshirefarmfoods.com/"},
]


def resources_for(scores: dict, postcode: str = "") -> list[dict]:
    wanted = set()
    if scores.get("social_connection", 100) < 70:
        wanted.update(["social", "learning"])
    if scores.get("mobility_independence", 100) < 70:
        wanted.update(["movement", "video"])
    if scores.get("nutrition_vitality", 100) < 70:
        wanted.update(["shopping", "meal_delivery"])
    if not wanted:
        wanted.update(["movement", "social", "learning"])
    return [{**r, "postcode_hint": postcode.split()[0] if postcode else "local"} for r in LOCAL_RESOURCES if r["kind"] in wanted]
