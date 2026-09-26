---
agent: agent
description: "Otwarcie nowego issue – tworzenie katalogu issue_, przenoszenie dokumentów i generowanie README.md"
---

# Procedura otwarcia nowego issue

Wykonaj poniższe kroki w podanej kolejności.

## Krok 1 – Identyfikacja

Użytkownik wskazał jeden lub więcej dokumentów (pliki, emaile, transkrypty, notatki) i chce otworzyć issue.

1. Odczytaj wskazane dokumenty w całości
2. Na podstawie ich treści zaproponuj nazwę katalogu w formacie `issue_{krótka_nazwa}` (małe litery, podkreślenia, bez polskich znaków, max 4 słowa)
3. Zapytaj użytkownika czy zgadza się z nazwą lub chce ją zmienić – **zanim przejdziesz dalej**

## Krok 2 – Analiza dokumentów

Przed stworzeniem katalogu przeanalizuj dokumenty pod kątem:

- **Kontekst:** czego dotyczy issue — zdrowie/terapia dziecka, sprawa urzędowa/prawna, AISP/firma, dom/motoryzacja, sport/życie, społeczność/kościół, finanse/ZUS
- **Cel:** co chcemy osiągnąć / co jest problemem do rozwiązania
- **Osoby i kontakty:** kto jest zaangażowany (imię, firma/instytucja, rola) — czy to ktoś z rodziny Paszko, specjalista, urzędnik
- **Korespondencja:** emaile, wiadomości, pisma urzędowe, odpowiedzi
- **Status:** co już zrobiono, co pozostaje do zrobienia
- **Terminy:** daty, deadliny, terminy urzędowe, terminy wizyt

## Krok 3 – Tworzenie katalogu i przenoszenie plików

1. Utwórz katalog `issue_{nazwa}/`
2. Przenieś wszystkie wskazane przez użytkownika dokumenty do `issue_{nazwa}/`
   - Użyj `mv` (nie kopiuj) – pliki mają trafić **wyłącznie** do katalogu issue
   - Zachowaj oryginalne nazwy plików
3. Sprawdź czy przeniesione pliki nie były powiązane (linkowane) w innych miejscach repozytorium i zaktualizuj takie linki, jeśli znajdziesz

## Krok 4 – Generowanie README.md

Stwórz plik `issue_{nazwa}/README.md` według poniższego szablonu:

```markdown
# Issue: {Tytuł opisowy – max 8 słów}

## Kontekst

{2–4 zdania opisu – czego dotyczy issue, skąd się wzięło, dlaczego jest ważne}

## Cel

{Co chcemy osiągnąć. Może być lista.}

## Osoby i kontakty

- **{Imię Nazwisko}** – {firma, rola}
- ...

## Materiały

- [{nazwa pliku}]({nazwa_pliku}) – {jedno zdanie opisu}
- ...

## Korespondencja

- [{nazwa emaila}]({nazwa_pliku}) – {data, krótki opis}
- ...

## Status

- [ ] {Następny krok 1}
- [ ] {Następny krok 2}
- [ ] Zamknięcie issue (ekstrakcja wiedzy do `wiedza/`)
```

**Zasady wypełniania README.md:**
- Sekcje `Korespondencja` i `Materiały` – tylko jeśli są odpowiednie pliki; pomiń pustą sekcję
- `Status` – zawsze zawiera co najmniej jeden konkretny next step i ostatni checkbox „Zamknięcie issue"
- Nazwa issue w tytule (nagłówek H1) powinna być czytelna dla człowieka, nie slug

## Krok 5 – Potwierdzenie

Wyświetl użytkownikowi:

```
✅ Issue otwarte: issue_{nazwa}/

Pliki przeniesione:
  - {plik 1} (z {oryginalna_ścieżka})
  - {plik 2} (z {oryginalna_ścieżka})

README.md wygenerowany.

Kolejne kroki (z README.md):
  - {krok 1}
  - {krok 2}
```

Zapytaj czy commitować zmiany do repozytorium.

> **Implikacje rodzinne / strategiczne:** jeśli nowe issue dotyczy:
> - **życia rodziny** (poważna decyzja zdrowotna, edukacyjna, financial, przeprowadzka, remont) – sprawdź czy wnioski należy odnotować w odpowiednim pliku `wiedza/` (np. `anna_paszko_profil_neuromotoryczny.md`, `jadwiga_paszko_dzialalnosc.md`)
> - **AISP / modelu biznesowego** (cennik, partnerstwo, roadmapa produktowa, nowy rynek) – sprawdź czy plik `agent_strateg/plan_strategia_2026.md` istnieje, a jeśli tak, oceń czy temat powinien być odnotowany przy odpowiedniej sekcji (nowe ryzyko, szansa, decyzja do podjęcia)
>
> Jeśli tak – dopisz krótką notkę w odpowiednim miejscu. Nie twórz pliku `plan_strategia_2026.md` jeśli nie istnieje.
