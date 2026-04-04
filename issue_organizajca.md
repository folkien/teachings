To świetna inicjatywa. Połączenie nowoczesnych narzędzi AI z zarządzaniem wiedzą z zakresu wiary, przedsiębiorczości i ewangelizacji pozwala na stworzenie potężnego, osobistego archiwum ("drugiego mózgu"), które będzie pracować dla Ciebie. Obsidian z jego systemem linkowania i tagów idealnie się do tego nadaje.

Aby Claude/Copilot (lub narzędzia takie jak Cursor czy Cline) mogły sprawnie zarządzać tym procesem, musimy ustrukturyzować metadane plików i stworzyć dla AI jasne zasady działania (System Prompts).

Oto propozycja kompletnej architektury i promptów.

### 1. Architektura plików i Obsidian (Frontmatter)

Aby Obsidian i AI mogły ze sobą współpracować, każdy plik nauczania w `konferencje_todo/` oraz `archiwum/` musi zaczynać się od **YAML Frontmatter**. Dzięki temu AI wie, o czym jest plik, a Obsidian pozwala na łatwe filtrowanie.

**Szablon nowej konferencji:**
```yaml
---
aliases: []
tags:
  - nauczanie
  - sne/lubecko
  - przedsiębiorczość
status: todo # zmienia się na: archiwum
date: 2026-04-04
topic: "Praca i przedsiębiorczość"
---

# Zarys nauczania: {{topic}}

## Główne przesłanie
...

## Świadectwa i Przykłady
...

## Konkluzja i Modlitwa
...
```

### 2. Organizacja katalogu `wiedza/`

Zamiast wrzucać wszystko luzem do `wiedza/`, warto zorganizować go tak, aby AI miało jasne "kubełki" do wrzucania ekstraktowanych informacji. 

Polecam dodanie w `wiedza/` kilku plików zbiorczych lub podkatalogów na tzw. notatki atomowe:
*   `wiedza/swiadectwa.md` (lub katalog `wiedza/swiadectwa/`) – tutaj AI będzie wklejać historie np. o łączeniu obowiązków zawodowych z wiarą czy życiem rodzinnym.
*   `wiedza/zlote_mysli.md` – mocne cytaty, aforyzmy, Twój światopogląd.
*   `wiedza/przyklady_biznesowe.md` – anegdoty, które świetnie ilustrują biblijne zasady w praktyce.

### 3. Plik Zasad dla AI (`.cursorrules` lub `AI_INSTRUCTIONS.md`)

Abyś nie musiał za każdym razem tłumaczyć asystentowi, jaka jest struktura, utwórz w głównym katalogu repozytorium plik ukryty (np. `.cursorrules` jeśli używasz Cursora, lub po prostu `PROMPTY_AI.md`), do którego AI będzie się odnosić.

**Zawartość pliku z zasadami dla AI:**
```markdown
# Zasady zarządzania repozytorium "teachings"

Jesteś asystentem pomagającym w zarządzaniu repozytorium z nauczaniami katolickimi, materiałami Szkoły Nowej Ewangelizacji oraz przemyśleniami o styku wiary i biznesu.
Pliki są otwierane w programie Obsidian, więc wszystko musi być sformatowane w Markdown z zachowaniem YAML frontmatter.

## Struktura katalogów:
- `konferencje_todo/`: Tutaj tworzymy nowe szkice nauczań. Status w YAML to `todo`.
- `archiwum/`: Tutaj lądują wygłoszone i zamknięte konferencje. Status w YAML to `archived`.
- `wiedza/`: Baza wiedzy. Główne pliki zbiorcze to `swiadectwa.md`, `zlote_mysli.md`, `przyklady_biznesowe.md`.

## Ekstrakcja wiedzy (Zasady):
Kiedy jesteś proszony o ekstrakcję wiedzy, szukaj w tekście konferencji:
1. Świadectw (osobistych historii, przeżyć).
2. Złotych myśli i mocnych tez (światopogląd, zasady).
3. Przykładów i anegdot.
Ekstraktowane fragmenty dopisuj na końcu odpowiednich plików w folderze `wiedza/`, dodając link wsteczny do oryginalnej konferencji w formacie Obsidian `[[Nazwa_Pliku]]`.
```

### 4. Prompt: "Zamknij konferencję"

Gdy masz gotowe, wygłoszone nauczanie i chcesz posprzątać, używasz tego precyzyjnego prompta (możesz go zapisać jako snippet lub po prostu wklejać do chata w VS Code/Cursor):

