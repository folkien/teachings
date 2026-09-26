---
agent: agent
description: "Zbieracz kontekstu – przeszukuje wiedza/ i issue_* pod podany temat, składa plik temp/context.md gotowy do przekazania innemu agentowi"
---

# Procedura zbierania kontekstu

Wykonaj poniższe kroki w podanej kolejności.

## Krok 1 – Identyfikacja tematu

Użytkownik podał temat (lub kilka słów kluczowych). Wyznacz:

- Główny temat zapytania (np. „sprzedaż auta", „terapia Ani", „budowa domu", „AISP strategia")
- Listę słów kluczowych, synonimów i nazw własnych powiązanych z tematem
- Czy temat dotyczy: osoby z rodziny / firmy / miejsca / obiektu technicznego / sprawy prawnej / issue aktywnego

Jeśli temat jest niejasny – zapytaj użytkownika o doprecyzowanie zanim przejdziesz dalej.

## Krok 2 – Skanowanie źródeł

Przeszukaj **wszystkie** poniższe lokalizacje pod kątem trafności dla tematu:

### 2a. Katalog `wiedza/`

Odczytaj listę plików i podkatalogów. Dla każdego pliku oceń trafność na podstawie:
- nazwy pliku
- nagłówków i sekcji (wystarczy przejrzeć plik, nie musisz czytać słowo po słowie)

Pliki do sprawdzenia:
- `wiedza/*.md` – pliki ogólne (osoby, obiekty techniczne, tematy życiowe)
- `wiedza/dokumenty/*.md` – wzorce komunikacji i dokumenty
- `wiedza/firmy/*.md` – profile firm i dostawców
- `wiedza/miejsca/*.md` – profile miejsc, szkół, terapeutów, serwisów
- `wiedza/umowy/*.md` – archiwum umów i kontraktów

### 2b. Aktywne issue (`issue_*/`)

Przejrzyj listę katalogów `issue_*/` w głównym katalogu repozytorium.
Dla katalogów, których nazwa sugeruje związek z tematem – odczytaj `README.md` i oceń trafność.
Jeśli issue jest wyraźnie powiązane z tematem – odczytaj wszystkie pliki `.md` z tego katalogu.

## Krok 3 – Selekcja i ekstrakcja

Dla każdego trafnego pliku/fragmentu oceń:

| Priorytet | Kryterium | Akcja |
|-----------|-----------|-------|
| Wysoki | Bezpośrednio dotyczy tematu, zawiera decyzje, dane, fakty, kontakty | Dołącz **cały plik** |
| Średni | Częściowo powiązany, zawiera 1-2 istotne sekcje | Wytnij **tylko trafne sekcje** z nagłówkami |
| Niski | Ogólne tło, wspomniane marginalnie | **Pomiń** lub wstaw jednolinijkowe streszczenie |

### Reguła bezwzględna formy ekstrakcji

W sekcji `## Zebrany kontekst` wolno użyć tylko dwóch form:

1. **Kopia całego pliku** (1:1, bez zmian treści).
2. **Dosłowny fragment źródła** (cytat 1:1, bez parafrazy), z nagłówkiem zawierającym ścieżkę i zakres linii.

Niedozwolone w sekcji `## Zebrany kontekst`:
- parafrazy,
- przepisywanie własnymi słowami,
- skróty redakcyjne zmieniające sens,
- miksowanie treści z wielu źródeł w jednym bloku bez wyraźnego rozdzielenia.

Dozwolone jest krótkie podsumowanie **wyłącznie** w sekcji `## Podsumowanie dla agenta`.

Nie dołączaj:
- surowych logów, tabel cen, rachunków bez kontekstu
- danych jednorazowych (np. ogłoszenia OLX, zrzuty z giełd)
- binarnych załączników (PDF, DOCX, grafiki)

## Krok 4 – Złożenie pliku `temp/context.md`

Utwórz katalog `temp/` jeśli nie istnieje, a następnie utwórz (lub nadpisz) plik `temp/context.md` według poniższej struktury:

```markdown
# Kontekst: {temat}

Data zebrania: {data}
Temat: {temat podany przez użytkownika}
Słowa kluczowe: {lista słów kluczowych}

---

## Źródła użyte

| Plik źródłowy | Co zawiera | Priorytet |
|---------------|------------|-----------|
| wiedza/plik.md | krótki opis | wysoki |
| issue_xyz/README.md | krótki opis | średni |

---

## Zebrany kontekst

{tu wklejaj treść – najpierw pliki wysokiego priorytetu, potem średniego}
{każdą sekcję oddzielaj nagłówkiem ## w formacie: "Źródło: ścieżka (cały plik)" albo "Źródło: ścieżka (linie X-Y)"}
{wklejana treść musi być dosłowną kopią źródła 1:1}

---

## Podsumowanie dla agenta

{2-5 zdań streszczenia tego co zebrałeś – co jest kluczowe dla tematu, jakie są otwarte pytania lub luki w wiedzy}
```

## Krok 5 – Podsumowanie dla użytkownika

Wyświetl:
- Ścieżkę do wygenerowanego pliku: `temp/context.md`
- Liczbę źródeł: ile plików pełnych, ile fragmentów, ile pominięto
- Listę źródeł z krótkim opisem co zawierają
- Czy są luki – czego brakuje, czego nie znaleziono w wiedzy

## Krok 6 – Zapytaj o dalsze działanie

Użyj narzędzia `vscode_askQuestions` z pytaniem:

```
question: "Co zrobić dalej z zebranym kontekstem?"
header: "dalsze_dzialanie"
options:
  - label: "gotowe – zostawiam temp/context.md do ręcznego użycia"
  - label: "uzupełnij – dodaj też pliki z agent_strateg/ lub agent_marketing/"
  - label: "otwórz issue – na podstawie kontekstu otwórz nowe issue"
```

---

## Wskazówki dodatkowe

- `temp/context.md` jest plikiem tymczasowym – informuj użytkownika, że może go ręcznie przekazać do innego agenta lub sesji
- Jeśli temat dotyczy konkretnej osoby z rodziny, zawsze dołącz jej profil z `wiedza/` (np. `anna_paszko_profil_neuromotoryczny.md`)
- Jeśli temat dotyczy auta – dołącz odpowiedni plik z `wiedza/ford_*.md`
- Jeśli znaleziono aktywne issue powiązane z tematem – zaznacz to wyraźnie w podsumowaniu, bo issue może być właściwym miejscem do pracy zamiast tworzenia kontekstu
- Staraj się, żeby `temp/context.md` był samowystarczalny – agent otrzymujący go nie ma dostępu do repozytorium
- Jeśli kopiujesz fragment, dbaj o pełne nagłówki sekcji i minimalny kontekst wokół fragmentu (tak, aby inny agent rozumiał treść bez otwierania repo).
