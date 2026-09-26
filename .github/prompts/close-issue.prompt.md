---
agent: agent
description: "Zamknięcie issue - ekstrakcja wiedzy do wiedza/ i archiwizacja lub usunięcie katalogu"
---

# Procedura zamknięcia issue

Wykonaj poniższe kroki w podanej kolejności.

## Krok 1 – Identyfikacja

Użytkownik podał nazwę issue do zamknięcia. Wyznacz katalog: `issue_{nazwa}/`.

Odczytaj wszystkie pliki tekstowe z tego katalogu (pomiń binarne: `.pdf`, `.docx`, `.xlsx`, `.png`, `.jpg`).
Zapoznaj się z ich pełną treścią.

## Krok 2 – Analiza wiedzy

Oceń każdy plik/element katalogu według poniższego klucza:

| Typ wiedzy | Gdzie zapisać |
|---|---|
| Wiedza o osobie z rodziny (profil, diagnoza, terapia, edukacja) | `wiedza/{imie_paszko_temat}.md` – sprawdź czy plik już istnieje i **dopisz**, np. `anna_paszko_profil_neuromotoryczny.md` |
| Wiedza o miejscu (terapeuta, szkoła, klinika, serwis, organizacja) | `wiedza/miejsca/{nazwa_miejsca}.md` – stwórz lub dopisz |
| Wiedza o instytucji publicznej (urząd, ZUS, GDDKiA, sąd) | `wiedza/urzedy/{nazwa_urzedu}.md` – stwórz lub dopisz |
| Informacje o firmie (dostawca, klient AISP, partner, konkurent) | `wiedza/firmy/{nazwa_firmy}.md` – stwórz lub dopisz |
| Decyzja życiowa lub wynik oceny (np. "nie robimy remontu", "rezygnujemy z terapeuty") | `wiedza/` – zaktualizuj plik powiązany z tematem lub stwórz ze znaczącą nazwą |
| Decyzja strategiczna AISP (model biznesowy, cennik, roadmapa) | `agent_strateg/` – zaktualizuj odpowiedni plik |
| Wiedza o obiekcie technicznym (auto, sprzęt, dom, instalacja) | `wiedza/` – plik opisowy np. `galax_ford_dpf.md` |
| Dokumentacja prawna / umowa (wzorzec, kontrakt, wniosek) | **Zawsze archiwizuj** w `wiedza/umowy/` (oryginał: PDF/DOCX/HTML/MD + opcjonalny skrót `.md`) |
| Dane jednorazowe (surowe logi, rachunki, tabele cen) | **Pomiń** – nie zapisuj do wiedza |
| Pliki binarne (PDF, DOCX, grafiki) | Oceń ważność. Jeśli ważne – **przenieś** do odpowiedniego katalogu `wiedza/`. Jeśli jednorazowe – **pomiń** |

**Zasada ogólna:** zapisuj wiedzę, która będzie użyteczna za 6–12 miesięcy przy podejmowaniu podobnych decyzji.

### Katalogi agentów — dodatkowe miejsce zapisu

Oprócz `wiedza/` sprawdź czy wiedza z issue nie jest trafna dla konkretnego agenta:

| Jeśli issue dotyczyło… | Sprawdź katalog agenta |
|---|---|
| Materiałów wizualnych, brandingu, projektu graficznego (blog Jadwigi, AISP, eventy) | `agent_grafik/` |
| Marketingu, contentu, SEO, bloga Jadwigi, promocji książki, Google Ads | `agent_marketing/` |
| Planowania AISP, analizy rynku, strategii firmy, cennika, ekspansji | `agent_strateg/` |

Jeśli katalog agenta nie istnieje – pomiń ten krok, nie twórz katalogu.

Jeśli tak – przejrzyj `README.md` danego agenta i oceń, czy zaktualizować jego pliki kontekstowe (np. strategię, dane rynkowe, notatki o klientach). Dopisuj, nie zastępuj.

