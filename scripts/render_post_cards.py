#!/usr/bin/env python3
"""
render_post_cards.py — Generuje grafiki PNG (1200×628 px) dla postów social media AISP.

Wejście:  plik posts.md z wygenerowanymi draftami
          katalog grafiki/ z zasobami wizualnymi AISP
Wyjście:  pliki PNG w formacie LinkedIn Open Graph (1200×628 px)

Kompozycja karty:
  - tło: obraz z grafiki/ dopasowany do tematu posta (gradient navy→obraz)
  - logo AISP (aisp_logo_row_alpha.png)
  - etykieta lejka (AWARENESS / EDUCATION / CONVERSION) + język
  - hook (pierwsze zdanie/y posta)
  - profil (AISP / CEO)
  - pasek Electric Cyan na dole

Użycie:
  uv run python3 scripts/render_post_cards.py <posts.md> <grafiki_dir> [output_dir]
"""

import os
import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- Stałe brandingowe AISP ---
CARD_W, CARD_H = 1200, 628


@dataclass(frozen=True)
class ColorTheme:
    name: str
    base_bg: tuple[int, int, int]
    overlay_color: tuple[int, int, int]
    accent: tuple[int, int, int]
    text_primary: tuple[int, int, int]
    text_secondary: tuple[int, int, int]
    awareness: tuple[int, int, int]
    education: tuple[int, int, int]
    conversion: tuple[int, int, int]
    tagline: tuple[int, int, int]
    minimal_bg: tuple[int, int, int]
    panel_bg: tuple[int, int, int]
    dot_color: tuple[int, int, int]
    gradient_blend: float
    fullbg_blend: float


THEMES: dict[str, ColorTheme] = {
    "navy": ColorTheme(
        name="navy",
        base_bg=(10, 25, 47),
        overlay_color=(10, 25, 47),
        accent=(0, 209, 255),
        text_primary=(255, 255, 255),
        text_secondary=(156, 175, 196),
        awareness=(0, 209, 255),
        education=(100, 220, 150),
        conversion=(255, 180, 50),
        tagline=(80, 110, 140),
        minimal_bg=(8, 20, 42),
        panel_bg=(8, 20, 38),
        dot_color=(0, 60, 80),
        gradient_blend=0.42,
        fullbg_blend=0.66,
    ),
    "light": ColorTheme(
        name="light",
        base_bg=(245, 250, 255),
        overlay_color=(255, 255, 255),
        accent=(0, 123, 255),
        text_primary=(18, 52, 86),
        text_secondary=(80, 118, 155),
        awareness=(0, 123, 255),
        education=(0, 163, 128),
        conversion=(255, 150, 70),
        tagline=(98, 134, 168),
        minimal_bg=(240, 247, 255),
        panel_bg=(233, 242, 252),
        dot_color=(170, 205, 235),
        gradient_blend=0.28,
        fullbg_blend=0.36,
    ),
}

# Typy layoutów kart
LAYOUT_GRADIENT = "gradient"  # navy lewy panel + zdjęcie po prawej (domyślny)
LAYOUT_FULLBG = "fullbg"  # pełnoekranowe zdjęcie z ciemną nakładką
LAYOUT_STAT = "stat"  # duża liczba/metryka, czyste navy
LAYOUT_MINIMAL = "minimal"  # czyste navy, gruby akcent cyan, typografia
LAYOUT_CEO = "ceo"  # portret CEO po prawej, panel osobisty po lewej
IMAGE_BACKED_LAYOUTS = {LAYOUT_GRADIENT, LAYOUT_FULLBG, LAYOUT_CEO}


def get_theme(theme_name: str) -> ColorTheme:
    """Zwraca motyw kolorystyczny; domyślnie navy."""
    return THEMES.get(theme_name, THEMES["navy"])


# Mapowanie słów kluczowych → pula grafik (szersza paleta + rotacja)
BG_SELECTION: list[tuple[list[str], list[str]]] = [
    (
        ["liczbox", "smart city", "gmina", "samorząd", "miasto", "municipal"],
        ["liczbox.jpg", "countbox_intersection.png", "polskie_skrzyzowanie.png", "warszawa_ulice.jpeg"],
    ),
    (
        ["alpr", "license plate", "tablica rejestracyjna", "tablice", "anpr"],
        ["alpr_road_count.png", "highway_counted.png", "detekcja_obiekty.png"],
    ),
    (
        ["chmura", "cloud", "saas", "upload", "processing"],
        ["ekran_chmura.png", "new_reporting.png", "locations_screen.png"],
    ),
    (
        ["wynik", "result", "raport", "report", "accuracy", "dokładność", "97%", "data", "count"],
        ["ekran_wyniki.png", "new_reporting.png", "rondo_counted_pl_interface.png", "highway_counted.png"],
    ),
    (
        ["v2d", "vision to decision", "workflow", "5 steps", "5 etap"],
        ["v2d.png", "road_screen.png", "big_cross_section.png"],
    ),
    (
        ["lokacja", "location", "project", "projekt", "manage"],
        ["ekran_lokacje.png", "locations_screen.png", "ekran_design.png"],
    ),
    (
        ["skrzyżowanie", "intersection", "drone", "rondo", "potok"],
        ["big_cross_section.png", "intersection_drone.png", "polskie_skrzyzowanie.png", "ruch_rondo.png"],
    ),
    (
        ["reporting", "nowy raport", "new report", "dashboard", "panel"],
        ["new_reporting.png", "ekran_wyniki.png", "ekran_design.png"],
    ),
    (
        ["rodo", "anonimizacja", "privacy", "gdpr"],
        ["anonimizacja.png", "detekcja_obiekty.png"],
    ),
    (
        ["wielokamer", "4 kamery", "4 streams", "multi-camera"],
        ["4streams_together.png", "countbox_intersection.png", "road_screen.png"],
    ),
    (
        ["event", "konferencja", "demo day", "networking", "prelekcja", "wystąpienie"],
        [
            "konferencja_spotkanie_sala_wwa.jpeg",
            "demo_day_concordia.jpg",
            "spaszko_talks_demoda1.jpeg",
            "spaszko_talks_demoda2.jpeg",
        ],
    ),
]


