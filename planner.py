import json
import re
from pathlib import Path
from tools import call_gemini_api
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
    Meghívja a Gemini modellt, hogy felismerje az intent-et és az entitásokat.
    Csak tiszta JSON-t várunk vissza.
    """
    prompt = f"""System:
Elemezd a következő felhasználói mondatot, és add vissza kizárólag JSON formátumban:
  {{
    "intent": "...",
    "entities": {{ ... }}
  }}
Ne írj semmi mást, csak a tiszta JSON-t.

User:
"{text}"
"""

    raw = call_gemini_api(model="gemini-2.0-flash", contents=prompt)
    # Tisztítás: eltávolítjuk a ```json ... ``` kereteket, ha vannak
    clean = re.sub(r"^```json\s*|\s*```$", "", raw.strip())

    try:
        data = json.loads(clean)
        return {
            "intent": data.get("intent"),
            "entities": data.get("entities", {})
        }
    except json.JSONDecodeError:
        return {"intent": None, "entities": {}}

if __name__ == "__main__":
    sample = "Hol tart az A1003-as rendelésem?"
    print("Parsed intent/entities:", parse_user_input(sample))
