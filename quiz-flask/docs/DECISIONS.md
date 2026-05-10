# Rozhodnutí (Technické návrhy a volby)

Tento dokument vysvětluje hlavní návrhová rozhodnutí projektu **Quiz Flask** — proč je aplikace strukturována právě tímto způsobem, jaké problémy řeší a jaké alternativy byly zvažovány.

---

## 1) Proč Flask (místo Django / FastAPI)

**Rozhodnutí:** Použití Flasku jako backend frameworku.

**Důvod:**

* Projekt je primárně výukový — cílem je pochopit tok **frontend → API → backend** a základní workflow na GitHubu.
* Flask umožňuje rychle vytvořit jednoduché API a single-page aplikaci bez zbytečné složitosti.
* Pro malý projekt s několika endpointy je Flask přehledný a snadno pochopitelný.

**Alternativy:**

* **Django**: Vhodnější pro větší aplikace (uživatelé, administrace, databáze, více stránek). V tomto případě by přidával zbytečnou komplexitu.
* **FastAPI**: Skvělé pro moderní API s type hinty a automatickou dokumentací, ale Flask je jednodušší a méně striktní pro začátečníky.

---

## 2) Proč Python backend + frontend logika v JavaScriptu

**Rozhodnutí:** Hra běží interaktivně v prohlížeči, přičemž většina herní logiky je řešena v JavaScriptu.

**Důvod:**

* Uživatelské rozhraní se aktualizuje okamžitě bez obnovování stránky.
* Backend funguje jako **vrstva pro data a validaci** (otázky + kontrola odpovědí).
* Frontend spravuje stav hry: `score`, `count`, přechody mezi otázkami a finální výsledky.

**Alternativa:**

* Přístup renderovaný na serveru (pouze Python + HTML) by vyžadoval obnovování stránky po každé odpovědi, což by vedlo k horšímu uživatelskému zážitku.

---

## 3) Proč jsou otázky uloženy v JSON

**Rozhodnutí:** Otázky jsou uloženy v `data/questions.json`.

**Důvod:**

* Snadná úprava a verzování na GitHubu.
* Čitelné pro člověka a nezávislé na programovacím jazyce.
* Dostatečné pro výukový projekt bez potřeby databáze.

**Omezení:**

* Chybí databázové funkce (indexování, pokročilé dotazy, administrační rozhraní).
* Nevhodné pro velké objemy dat.

**Alternativa:**

* Databáze (SQLite / PostgreSQL) by byla vhodnější při rozšíření projektu:

  * velké množství otázek
  * uživatelské účty
  * statistiky
  * administrace

---

## 4) Proč backend vybírá otázky náhodně

**Rozhodnutí:** Náhodný výběr otázek zajišťuje endpoint `/api/question`.

**Důvod:**

* Centralizovaná kontrola nad tím, co je uživateli odesláno.
* Frontend nepotřebuje přístup k celé databázi otázek.
* Jednodušší budoucí rozšíření (např. vážení obtížnosti, logování, analytika).

---

## 5) Proč se `answerIndex` neposílá na frontend

**Rozhodnutí:** API vrací pouze `choices`, nikoliv index správné odpovědi.

**Důvod:**

* Zobrazení správné odpovědi by usnadnilo podvádění pomocí browser devtools nebo síťové komunikace.
* Backend funguje jako **source of truth** a ověřuje odpovědi přes `/api/answer`.

---

## 6) Proč `/api/answer` přijímá text odpovědi místo indexu

**Rozhodnutí:** Frontend posílá vybranou odpověď jako text (`selectedText`).

**Důvod:**

* Odpovědi jsou na frontendu zamíchány, takže indexy nejsou stabilní.
* Validace pomocí textu je odolná vůči zamíchání odpovědí.

---

## 7) Proč jsou odpovědi zamíchány

**Rozhodnutí:** Možnosti odpovědí jsou před zobrazením náhodně promíchány.

**Důvod:**

* Zabraňuje zapamatování pozic místo skutečných znalostí.
* Zvyšuje férovost a znovuhratelnost hry.

---

## 8) Proč se otázky během jedné relace neopakují

**Rozhodnutí:** Otázky se během jedné relace neopakují (frontend posílá `exclude`).

**Důvod:**

* Hra je zábavnější a férovější.
* Poskytuje pocit postupu hrou.
* Frontend sleduje `usedIds` a posílá je backendu.

**Poznámka:**

* Pokud pro danou kategorii nebo obtížnost nejsou dostupné další otázky, backend vrátí chybu (např. „No more questions…“).

---

## 9) Proč mají špatné odpovědi delší prodlevu

**Rozhodnutí:** Po nesprávné odpovědi se zobrazí delší prodleva než po správné.

**Důvod:**

* Uživatel má čas pochopit chybu a poučit se z ní.
* Zvyšuje vzdělávací hodnotu aplikace.

---

## 10) Proč se na konci zobrazuje procento a emoji

**Rozhodnutí:** Finální obrazovka zobrazuje skóre (`x/y`), procentuální úspěšnost a emoji.

**Důvod:**

* Procenta poskytují rychlý a přehledný ukazatel výkonu.
* Emoji přidává motivační a UX prvek.

---

## Budoucí vylepšení

* Přidání databáze a administračního rozhraní pro správu otázek
* Leaderboard / tabulka nejlepších skóre
* Uživatelské účty
* Více úrovní obtížnosti a filtrování kategorií
* Logování a analytika (např. nejčastější chyby)