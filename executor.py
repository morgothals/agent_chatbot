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
    2.6 + 2.7: 
      - parse → intent+entities 
      - missing / multi-entity / invalid-id edge-case-ek
      - tool invoke 
      - memory log 
      - reply
    """
    # 1) Planner
    res = plan(text)
    intent   = res.get("intent")
    entities = res.get("entities", {})

    # 2a) Validációs és missing-entity hibák
    if "error" in res:
        reply = res["error"]
        log_interaction(text, intent, entities, reply)
        return {"agent_reply": reply}

    # 2b) Több entity esetén kérdés
    oid = entities.get("order_id")
    if isinstance(oid, list) and len(oid) > 1:
        # pl. ["A1003", "A1004"]
        opts = " vagy ".join(oid)
        reply = f"Melyik rendelésre gondolsz: {opts}?"
        log_interaction(text, intent, entities, reply)
        return {"agent_reply": reply}

    # 3) Tool invocation
    if intent in ("order_status", "shipping_time"):
        result = get_order_info({"order_id": oid})
    else:
        result = {"error": f"Nem kezelt intent: {intent}"}

    # 4) Válasz formázása + special-case hibák
    if "error" in result:
        err = result["error"]
        if err.startswith("Nincs ilyen rendelés"):
            reply = "Nincs ilyen rendelés"
        else:
            reply = err
    else:
        if intent == "order_status":
            reply = f"Az {result['order_id']} rendelés státusza: {result['status']}."
        elif intent == "shipping_time":
            reply = (f"Az {result['order_id']} csomag feladásának dátuma: "
                     f"{result['shipping_date']}, várható érkezés: {result['delivery_estimate']}.")
        else:
            reply = json.dumps(result, ensure_ascii=False)

    # 5) Memória naplózása
    log_interaction(text, intent, entities, reply)

    return {
        "intent": intent,
        "entities": entities,
        "result": result,
        "agent_reply": reply
    }

if __name__ == "__main__":
    for utt in [
        "Hol tart az A1003-as rendelésem?",
        "Hol tart a A1003 as rendelésem?",
        "Hiányzó id teszt",
        "Többszörös id teszt"
    ]:
        # demo: multi-entity szimulációhoz manuálisan
        if "Többszörös" in utt:
            demo_entities = {"order_id": ["A1003", "A1004"]}
            demo_res = {"intent": "order_status", "entities": demo_entities}
            # kicseréljük a plan-t
            from planner import parse_user_input
            def fake_plan(_): return demo_res
            import planner; planner.plan = fake_plan
            out = handle_user_request(utt)
        else:
            out = handle_user_request(utt)
        print(f">>> {utt}\n→ {out['agent_reply']}\n")
