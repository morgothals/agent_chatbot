import json
import re
from pathlib import Path
from tools import call_gemini_api
from validator import validate_intent, validate_entities, ValidationError

# ——————————————————————————————————————————————
# Konfiguráció betöltése
# ——————————————————————————————————————————————
CONFIG_DIR = Path(__file__).parent / "config"
INTENTS = json.loads((CONFIG_DIR / "intents.json").read_text(encoding="utf-8"))
ENTITIES = json.loads((CONFIG_DIR / "entities.json").read_text(encoding="utf-8"))
VALID_INTENTS = ", ".join(INTENTS.keys())

def parse_user_input(text: str) -> dict:
    """
    Meghívja a Gemini-2.0-flash modellt, hogy felismerje az intent-et és az entitásokat.
    Csak tiszta JSON-t várunk vissza.
    """
    # Normalizáció
    text = text.strip()
    text = re.sub(r"\b([Aa][0-9]{4}) as\b", r"\1-as", text)
    text = re.sub(r"\ba\s+([AEIOUÁÉÍÓÖŐÚÜŰaeiouáéíóöőúüű])", r"az \1", text)

    prompt = f"""System:
Az alábbi intent-ek közül válassz: {VALID_INTENTS}.
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
    clean = re.sub(r"^```json\s*|\s*```$", "", raw.strip())

    try:
        data = json.loads(clean)
        return {
            "intent": data.get("intent"),
            "entities": data.get("entities", {})
        }
    except json.JSONDecodeError:
        return {"intent": None, "entities": {}}


def plan(text: str) -> dict:
    """
    Planner főfüggvénye:
      1) parse_user_input → intent+entities
      2) hibakezelés:
         - nincs intent → error
         - több order_id → clarify
         - hiányzó kötelező entity → error
         - validációs hiba → error
      3) siker → { intent, entities }
    """
    parsed = parse_user_input(text)
    intent = parsed.get("intent")
    entities = parsed.get("entities", {})

    # nincs intent
    if not intent:
        return {"error": "Sajnálom, nem értettem a kérdés típusát. Kérlek, fogalmazd át!"}

    # többféle order_id esetén tisztázó kérdés
    if intent in ("order_status", "shipping_time"):
        oid = entities.get("order_id")
        if isinstance(oid, list) and len(oid) > 1:
            opts = " vagy ".join(oid)
            return {"clarify": f"Melyik rendelésre gondolsz: {opts}?"}

    # hiányzó kötelező entitások
    required = INTENTS.get(intent, {}).get("required_entities", [])
    missing = [e for e in required if e not in entities or not entities[e]]
    if missing:
        names = ", ".join(missing)
        return {"error": f"Kérem, add meg a következő adatot a folytatáshoz: {names}."}

    # validáció
    try:
        validate_intent(intent)
        validate_entities(intent, entities)
    except ValidationError as e:
        return {"error": str(e)}

    # minden rendben
    return {"intent": intent, "entities": entities}


if __name__ == "__main__":
    # Gyors manuális teszt
    samples = [
        "Hol tart az A1003-as rendelésem?",
        "Mikorra várható az A1005 szállítása?",
        "Foo Bar",
        # Több entity demo (itt a plan-t monkeypatch-eld a teszt során)
    ]
    for utt in samples:
        print(f">>> {utt}\n    → {plan(utt)}\n")
