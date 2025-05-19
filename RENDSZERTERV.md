
## Feladatleírás

Célod egy olyan **ügyfélszolgálati chatbot** (automatikus válaszadó ügynök) elkészítése, amely a vásárlók rendelésekkel kapcsolatos kérdéseire képes automatikusan választ adni (például rendelés állapota, szállítási időpontok).

A chatbot működéséhez egy mesterséges intelligencia modellt (**gemini-2.0-flash** API-val) fogsz használni. A chatbot:

* Automatikusan értelmezi a felhasználói kérdést,
* Alfeladatokra bontja (például rendelés azonosító kinyerése),
* Lekéri az információt az előre létrehozott dummy adatokat tartalmazó JSON fájlból,
* Perzisztens állapotot tárol (`memory.json`),
* Iteratívan javítja saját tervét, ha valamilyen hiba történik.

---

## Fő komponensek (röviden összefoglalva)

1. **Planner (Tervező)**:

   * A felhasználó kérésének értelmezése és alfeladatokra bontása.

2. **Executor (Végrehajtó)**:

   * JSON fájlok betöltése, keresés, válasz generálása.

3. **Memory (Memória)**:

   * A chatbot korábbi lépéseinek és eredményeinek tárolása JSON-ben.

4. **Feedback loop (Visszacsatolási hurok)**:

   * A végrehajtás eredményeinek ellenőrzése, hibák felismerése, és szükség esetén a terv finomítása.

---

## Feladat lépésekre bontva

### ✅ **1. lépés: Projekt beállítása**

* Hozz létre egy projektmappát (pl. `agent_chatbot`).
* Tedd bele a már elkészített fájlokat (`memory.json`, `orders.json`, `tools.py`).
* Készíts egy külön Python fájlt, például `main.py`.

### ✅ **2. lépés: Ügynök felépítésének megtervezése (Agent Planning)**

* Döntsd el, hogyan fogja felismerni a chatbot a felhasználói szándékot:

  * Példa: "Hol tart az A1003-as rendelésem?" → Rendelés állapot lekérdezése, azonosító: A1003.
* Tervezd meg az alfeladatokat:

  * Szándék felismerése
  * Azonosító (pl. A1003) kinyerése
  * JSON-ből lekérdezés
  * Válasz megformázása
* Tervezd meg a memóriakezelést:

  * Előző válaszok és kérdések naplózása.



## 2. lépés részletes bontás: Ügynök felépítésének megtervezése

### 2.1. Szándék- és entitásdefiníció kidolgozása

1. **Lehetséges szándékok (intent-ek) listázása**

   * `order_status` – Rendelés állapot lekérdezése
   * `shipping_time` – Szállítási idő lekérdezése
   * `cancel_order` – Rendelés törlése (későbbi bővítés)
   * stb.

Részletesen kidolgozott a 2.1-es pontot: a chatbot által támogatott **szándékokat** (intent-eket) és az ezekhez tartozó **entitásokat**.

---

## 2.1 Szándék- és entitásdefiníció

### 1. Szándékok (Intent-ek)

