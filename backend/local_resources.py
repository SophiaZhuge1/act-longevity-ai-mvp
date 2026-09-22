from __future__ import annotations


LOCAL_RESOURCES = [
    {"name": "Age UK social groups and activities", "kind": "social", "category": "Community near you", "icon": "users", "why": "Find coffee mornings, friendship groups, lunch clubs, arts, quizzes and other activities designed for older people.", "url": "https://www.ageuk.org.uk/services/in-your-area/social-activities/?ClearMultiLocationData=true", "search_query": "Age UK social activities for older people", "local_search": True},
    {"name": "u3a workshops and interest groups", "kind": "learning", "category": "Community near you", "icon": "book", "why": "Local workshops, talks and shared-interest groups can provide regular contact, purpose and opportunities to learn.", "url": "https://www.u3a.org.uk/find", "search_query": "u3a workshops and groups", "local_search": True},
    {"name": "Ramblers Wellbeing Walks", "kind": "movement", "category": "Community near you", "icon": "walking", "why": "Short, friendly group walks offer gentle movement and a chance to meet people locally.", "url": "https://www.ramblers.org.uk/go-walking/wellbeing-walks", "search_query": "Ramblers Wellbeing Walks", "local_search": True},
    {"name": "Older-adult exercise classes", "kind": "movement", "category": "Community near you", "icon": "walking", "why": "Search for chair exercise, strength and balance, tai chi or gentle yoga classes intended for older adults.", "url": "https://www.ageuk.org.uk/services/in-your-area/exercise/", "search_query": "exercise classes for older adults", "local_search": True},
    {"name": "Grocery delivery services", "kind": "shopping", "category": "Practical support", "icon": "shopping", "why": "Home delivery can make regular shopping easier; compare delivery slots and accessibility across local supermarkets.", "url": "https://www.tesco.com/groceries/en-GB/", "search_query": "grocery delivery service", "local_search": True},
    {"name": "Prepared meals delivered at home", "kind": "meal_delivery", "category": "Practical support", "icon": "meal", "why": "Ready-made meals can help maintain regular nutrition when shopping, standing or cooking feels tiring.", "url": "https://www.gov.uk/meals-home", "search_query": "meals on wheels older people", "local_search": True},
    {"name": "Care needs assessment", "kind": "care", "category": "Practical support", "icon": "home", "why": "Your council can assess whether help at home, equipment, adaptations or day services could support your independence.", "url": "https://www.gov.uk/apply-needs-assessment-social-services", "search_query": "adult social care needs assessment", "local_search": True},
    {"name": "CQC-regulated home care", "kind": "care", "category": "Practical support", "icon": "home", "why": "Use the independent regulator's directory and inspection reports when comparing home-care providers.", "url": "https://www.cqc.org.uk/care-services", "search_query": "CQC regulated home care", "local_search": True},
    {"name": "NHS high blood pressure guidance", "kind": "health_guidance", "category": "Trusted health guidance", "icon": "heart", "why": "Clear NHS information on blood pressure checks, readings, treatment and when to seek medical help.", "url": "https://www.nhs.uk/conditions/high-blood-pressure/", "local_search": False},
    {"name": "WHO hypertension information", "kind": "health_guidance", "category": "Trusted health guidance", "icon": "heart", "why": "Evidence-based information on hypertension, risk factors, prevention and treatment from the World Health Organization.", "url": "https://www.who.int/news-room/fact-sheets/detail/hypertension", "local_search": False},
    {"name": "NHS Better Health movement guidance", "kind": "health_guidance", "category": "Trusted health guidance", "icon": "heart", "why": "Reliable guidance for building physical activity gradually alongside your own health needs.", "url": "https://www.nhs.uk/better-health/get-active/", "local_search": False},
]


def resources_for(scores: dict, postcode: str = "", answers: dict | None = None) -> list[dict]:
    answers = answers or {}
    wanted = set()
    if scores.get("social_connection", 100) < 70:
        wanted.update(["social", "learning", "community_movement"])
    if scores.get("independence", 100) < 95 or any(answers.get(key) == "No" for key in ["shopping", "dressing", "bathing", "toileting", "transfers", "indoors"]):
        wanted.update(["shopping", "meal_delivery", "care"])
    if scores.get("nutrition_vitality", 100) < 72 or answers.get("diet_concern") == "Yes":
        wanted.update(["shopping", "meal_delivery"])
    if scores.get("staying_healthy", 100) < 72 or answers.get("regular_exercise") == "No":
        wanted.update(["community_movement", "movement_guidance"])
    if answers.get("bp_checked") in {"No", "Not sure"}:
        wanted.add("blood_pressure")
    if scores.get("accommodation", 100) < 70:
        wanted.add("care")
    if not wanted:
        wanted.update(["social", "learning", "community_movement", "movement_guidance"])

    selected = []
    for resource in LOCAL_RESOURCES:
        name = resource["name"]
        include = (
            (resource["kind"] == "social" and "social" in wanted)
            or (resource["kind"] == "learning" and "learning" in wanted)
            or (name in {"Ramblers Wellbeing Walks", "Older-adult exercise classes"} and "community_movement" in wanted)
            or (resource["kind"] == "shopping" and "shopping" in wanted)
            or (resource["kind"] == "meal_delivery" and "meal_delivery" in wanted)
            or (resource["kind"] == "care" and "care" in wanted)
            or (name in {"NHS high blood pressure guidance", "WHO hypertension information"} and "blood_pressure" in wanted)
            or (name == "NHS Better Health movement guidance" and "movement_guidance" in wanted)
        )
        if include:
            selected.append({**resource, "postcode_hint": postcode.split()[0].upper() if postcode else "your area"})
    return selected