## Krok 3 – Zapis do wiedza/

Dla każdego elementu wartego zachowania:

1. Sprawdź czy docelowy plik już istnieje
2. Jeśli tak – **dopisz** na końcu nową sekcję, nie zastępuj istniejącej treści
3. Jeśli nie – stwórz nowy plik z nagłówkiem opisującym temat i datą (`## Aktualizacja {data}`)
4. Pisz zwięźle i faktograficznie – ma być czytelne zarówno dla LLM jak i dla człowieka
5. Zawsze dodaj na końcu: `*Źródło: zamknięcie issue_{nazwa}, {data}*`

### Reguła bezwzględna dla umów

1. Każdy plik umowny z issue (`umowa*`, `kontrakt*`, aneksy, wzory) **musi** zostać skopiowany do `wiedza/umowy/` przed usunięciem/przeniesieniem katalogu issue.
2. Zachowaj oryginalny format pliku (np. `.pdf`, `.docx`, `.html`) oraz dodaj datę do nazwy, jeśli to pomaga odróżnić wersje.
3. Jeśli istnieje wersja robocza i podpisana — archiwizuj obie, z jasnym dopiskiem w nazwie lub w pliku indeksu.
4. W podsumowaniu zamknięcia issue obowiązkowo pokaż listę zarchiwizowanych umów.

## Krok 4 – Podsumowanie

Wyświetl użytkownikowi:
- listę plików, które **zapisałeś/zaktualizowałeś** w `wiedza/` (co i gdzie)
- listę plików, które **pominąłeś** i dlaczego
- decyzje strategiczne, które odnotowałeś

## Krok 5 – Zapytaj o los katalogu

Użyj narzędzia `vscode_askQuestions` (NIE pytaj tekstowo) z pytaniem:

```
question: "Co zrobić z katalogiem issue_{nazwa}/?"
header: "los_katalogu"
options:
  - label: "usuń – trwale usuń katalog (rm -rf)"
  - label: "archiwum – przenieś do archiwum/issue_{nazwa}/"
```

## Krok 6 – Wykonaj akcję

Na podstawie odpowiedzi użytkownika wykonaj:

**Usunięcie:**
```bash
rm -rf issue_{nazwa}/
```

**Przeniesienie do archiwum:**
```bash
mv issue_{nazwa}/ archiwum/
```

Potwierdź wykonanie.

---

## Wskazówki dodatkowe

- Jeśli issue dotyczyło konkretnej firmy lub usługodawcy – zawsze sprawdź czy profil jest już w `wiedza/firmy/` lub `wiedza/miejsca/` i zaktualizuj go
- Jeśli issue dotyczyło konkretnej osoby z rodziny (Ania, bliźniaczki, Jan, Marta, Jadwiga, Sławomir) – sprawdź odpowiedni plik w `wiedza/` i dopisz wnioski
- Jeśli issue zawierało decyzję "nie robimy / nie jedziemy / rezygnujemy" – zapisz ją jako oddzielną sekcję z uzasadnieniem, to ważny kontekst dla przyszłych decyzji
- Jeśli issue miało rozwiązane zadanie techniczne (konfiguracja auta, naprawa sprzętu, ustawienia) – rozważ czy warto zapisać w `wiedza/` jako know-how
- Nie twórz redundantnych plików – lepiej dopisać do istniejącego niż tworzyć nowy z podobną treścią
- Umowy i aneksy mają priorytet archiwizacji: **nigdy nie pomijaj** ich przy zamknięciu issue
- **Aktualizacja strategii AISP:** jeśli issue zakończyło się decyzją wpływającą na model biznesowy, priorytet rynku, cennik, partnerstwo lub roadmapę produktową – sprawdź czy plik `agent_strateg/plan_strategia_2026.md` istnieje i jeśli tak, dopisz wnioski do odpowiedniej sekcji. Dopisz też blok `## Aktualizacja {data} – zamknięcie issue_{nazwa}` na końcu `agent_strateg/README.md`.