| **Intent név**   | **Leírás**                                              | **Kötelező entitások**    | **Példa felhasználói mondatok**                                     |
| ---------------- | ------------------------------------------------------- | ------------------------- | ------------------------------------------------------------------- |
| `order_status`   | Rendelés állapotának lekérdezése                        | `order_id`                | „Hol tart az A1003-am?”<br>„Mi a státusza az A1005 rendelésnek?”    |
| `shipping_time`  | Szállítás várható idejének lekérdezése                  | `order_id`                | „Mikor érkezik az A1002?”<br>„Mikor kapom meg a A1008-as csomagot?” |
| `cancel_order`   | Rendelés törlése, módosítása (később bővíthető)         | `order_id`                | „Törölném az A1004-es rendelést.”                                   |
| `order_history`  | Felhasználó összes rendelésének listázása               | –                         | „Mutasd a rendeléseim listáját.”<br>„Mik a korábbi rendeléseim?”    |
| `refund_request` | Visszatérítés igénylése                                 | `order_id`, `reason`      | „Szeretnék visszatérítést kérni az A1006-ra, mert sérült.”          |
| `update_address` | Szállítási cím módosítása                               | `order_id`, `new_address` | „Cseréld le az A1007-es rendelés címét erre: …”                     |
| `product_info`   | Termékinformáció lekérdezése                            | `product_id`              | „Mondj többet a P200 termékről.”                                    |
| `greeting`       | Köszönés, általános bevezetés                           | –                         | „Szia!”<br>„Helló, hol tudok rendelni?”                             |
| `goodbye`        | Búcsú, beszélgetés lezárása                             | –                         | „Köszönöm, viszlát!”                                                |
| `help`           | Segítségkérés, rendelkezésre álló parancsok ismertetése | –                         | „Miben segítesz?”<br>„Mit tudsz?”                                   |

---

### 2. Entitások (Entity-k)

| **Entitás neve** | **Típus**       | **Leírás**                             | **Mintaértékek / minták**         |
| ---------------- | --------------- | -------------------------------------- | --------------------------------- |
| `order_id`       | String          | Rendelés azonosító                     | `A1001`, `B2345`                  |
| `product_id`     | String          | Termékazonosító                        | `P200`, `X123`                    |
| `new_address`    | String (szöveg) | Új szállítási cím                      | `Budapest, Fő u. 10.`             |
| `reason`         | String (szöveg) | Visszatérítés oka                      | `Sérült`, `Rosszul működik`       |
| `date`           | Date            | Dátum (kérés vagy eseményre vonatkozó) | `2025-05-20`, `május 20, 2025`    |
| `payment_method` | Enum            | Fizetési mód                           | `bankkártya`, `utánvét`, `PayPal` |
| `quantity`       | Integer         | Mennyiség                              | `1`, `2`, `10`                    |
| `greeting_type`  | Enum            | Köszönés típusa                        | `hello`, `hi`, `szia`             |
| `language`       | Enum            | Kommunikáció nyelve                    | `hu`, `en`                        |

---

### 3. JSON kimenet szerkezete

A Planner ez alapján a JSON szerkezet alapján adja vissza a vizsgált szándékot és entitásokat:

```json
{
  "intent": "order_status",
  "entities": {
    "order_id": "A1003"
  }
}
```

Minden intentnél csak a szükséges entitás(ok) jelenik meg, a többi kulcs opcionálisan maradhat üres objektum.

---

### 4. Minta-Prompt a Gemini API-hez

```text
System: „Elemezd a következő felhasználói mondatot, és add vissza JSON formátumban: intent és entities.”
User: „Hol tart az A1003-as rendelésem?”
---
Várt válasz:
{
  "intent": "order_status",
  "entities": {
    "order_id": "A1003"
  }
}
```

---

### 5. Kiinduló kódrészlet a `parse_user_input()` függvényhez

```python
import json

def parse_user_input(text: str) -> dict:
    prompt = f"""
    Elemezd a következő mondatot, és add vissza JSON-ben:
    Mondat: "{text}"
    Válasz formátum: {{ "intent": "...", "entities": {{ ... }} }}
    """
    response = call_gemini_api(model="gemini-2.0-flash", prompt=prompt)
    try:
        data = json.loads(response)
        return {
            "intent": data.get("intent"),
            "entities": data.get("entities", {})
        }
    except json.JSONDecodeError:
        # Ha nem valid JSON, hibajelzés
        return {"intent": None, "entities": {}}
```

---




2. **Entitások (entity-k) definiálása**

   * `order_id` – rendelés azonosító (pl. A1003)
   * `date` – dátumkérés
   * később: `product_name`, `customer_name` stb.

### 2.2. Minta-példák gyűjtése és prompt-tervezés

