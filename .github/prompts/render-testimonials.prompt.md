# Prompt: Renderuj karty ze świadectwami SNE

## Cel

Wczytaj plik ze świadectwami, wybierz losowo 10 świadectw z podpisami i wyrenderuj 10 kart graficznych PNG przy użyciu skryptu `scripts/render_testimonial_cards.py`.

## Użycie

```
@workspace /render-testimonials
  --testimonials <ścieżka_do_pliku_md>
  --photos <ścieżka_do_katalogu_ze_zdjęciami>
  [--output <katalog_wyjściowy>]
  [--theme red|dark]
```

Przykład:
```
@workspace /render-testimonials
  --testimonials nowe_zycie_26/swiadectwa_nz_260502_1634.md
  --photos /home/user/zdjecia/kurs
  --output output/sne_cards
```

## Instrukcje dla agenta

Wykonaj poniższe kroki po kolei:

### Krok 1 — Wczytaj i sparsuj świadectwa

Wczytaj plik podany przez użytkownika jako `--testimonials`. Plik zawiera świadectwa w formacie:

```
<treść świadectwa (jeden lub więcej akapitów)>
<Imię autora>

<treść świadectwa>
<Imię autora>
```

Zbuduj listę par `(tekst, autor)`. Pomiń:
- nagłówki markdown (`#`, `##`)
- linie zawierające „Świadectwa niepodpisane"
- wpisy krótsze niż 40 znaków

### Krok 2 — Losowy wybór 10 świadectw

Wybierz losowo **10** świadectw z listy (bez powtórzeń). Jeśli w pliku jest mniej niż 10, użyj wszystkich.

Dla każdego wybranego świadectwa:
- ogranicz tekst do 220 znaków (nie ucinaj w środku słowa, dodaj `…`)
- zachowaj oryginalny podpis autora

### Krok 3 — Renderuj 10 kart

Dla każdego z 10 wybranych świadectw wywołaj skrypt:

```bash
python3 scripts/render_testimonial_cards.py \
  --photos <ścieżka_do_zdjęć> \
  --output <katalog_wyjściowy> \
  --logo images/logotyp.png \
  --author "<autor>" \
  --text "<tekst>" \
  --theme red
```

Karty są generowane z **losowym layoutem** (gradient / fullbg / minimal / stat) — nie podawaj `--layout`, żeby był losowany automatycznie.

Nazwy plików wyjściowych: `01_<slug_autora>.png`, `02_<slug_autora>.png`, …

### Krok 4 — Podsumowanie

Po wygenerowaniu wszystkich kart wypisz tabelę:

| Nr | Autor | Fragment tekstu (pierwsze 60 znaków) | Layout | Plik |
|----|-------|--------------------------------------|--------|------|
| 1  | Iza   | Kurs pozwolił mi zbliżyć się do…     | fullbg | 01_iza.png |
| …  | …     | …                                    | …      | …    |

---

## Zasady techniczne

- Używaj `python3 scripts/render_testimonial_cards.py` (lub `uv run python3 …` jeśli projekt używa uv)
- Katalog wyjściowy twórz automatycznie (`mkdir -p`)
- Jeśli `images/logotyp.png` nie istnieje, skrypt użyje tekstu zastępczego — nie przerywaj procesu
- Katalog ze zdjęciami musi zawierać pliki `.jpg`, `.jpeg`, `.png` lub `.webp`
- Każda karta to `1200×628 px` (LinkedIn Open Graph)
- Motyw domyślny: `red` (czerwona kolorystyka SNE)

## Schemat wywołania z terminala (skrót)

```bash
python3 scripts/render_testimonial_cards.py \
  --testimonials nowe_zycie_26/swiadectwa_nz_260502_1634.md \
  --photos /ścieżka/do/zdjęć \
  --output output/sne_cards \
  --count 10 \
  --theme red
```

To polecenie wykona całość automatycznie (parsowanie + losowanie 10 + renderowanie z losowym layoutem).