def parse_posts(text: str) -> list[dict]:
    """Parsuje plik posts.md i zwraca listę słowników z danymi postów."""
    posts = []
    blocks = re.split(r"\n---+\n", text)
    for block in blocks:
        cel = re.search(r"\[CEL POSTA\]:\s*(.+)", block)
        profil = re.search(r"\[PROFIL\]:\s*(.+)", block)
        jezyk = re.search(r"\[JĘZYK\]:\s*(.+)", block)
        fmt = re.search(r"\[FORMAT\]:\s*(.+)", block)
        tresc = re.search(r"\[TREŚĆ POSTA\]:\s*\n(.*?)(?=\n\[PROPOZYCJA|\Z)", block, re.DOTALL)
        if cel and profil and jezyk and tresc:
            posts.append(
                {
                    "cel": cel.group(1).strip(),
                    "profil": profil.group(1).strip(),
                    "jezyk": jezyk.group(1).strip(),
                    "format": fmt.group(1).strip().lower() if fmt else "",
                    "tresc": tresc.group(1).strip(),
                    "number": len(posts) + 1,
                }
            )
    return posts


def is_text_heavy_post(post: dict) -> bool:
    """Wykrywa posty bardziej tekstowe, gdzie brandingowe tło sprawdza się lepiej."""
    content = post.get("tresc", "")
    fmt = post.get("format", "").lower()
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    sentence_count = len(re.findall(r"[\.!?]", content))

    if any(tag in fmt for tag in ["mini-seria", "tips", "tip", "edukacyjny", "longform"]):
        return True
    if len(content) >= 420:
        return True
    if len(lines) >= 6:
        return True
    return sentence_count >= 5


def select_background(post: dict, grafiki_dir: Path, variant_index: int = 0) -> Path:
    """Wybiera obraz tła z grafiki/ na podstawie treści i profilu posta."""
    profil_lower = post["profil"].lower()
    content_lower = post["tresc"].lower()
    post_number = max(1, int(post.get("number", 1))) + max(0, variant_index)
    brand_bg = grafiki_dir / "aisp_tlo_brand.jpg"

    # CEO / post osobisty → portret Sławka
    if "osobisty" in profil_lower or "sławomir" in profil_lower or "ceo" in profil_lower:
        ceo_candidates = [
            "slawomir_paszko_talking.jpg",
            "spaszko_talks_demoda1.jpeg",
            "spaszko_talks_demoda2.jpeg",
            "slawomir_paszko.jpg",
            "slawomir_paszko_ceo.png",
        ]
        existing_ceo = [grafiki_dir / name for name in ceo_candidates if (grafiki_dir / name).exists()]
        if existing_ceo:
            return existing_ceo[(post_number - 1) % len(existing_ceo)]

    # Dopasowanie wg słów kluczowych (zbierz wszystkie najlepsze kategorie)
    best_score = 0
    best_files: list[str] = []
    for keywords, filenames in BG_SELECTION:
        score = sum(content_lower.count(kw) for kw in keywords)
        if score <= 0:
            continue
        if score > best_score:
            best_score = score
            best_files = list(filenames)
        elif score == best_score:
            best_files.extend(filenames)

    # Promocja tła brandingowego przy postach bardziej tekstowych.
    if brand_bg.exists() and is_text_heavy_post(post):
        # Dla słabszego dopasowania tematycznego pokazuj brand częściej (2/3 wariantów).
        if best_score <= 2 and (post_number % 3) != 0:
            return brand_bg
        # Dla mocnego dopasowania wciąż dodaj brand do puli wariantów.
        best_files = ["aisp_tlo_brand.jpg", *best_files]

    if best_files:
        unique_files = list(dict.fromkeys(best_files))
        existing_candidates = [grafiki_dir / name for name in unique_files if (grafiki_dir / name).exists()]
        if existing_candidates:
            return existing_candidates[(post_number - 1) % len(existing_candidates)]

    # Fallback: szeroka rotacja bez słów kluczowych
    default_candidates = [
        "aisp_tlo_brand.jpg",
        "ekran_design.png",
        "road_screen.png",
        "ekran_wyniki.png",
        "ekran_chmura.png",
        "big_cross_section.png",
        "intersection_drone.png",
        "new_reporting.png",
    ]
    existing_defaults = [grafiki_dir / name for name in default_candidates if (grafiki_dir / name).exists()]
    if existing_defaults:
        return existing_defaults[(post_number - 1) % len(existing_defaults)]

    fallback = grafiki_dir / "road_screen.png"
    return fallback if fallback.exists() else next(grafiki_dir.glob("*.png"), grafiki_dir / "ekran_design.png")


