// ================================
// Odkazy na HTML prvky (DOM)
// -------------------------------
// Získání odkazů z index.html, abychom mohli:
// - číst hodnoty (vybraná kategorie / obtížnost / limit)
// - aktualizovat UI (otázka, odpovědi, skóre, chybové zprávy)
// ================================
const elCategory = document.getElementById("category");
const elDifficulty = document.getElementById("difficulty");
const elLimit = document.getElementById("limit");
const elLoad = document.getElementById("load");
const elQuiz = document.getElementById("quiz");
const elMeta = document.getElementById("meta");
const elQuestion = document.getElementById("question");
const elChoices = document.getElementById("choices");
const elError = document.getElementById("error");
const elScore = document.getElementById("score");
const elCount = document.getElementById("count");
const elTotal = document.getElementById("total");
const elFinish = document.getElementById("finish");
const elFinalScore = document.getElementById("finalScore");
const elRestart = document.getElementById("restart");
const elTheme = document.getElementById("theme");

// ================================
// Přepínání motivu
// -------------------------------
const savedTheme = localStorage.getItem("theme") || "dark";
document.body.setAttribute("data-theme", savedTheme);

if (elTheme) {
  elTheme.value = savedTheme;

  elTheme.addEventListener("change", () => {
    document.body.setAttribute("data-theme", elTheme.value);
    localStorage.setItem("theme", elTheme.value);
  });
}

// ================================
// Překlad obtížnosti pro zobrazení v metadatech otázky
// -------------------------------
function translateDifficulty(difficulty) {
  if (difficulty === "easy") return "Lehká";
  if (difficulty === "medium") return "Střední";
  return difficulty;
}

// ================================
// Stav hry
// -------------------------------
let currentQuestionId = null;
let score = 0;
let count = 0;
let totalQuestions = 10;
let selectedDifficulty = "easy";
let usedIds = [];

// ================================
// Pomocná funkce: shuffle
// -------------------------------
function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// ================================
// Pomocná funkce: sleep
// -------------------------------
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ================================
// Konec hry: zobrazení finálního výsledku
// -------------------------------
function showFinish() {
  const percent = Math.round((score / totalQuestions) * 100);

  const emoji =
    percent === 100 ? "🔥" :
    percent >= 75 ? "😄" :
    percent >= 50 ? "🙂" :
    "😕";

  elFinalScore.textContent = `${score}/${totalQuestions} = ${percent} % správných odpovědí ${emoji}`;

  elQuiz.classList.add("hidden");
  elFinish.classList.remove("hidden");
}

// ================================
// Načtení jedné otázky z backendu (Flask API)
// -------------------------------
async function loadQuestion() {
  elError.textContent = "";
  elQuiz.classList.add("hidden");

  const category = elCategory.value;
  const exclude = usedIds.join(",");

  const res = await fetch(
    `/api/question?category=${encodeURIComponent(category)}&difficulty=${encodeURIComponent(selectedDifficulty)}&exclude=${encodeURIComponent(exclude)}`
  );
  const data = await res.json();

  if (!res.ok) {
    elError.textContent = data.error || "Chyba.";
    return;
  }

  currentQuestionId = data.id;
  usedIds.push(currentQuestionId);

  elMeta.textContent = `${data.category} • ${translateDifficulty(data.difficulty)}`;
  elQuestion.textContent = data.question;
  elChoices.innerHTML = "";

  const shuffledChoices = shuffle(data.choices);

  shuffledChoices.forEach((text, idx) => {
    const btn = document.createElement("button");
    btn.className = "choice";
    btn.textContent = `${String.fromCharCode(65 + idx)}) ${text}`;
    btn.onclick = () => submitAnswer(text, btn);

    elChoices.appendChild(btn);
  });

  elQuiz.classList.remove("hidden");
}

// ================================
// Odeslání odpovědi a vyhodnocení výsledku
// -------------------------------
async function submitAnswer(selectedText, button) {
  [...elChoices.children].forEach(b => {
    b.disabled = true;
  });

  const res = await fetch("/api/answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id: currentQuestionId,
      selectedText: selectedText
    })
  });

  const data = await res.json();

  if (data.correct) {
    score += 1;
    elScore.textContent = String(score);
    elTotal.textContent = String(totalQuestions);
    button.classList.add("correct");
  } else {
    button.classList.add("wrong");

    [...elChoices.children].forEach(b => {
      const txt = b.textContent.split(") ").slice(1).join(") ");
      if (txt === data.correctText) {
        b.classList.add("correct");
      }
    });
  }

  count += 1;
  elCount.textContent = String(count);

  const pauseMs = data.correct ? 1200 : 3000;
  await sleep(pauseMs);

  if (count >= totalQuestions) {
    showFinish();
    return;
  }

  await loadQuestion();
}

// ================================
// Spuštění hry
// -------------------------------
elLoad.addEventListener("click", async () => {
  selectedDifficulty = elDifficulty.value;

  totalQuestions = Number(elLimit.value);
  if (!Number.isFinite(totalQuestions) || totalQuestions < 1) {
    totalQuestions = 10;
  }

  score = 0;
  count = 0;
  usedIds = [];

  elScore.textContent = "0";
  elCount.textContent = "0";
  elTotal.textContent = String(totalQuestions);

  elFinish.classList.add("hidden");
  elError.textContent = "";

  await loadQuestion();
});

// ================================
// Restart hry
// -------------------------------
elRestart.addEventListener("click", async () => {
  score = 0;
  count = 0;
  usedIds = [];

  selectedDifficulty = elDifficulty.value;
  totalQuestions = Number(elLimit.value);
  if (!Number.isFinite(totalQuestions) || totalQuestions < 1) {
    totalQuestions = 10;
  }

  elScore.textContent = "0";
  elCount.textContent = "0";
  elTotal.textContent = String(totalQuestions);

  elFinish.classList.add("hidden");
  elError.textContent = "";

  await loadQuestion();
});