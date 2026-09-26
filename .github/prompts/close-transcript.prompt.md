---
agent: agent
description: "Analiza transkryptów – podsumowanie, ekstrakcja wiedzy, aktualizacja issues i agentów"
---

# Analiza transkryptów

Wykonaj pełną ekstrakcję wiedzy, aktualizację issues i agentów na podstawie transkryptów.

## Krok 1 – Ustal źródło transkryptów

**Wariant A – użytkownik załączył pliki tekstowe:**
Jeśli użytkownik dołączył pliki tekstowe (np. jako załączniki do wiadomości lub wskazał konkretne pliki), użyj ich bezpośrednio jako materiału do analizy. Pomiń wyszukiwanie w katalogu `transcripts/`.

**Wariant B – brak załączonych plików (tryb dzienny):**
Przejrzyj katalog `transcripts/` i znajdź pliki `.md` (pomiń `summary_*.md` i `README.md`), których nazwa zawiera dzisiejszą datę w formacie `YYMMDD`.

Przykład: jeśli dziś jest 11.03.2026, szukaj plików z `260311` w nazwie (np. `daily_260311_0959.md`).

Jeśli nie ma ani załączonych plików, ani plików z dzisiejszą datą w `transcripts/` – poinformuj użytkownika i zakończ.

## Krok 2 – Przeczytaj i przeanalizuj transkrypty

Dla każdego znalezionego pliku:

1. Odczytaj pełną zawartość
2. Przeanalizuj treść rozmowy i zidentyfikuj:

| Kategoria | Co szukać |
| **Zadania omówione** | Postępy w bieżących zadaniach, co zrobiono, co planowane |
| **Nowe pomysły/zadania** | Nowe koncepcje, funkcjonalności, inicjatywy do podjęcia |

## Krok 3 – Zapisz podsumowanie

Utwórz plik `transcripts/summary_{oryginalna_nazwa}.md` z podsumowaniem w formacie:

```markdown
# Podsumowanie: {nazwa pliku}
Data analizy: {dzisiejsza data}

...

# Zadania omówione
...

# Nowe pomysły/zadania
...
```

Jeśli dany temat nie występuje w rozmowie, wpisz "Nie poruszany."

## Krok 4 – Ekstrakcja wiedzy do `wiedza/`

Oceń wyciągnięte informacje według klucza (analogicznie do procedury zamykania issues):

| Typ wiedzy | Gdzie zapisać |
|---|---|
| Informacje o konkretnej firmie (klient, lead, partner, konkurent) | `wiedza/firmy/{nazwa_firmy}.md` – sprawdź czy plik istnieje i **dopisz** do sekcji `## Historia kontaktów` lub `## Notatki`. Jeśli nie istnieje – stwórz nowy wg konwencji z `wiedza/firmy/README.md` |
| Wiedza o rynku, wydarzeniu, konkursie | `wiedza/` – sprawdź czy pasuje do istniejącego pliku |
| Dane jednorazowe (prywatne anegdoty, small talk) | **Pomiń** – nie zapisuj |

**Zasada ogólna:** zapisuj wiedzę, która będzie użyteczna za 6–12 miesięcy.

Dla każdego zapisu:
1. Sprawdź czy docelowy plik już istnieje
2. Jeśli tak – **dopisz** na końcu odpowiedniej sekcji, nie zastępuj treści
3. Jeśli nie – stwórz nowy plik z nagłówkiem i datą
4. Pisz zwięźle i faktograficznie
5. Dodaj na końcu: `*Źródło: transkrypt {nazwa_pliku}, {data}*`

## Krok 5 – Aktualizacja istniejących issues

Przejrzyj listę aktywnych katalogów `issue_*/` w repozytorium. Dla każdego sprawdź, czy w transkrypcie pojawiły się informacje powiązane z tym issue.

Jeśli tak:
- Odczytaj pliki w katalogu issue (zwłaszcza `todo.md`, `plan.md`, `konwersacja.md` lub podobne)
- **Dopisz** nowe informacje do odpowiedniego pliku w katalogu issue
- Format dopiski: `## Aktualizacja {data} (z transkryptu)\n{treść}`

Przykłady powiązań:
- Rozmowa o przetargu → `issue_radom_its/`
- Rozmowa o webinarze PAP → `issue_pap/`

## Krok 6 – Tworzenie nowych issues

Jeśli w transkrypcie pojawił się **nowy temat**, który:
- wymaga działania (nie jest tylko dyskusją akademicką)
- nie ma jeszcze katalogu `issue_*/`
- nie pasuje do żadnego istniejącego issue

Wtedy zapytaj użytkownika za pomocą narzędzia `ask_questions`:

```
question: "W transkrypcie znaleziono nowy temat: '{opis tematu}'. Czy utworzyć issue?"
header: "nowe_issue"
options:
  - label: "tak – utwórz issue_{proponowana_nazwa}/"
  - label: "nie – pomiń"
```

Jeśli użytkownik potwierdzi – utwórz katalog `issue_{nazwa}/` z plikiem `README.md` zawierającym:
```markdown
# {Tytuł issue}

## Kontekst
{Skąd pochodzi – z jakiego transkryptu, data}

## Opis
{Co trzeba zrobić / o co chodzi}

## Notatki
{Kluczowe informacje z transkryptu}
```


## Krok 8 – Archiwizacja oryginałów

Zapytaj użytkownika za pomocą narzędzia `ask_questions`:

```
question: "Co zrobić z oryginalnymi transkryptami po analizie?"
header: "archiwizacja"
options:
  - label: "archiwum – przenieś do archiwum/transcripts/"
  - label: "zostaw – nie przenoś, zostaw w transcripts/"
```

Jeśli archiwizacja:
```bash
mkdir -p archiwum/transcripts
mv transcripts/{nazwa_pliku} archiwum/transcripts/
```

## Wskazówki

- **Nie twórz redundantnych plików** – lepiej dopisać do istniejącego niż tworzyć nowy z podobną treścią
- **Informacje o firmach** zawsze trafiają do `wiedza/firmy/` – nawet jeśli zostały też zapisane gdzie indziej
- **Decyzje negatywne** („nie robimy", „rezygnujemy", „nie jedziemy") są równie ważne jak pozytywne – zapisuj z uzasadnieniem
- **Nowe pomysły na feature'y** mogą trafić do `agent_new_business_cases/` jako nowy plik `feature_*.md` lub `case_*.md`
- **Dyskusje techniczne** (algorytmy, architektura) – jeśli zawierają konkluzję lub decyzję, zapisz w `wiedza/` jako know-how
- Grupuj pytania do użytkownika w jak najmniejszą liczbę interakcji
