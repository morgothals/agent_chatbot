# executor.py

import json
from planner import plan
from tools import get_order_info
from memory import log_interaction

def invoke_order_status(order_id: str) -> dict:
    """
    Csak a get_order_info() eredményét adja vissza JSON-ként,
    hibával vagy sikeres adatcsomaggal.
    """
    return get_order_info({"order_id": order_id})


def handle_user_request(text: str) -> dict:
    """
    Visszacsatolási hurokhoz igazított executor:
      1) parse → intent+entities
      2) missing‐entity és multi‐entity kezelése
      3) tool invoke
      4) tool‐szintű hibák → clarify
      5) válasz formázása
      6) memória naplózás
    Visszatér egy dict-tel, mely vagy
      • {"clarify": "..."}  – kérd további inputot
      • {"error": "..."}    – végleges hiba
      • {"agent_reply": "..."} – végleges sikeres válasz
    """
    # 1) Planner
    res = plan(text)
    intent = res.get("intent")
    entities = res.get("entities", {})

    # 2a) Planner-szintű error
    if "error" in res:
        reply = res["error"]
        log_interaction(text, intent, entities, reply)
        return {"error": reply}

    # 2b) Több entity esetén tisztázás
    oid = entities.get("order_id")
    if isinstance(oid, list) and len(oid) > 1:
        opts = " vagy ".join(oid)
        reply = f"Melyik rendelésre gondolsz: {opts}?"
        log_interaction(text, intent, entities, reply)
        return {"clarify": reply}

    # 3) Tool invocation
    result = {}
    if intent in ("order_status", "shipping_time"):
        result = invoke_order_status(oid)
    else:
        result = {"error": f"Nem kezelt intent: {intent}"}

    # 4) Tool-szintű hiba → clarify
    if "error" in result and result["error"].startswith("Nincs ilyen rendelés"):
        reply = "Nincs ilyen rendelés. Kérlek, add meg egy másik rendelésazonosítót!"
        log_interaction(text, intent, entities, reply)
        return {"clarify": reply}

    # 5) Válasz formázása
    if "error" in result:
        # más típusú hiba végleges
        reply = result["error"]
    else:
        if intent == "order_status":
            reply = f"Az {result['order_id']} rendelés státusza: {result['status']}."
        elif intent == "shipping_time":
            reply = (
                f"Az {result['order_id']} csomag feladásának dátuma: "
                f"{result['shipping_date']}, várható érkezés: {result['delivery_estimate']}."
            )
        else:
            reply = json.dumps(result, ensure_ascii=False)

    # 6) Memória naplózása
    log_interaction(text, intent, entities, reply)

    return {"agent_reply": reply}


if __name__ == "__main__":
    # Gyors manuális teszt
    for utt in [
        "Hol tart az A1003-as rendelésem?",
        "Hol tart a A1003 as rendelésem?",
        "Mi a helyzet az A9999 rendelésemmel?"
    ]:
        resp = handle_user_request(utt)
        # Ha kérdés jött vissza, szimuláljuk a user újabb inputját
        if "clarify" in resp:
            print(resp["clarify"])
            # itt a demo miatt a helyes azonosítót adjuk
            resp = handle_user_request("A1003")
        print(f">>> {utt}\n→ {resp.get('agent_reply')}\n")
