from pathlib import Path

def main():
    # Aktuális munkakönyvtár
    script_dir = Path(__file__).resolve().parent
    # Létrehozandó fájl neve
    summary_file = script_dir / "summary.txt"

    # Megnyitjuk írásra (felülírja a meglévőt)
    with summary_file.open("w", encoding="utf-8") as out:
        # Bejárjuk az összes fájlt a mappában és almappáiban
        for path in script_dir.rglob("*"):
            # Csak a fájlok érdekelnek, és kihagyjuk a summary.txt-et
            if path.is_file() and path.name != summary_file.name and path.name != "summarycreator.py":
                # Relatív útvonal készítése
                rel_path = path.relative_to(script_dir)
                # Fejléc írása
                out.write(f"{rel_path} tartalma:\n")
                try:
                    # Fájl tartalmának beolvasása és írása
                    content = path.read_text(encoding="utf-8")
                    out.write(content)
                except Exception as e:
                    # Hiba esetén jelzés
                    out.write(f"<Nem olvasható: {e}>\n")
                # Pár üres sor az elkülönítéshez
                out.write("\n\n")

if __name__ == "__main__":
    main()
