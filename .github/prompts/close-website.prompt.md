---
agent: agent
description: "Analiza strony WWW – ekstrakcja wiedzy "
---

# Analiza strony WWW

Użytkownik podał jeden lub więcej adresów URL. Wykonaj pełną analizę i ekstrakcję wiedzy w podanej kolejności.

## Krok 1 – Pobranie treści

Pobierz zawartość każdego podanego URL za pomocą dostępnych narzędzi sieciowych (fetch/browser).

Jeśli strona jest niedostępna lub pusta – poinformuj użytkownika i zakończ.

## Krok 2 – Streszczenie Celowe

Podsumuj główny przekaz strony w 3-4 zdaniach, skupiając się na tym, co może być przydatne do głoszenia (konferencji, nauk).

## Krok 3 – Filtracja przez Wizję

Odnieś treść do założeń z pliku `wiedza/wizja_sne_lubecko.md` (oraz SESA/Alpha). Wypunktuj:
- Co rezonuje z wizją SNE i metodologią SESA/Alpha
- Co wymaga ostrożności lub krytycznej oceny w świetle wiary

## Krok 4 – Ekstrakcja do Obsidiana

- Znajdź przydatne definicje, cytaty lub przykłady.
- Podziel je na kategorie: świadectwa, złote myśli, przykłady/analogie.
- Dopisz do odpowiednich plików w `wiedza/` (`swiadectwa.md`, `zlote_mysli.md`, `przyklady.md`).
- Wygeneruj też notatkę źródłową w `wiedza/` o nazwie nawiązującej do tematu strony.

Notatka źródłowa musi zawierać YAML frontmatter:
```yaml
---
tags: [źródło/www, do_przetworzenia]
url: URL_STRONY
date: YYYY-MM-DD
---
```

Dodaj tagi tematyczne (jeden lub kilka) adekwatnie do tresci strony:
- `temat/finanse`
- `temat/rodzicielstwo`
- `temat/praca`
- `temat/dom`
- `temat/relacje`
- `temat/kosciol`
- `temat/wspolnota`
- `temat/wiara`
- `temat/modlitwa`
- `temat/styl-zycia`
- `temat/lifestyle`
- `temat/uzdrowienie`

Jeśli treść strony dotyczy konkretnego kursu SESA, rozszerz tagi notatki źródłowej o:
- `sesa/kurs/<slug_kursu>`

## Krok 5 – Zastosowanie Duszpasterskie (Opcjonalnie)

Jeśli treść zawiera elementy mogące posłużyć jako analogie dla przedsiębiorców lub ludzi technologii – zaznacz je wyraźnie jako potencjalne przykłady do konferencji o wierze i pracy.

## Wskazówki

- **Wiele URL tego samego podmiotu** – agreguj informacje w jednym pliku, nie twórz osobnych wpisów.
- **Źródła watykańskie / kościelne** – traktuj jako autorytatywne, cytuj dokładnie.
- **Źródła biznesowe / technologiczne** – szukaj analogii do Słowa Bożego.

