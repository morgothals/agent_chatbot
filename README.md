# 💬 Ügyfélszolgálati Chatbot – Rendelések kezelése

## Készítette: Borbás Péter & ChatGPT

Ez a projekt egy **egyszerű, de moduláris chatbot**, amely képes vásárlói kérdésekre válaszolni rendelések állapotával kapcsolatban. A rendszer egy **ügynök-alapú architektúrát** követ, szándékfelismeréssel, entitáskinyeréssel, válaszgenerálással és memóriakezeléssel.

---

## 🎯 Cél

A chatbot automatikusan válaszol a következő típusú kérdésekre:

- Hol tart a rendelésem? (állapot)
- Mikorra várható a kiszállítás? (dátumok)
- Köszönés / búcsú / segítségkérés

- Egyéb kérdésre az alapmodellhez fordul természetesebb chatélményért.

A háttérben egy **Gemini 2.0 Flash** modell segíti az intent és entity felismerést.

---

## ⚙️ Fő funkciók

- 🧠 **Intent és entity felismerés**: Gemini API segítségével
- 📁 **Rendelések kezelése**: előre definiált `orders.json` fájlból
- 🪪 **Memória**: beszélgetési előzmények naplózása `memory.json`-ba
- 🔁 **Feedback loop**: hiányzó vagy többértelmű információ esetén tisztázó kérdések
- 📦 **Modularitás**: különálló modulok (planner, executor, memory, tools)



