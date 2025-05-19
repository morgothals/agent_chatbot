# main.py

from executor import handle_user_request
from tools import load_memory

def main():
    # Memória inicializálása
    load_memory()
    print("=== Ügynök Chatbot CLI ===")
    print("Írj be egy kérdést (kilépés: 'exit')\n")

    while True:
        text = input("Felhasználó: ").strip()
        if text.lower() in ("exit", "quit"):
            print("Chatbot: Viszlát!")
            break

        # Első futtatás
        resp = handle_user_request(text)

        # Ha tisztázást kér, addig kérdezünk vissza
        while "clarify" in resp:
            print(f"Chatbot: {resp['clarify']}")
            text = input("Felhasználó: ").strip()
            resp = handle_user_request(text)

        # Végső válasz
        print("Chatbot:")
        print(resp.get("agent_reply"), "\n")

if __name__ == "__main__":
    main()
