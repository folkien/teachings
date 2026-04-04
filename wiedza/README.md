---
tags: [wiedza, meta, readme]
type: readme
topic: "Baza Wiedzy – opis i plan"
---

# Baza Wiedzy (`wiedza/`)

Ten katalog to **"drugi mózg"** – zbiór atomów wiedzy wyekstrahowanych z konferencji, artykułów i osobistych przemyśleń. Każdy plik to oddzielny "kubełek" tematyczny, do którego AI dopisuje treści podczas archiwizacji nauczań.

---

## Pliki Zbiorcze (Baza Wiedzy)

| Plik | Zawartość | Typ |
|---|---|---|
| [[swiadectwa]] | Osobiste świadectwa, przeżycia, historie łączące wiarę z życiem | `baza_wiedzy` |
| [[cytaty_wazne]] | Mocne cytaty, tezy, kerygmatyczne zdania, światopogląd | `baza_wiedzy` |
| [[cytaty_kk]] | Cytaty z dokumentów Kościoła (KKK, encykliki, dokumenty soborowe) | `baza_wiedzy` |
| [[przyklady]] | Anegdoty, analogie z biznesu, technologii i codziennego życia | `baza_wiedzy` |

## Pliki Kontekstowe (Stałe)

| Plik | Zawartość | Typ |
|---|---|---|
| [[moje_zasady]] | Osobiste zasady życia autora – kontekst głoszącego | `zasady` |
| [[wizja_sne_lubecko]] | Wizja, misja i charyzmat wspólnoty SNE Lubecko | `wizja` |

---

## Jak to działa?

### Ekstrakcja z konferencji
Gdy zamykasz nauczanie (`close-teaching.prompt.md`), AI automatycznie:
1. Wyciąga świadectwa → dopisuje do [[swiadectwa]]
2. Wyciąga mocne zdania → dopisuje do [[zlote_mysli]]
3. Wyciąga przykłady i analogie → dopisuje do [[przyklady]]

Każdy fragment ma link wsteczny do źródłowego nauczania: `(Źródło: [[Nazwa_Pliku]])`.

### Ekstrakcja ze stron WWW
Gdy przetwarzasz artykuł (`close-website.prompt.md`), AI tworzy notatkę źródłową w tym katalogu i dopisuje wyekstrahowane treści do plików zbiorczych.

### Notatki źródłowe (WWW)
Pliki z tagiem `źródło/www` to przetworzone artykuły z internetu. Format nazwy: `YYYYMMDD_skrot_tytulu.md`.

---

## Filtr Duszpasterski

Wszystkie treści w tej bazie są filtrowane przez:
- **Metodologię SESA** – kerygmat, obrazowość, dynamika
- **Wizję SNE Lubecko** – zob. [[wizja_sne_lubecko]]
- **Kurs Alpha** – otwartość, gościnność, budowanie relacji
- **Wiarę i Przedsiębiorczość** – powiązania Słowa Bożego z życiem zawodowym
