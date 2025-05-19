# main.py

from executor import handle_user_request
from tools import load_memory

def main():
    print("=== Ügynök Chatbot CLI ===")
    load_memory()  
    print("=== Ügynök elindult, memória betöltve ===")
    print("Írj be egy kérdést (kilépés: 'exit')\n")
    while True:
        text = input(">> ").strip()
        if text.lower() in ("exit", "quit"):
            print("Viszlát!")
            break
        response = handle_user_request(text)
        print(response["agent_reply"], "\n")

if __name__ == "__main__":
    main()
