import json
from pathlib import Path
from tools import call_gemini_api  # Feltételezzük, hogy a tools.py tartalmaz egy ilyen függvényt
from validator import validate_intent, validate_entities, ValidationError

# Konfiguráció betöltése
CONFIG_DIR = Path(__file__).parent / "config"
INTENTS = json.loads((CONFIG_DIR / "intents.json").read_text(encoding="utf-8"))
ENTITIES = json.loads((CONFIG_DIR / "entities.json").read_text(encoding="utf-8"))


def plan(text: str) -> dict:
    parsed = parse_user_input(text)
    try:
        validate_intent(parsed["intent"])
        validate_entities(parsed["intent"], parsed["entities"])
    except ValidationError as e:
        return {"error": str(e)}
    return parsed


def parse_user_input(text: str) -> dict:
    """
    Meghívja a Gemini modellt, hogy felismerje a szándékot (intent) és az
    entitásokat (order_id, stb.) a szövegben.
    Visszatérési formátum: { "intent": str, "entities": { ... } }
    """
    prompt = f"""
System: Elemezd a következő mondatot, és add vissza JSON formátumban:
  - intent: melyik intent-be tartozik?
  - entities: a szükséges entitások kulcs-érték párjai

User: "{text}"
    
Válasz JSON-ként, pl.:
{{
  "intent": "order_status",
  "entities": {{ "order_id": "A1003" }}
}}
"""
    # API hívás
    response = call_gemini_api(
        model="gemini-2.0-flash",
        prompt=prompt
    )
    try:
        data = json.loads(response)
        return {
            "intent": data.get("intent"),
            "entities": data.get("entities", {})
        }
    except json.JSONDecodeError:
        # Ha nem valid JSON érkezik, fallback üzenet
        return {"intent": None, "entities": {}}



# Példa használat
if __name__ == "__main__":
    sample = "Hol tart az A1003-as rendelésem?"
    result = parse_user_input(sample)
    print("Parsed intent/entities:", result)
