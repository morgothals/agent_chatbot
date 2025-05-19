import json
from pathlib import Path
from google import genai

# ——————————————————————————————————————————————
# OpenAI Gemini (Google GenAI) kliens inicializálása
# ——————————————————————————————————————————————
API_KEY = "AIzaSyAy3PX1bQX5i8N6ZivmYv5r7HYk3couFQA"
client = genai.Client(api_key=API_KEY)

def call_gemini_api(model: str, contents: str) -> str:
    """
    Meghívja a Google GenAI Gemini modellt.
    Paraméterek:
      - model: pl. "gemini-2.0-flash"
      - contents: a prompt, amire JSON-t fog kérni például intent/entity parsing-re
    Visszatér:
      a Gemini válaszának szöveges tartalma (általában JSON-formátum).
    """
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents
        )
        return response.text
    except Exception as e:
        # Hibát JSON-ben visszaadjuk, hogy a parser kezelni tudja
        return json.dumps({"error": str(e)})

# ——————————————————————————————————————————————
# Order-tool: rendelés-adatok lekérése orders.json-ből
# ——————————————————————————————————————————————
def get_order_info(args: dict) -> dict:
    """
    Betölti az 'orders.json'-t és visszaadja a megadott order_id-hez tartozó
    rendelés-objektumot. Ha nincs találat, {"error": "..."}-t ad vissza.
    """
    try:
        with open("orders.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {"error": "orders.json fájl nem található."}

    for order in data.get("orders", []):
        if order.get("order_id") == args.get("order_id"):
            return order
    return {"error": f"Nincs ilyen rendelés: {args.get('order_id')}"}

# ——————————————————————————————————————————————
# Memória-tool: beszélgetési előzmények mentése/beolvasása
# ——————————————————————————————————————————————
def load_memory() -> dict:
    """
    Betölti a 'memory.json'-t. Ha nincs, üres history-val tér vissza.
    """
    try:
        with open("memory.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"history": []}

def save_memory(mem: dict) -> None:
    """
    Elmenti a mem dict-et 'memory.json' néven, szép formázással.
    """
    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)
