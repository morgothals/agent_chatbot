# main.py

from executor import handle_user_request
from tools import load_memory

def main():
    # Inicializáljuk a memóriát, hogy létrejöjjön a memory.json, ha még nincs
    load_memory()
    print("=== Ügynök Chatbot CLI ===")
    print("Írj be egy kérdést (kilépés: 'exit')\n")

    while True:
        text = input(">> ").strip()
        if text.lower() in ("exit", "quit"):
            print("Viszlát!")
            break

        # Első futtatás
        resp = handle_user_request(text)

        # Ha clarify kérés jött, addig kérünk új inputot, míg végleges válasz nem érkezik
        while "clarify" in resp:
            print(resp["clarify"])
            text = input(">> ").strip()
            resp = handle_user_request(text)

        # Error vagy agent_reply
        if "error" in resp:
            print(resp["error"], "\n")
        else:
            print(resp["agent_reply"], "\n")


if __name__ == "__main__":
    main()
