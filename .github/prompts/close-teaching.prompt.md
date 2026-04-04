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
- **Styl pisania autora** – charakterystyczne cechy języka i przekazu (np. ton, rytm, słownictwo, sposób budowania obrazów, typowe konstrukcje, częste wezwania/dopełnienia).

## Krok 3 – Zapis Wiedzy

Podziel wyekstrahowane treści wg kategorii i dopisz je na koniec odpowiednich plików w `wiedza/`:

- Świadectwa → `wiedza/swiadectwa.md`
- Cytaty ważne / złote myśli → `wiedza/cytaty_wazne.md`
- Cytaty z Kościoła (KKK, dokumenty) → `wiedza/cytaty_kk.md`
- Przykłady → `wiedza/przyklady.md`
- Styl pisania autora → `wiedza/styl_pisania.md`

W `wiedza/styl_pisania.md` nie tylko dopisuj obserwacje, ale aktualizuj istniejący szablon stylu autora:
- dopisz nowe cechy, jeśli są powtarzalne i charakterystyczne,
- popraw/uzupełnij sekcje, jeśli nowe nauczanie pokazuje dojrzalszy lub inny sposób komunikacji,
- zachowuj formę krótkich, praktycznych punktów do użycia przy tworzeniu kolejnych nauczań.

Do każdego fragmentu dodaj na końcu link wsteczny w formacie Obsidian:
`(Źródło: [[Nazwa_Pliku_Bez_Rozszerzenia]])`

Jeśli plik w `wiedza/` nie istnieje – utwórz go z nagłówkiem `# Tytuł`.

## Krok 4 – Aktualizacja Frontmatter

W pliku nauczania zmień pole `status: todo` na `status: archived`.
Upewnij się, że tagi są adekwatne do wyciągniętej treści.

## Krok 5 – Przeniesienie pliku

Upewnij się, że nazwa pliku jest zgodna z konwencją `YYYYMMDD_NAZWA.md`.
Jeśli plik nie ma prefiksu daty – przed przeniesieniem zmień jego nazwę dodając datę z frontmatter.

Archiwizacja ma być rzeczywistym **przeniesieniem**, nie kopiowaniem:
- po wykonaniu kroku plik ma istnieć tylko w `archiwum/`
- plik ma zostać usunięty z `konferencje_todo/`

Uruchom w terminalu komendę przenoszącą plik z `konferencje_todo/` do `archiwum/`:

```bash
mv konferencje_todo/NAZWA_PLIKU.md archiwum/NAZWA_PLIKU.md
```

Po przeniesieniu zweryfikuj:
- `archiwum/NAZWA_PLIKU.md` istnieje
- `konferencje_todo/NAZWA_PLIKU.md` nie istnieje

## Podsumowanie

Zwróć krótkie podsumowanie w punktach:
- Co wyekstrahowano (ile świadectw, myśli, przykładów oraz jakie zmiany w szablonie stylu)
- Do jakich plików wiedzy dopisano treści
- Potwierdzenie przeniesienia pliku oraz usunięcia go z `konferencje_todo/`