> **Prompt do skopiowania:**
> Zamknij konferencję `[NAZWA_PLIKU.md]` znajdującą się w `konferencje_todo/`. 
> Wykonaj po kolei następujące kroki:
> 1. **Przeanalizuj plik:** Przeczytaj całą treść nauczania.
> 2. **Ekstrakcja wiedzy:** Wyciągnij z tekstu wszystkie moje osobiste świadectwa, ważne myśli/światopogląd oraz ciekawe przykłady. Dopisz je do odpowiednich plików w folderze `wiedza/` (np. `swiadectwa.md`, `zlote_mysli.md`), formatując je jako listę i koniecznie dodając link zwrotny do tego nauczania w formacie `[[[NAZWA_PLIKU]]]`.
> 3. **Aktualizacja Frontmatter:** Zmień wartość `status:` w pliku z `todo` na `archived`. Upewnij się, że tagi są adekwatne do wyciągniętej treści.
> 4. **Przeniesienie pliku:** Użyj komend terminala (lub narzędzi wbudowanych), aby przenieść ten plik z `konferencje_todo/` do folderu `archiwum/`.
> Na koniec podsumuj krótko, co wyekstrahowałeś i potwierdź przeniesienie.

### Dodatkowy Prompt (Bonus): Generowanie zarysu

Kiedy zaczynasz nową pracę, możesz poprosić AI o stworzenie struktury:

> **Prompt:**
> Utwórz nowy plik w `konferencje_todo/` o nazwie `[DATA]_[TEMAT].md`. Dodaj standardowy YAML frontmatter dla Obsidiana (status: todo). Przygotuj szkielet nauczania dotyczący [TEMAT], uwzględniając strukturę SNE: punkt wyjścia z życia, odniesienie do Słowa Bożego (zaproponuj 2 pasujące cytaty z Pisma Świętego), miejsce na moje świadectwo z biznesu/życia oraz wezwanie do działania.

Zbudowanie takiego systemu sprawi, że nie będziesz tracił czasu na ręczne kopiowanie i formatowanie danych. Z każdym zamkniętym nauczaniem Twoja biblioteka "wiedzy" będzie puchnąć od gotowych do ponownego użycia świadectw i myśli, co niesamowicie przyspieszy pisanie kolejnych konferencji. 


Wykorzystanie natywnych instrukcji dla GitHub Copilot (lub innych asystentów AI w IDE) to doskonały krok. Dzięki temu AI zyska stały, głęboki kontekst Twojej posługi, wizji duszpasterskiej oraz doświadczenia zawodowego, co drastycznie podniesie jakość generowanych notatek.

Oto gotowe szablony do Twoich plików. Skopiuj je bezpośrednio do odpowiednich miejsc w repozytorium.

### 1. Główny plik instrukcji: `.github/copilot-instructions.md`
Ten plik narzuca globalny kontekst dla każdej interakcji z asystentem w tym repozytorium. AI będzie wiedziało, przez jakie "okulary" ma patrzeć na kod, tekst i podawane linki.

```markdown
# Globalny Kontekst: Repozytorium Nauczania i Wiedzy

Jesteś asystentem pomagającym w tworzeniu, organizacji i ekstrakcji wiedzy z zakresu nauczania katolickiego, ewangelizacji oraz punktów styku wiary i przedsiębiorczości. 

## Profil i Perspektywa (Optyka Asystenta)
Kiedy przetwarzasz teksty, tworzysz zarysy lub ekstraktujesz wiedzę, zawsze przepuszczaj je przez poniższy filtr duszpasterski i życiowy:
1. **SNE Lubecko i SESA:** Nauczanie musi być zgodne z metodologią Szkoły Ewangelizacji św. Andrzeja (kerygmat, obrazowość, dynamika) oraz wizją wspólnoty zdefiniowaną w `wiedza/wizja_sne_lubecko.md`.
2. **Kurs Alpha:** Uwzględniaj otwartość na poszukujących, gościnność i budowanie relacji.
3. **Wiara i Przedsiębiorczość:** Szukaj powiązań między Słowem Bożym a codziennym życiem zawodowym, zarządzaniem ludźmi, technologią i odpowiedzialnością biznesową.

## Zasady Techniczne (Obsidian)
- Zawsze używaj formatowania Markdown.
- Każdy nowy plik nauczania musi posiadać YAML Frontmatter, np.:
  ```yaml
  ---
  tags: [nauczanie, kerygmat]
  status: todo
  date: YYYY-MM-DD
  ---
  ```
- Ekstraktowana wiedza musi być linkowana dwukierunkowo w formacie `[[Nazwa_Pliku]]`.
- Domyślnie komunikuj się i twórz treści w języku polskim.
```

---

