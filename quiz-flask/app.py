from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path
import random

app = Flask(__name__)

# Cesta k souboru s daty otázek.
# Path(__file__).parent udržuje cestu stabilní i v případě, že je projekt přesunut
# nebo spuštěn z jiné pracovní složky.
DATA_PATH = Path(__file__).parent / "data" / "questions.json"

def load_questions():
    # Načtení otázek ze souboru JSON.
    # Umístění do samostatné funkce pomáhá:
    # - vyhnout se opakování stejného kódu ve více endpointech
    # - jasně určit zdroj dat
    #
    # Ve větším projektu by se toto často cachovalo místo čtení
    # souboru při každém požadavku, ale pro výukový projekt je to jednodušší
    # a srozumitelnější.
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]

@app.route("/")
def home():
    # Hlavní stránka:
    # - načte všechny otázky
    # - vytvoří seznam kategorií (unikátní hodnoty q["category"])
    # - předá je do Jinja šablony, aby byl výběr kategorií
    #   naplněn hned při načtení stránky
    questions = load_questions()
    categories = sorted({q["category"] for q in questions})

    # total se předává do šablony jako základní informace o tom,
    # kolik otázek celkem existuje.
    # Skutečný limit kvízu stále řídí frontend.
    return render_template("index.html", total=len(questions), categories=categories)

@app.route("/api/categories")
def api_categories():
    # API endpoint pro kategorie.
    # Byl přidán jako možnost pro případ, že by se kategorie později načítaly
    # dynamicky pomocí fetch v JavaScriptu místo server-side renderingu.
    #
    # V aktuální verzi jsou kategorie už předávány přes "/"
    # pomocí render_template, ale tento endpoint je stále užitečný jako čistý,
    # rozšiřitelný API přístup.
    questions = load_questions()
    categories = sorted({q["category"] for q in questions})
    return jsonify(categories)

@app.route("/api/question")
def api_question():
    # Endpoint používaný frontendem pro vyžádání jedné otázky.
    # Query parametry odesílané z app.js:
    # - category: vybraná kategorie (povinné)
    # - difficulty: easy / medium (volitelné, ale aktuální UI je vždy posílá)
    # - exclude: seznam již použitých ID otázek oddělených čárkou
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    exclude = request.args.get("exclude", "")

    # Kategorie je povinná, jinak bychom nevěděli, který okruh otázek použít.
    if not category:
        return jsonify({"error": "Missing category"}), 400

    # exclude_ids:
    # Přichází jako text například "101,102,103".
    # Převede se na množinu celých čísel, abychom mohli:
    # - efektivně filtrovat
    # - zabránit opakování otázek během jedné relace
    exclude_ids = set()
    if exclude.strip():
        try:
            exclude_ids = {int(x) for x in exclude.split(",") if x.strip()}
        except ValueError:
            # Pokud přijde nečíselná hodnota, vrátí se chyba.
            return jsonify({"error": "Invalid exclude"}), 400

    questions = load_questions()

    # Základní filtr: nejdříve ponechá pouze otázky z vybrané kategorie.
    candidates = [q for q in questions if q["category"] == category]

    # Filtr obtížnosti:
    # Frontend posílá vybranou obtížnost, aby hráč dostal pouze
    # otázky odpovídající dané úrovni.
    if difficulty:
        candidates = [q for q in candidates if q["difficulty"] == difficulty]

    # Filtr bez opakování:
    # Odstraní otázky, jejichž ID už jsou v exclude_ids.
    if exclude_ids:
        candidates = [q for q in candidates if q["id"] not in exclude_ids]

    # Pokud nezbývají žádné otázky, hra nemůže pokračovat.
    # To může nastat, když:
    # - uživatel vybere malý okruh kategorie/obtížnosti
    # - a požaduje více otázek, než je dostupné
    if not candidates:
        return jsonify({"error": "No more questions for this selection"}), 404

    # Vybere jednu náhodnou otázku.
    # Náhodný výběr je řešen na backendu, aby bylo doručování otázek
    # řízeno z jednoho místa.
    q = random.choice(candidates)

    # Důležitý detail pro hratelnost / integritu:
    # answerIndex neposíláme na frontend, takže hráč nemůže
    # snadno zjistit správnou odpověď ze síťových odpovědí nebo stavu JS.
    # Frontend dostane pouze možnosti odpovědí a odešle vybranou
    # odpověď zpět na /api/answer k ověření.
    return jsonify({
        "id": q["id"],
        "category": q["category"],
        "difficulty": q["difficulty"],
        "question": q["question"],
        "choices": q["choices"]
    })

@app.route("/api/answer", methods=["POST"])
def api_answer():
    # Endpoint pro ověření odpovědi.
    # Frontend posílá JSON v tomto formátu:
    # {
    #   id: currentQuestionId,
    #   selectedText: "selected answer text"
    # }
    #
    # Proč posílat selectedText místo answerIndex?
    # Protože odpovědi jsou na frontendu zamíchány.
    # Index by už nebyl spolehlivý, ale text odpovědi zůstává stabilní.

    data = request.json
    qid = data.get("id")
    selected_text = data.get("selectedText")

    # Validace vstupu: bez ID otázky a vybrané odpovědi
    # nelze odpověď vyhodnotit.
    if qid is None or selected_text is None:
        return jsonify({"error": "Missing data"}), 400

    questions = load_questions()

    # Najde otázku podle ID.
    # next(..., None) vrátí první shodu, nebo None, pokud se nic nenajde.
    q = next((x for x in questions if x["id"] == qid), None)

    if not q:
        return jsonify({"error": "Question not found"}), 404

    # Získá text správné odpovědi ze zdrojových dat.
    # answerIndex ukazuje na správnou možnost v q["choices"].
    correct_text = q["choices"][q["answerIndex"]]

    # Vyhodnotí odpověď porovnáním vybraného textu
    # s textem správné odpovědi.
    correct = (selected_text == correct_text)

    # Vrací:
    # - correct: aby frontend věděl, zda přičíst bod
    #   a jak stylovat vybrané tlačítko
    # - correctText: aby frontend mohl zvýraznit správnou odpověď,
    #   pokud uživatel odpověděl špatně
    return jsonify({
        "correct": correct,
        "correctText": correct_text
    })

# Spuštění aplikace lokálně.
# debug=True je užitečné během vývoje (automatické načítání změn + detailní chybové stránky),
# ale v produkci by mělo být vypnuté.
if __name__ == "__main__":
    app.run(debug=True)