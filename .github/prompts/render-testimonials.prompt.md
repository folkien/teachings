---
agent: agent
description: "Renderuj karty ze świadectwami SNE – wybór 10 losowych świadectw z pliku i generowanie graficznych kart PNG"
---
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

### Krok 3 — Renderuj 10 kart × 3 motywy = 30 kart

Dla każdego z 10 wybranych świadectw wygeneruj **po 3 karty** — po jednej dla każdego motywu kolorystycznego: `red`, `dark`, `light`.

Każdą kartę wywołaj skryptem:

```bash
python3 scripts/render_testimonial_cards.py \
  --photos <ścieżka_do_zdjęć> \
  --output <katalog_wyjściowy> \
  --logo images/logotyp/sne_kwadrat.png \
  --author "<autor>" \
  --text "<tekst>" \
  --theme <red|dark|light>
```

Karty są generowane z **losowym layoutem** (gradient / gradient_rtl / fullbg / minimal / stat) — nie podawaj `--layout`, żeby był losowany automatycznie.

Nazwy plików wyjściowych: `01_<slug_autora>_red.png`, `01_<slug_autora>_dark.png`, `01_<slug_autora>_light.png`, `02_…` itd.

Alternatywnie możesz użyć jednego wywołania zbiorczego na motyw (wszystkie 10 świadectw naraz):

```bash
# red
python3 scripts/render_testimonial_cards.py \
  --testimonials <plik_md> --photos <zdjęcia> \
  --output <katalog>/red --count 10 --theme red --seed <N>

# dark
python3 scripts/render_testimonial_cards.py \
  --testimonials <plik_md> --photos <zdjęcia> \
  --output <katalog>/dark --count 10 --theme dark --seed <N>

# light
python3 scripts/render_testimonial_cards.py \
  --testimonials <plik_md> --photos <zdjęcia> \
  --output <katalog>/light --count 10 --theme light --seed <N>
```

Użyj **tego samego seed** dla wszystkich trzech wywołań, by każdy motyw dotyczył tych samych 10 świadectw.

### Krok 4 — Podsumowanie

Po wygenerowaniu wszystkich kart wypisz tabelę (30 wierszy = 10 świadectw × 3 motywy):

| Nr | Autor | Fragment tekstu (pierwsze 60 znaków) | Layout | Motyw | Plik |
|----|-------|--------------------------------------|--------|-------|------|
| 1  | Iza   | Kurs pozwolił mi zbliżyć się do…     | fullbg | red   | 01_iza_red.png |
| 1  | Iza   | Kurs pozwolił mi zbliżyć się do…     | fullbg | dark  | 01_iza_dark.png |
| 1  | Iza   | Kurs pozwolił mi zbliżyć się do…     | fullbg | light | 01_iza_light.png |
| …  | …     | …                                    | …      | …     | … |

---

## Zasady techniczne

- Używaj `python3 scripts/render_testimonial_cards.py` (lub `uv run python3 …` jeśli projekt używa uv)
- Katalog wyjściowy twórz automatycznie (`mkdir -p`)
- Jeśli `images/logotyp.png` nie istnieje, skrypt użyje tekstu zastępczego — nie przerywaj procesu
- Katalog ze zdjęciami musi zawierać pliki `.jpg`, `.jpeg`, `.png` lub `.webp`
- Każda karta to `1200×628 px` (LinkedIn Open Graph)
- Motyw domyślny: `red` (czerwona kolorystyka SNE)

## Schemat wywołania z terminala (skrót)

Trzy wywołania z tym samym seed generują 30 kart (10 świadectw × 3 motywy):

```bash
SEED=42
for THEME in red dark light; do
  python3 scripts/render_testimonial_cards.py \
    --testimonials nowe_zycie_26/swiadectwa_nz_260502_1634.md \
    --photos /ścieżka/do/zdjęć \
    --output output/sne_cards/$THEME \
    --count 10 \
    --theme $THEME \
    --seed $SEED
done
```
