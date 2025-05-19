import re
import json
from pathlib import Path

# Konfiguráció betöltése
CONFIG_DIR = Path(__file__).parent / "config"
INTENTS = json.loads((CONFIG_DIR / "intents.json").read_text(encoding="utf-8"))
ENTITIES = json.loads((CONFIG_DIR / "entities.json").read_text(encoding="utf-8"))

class ValidationError(Exception):
    pass

def validate_intent(intent: str):
    if intent not in INTENTS:
        raise ValidationError(f"Ismeretlen intent: {intent}")

def validate_entities(intent: str, entities: dict):
    # Kötelező entitások ellenőrzése
    required = INTENTS[intent]["required_entities"]
    missing = [e for e in required if e not in entities or not entities[e]]
    if missing:
        raise ValidationError(f"Hiányzó entitás(ok): {', '.join(missing)}")
    # Formátum-ellenőrzés az entities.json pattern alapján
    for name, value in entities.items():
        spec = ENTITIES.get(name)
        if spec and "pattern" in spec:
            if not re.match(spec["pattern"], value):
                raise ValidationError(f"Érvénytelen formátumú entitás `{name}`: `{value}`")

def parse_and_validate(text: str) -> dict:
    from planner import parse_user_input
    res = parse_user_input(text)
    intent, entities = res["intent"], res["entities"]
    validate_intent(intent)
    validate_entities(intent, entities)
    return res