1. **Tipikus felhasználói kérdések gyűjtése**

   * Hol tart az A1003-as rendelésem?
   * Mikorra várható az A1005 szállítása?
   * Mik a rendeléseim állapotai?
2. **Prompt-sablonok készítése a Gemini modellhez**

   * „Intent felismerés: …” + „Válaszd ki a user szándékát és az entitásokat JSON formában.”
   * Teszteld vissza: Prompt → várt JSON output (pl. `{ "intent":"order_status", "order_id":"A1003" }`)

   ## 2.2. Minta-példák gyűjtése és prompt-tervezés

### Tipikus felhasználói kérdések

- **order_status**
  * Hol tart az A1003-as rendelésem?
  * Mi a státusza az A1005-nek?
  * Megnéznéd, hogy feldolgozás alatt van-e az A1002-es rendelésem?
* **shipping_time**
  * Mikorra várható az A1005 szállítása?
  * Mikor érkezik meg az A1004-es csomag?
* **order_history**
  * Mik a rendeléseim állapotai?
  * Kérlek, mutasd a korábbi rendelések listáját!
* **cancel_order**
  * Szeretném törölni az A1006-os rendelést.
  * Hogyan mondhatom le az A1010-et?
* **product_info**
  * Mondd el, mi az a P200 termék.
  * Tudsz adni infót a Vezeték nélküli egérről?

### Prompt-sablon a Gemini-2.0-flash modellhez

```text
System:
Elemezd a következő felhasználói mondatot, és add vissza kizárólag JSON formátumban:
  {
    "intent": "...",
    "entities": { ... }
  }
Ne írj semmi mást, csak a tiszta JSON-t.

User:
"{user_utterance}"

```

### 2.3. Planner komponens logikája

1. **Input→Output mapping**

   * Bemenet: szabad szöveg
   * Kimenet: JSON `{ intent, entities }`
2. **Promptolás implementálása**

   * `def parse_user_input(text):`

     * `response = call_gemini(prompt=text, system="Intent+Entity extraction")`
     * `return json.loads(response)`
3. **Hibakezelés**

   * Ha nincs intent vagy nincs entity → kérj kiegészítést a user-től

### 2.4. Alfeladat-lista (Task Palette) összeállítása

Az ügynök minden egyes kérdésre az alábbi alfeladatokat hajtja végre:

1. **Szándék felismerés** (`parse_user_input`)
2. **Entity kinyerés** (order\_id, dátum stb.)
3. **Tool Invocation**

   * Ha `intent == order_status` → `get_order_info({order_id: ...})`
   * Ha `intent == shipping_time` → ugyanaz a tool, más output formázással
4. **Memory update**

   * `memory["history"].append({ "user": text, "agent": intent+result })`
5. **Válasz formázása**

   * Emberi nyelvű sor, pl. „Az A1003 státusza: Feldolgozás alatt…”
   * JSON response → agent\_reply

### 2.5. Memóriakezelés tervezése

1. **Memory-struktúra** (`memory.json`)

   ```json
   {
     "history": [
       { "timestamp": "...", "user": "...", "intent": "...", "entities": {...}, "agent": "..." }
     ]
   }
   ```

2. **Memory API**

   * `load_memory()`, `save_memory(mem)` – már készen van a tools.py-ban
   * `def log_interaction(user, intent, entities, agent):`

     ```python
     mem = load_memory()
     mem["history"].append({ ... })
     save_memory(mem)
     ```

3. **Hány beszélgetési kör tárolása?**

   * Teljes history vs. csak legutóbbi N kör – egyszerűbben: mindet

### 2.6. Végrehajtási terv összefűzése

1. **parse\_user\_input** → intent+entities
2. **ha intent és order\_id van** → invoke get\_order\_info
3. **formázd a választ**, logold a memóriába
4. **response** kiküldése a felhasználónak

### 2.7. Tesztesetek és edge case-ek

