# executor.py

import json
import re
from planner import plan
from tools import get_order_info, load_memory, call_gemini_api
from memory import log_interaction

def invoke_order_status(order_id: str) -> dict:
    """
    Csak a get_order_info() eredményét adja vissza JSON-ként,
    hibával vagy sikeres adatcsomaggal.
    """
    return get_order_info({"order_id": order_id})


def handle_user_request(text: str) -> dict:
    """
    Ügynök főfüggvénye:
      1) Planner → intent+entities
      2) Planner‐szintű error/clarify
      3) Memória‐fallback hiányzó order_id-re
      4) Több entity esetén clarify
      5) Tool invoke
      6) Tool‐szintű hiba → clarify
      7) Válasz formázása vagy generatív fallback
      8) Memória naplózása
    """
    # 1) Szándék+entitás meghatározása
    res = plan(text)
    intent   = res.get("intent")
    entities = res.get("entities", {})

    # 2a) Planner‐szintű végleges hiba
    if "error" in res:
        err = res["error"]
        # 3) Ha hiányzó order_id, memória‐fallback
        if "order_id" in err:
            mem = load_memory()
            prev = next(
                (e for e in reversed(mem.get("history", []))
                 if e.get("entities", {}).get("order_id")),
                None
            )
            if prev:
                entities["order_id"] = prev["entities"]["order_id"]
                intent = prev["intent"] or intent
                result = invoke_order_status(entities["order_id"])
            else:
                reply = err
                log_interaction(text, intent, entities, reply)
                return {"error": reply}
        else:
            reply = err
            log_interaction(text, intent, entities, reply)
            return {"error": reply}
    # 2b) Planner‐szintű kiegészítés (clarify)
    elif "clarify" in res:
        reply = res["clarify"]
        log_interaction(text, intent, entities, reply)
        return {"clarify": reply}
    else:
        # 5) Ha minden rendben, tool invoke az ismert intenteknél
        if intent in ("order_status", "shipping_time"):
            result = invoke_order_status(entities.get("order_id"))
        else:
            # 7) Generatív fallback a Gemini-vel
            fallback_prompt = f"""Válaszold meg ügyfélszolgálati chatbotként a következő kérdést magyarul:
\"{text}\""""
            raw = call_gemini_api(model="gemini-2.0-flash", contents=fallback_prompt)
            # töröljük a ```json``` vagy egyéb markdown kereteket
            clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
            reply = clean.strip()
            log_interaction(text, intent, entities, reply)
            return {"agent_reply": reply}

    # 6) Tool‐szintű hiba → clarify
    if "error" in result and result["error"].startswith("Nincs ilyen rendelés"):
        reply = "Nem találom a rendelést. Kérlek ellenőrizd az azonosítót és próbáld újra!"
        log_interaction(text, intent, entities, reply)
        return {"clarify": reply}

    # 7) Válasz formázása az ismert intentekre
    if intent == "order_status":
        oid    = result["order_id"]
        status = result["status"]
        ship   = result["shipping_date"]
        arrive = result["delivery_estimate"]
        reply = (
            f"Az {oid} rendelés státusza: {status}.\n"
            f"Szállítás dátuma: {ship}, várható érkezés: {arrive}."
        )
    elif intent == "shipping_time":
        ship   = result.get("shipping_date", "–")
        arrive = result.get("delivery_estimate", "–")
        reply = f"{ship} → {arrive}"
    else:
        # Ezt a blokk elvileg sosem fut, mert a fallback már visszatért
        reply = json.dumps(result, ensure_ascii=False)

    # 8) Memória naplózása
    log_interaction(text, intent, entities, reply)

    return {"agent_reply": reply}


if __name__ == "__main__":
    # Demo CLI nélkül
    samples = [
        "Milyen idő lesz holnap?",
        "Hol tart az A1003-as rendelésem?",
        "Mi a rendelés státusza?"
    ]
    for utt in samples:
        resp = handle_user_request(utt)
        out = resp.get("clarify") or resp.get("error") or resp.get("agent_reply")
        print(f">>> {utt}\n→ {out}\n")