# Tła, które wyglądają najlepiej z minimalnym gradientem (czyste, teksturowane).
_LOW_GRADIENT_BACKGROUNDS: frozenset[str] = frozenset({"aisp_tlo_brand.jpg"})


def bg_gradient_factor(bg_path: Path) -> float:
    """Zwraca mnożnik siły gradientu/przyciemnienia dla danego tła.

    1.0 → pełna siła (wszystkie zwykłe tła)
    0.25 → bardzo subtelny gradient (aisp_tlo_brand.jpg i podobne)
    """
    return 0.25 if bg_path.name in _LOW_GRADIENT_BACKGROUNDS else 1.0


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Ładuje czcionkę systemową (DejaVu → Liberation → FreeSans → default)."""
    suffix_bold = "-Bold" if bold else ""
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{suffix_bold}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans{suffix_bold if bold else '-Regular'}.ttf",
        f"/usr/share/fonts/truetype/freefont/FreeSans{'Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/ubuntu/Ubuntu{'B' if bold else ''}.ttf",
        "/System/Library/Fonts/Helvetica.ttc",  # macOS fallback
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def gradient_mask(width: int, height: int) -> Image.Image:
    """Tworzy maskę gradientową: navy po lewej → widoczne tło po prawej."""
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    start_x = int(width * 0.28)
    end_x = int(width * 0.62)
    for x in range(start_x, width):
        val = (
            int(210 * (x - start_x) / max(1, end_x - start_x)) if x < end_x else 210
        )  # Lekkie przyciemnienie po prawej
        draw.line([(x, 0), (x, height - 1)], fill=val)
    return mask


def vertical_gradient_overlay(
    width: int,
    height: int,
    color: tuple[int, int, int],
    top_h: int = 150,
    bottom_h: int = 120,
    max_alpha: int = 220,
) -> Image.Image:
    """Tworzy gradientową nakładkę NAVY na górę i dół karty — ochrona kontrastu logo i tekstów."""
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    r, g, b = color
    # Gradient od góry: pełny NAVY → przezroczysty
    for y in range(top_h):
        alpha = int(max_alpha * (1 - y / top_h) ** 1.4)
        draw.line([(0, y), (width - 1, y)], fill=(r, g, b, alpha))
    # Gradient od dołu: przezroczysty → pełny NAVY
    for y in range(bottom_h):
        alpha = int(max_alpha * (1 - y / bottom_h) ** 1.4)
        draw.line([(0, height - 1 - y), (width - 1, height - 1 - y)], fill=(r, g, b, alpha))
    return overlay


def strip_emoji(text: str) -> str:
    """Usuwa emoji, które nie renderują się poprawnie w DejaVu."""
    return re.sub(r"[^\u0000-\u007E\u00C0-\u024F\u0100-\u024F\u2000-\u206F ]", "", text).strip()


def extract_hook(tresc: str, max_chars: int = 140) -> str:
    """Wyciąga haczyk (pierwsze zdanie/a) z treści posta, bez emoji."""
    lines = [l.strip() for l in tresc.split("\n") if l.strip()]
    if not lines:
        return ""
    hook = strip_emoji(lines[0])
    # Jeśli pierwsza linia jest bardzo krótka, dodaj drugą
    if len(hook) < 65 and len(lines) > 1:
        second = strip_emoji(lines[1])
        if second:
            hook = hook + " " + second
    return hook[:max_chars]


def cel_to_label(cel: str, theme: ColorTheme) -> tuple[str, tuple[int, int, int]]:
    """Zwraca klucz lejka i kolor akcentu dla danego celu (używane do koloru tekstu)."""
    cel_lower = cel.lower()
    if any(w in cel_lower for w in ["świadomość", "góra", "awareness"]):
        return "awareness", theme.awareness
    if any(w in cel_lower for w in ["edukacja", "środek", "education"]):
        return "education", theme.education
    if any(w in cel_lower for w in ["konwersja", "dół", "conversion"]):
        return "conversion", theme.conversion
    return "awareness", theme.text_secondary


# Brandingowe hasła per (lejek, język) — widoczne na kartach LinkedIn
_FUNNEL_TAGLINES: dict[tuple[str, str], str] = {
    ("awareness", "EN"): "Count traffic and pedestrians from any video",
    ("awareness", "PL"): "Zmierz ruch AI z twojej kamery",
    ("education", "EN"): "97% counting accuracy · Define relationships as you wish",
    ("education", "PL"): "97% dokładności zliczania · Definuj relacje jak chcesz ",
    ("conversion", "EN"): "Cut traffic survey costs by 70%",
    ("conversion", "PL"): "Zredukuj koszty pomiarów ruchu o 70%",
}


def funnel_tagline(cel: str, jezyk: str) -> str:
    """Zwraca brandingowe hasło dla danej pozycji w lejku i języka."""
    key, _ = cel_to_label(cel, THEMES["navy"])  # klucz niezależny od motywu
    lang = "PL" if jezyk.upper() == "PL" else "EN"
    return _FUNNEL_TAGLINES.get((key, lang), "From camera to traffic data.")


def pick_layout(post: dict) -> str:
    """Wybiera optymalny layout na podstawie profilu, formatu i treści posta."""
    profil_lower = post["profil"].lower()
    content_lower = post["tresc"].lower()
    fmt = post.get("format", "")

    # CEO / post osobisty → portret Sławka
    if "osobisty" in profil_lower or "sławomir" in profil_lower or "ceo" in profil_lower:
        return LAYOUT_CEO

    # Ankieta lub mini-seria → minimal (czysty, bez hałaśliwego tła)
    if "ankieta" in fmt or "poll" in fmt or "mini-seria" in fmt:
        return LAYOUT_MINIMAL

    # Posty z silnymi statystykami → STAT
    stat_hits = len(re.findall(r"\d+\s*%|\d{3,}\s*(?:pojazdów|vehicles|counts?|pomiarów|mln)", content_lower))
    if stat_hits >= 1:
        return LAYOUT_STAT

    # Drone/skrzyżowanie → pełnoekranowe zdjęcie
    if any(kw in content_lower for kw in ["drone", "dron", "intersection", "skrzyżowanie", "noc", "night"]):
        return LAYOUT_FULLBG

    # Rotacja: co 4. post → minimal dla uniknięcia monotonii
    if post.get("number", 1) % 4 == 0:
        return LAYOUT_MINIMAL

    return LAYOUT_GRADIENT


def render_card_gradient(
    post: dict, grafiki_dir: Path, output_path: Path, variant_index: int = 0, theme_name: str = "navy"
) -> None:
    """Layout GRADIENT: panel navy po lewej + zdjęcie po prawej (domyślny)."""

    # 1. Bazowe płótno w kolorze navy
    theme = get_theme(theme_name)
    card = Image.new("RGB", (CARD_W, CARD_H), theme.base_bg)

    # 2. Obraz tła z gradientem (prawa strona)
    bg_path = select_background(post, grafiki_dir, variant_index)
    gfactor = bg_gradient_factor(bg_path)
    try:
        bg = Image.open(bg_path).convert("RGB")
        scale = max(CARD_W / bg.width, CARD_H / bg.height)
        bg = bg.resize((int(bg.width * scale), int(bg.height * scale)), Image.LANCZOS)
        x0 = (bg.width - CARD_W) // 2
        y0 = (bg.height - CARD_H) // 2
        bg = bg.crop((x0, y0, x0 + CARD_W, y0 + CARD_H))
        # Przyciemnij obraz tła (siła skalowana przez gfactor)
        dimmed = Image.blend(
            bg, Image.new("RGB", (CARD_W, CARD_H), theme.overlay_color), theme.gradient_blend * gfactor
        )
        card.paste(dimmed, (0, 0), gradient_mask(CARD_W, CARD_H))
        # Pionowe gradienty na górę i dół — siła zależna od tła
        vgrad = vertical_gradient_overlay(CARD_W, CARD_H, color=theme.overlay_color, max_alpha=int(190 * gfactor))
        card_rgba = card.convert("RGBA")
        card_rgba = Image.alpha_composite(card_rgba, vgrad)
        card = card_rgba.convert("RGB")
    except Exception as e:
        print(f"  [warn] Tło {bg_path.name}: {e}")

    draw = ImageDraw.Draw(card)
    PAD_X, PAD_Y = 72, 52

    # 3. Logo AISP
    logo_path = grafiki_dir / "aisp_logo_row_alpha.png"
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo_h = 38
        logo_w = int(logo.width * logo_h / logo.height)
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        card.paste(logo, (PAD_X, PAD_Y), logo)
        y_after_logo = PAD_Y + logo_h + 22
    except Exception:
        draw.text((PAD_X, PAD_Y), "AISP", font=load_font(28, bold=True), fill=theme.accent)
        y_after_logo = PAD_Y + 50

    # 4. Brandingowe hasło (lejek + język)
    _, label_color = cel_to_label(post["cel"], theme)
    draw.text((PAD_X, y_after_logo), funnel_tagline(post["cel"], post["jezyk"]), font=load_font(13), fill=label_color)

    # 5. Hook (pierwsze zdanie posta)
    hook = extract_hook(post["tresc"])
    font_hook = load_font(31, bold=True)
    wrapped_lines = textwrap.wrap(hook, width=30)[:4]
    y_hook = y_after_logo + 30
    line_height = 44
    for line in wrapped_lines:
        draw.text((PAD_X, y_hook), line, font=font_hook, fill=theme.text_primary)
        y_hook += line_height

    # 6. Separator cyan
    sep_y = min(y_hook + 18, CARD_H - 130)
    draw.line([(PAD_X, sep_y), (PAD_X + 60, sep_y)], fill=theme.accent, width=3)

    # 7. Profil
    profil = post["profil"]
    if "firmowy" in profil.lower() or ("aisp" in profil.lower() and "osobisty" not in profil.lower()):
        profil_label = "linkedin.com/company/aisp-poland"
    else:
        profil_label = "Sławomir Paszko  ·  CEO AISP"
    draw.text((PAD_X, CARD_H - PAD_Y - 36), profil_label, font=load_font(15), fill=theme.text_secondary)

    # 8. Tagline
    draw.text(
        (PAD_X, CARD_H - PAD_Y - 16),
        "aisp.pl  ·  From camera to traffic data. Automatically.",
        font=load_font(13),
        fill=theme.tagline,
    )

    # 9. Pasek Electric Cyan na dole
    draw.rectangle([(0, CARD_H - 5), (CARD_W, CARD_H)], fill=theme.accent)

    # Zapis
    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(str(output_path), "PNG", optimize=True)
    print(f"  ✓ {output_path.name}  [tło: {bg_path.name}]")


def render_card_fullbg(
    post: dict, grafiki_dir: Path, output_path: Path, variant_index: int = 0, theme_name: str = "navy"
) -> None:
    """Layout FULLBG: pełnoekranowe zdjęcie z ciemną nakładką i wyśrodkowanym hookiem."""
    theme = get_theme(theme_name)
    card = Image.new("RGB", (CARD_W, CARD_H), theme.base_bg)
    bg_path = select_background(post, grafiki_dir, variant_index)
    gfactor = bg_gradient_factor(bg_path)

    try:
        bg = Image.open(bg_path).convert("RGB")
        scale = max(CARD_W / bg.width, CARD_H / bg.height)
        bg = bg.resize((int(bg.width * scale), int(bg.height * scale)), Image.LANCZOS)
        x0 = (bg.width - CARD_W) // 2
        y0 = (bg.height - CARD_H) // 2
        bg = bg.crop((x0, y0, x0 + CARD_W, y0 + CARD_H))
        overlay = Image.new("RGB", (CARD_W, CARD_H), theme.overlay_color)
        card = Image.blend(bg, overlay, theme.fullbg_blend * gfactor)
        # Pionowe gradienty — siła zależna od tła
        vgrad = vertical_gradient_overlay(
            CARD_W, CARD_H, color=theme.overlay_color, top_h=170, bottom_h=130, max_alpha=int(180 * gfactor)
        )
        card_rgba = card.convert("RGBA")
        card_rgba = Image.alpha_composite(card_rgba, vgrad)
        card = card_rgba.convert("RGB")
    except Exception as e:
        print(f"  [warn] Tło {bg_path.name}: {e}")

    draw = ImageDraw.Draw(card)
    PAD_X, PAD_Y = 80, 48

    # Logo top-left
    logo_path = grafiki_dir / "aisp_logo_row_alpha.png"
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo_h = 36
        logo_w = int(logo.width * logo_h / logo.height)
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        card.paste(logo, (PAD_X, PAD_Y), logo)
    except Exception:
        draw.text((PAD_X, PAD_Y), "AISP", font=load_font(28, bold=True), fill=theme.accent)

    # Brandingowe hasło — top right
    _, label_color = cel_to_label(post["cel"], theme)
    label_text = funnel_tagline(post["cel"], post["jezyk"])
    label_font = load_font(13)
    bbox = draw.textbbox((0, 0), label_text, font=label_font)
    label_w = bbox[2] - bbox[0]
    draw.text((CARD_W - PAD_X - label_w, PAD_Y + 10), label_text, font=label_font, fill=label_color)

    # Hook — wyśrodkowany, duży
    hook = extract_hook(post["tresc"], max_chars=120)
    font_hook = load_font(38, bold=True)
    wrapped_lines = textwrap.wrap(hook, width=28)[:4]
    total_h = len(wrapped_lines) * 54
    y_start = (CARD_H - total_h) // 2 - 20
    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font_hook)
        lw = bbox[2] - bbox[0]
        draw.text(((CARD_W - lw) // 2, y_start), line, font=font_hook, fill=theme.text_primary)
        y_start += 54

    # Profil — wyśrodkowany w dolnej części
    profil = post["profil"]
    if "firmowy" in profil.lower() or ("aisp" in profil.lower() and "osobisty" not in profil.lower()):
        profil_label = "linkedin.com/company/aisp-poland"
    else:
        profil_label = "Sławomir Paszko  ·  CEO AISP"
    pfont = load_font(15)
    bbox = draw.textbbox((0, 0), profil_label, font=pfont)
    pw = bbox[2] - bbox[0]
    draw.text(((CARD_W - pw) // 2, CARD_H - PAD_Y - 36), profil_label, font=pfont, fill=theme.text_secondary)

    tagline = "aisp.pl  ·  From camera to traffic data. Automatically."
    tfont = load_font(13)
    bbox = draw.textbbox((0, 0), tagline, font=tfont)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_W - tw) // 2, CARD_H - PAD_Y - 16), tagline, font=tfont, fill=theme.tagline)

    draw.rectangle([(0, CARD_H - 5), (CARD_W, CARD_H)], fill=theme.accent)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(str(output_path), "PNG", optimize=True)
    print(f"  ✓ {output_path.name}  [fullbg: {bg_path.name}]")


def render_card_stat(
    post: dict, grafiki_dir: Path, output_path: Path, variant_index: int = 0, theme_name: str = "navy"
) -> None:
    """Layout STAT: duża liczba/metryka centralnie, czyste navy z akcentem cyan."""
    theme = get_theme(theme_name)
    card = Image.new("RGB", (CARD_W, CARD_H), theme.base_bg)
    draw = ImageDraw.Draw(card)
    PAD_X, PAD_Y = 80, 48

    # Trzy cienkie ramy cyan (góra, dół, lewy pasek)
    draw.rectangle([(0, 0), (CARD_W, 5)], fill=theme.accent)
    draw.rectangle([(0, CARD_H - 5), (CARD_W, CARD_H)], fill=theme.accent)
    draw.rectangle([(0, 0), (6, CARD_H)], fill=theme.accent)

    # Ciemniejszy prostokąt wewnętrzny
    draw.rectangle([(PAD_X - 10, 70), (CARD_W - PAD_X + 10, CARD_H - 70)], fill=theme.panel_bg)

    # Logo top-left
    logo_path = grafiki_dir / "aisp_logo_row_alpha.png"
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo_h = 34
        logo_w = int(logo.width * logo_h / logo.height)
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        card.paste(logo, (PAD_X, PAD_Y + 14), logo)
    except Exception:
        draw.text((PAD_X, PAD_Y + 14), "AISP", font=load_font(24, bold=True), fill=theme.accent)

    # Próba wyciągnięcia statystyki z treści
    stat_match = re.search(
        r"(\d+[\.,]?\d*\s*%|\d{2,}\s*(?:pojazdów|vehicles|pomiarów|mln|k\b))",
        post["tresc"],
        re.IGNORECASE,
    )
    if stat_match:
        stat_text = stat_match.group(1).strip()
        font_big = load_font(100, bold=True)
        bbox = draw.textbbox((0, 0), stat_text, font=font_big)
        sw = bbox[2] - bbox[0]
        draw.text(((CARD_W - sw) // 2, 155), stat_text, font=font_big, fill=theme.accent)
        y_hook = 300
    else:
        y_hook = 155

    # Hook — wyśrodkowany
    hook = extract_hook(post["tresc"], max_chars=110)
    font_hook = load_font(32, bold=True)
    wrapped_lines = textwrap.wrap(hook, width=34)[:3]
    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font_hook)
        lw = bbox[2] - bbox[0]
        draw.text(((CARD_W - lw) // 2, y_hook), line, font=font_hook, fill=theme.text_primary)
        y_hook += 46

    # Brandingowe hasło i tagline na dole
    _, label_color = cel_to_label(post["cel"], theme)
    draw.text(
        (PAD_X, CARD_H - PAD_Y - 36), funnel_tagline(post["cel"], post["jezyk"]), font=load_font(13), fill=label_color
    )
    draw.text(
        (PAD_X, CARD_H - PAD_Y - 16),
        "aisp.pl  ·  From camera to traffic data. Automatically.",
        font=load_font(13),
        fill=theme.tagline,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(str(output_path), "PNG", optimize=True)
    print(f"  ✓ {output_path.name}  [stat layout]")


def render_card_minimal(
    post: dict, grafiki_dir: Path, output_path: Path, variant_index: int = 0, theme_name: str = "navy"
) -> None:
    """Layout MINIMAL: czyste navy, gruby pionowy akcent cyan, duża typografia."""
    theme = get_theme(theme_name)
    card = Image.new("RGB", (CARD_W, CARD_H), theme.minimal_bg)
    draw = ImageDraw.Draw(card)
    PAD_X, PAD_Y = 88, 52

    # Gruby pionowy pasek cyan po lewej
    draw.rectangle([(PAD_X - 44, 0), (PAD_X - 32, CARD_H)], fill=theme.accent)
    # Dolny pasek
    draw.rectangle([(0, CARD_H - 5), (CARD_W, CARD_H)], fill=theme.accent)
    # Subtelne punkty dekoracyjne (prawa strona)
    for row in range(6):
        for col in range(5):
            cx = CARD_W - 120 + col * 22
            cy = 80 + row * 22
            draw.ellipse([(cx - 2, cy - 2), (cx + 2, cy + 2)], fill=theme.dot_color)

    # Logo
    logo_path = grafiki_dir / "aisp_logo_row_alpha.png"
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo_h = 34
        logo_w = int(logo.width * logo_h / logo.height)
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        card.paste(logo, (PAD_X, PAD_Y), logo)
    except Exception:
        draw.text((PAD_X, PAD_Y), "AISP", font=load_font(24, bold=True), fill=theme.accent)

    # Brandingowe hasło
    _, label_color = cel_to_label(post["cel"], theme)
    draw.text((PAD_X, PAD_Y + 52), funnel_tagline(post["cel"], post["jezyk"]), font=load_font(13), fill=label_color)

    # Hook — duży, lewy
    hook = extract_hook(post["tresc"], max_chars=130)
    font_hook = load_font(36, bold=True)
    wrapped_lines = textwrap.wrap(hook, width=28)[:4]
    y_hook = PAD_Y + 90
    for line in wrapped_lines:
        draw.text((PAD_X, y_hook), line, font=font_hook, fill=theme.text_primary)
        y_hook += 50

    # Druga linia treści jako podtytuł
    lines_all = [li.strip() for li in post["tresc"].split("\n") if li.strip()]
    if len(lines_all) > 1:
        context = strip_emoji(lines_all[1])[:100]
        if context:
            draw.text((PAD_X, y_hook + 14), context, font=load_font(18), fill=theme.text_secondary)

    # Profil i tagline
    profil = post["profil"]
    if "firmowy" in profil.lower() or ("aisp" in profil.lower() and "osobisty" not in profil.lower()):
        profil_label = "linkedin.com/company/aisp-poland"
    else:
        profil_label = "Sławomir Paszko  ·  CEO AISP"
    draw.text((PAD_X, CARD_H - PAD_Y - 36), profil_label, font=load_font(15), fill=theme.text_secondary)
    draw.text(
        (PAD_X, CARD_H - PAD_Y - 16),
        "aisp.pl  ·  From camera to traffic data. Automatically.",
        font=load_font(13),
        fill=theme.tagline,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(str(output_path), "PNG", optimize=True)
    print(f"  ✓ {output_path.name}  [minimal layout]")


def render_card_ceo(
    post: dict, grafiki_dir: Path, output_path: Path, variant_index: int = 0, theme_name: str = "navy"
) -> None:
    """Layout CEO: portret Sławka ostry po prawej, panel osobisty po lewej."""
    theme = get_theme(theme_name)
    card = Image.new("RGB", (CARD_W, CARD_H), theme.base_bg)

    # Portret — prawa 46% karty
    ceo_candidates = [
        "slawomir_paszko_talking.jpg",
        "spaszko_talks_demoda1.jpeg",
        "spaszko_talks_demoda2.jpeg",
        "slawomir_paszko.jpg",
        "slawomir_paszko_ceo.png",
    ]
    existing_ceo = [grafiki_dir / name for name in ceo_candidates if (grafiki_dir / name).exists()]
    portrait_path = (
        existing_ceo[variant_index % len(existing_ceo)] if existing_ceo else grafiki_dir / "slawomir_paszko.jpg"
    )
    portrait_w = int(CARD_W * 0.46)
    bg_name = portrait_path.name
    try:
        portrait = Image.open(portrait_path).convert("RGB")
        scale = max(portrait_w / portrait.width, CARD_H / portrait.height)
        portrait = portrait.resize((int(portrait.width * scale), int(portrait.height * scale)), Image.LANCZOS)
        x0 = max(0, (portrait.width - portrait_w) // 2)
        portrait = portrait.crop((x0, 0, x0 + portrait_w, CARD_H))
        # Gradientowa maska — rozmycie lewej krawędzi portretu
        mask = Image.new("L", (portrait_w, CARD_H), 255)
        md = ImageDraw.Draw(mask)
        blend_w = 200
        for x in range(blend_w):
            val = int(255 * (x / blend_w) ** 1.8)
            md.line([(x, 0), (x, CARD_H - 1)], fill=val)
        card.paste(portrait, (CARD_W - portrait_w, 0), mask)
        # Pionowe gradienty NAVY na obszar portretu — ochrona kontrastu
        vgrad = vertical_gradient_overlay(
            portrait_w, CARD_H, color=theme.overlay_color, top_h=130, bottom_h=100, max_alpha=160
        )
        portrait_area = card.crop((CARD_W - portrait_w, 0, CARD_W, CARD_H))
        portrait_area_rgba = portrait_area.convert("RGBA")
        portrait_area_rgba = Image.alpha_composite(portrait_area_rgba, vgrad)
        card.paste(portrait_area_rgba.convert("RGB"), (CARD_W - portrait_w, 0))
    except Exception as e:
        print(f"  [warn] Portret CEO: {e}")

    # Lewy panel — neprzezroczysty navy do ~58% szerokości
    panel_overlay = Image.new("RGB", (int(CARD_W * 0.60), CARD_H), theme.base_bg)
    card.paste(panel_overlay, (0, 0))

    draw = ImageDraw.Draw(card)
    PAD_X, PAD_Y = 60, 48

    # Cienka pionowa linia cyan
    draw.rectangle([(PAD_X - 16, PAD_Y + 10), (PAD_X - 10, CARD_H - PAD_Y - 10)], fill=theme.accent)
    # Dolny pasek cyan
    draw.rectangle([(0, CARD_H - 5), (CARD_W, CARD_H)], fill=theme.accent)

    # Logo
    logo_path = grafiki_dir / "aisp_logo_row_alpha.png"
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo_h = 34
        logo_w = int(logo.width * logo_h / logo.height)
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        card.paste(logo, (PAD_X, PAD_Y), logo)
    except Exception:
        draw.text((PAD_X, PAD_Y), "AISP", font=load_font(24, bold=True), fill=theme.accent)

    # Brandingowe hasło
    _, label_color = cel_to_label(post["cel"], theme)
    draw.text((PAD_X, PAD_Y + 52), funnel_tagline(post["cel"], post["jezyk"]), font=load_font(13), fill=label_color)

    # Hook — lewy panel, wrap węższy (portret zajmuje prawą stronę)
    hook = extract_hook(post["tresc"], max_chars=120)
    font_hook = load_font(32, bold=True)
    wrapped_lines = textwrap.wrap(hook, width=22)[:5]
    y_hook = PAD_Y + 88
    for line in wrapped_lines:
        draw.text((PAD_X, y_hook), line, font=font_hook, fill=theme.text_primary)
        y_hook += 46

    # Profil CEO — cyan (wyróżniony)
    draw.text((PAD_X, CARD_H - PAD_Y - 36), "Sławomir Paszko  ·  CEO AISP", font=load_font(15), fill=theme.accent)
    draw.text(
        (PAD_X, CARD_H - PAD_Y - 16),
        "aisp.pl  ·  From camera to traffic data. Automatically.",
        font=load_font(13),
        fill=theme.tagline,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(str(output_path), "PNG", optimize=True)
    print(f"  ✓ {output_path.name}  [CEO layout: {bg_name}]")


def pick_layout_variant(post: dict, variant_index: int) -> str:
    """Wybiera layout wariantu — rotuje layouty obrazkowe dla wizualnej różnorodności."""
    base_layout = pick_layout(post)

    profil_lower = post["profil"].lower()
    is_ceo = "osobisty" in profil_lower or "sławomir" in profil_lower or "ceo" in profil_lower

    if is_ceo:
        # CEO: wariant 0 → portret, wariant 1 → gradient z innym zdjęciem CEO
        ceo_layouts = [LAYOUT_CEO, LAYOUT_GRADIENT, LAYOUT_FULLBG]
        return ceo_layouts[variant_index % len(ceo_layouts)]

    # Wymuszenie tła obrazkowego: bez wariantów stat/minimal.
    normalized_base = base_layout if base_layout in IMAGE_BACKED_LAYOUTS else LAYOUT_GRADIENT
    layouts = [normalized_base, LAYOUT_FULLBG, LAYOUT_GRADIENT]
    unique_layouts = list(dict.fromkeys(layouts))
    return unique_layouts[variant_index % len(unique_layouts)]


def render_card(
    post: dict, grafiki_dir: Path, output_path: Path, variant_index: int = 0, theme_name: str = "navy"
) -> None:
    """Dispatcher — wybiera layout i renderuje kartę posta."""
    layout = pick_layout_variant(post, variant_index)
    if layout == LAYOUT_FULLBG:
        render_card_fullbg(post, grafiki_dir, output_path, variant_index, theme_name)
    elif layout == LAYOUT_STAT:
        render_card_stat(post, grafiki_dir, output_path, variant_index, theme_name)
    elif layout == LAYOUT_MINIMAL:
        render_card_minimal(post, grafiki_dir, output_path, variant_index, theme_name)
    elif layout == LAYOUT_CEO:
        render_card_ceo(post, grafiki_dir, output_path, variant_index, theme_name)
    else:
        render_card_gradient(post, grafiki_dir, output_path, variant_index, theme_name)


def main() -> None:
    if len(sys.argv) < 3:
        print("Użycie: render_post_cards.py <posts.md> <grafiki_dir> [output_dir] [variants] [theme: navy|light|both]")
        sys.exit(1)

    posts_md_path = Path(sys.argv[1])
    grafiki_dir = Path(sys.argv[2])

    output_dir = posts_md_path.parent / "images"
    variants = 1
    theme_mode = "navy"
    if len(sys.argv) > 3:
        if sys.argv[3].isdigit():
            variants = max(1, int(sys.argv[3]))
        elif sys.argv[3].lower() in {"navy", "light", "both"}:
            theme_mode = sys.argv[3].lower()
        else:
            output_dir = Path(sys.argv[3])
    if len(sys.argv) > 4 and sys.argv[4].isdigit():
        variants = max(1, int(sys.argv[4]))
    if len(sys.argv) > 4 and sys.argv[4].lower() in {"navy", "light", "both"}:
        theme_mode = sys.argv[4].lower()
    if len(sys.argv) > 5 and sys.argv[5].lower() in {"navy", "light", "both"}:
        theme_mode = sys.argv[5].lower()

    if not posts_md_path.exists():
        print(f"Błąd: plik {posts_md_path} nie istnieje.")
        sys.exit(1)

    if not grafiki_dir.is_dir():
        print(f"Błąd: katalog {grafiki_dir} nie istnieje.")
        sys.exit(1)

    text = posts_md_path.read_text(encoding="utf-8")
    posts = parse_posts(text)

    if not posts:
        print(f"Nie znaleziono postów w {posts_md_path}. Sprawdź format [CEL POSTA], [PROFIL] itp.")
        sys.exit(0)

    themes_to_render = ["navy", "light"] if theme_mode == "both" else [theme_mode]

    print(
        f"Znaleziono {len(posts)} postów. Renderuję karty LinkedIn (1200×628 px), "
        f"warianty: {variants}, motywy: {', '.join(themes_to_render)}..."
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    for post in posts:
        lang_slug = post["jezyk"].lower().replace("/", "_").replace(" ", "")
        for theme_name in themes_to_render:
            theme_suffix = "" if len(themes_to_render) == 1 else f"_{theme_name}"
            for variant_index in range(variants):
                suffix = "" if variants == 1 else f"_v{variant_index + 1}"
                filename = f"post{post['number']}_{lang_slug}{theme_suffix}{suffix}.png"
                render_card(post, grafiki_dir, output_dir / filename, variant_index, theme_name)

    print(f"\nGotowe — {len(posts) * variants * len(themes_to_render)} kart w: {output_dir}")


if __name__ == "__main__":
    main()