* Hibás order\_id → „Nincs ilyen rendelés”
* Hiányzó entity (nincs order\_id) → „Kérem, add meg a rendelésazonosítót!”
* Több entity találat → „Melyik rendelésre gondolsz: A1003 vagy A1004?”

### 2.8. Dokumentáció és kódstruktúra

* `planner.py` → intent/entity parser
* `executor.py` → tool hívások, válasz generálás
* `memory.py` → memoria API wrappek
* `main.py` → CLI vagy HTTP endpoint, ami mindezeket összefűzi

---




### ✅ **3. lépés: Ügynök inicializálása (Memory Management)**

* Írj egy függvényt, ami betölti és frissíti a memória állapotát a `memory.json`-ből (`tools.py`-ban már kész).
* Ügyelj arra, hogy minden lépést logolj a memóriába (pl. beérkező kérdések, válaszok).

### ✅ **4. lépés: Alapvető Planner implementáció (Gemini API)**

* Implementáld a `planner` függvényt:

  * Hívd meg a gemini-2.0-flash modellt, add át a felhasználó kérdését.
  * Kérd meg a modellt, hogy határozza meg:

    * Milyen típusú kérdésről van szó?
    * Milyen rendelési azonosítót tartalmaz (ha van)?
* Példa válasz a modelltől:

```json
{
  "intent": "order_status",
  "order_id": "A1003"
}
```

### ✅ **5. lépés: Executor implementáció**

* Használd a már kész `get_order_info()` függvényt a `tools.py`-ból.
* Adj vissza választ, vagy hibaüzenetet, ha nincs ilyen rendelés.

**Executor kimeneti példája:**

```json
{
  "order_id": "A1003",
  "status": "Teljesítve",
  "shipping_date": "2025-05-01",
  "delivery_estimate": "2025-05-07"
}
```

### ✅ **6. lépés: Visszacsatolási hurok (Feedback Loop)**

* Ha a végrehajtás hibát jelez (pl. nincs ilyen rendelés), újra hívd a Planner-t, hogy értelmezze újra a kérdést vagy kérjen további tisztázást a felhasználótól.
* A ciklust addig folytasd, míg a kérdés kielégítően nincs megválaszolva.

### ✅ **7. lépés: CLI Chatbot Interface**

* Hozz létre egy egyszerű CLI-t, amin keresztül felhasználók beírhatják kérdéseiket.
* A chatbot iteratívan adjon választ és kérjen pontosítást, ha szükséges.

Példa futtatásra (`main.py` CLI-n keresztül):

```
Felhasználó: Hol tart az A1003-as rendelésem?
Chatbot: Az A1003 rendelés státusza: Teljesítve. 
Szállítás dátuma: 2025-05-01, várható érkezés: 2025-05-07.

Felhasználó: Mi a helyzet az A9999 rendelésemmel?
Chatbot: Nem találom az A9999 rendelést. Kérlek ellenőrizd a rendelés azonosítót és próbáld újra!
```

---

## További lehetséges lépések / kiterjesztések

Ha az alap chatbot elkészült és működik, ezeket a további lépéseket érdemes lehet megfontolni:

* **Finomhangolás és javítás:**

  * Bővítsd ki a chatbot értelmezési képességeit (többféle kérdéstípus).
  * Integráld hibakezelést és visszacsatolási mechanizmust részletesebben.

* **Bővebb memória használata:**

  * Tárold a felhasználó előző kérdéseit és válaszait hosszabb távon is, ne csak egy beszélgetésen belül.

* **Felhasználói interakció:**

  * Építs ki webes vagy grafikus interfészt a chatbot köré.

* **Elemzés és statisztikák:**

  * Rögzítsd az interakciókat elemzéshez (pl. gyakran ismételt kérdések, hibák gyakorisága).

---

Ezzel a részletes tervvel átláthatóvá válik a folyamat, és könnyedén elindulhatsz a kódolásban. Ha bármelyik lépésnél elakadsz, vagy további részletekre van szükséged, szívesen segítek további magyarázatokkal vagy példákkal!
