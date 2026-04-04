---
agent: agent
description: "Zamknięcie konferencji - ekstrakcja wiedzy do wiedza/ i archiwizacja nauczania"
---

# Cel: Archiwizacja i ekstrakcja wiedzy z gotowego nauczania

Wykonaj poniższe kroki dla wskazanego pliku nauczania z katalogu `konferencje_todo/`:

## Krok 1 – Analiza treści

Przeczytaj dokładnie cały plik. Zapamiętaj jego nazwę (bez rozszerzenia) – będzie potrzebna jako link wsteczny.

## Krok 2 – Ekstrakcja (Złote Bryłki)

Znajdź w tekście i wyekstrahuj:

- **Świadectwa** – osobiste historie i przeżycia (szczególnie łączące biznes, rodzinę i wiarę).
- **Złote myśli** – kluczowe tezy, światopogląd, mocne kerygmatyczne zdania.
- **Przykłady i analogie** – anegdoty, obrazy, nawiązania do technologii, AI, zarządzania.

## Krok 3 – Zapis Wiedzy

Podziel wyekstrahowane treści wg kategorii i dopisz je na koniec odpowiednich plików w `wiedza/`:

- Świadectwa → `wiedza/swiadectwa.md`
- Złote myśli → `wiedza/zlote_mysli.md`
- Przykłady → `wiedza/przyklady.md`

Do każdego fragmentu dodaj na końcu link wsteczny w formacie Obsidian:
`(Źródło: [[Nazwa_Pliku_Bez_Rozszerzenia]])`

Jeśli plik w `wiedza/` nie istnieje – utwórz go z nagłówkiem `# Tytuł`.

## Krok 4 – Aktualizacja Frontmatter

W pliku nauczania zmień pole `status: todo` na `status: archived`.
Upewnij się, że tagi są adekwatne do wyciągniętej treści.

## Krok 5 – Przeniesienie pliku

Upewnij się, że nazwa pliku jest zgodna z konwencją `YYYYMMDD_NAZWA.md`.
Jeśli plik nie ma prefiksu daty – przed przeniesieniem zmień jego nazwę dodając datę z frontmatter.

Uruchom w terminalu komendę przenoszącą plik z `konferencje_todo/` do `archiwum/`:

```bash
mv konferencje_todo/NAZWA_PLIKU.md archiwum/NAZWA_PLIKU.md
```

## Podsumowanie

Zwróć krótkie podsumowanie w punktach:
- Co wyekstrahowano (ile świadectw, myśli, przykładów)
- Do jakich plików wiedzy dopisano treści
- Potwierdzenie przeniesienia pliku

