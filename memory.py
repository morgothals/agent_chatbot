import json
from datetime import datetime
from tools import load_memory, save_memory

def log_interaction(user: str, intent: str, entities: dict, agent: str) -> None:
    """
    Naplózza a beszélgetési lépést a memory.json-ben.
    A bejegyzés tartalmazza:
      - timestamp: ISO formátumú UTC időpont
      - user: a felhasználó kérdése
      - intent: a felismerés szerinti intent név (vagy None)
      - entities: a kivont entitások dict
      - agent: a chatbot emberi nyelvű válasza vagy hibaüzenete
    """
    mem = load_memory()
    # Bizonyosodjunk meg róla, hogy van history kulcs
    if "history" not in mem or not isinstance(mem["history"], list):
        mem["history"] = []
    # Új bejegyzés hozzáadása
    mem["history"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "intent": intent,
        "entities": entities,
        "agent": agent
    })
    save_memory(mem)
