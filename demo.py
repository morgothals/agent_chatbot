# demo.py
from tools import get_order_info, load_memory, save_memory, call_gemini_api
from planner import parse_user_input, plan
from validator import parse_and_validate

def main():
    print("=== Order lookup ===")
    print(get_order_info({"order_id": "A1003"}))  
    print(get_order_info({"order_id": "XXXX"}))   # hibakezelés

    print("\n=== Memory load/save ===")
    mem = load_memory()
    print("Before:", mem)
    mem["history"].append({"user":"Teszt","bot":"Válasz"})
    save_memory(mem)
    print("After:", load_memory())

    print("\n=== Intent/entity parsing ===")
    utterance = "Hol tart az A1003-as rendelésem?"
    parsed = parse_user_input(utterance)
    print("parse_user_input:", parsed)

    print("\n=== Validation ===")
    try:
        ok = parse_and_validate(utterance)
        print("parse_and_validate:", ok)
    except Exception as e:
        print("Validation error:", e)

    # GEMINI API hívás (ha éles kulccsal futtatod)
    print("\n=== call_gemini_api demo ===")
    resp = call_gemini_api(
        model="gemini-2.0-flash",
        contents="Generate JSON with intent and entities for: Hol tart az A1003-as rendelésem?"
    )
    print("RAW GEMINI:", resp)

if __name__ == "__main__":
    main()