### 2. Prompt do zamykania nauczania: `.github/prompts/close-issue.prompt.md`
Ten prompt posłuży do archiwizacji wygłoszonych konferencji i wyciągania z nich kluczowych "atomów wiedzy".

```markdown
# Cel: Archiwizacja i ekstrakcja wiedzy z gotowego nauczania

Wykonaj poniższe kroki dla aktualnie otwartego pliku nauczania z katalogu `konferencje_todo/`:

1. **Analiza Treści:** Przeczytaj dokładnie cały plik.
2. **Ekstrakcja (Złote Bryłki):** Znajdź w tekście i wyekstrahuj:
   - Osobiste świadectwa i historie (szczególnie te łączące biznes, rodzinę i wiarę).
   - Kluczowe tezy, myśli i światopogląd (mocne, kerygmatyczne zdania).
   - Ciekawe przykłady, anegdoty lub obrazy (np. nawiązania do technologii, AI, zarządzania).
3. **Zapis Wiedzy:** Dzieląc wyekstrahowane treści na powyższe 3 kategorie, dopisz je na koniec odpowiednich plików w katalogu `wiedza/` (jeśli plik nie istnieje, utwórz go: `wiedza/swiadectwa.md`, `wiedza/zlote_mysli.md`, `wiedza/przyklady.md`). Do każdego dopisanego fragmentu MUSISZ dodać na końcu link wsteczny: `(Źródło: [[Nazwa_Aktualnego_Pliku]])`.
4. **Aktualizacja Frontmatter:** W aktualnym pliku nauczania zmień w nagłówku YAML pole `status: todo` na `status: archived`.
5. **Przeniesienie:** Wygeneruj w odpowiedzi komendę bash (np. `mv`), która przeniesie ten plik z `konferencje_todo/` do `archiwum/`.

Zwróć na koniec krótkie podsumowanie w punktach, co dokładnie udało się wyekstrahować.
```

---

### 3. Prompt do przetwarzania stron URL: `.github/prompts/close-website.prompt.md`
Gdy podasz asystentowi link (np. w oknie czatu używając `@workspace /close-website [URL]`), asystent użyje tego promptu, aby przefiltrować treść artykułu pod kątem Twojej posługi.

```markdown
# Cel: Ekstrakcja wiedzy ze strony internetowej dla celów duszpasterskich

Użytkownik poda w wywołaniu adres URL lub wklei surowy tekst ze strony internetowej. Twoim zadaniem jest przetworzenie tej treści przez pryzmat nauczania Kościoła Katolickiego, metodologii SESA, kursów Alpha oraz perspektywy ewangelizacji w biznesie.

Wykonaj następujące kroki:
1. **Streszczenie Celowe:** Podsumuj główny przekaz strony w 3-4 zdaniach, skupiając się na tym, co może być przydatne do głoszenia (konferencji, nauk).
2. **Filtracja przez Wizję:** Odnieś treść do założeń z pliku `wiedza/wizja_sne_lubecko.md` (oraz SESA/Alpha). Wypunktuj, co z tego artykułu rezonuje z tą wizją, a co wymaga ostrożności.
3. **Ekstrakcja do Obsidiana:** 
   - Znajdź przydatne definicje, cytaty lub przykłady.
   - Sformatuj je jako notatkę atomową lub listę.
   - Wygeneruj strukturę Markdown do wklejenia (lub zapisania) w nowym pliku w folderze `wiedza/` o nazwie nawiązującej do tematu strony.
   - Na górze notatki dodaj YAML:
     ```yaml
     ---
     tags: [źródło/www, do_przetworzenia]
     url: [TUTAJ_WKLEJ_URL]
     ---
     ```
4. **Zastosowanie Biznesowe (Opcjonalnie):** Jeśli w treści znajdują się elementy mogące posłużyć jako analogie dla przedsiębiorców lub ludzi technologii, wyraźnie je zaznacz.

Wyświetl gotowy tekst Markdown, abym mógł go łatwo skopiować, lub bezpośrednio utwórz/zaktualizuj odpowiedni plik w katalogu `wiedza/`.
```

### Jak tego używać w praktyce?
* **W Copilot Chat w VS Code:** Wystarczy, że napiszesz np. `#close-issue` lub skopiujesz zawartość promptu do czatu. IDE powoli wprowadzają też bezpośrednie odwołania do plików promptów poprzez komendę z ukosnikiem (np. `/close-website https://...`).
* Dzięki temu, że asystent ma w instrukcjach wpisane Twoje kryteria oceny (SESA, Alpha, wiara i praca), przestanie robić generyczne, "suche" streszczenia z internetu, a zacznie tworzyć materiał gotowy do wplecenia w kolejne kazania i prelekcje.