#!/usr/bin/env python3
"""
render_testimonial_cards.py — Generuje grafiki PNG (1200x628 px) ze świadectwami SNE.

Kolorystyka: czerwona (SNE Lubecko).
Logo: images/logotyp.png (lub --logo).
Tło: losowe zdjęcie z katalogu --photos.

Użycie:
  # Losowe świadectwa z pliku:
  python3 scripts/render_testimonial_cards.py \\
      --testimonials nowe_zycie_26/swiadectwa_nz_260502_1634.md \\
      --photos /ścieżka/do/zdjęć \\
      --count 10 \\
      --output output/cards

  # Podane ręcznie:
  python3 scripts/render_testimonial_cards.py \\
      --photos /ścieżka/do/zdjęć \\
      --author "Iza" \\
      --text "Kurs pozwolił mi zbliżyć się do Boga..." \\
      --output output/cards
"""

import argparse
import random
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Wymiary karty (LinkedIn Open Graph)
# ---------------------------------------------------------------------------
CARD_W, CARD_H = 1200, 628


# ---------------------------------------------------------------------------
# Paleta kolorów SNE (czerwona)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ColorTheme:
    name: str
    base_bg: tuple[int, int, int]
    overlay_color: tuple[int, int, int]
    accent: tuple[int, int, int]
    text_primary: tuple[int, int, int]
    text_secondary: tuple[int, int, int]
    panel_bg: tuple[int, int, int]
    tagline_color: tuple[int, int, int]
    quote_color: tuple[int, int, int]
    gradient_blend: float
    fullbg_blend: float
    shadow_color: tuple[int, int, int] = (0, 0, 0)


# Bazowy odcień SNE: #D3413F
_ACCENT = (211, 65, 63)  # #D3413F

SNE_RED = ColorTheme(
    name="sne_red",
    base_bg=(45, 6, 6),  # bardzo ciemna czerwień
    overlay_color=(60, 8, 8),
    accent=_ACCENT,
    text_primary=(255, 250, 248),  # niemal biały
    text_secondary=(240, 210, 208),  # jasny różowawy
    panel_bg=(30, 4, 4),
    tagline_color=(200, 150, 148),
    quote_color=(255, 220, 215),
    gradient_blend=0.40,
    fullbg_blend=0.40,  # słabszy — czerwień nie bije po oczach
    shadow_color=(0, 0, 0),
)

SNE_DARK = ColorTheme(
    name="sne_dark",
    base_bg=(18, 3, 3),
    overlay_color=(18, 3, 3),
    accent=_ACCENT,
    text_primary=(255, 252, 250),
    text_secondary=(220, 180, 178),
    panel_bg=(12, 2, 2),
    tagline_color=(255, 160, 160),
    quote_color=(255, 210, 205),
    gradient_blend=0.40,
    fullbg_blend=0.44,  # trochę słabsze niż poprzednie 0.76
    shadow_color=(0, 0, 0),
)

# Schemat odwrotny: białe tło, czerwone akcenty, szare teksty pomocnicze
_ACCENT_LIGHT = (230, 100, 98)  # jaśniejsza czerwień dla motywu light na zdjęciu
SNE_LIGHT = ColorTheme(
    name="sne_light",
    base_bg=(255, 255, 255),
    overlay_color=(245, 240, 240),
    accent=_ACCENT,
    text_primary=(30, 20, 20),  # ciemny — czytelny na jasnym tle
    text_secondary=(51, 51, 51),  # #333333 — ciemny szary
    panel_bg=(245, 240, 240),
    tagline_color=(100, 100, 100),
    quote_color=_ACCENT_LIGHT,  # akcent czerwony na jasnym tle
    gradient_blend=0.25,
    fullbg_blend=0.40,
    shadow_color=(255, 255, 255),  # biały cień na jasnym tle
)

THEMES = {"red": SNE_RED, "dark": SNE_DARK, "light": SNE_LIGHT}

# Typy layoutów (identyczne jak w render_post_cards.py)
LAYOUT_GRADIENT = "gradient"  # panel po lewej + zdjęcie po prawej
LAYOUT_GRADIENT_RTL = "gradient_rtl"  # panel po prawej + zdjęcie po lewej
LAYOUT_FULLBG = "fullbg"  # pełnoekranowe zdjęcie z nakładką
LAYOUT_MINIMAL = "minimal"  # czyste tło, pionowy akcent, typografia
LAYOUT_STAT = "stat"  # duży cytat centralnie, czyste tło
ALL_LAYOUTS = [
    LAYOUT_GRADIENT,
    LAYOUT_GRADIENT_RTL,
    LAYOUT_FULLBG,
    LAYOUT_MINIMAL,
    LAYOUT_STAT,
]

TAGLINE_MOTTO = "Nie bądź sam ze swoją wiarą"
TAGLINE_BRAND = "SNE Lubecko  ·  sne.lubecko.pl"


# ---------------------------------------------------------------------------
# Parser świadectw
# ---------------------------------------------------------------------------
def parse_testimonials(path: Path) -> list[dict]:
    """
    Parsuje plik .md ze świadectwami w formacie:
        <tekst akapitu>
        <Imię autora>

        <tekst akapitu>
        <Imię autora>
        ...
    Zwraca listę słowników {"text": str, "author": str}.
    """
    text = path.read_text(encoding="utf-8")

    # Usuń nagłówki markdown i sekcje meta
    text = re.sub(r"^#{1,6}.*$", "", text, flags=re.MULTILINE)

    # Podziel na bloki (puste linie jako separator)
    raw_blocks = re.split(r"\n{2,}", text.strip())

    testimonials = []
    for block in raw_blocks:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        if len(lines) < 2:
            continue
        # Pomijamy bloki meta (Anonimowe, niepodpisane — sekcja pomocnicza)
        if lines[0].startswith("Wszystko było piękne"):
            continue
        author = lines[-1]
        body = " ".join(lines[:-1])
        # Odfiltruj zbyt krótkie
        if len(body) < 30:
            continue
        testimonials.append({"text": body, "author": author})

    return testimonials


# ---------------------------------------------------------------------------
# Narzędzia pomocnicze
# ---------------------------------------------------------------------------
def load_font_italic(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-RI.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    suffix_bold = "-Bold" if bold else ""
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{suffix_bold}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans{'-Bold' if bold else '-Regular'}.ttf",
        f"/usr/share/fonts/truetype/freefont/FreeSans{'Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/ubuntu/Ubuntu{'B' if bold else ''}.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def strip_emoji(text: str) -> str:
    return re.sub(r"[^\u0000-\u007E\u00C0-\u024F\u2000-\u206F ]", "", text).strip()


def truncate_text(text: str, max_chars: int = 220) -> str:
    """Skraca tekst do max_chars, nie ucinając w połowie słowa."""
    text = strip_emoji(text)
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(" ", 1)[0]
    return cut.rstrip(".,;:") + "…"


def random_photo(photos_dir: Path) -> Path | None:
    extensions = {".jpg", ".jpeg", ".png", ".webp"}
    photos = [p for p in photos_dir.iterdir() if p.suffix.lower() in extensions]
    return random.choice(photos) if photos else None


def gradient_mask(
    width: int,
    height: int,
    start_frac: float = 0.28,
    end_frac: float = 0.62,
    rtl: bool = False,
) -> Image.Image:
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    start_x = int(width * start_frac)
    end_x = int(width * end_frac)
    for x in range(start_x, width):
        alpha = int(255 * min(1.0, (x - start_x) / max(1, end_x - start_x)))
        draw.line([(x, 0), (x, height)], fill=alpha)
    if rtl:
        mask = mask.transpose(Image.FLIP_LEFT_RIGHT)
    return mask


def vertical_gradient_overlay(
    width: int,
    height: int,
    color: tuple[int, int, int],
    top_h: int = 160,
    bottom_h: int = 130,
    max_alpha: int = 230,
) -> Image.Image:
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    r, g, b = color
    for y in range(top_h):
        a = int(max_alpha * (1 - y / top_h))
        draw.line([(0, y), (width, y)], fill=(r, g, b, a))
    for y in range(bottom_h):
        a = int(max_alpha * (y / bottom_h))
        draw.line(
            [(0, height - bottom_h + y), (width, height - bottom_h + y)],
            fill=(r, g, b, a),
        )
    return overlay


def draw_logo(
    card: Image.Image, logo_path: Path, pad_x: int, pad_y: int, size: int = 60
) -> int:
    """Nakłada kwadratowy logotyp i zwraca y po logo."""
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((size, size), Image.LANCZOS)
        card.paste(logo, (pad_x, pad_y), logo)
        return pad_y + size + 14
    except Exception:
        draw = ImageDraw.Draw(card)
        draw.text(
            (pad_x, pad_y),
            "SNE Lubecko",
            font=load_font(22, bold=True),
            fill=_ACCENT,
        )
        return pad_y + 36 + 14


def draw_quote_mark(
    draw: ImageDraw.ImageDraw, x: int, y: int, color: tuple, size: int = 72
) -> None:
    font = load_font(size, bold=True)
    draw.text((x, y), "\u201e", font=font, fill=color)


def draw_shadow_text(
    draw: ImageDraw.ImageDraw,
    pos: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple,
    shadow_offset: int = 2,
    shadow_alpha: int = 180,
    shadow_base: tuple[int, int, int] = (0, 0, 0),
) -> None:
    """Rysuje tekst z cieniem (offset px w dół i w prawo)."""
    sx, sy = pos[0] + shadow_offset, pos[1] + shadow_offset
    shadow_color = (*shadow_base, shadow_alpha) if len(fill) == 4 else shadow_base
    draw.text((sx, sy), text, font=font, fill=shadow_color)
    draw.text(pos, text, font=font, fill=fill)


# ---------------------------------------------------------------------------
# Layouty renderowania
# ---------------------------------------------------------------------------
def render_gradient(
    text: str,
    author: str,
    photos_dir: Path,
    logo_path: Path,
    output_path: Path,
    theme: ColorTheme = SNE_RED,
) -> None:
    """Panel czerwony po lewej + zdjęcie po prawej."""
    card = Image.new("RGB", (CARD_W, CARD_H), theme.base_bg)

    photo = random_photo(photos_dir)
    if photo:
        try:
            bg = Image.open(photo).convert("RGB")
            scale = max(CARD_W / bg.width, CARD_H / bg.height)
            bg = bg.resize(
                (int(bg.width * scale), int(bg.height * scale)), Image.LANCZOS
            )
            x_off = (bg.width - CARD_W) // 2
            y_off = (bg.height - CARD_H) // 2
            bg = bg.crop((x_off, y_off, x_off + CARD_W, y_off + CARD_H))

            panel = Image.new("RGB", (CARD_W, CARD_H), theme.base_bg)
            mask = gradient_mask(CARD_W, CARD_H)
            blended = Image.composite(bg, panel, mask)
            # Przyciemnij prawą stronę
            dark = Image.new("RGB", (CARD_W, CARD_H), theme.overlay_color)
            alpha_arr = Image.new(
                "L", (CARD_W, CARD_H), int(255 * theme.gradient_blend)
            )
            blended = Image.composite(dark, blended, alpha_arr)
            card.paste(blended)
        except Exception as e:
            print(f"  [ostrzeżenie] Nie można załadować zdjęcia {photo}: {e}")

    # Pionowy pasek akcentowy
    draw = ImageDraw.Draw(card)
    draw.rectangle([(0, 0), (6, CARD_H)], fill=theme.accent)

    PAD_X, PAD_Y = 54, 44

    y = draw_logo(card, logo_path, PAD_X, PAD_Y)
    draw = ImageDraw.Draw(card)

    # Cudzysłów dekoracyjny — wyżej, nie zlewa się z tekstem
    draw_quote_mark(draw, PAD_X - 4, y - 30, (*theme.accent, 120))

    # Tekst świadectwa
    wrapped = textwrap.wrap(truncate_text(text, 200), width=34)[:6]
    font_text = load_font(28, bold=False)
    line_h = 40
    y_text = y + 56
    for line in wrapped:
        draw.text((PAD_X, y_text), line, font=font_text, fill=theme.text_primary)
        y_text += line_h

    # Separator
    sep_y = min(y_text + 14, CARD_H - 110)
    draw.line([(PAD_X, sep_y), (PAD_X + 70, sep_y)], fill=theme.accent, width=3)

    # Autor
    draw.text(
        (PAD_X, CARD_H - PAD_Y - 54),
        f"— {author}",
        font=load_font(18, bold=True),
        fill=theme.text_primary,
    )
    # Motto + brand  (kursywa dla motto)
    draw.text(
        (PAD_X, CARD_H - PAD_Y - 32),
        TAGLINE_MOTTO,
        font=load_font_italic(12),
        fill=theme.tagline_color,
    )
    draw.text(
        (PAD_X, CARD_H - PAD_Y - 14),
        TAGLINE_BRAND,
        font=load_font(11),
        fill=theme.tagline_color,
    )

    # Pasek dolny
    draw.rectangle([(0, CARD_H - 5), (CARD_W, CARD_H)], fill=theme.accent)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(str(output_path), "PNG", optimize=True)
    print(
        f"  ✓ {output_path.name}  [gradient | {photo.name if photo else 'brak zdjęcia'}]"
    )


def render_gradient_right(
    text: str,
    author: str,
    photos_dir: Path,
    logo_path: Path,
    output_path: Path,
    theme: ColorTheme = SNE_RED,
) -> None:
    """Panel tekstowy po PRAWEJ + zdjęcie po lewej — lustrzane odbicie render_gradient."""
    card = Image.new("RGB", (CARD_W, CARD_H), theme.base_bg)

    photo = random_photo(photos_dir)
    if photo:
        try:
            bg = Image.open(photo).convert("RGB")
            scale = max(CARD_W / bg.width, CARD_H / bg.height)
            bg = bg.resize(
                (int(bg.width * scale), int(bg.height * scale)), Image.LANCZOS
            )
            x_off = (bg.width - CARD_W) // 2
            y_off = (bg.height - CARD_H) // 2
            bg = bg.crop((x_off, y_off, x_off + CARD_W, y_off + CARD_H))

            panel = Image.new("RGB", (CARD_W, CARD_H), theme.base_bg)
            # Gradient od prawej do lewej
            mask = gradient_mask(CARD_W, CARD_H, rtl=True)
            blended = Image.composite(bg, panel, mask)
            dark = Image.new("RGB", (CARD_W, CARD_H), theme.overlay_color)
            alpha_arr = Image.new(
                "L", (CARD_W, CARD_H), int(255 * theme.gradient_blend)
            )
            blended = Image.composite(dark, blended, alpha_arr)
            card.paste(blended)
        except Exception as e:
            print(f"  [ostrzeżenie] Nie można załadować zdjęcia {photo}: {e}")

    draw = ImageDraw.Draw(card)
    # Pionowy pasek akcentowy po PRAWEJ stronie
    draw.rectangle([(CARD_W - 6, 0), (CARD_W, CARD_H)], fill=theme.accent)

    # Tekst wyrównany do prawej krawędzi — z marginesem by nie ucinało
    PAD_Y = 44
    CONTENT_W = 440  # szerokość obszaru tekstowego
    TEXT_LEFT = (
        CARD_W // 2 - 20
    )  # lewa krawędź tekstu: środek karty z lekkim przesunięciem

    y = draw_logo(card, logo_path, TEXT_LEFT, PAD_Y)
    draw = ImageDraw.Draw(card)

    # Cudzysłów dekoracyjny — wyżej
    draw_quote_mark(draw, TEXT_LEFT - 4, y - 30, (*theme.accent, 120))

    # Tekst świadectwa
    wrapped = textwrap.wrap(truncate_text(text, 200), width=34)[:6]
    font_text = load_font(28, bold=False)
    line_h = 40
    y_text = y + 56
    for line in wrapped:
        draw.text(
            (TEXT_LEFT, y_text),
            line,
            font=font_text,
            fill=theme.text_primary,
        )
        y_text += line_h

    # Separator
    sep_y = min(y_text + 14, CARD_H - 110)
    draw.line(
        [(TEXT_LEFT, sep_y), (TEXT_LEFT + 70, sep_y)],
        fill=theme.accent,
        width=3,
    )

    # Autor
    draw.text(
        (TEXT_LEFT, CARD_H - PAD_Y - 54),
        f"— {author}",
        font=load_font(18, bold=True),
        fill=theme.text_primary,
    )
    # Motto kursywą + brand
    draw.text(
        (TEXT_LEFT, CARD_H - PAD_Y - 32),
        TAGLINE_MOTTO,
        font=load_font_italic(12),
        fill=theme.tagline_color,
    )
    draw.text(
        (TEXT_LEFT, CARD_H - PAD_Y - 14),
        TAGLINE_BRAND,
        font=load_font(11),
        fill=theme.tagline_color,
    )

    # Pasek dolny
    draw.rectangle([(0, CARD_H - 5), (CARD_W, CARD_H)], fill=theme.accent)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(str(output_path), "PNG", optimize=True)
    print(
        f"  ✓ {output_path.name}  [gradient_rtl | {photo.name if photo else 'brak zdjęcia'}]"
    )


def render_fullbg(
    text: str,
    author: str,
    photos_dir: Path,
    logo_path: Path,
    output_path: Path,
    theme: ColorTheme = SNE_RED,
) -> None:
    """Pełnoekranowe zdjęcie z ciemną nakładką, wyśrodkowany tekst."""
    card = Image.new("RGB", (CARD_W, CARD_H), theme.base_bg)

    photo = random_photo(photos_dir)
    if photo:
        try:
            bg = Image.open(photo).convert("RGB")
            scale = max(CARD_W / bg.width, CARD_H / bg.height)
            bg = bg.resize(
                (int(bg.width * scale), int(bg.height * scale)), Image.LANCZOS
            )
            x_off = (bg.width - CARD_W) // 2
            y_off = (bg.height - CARD_H) // 2
            bg = bg.crop((x_off, y_off, x_off + CARD_W, y_off + CARD_H))
            dark = Image.new("RGB", (CARD_W, CARD_H), theme.overlay_color)
            alpha_arr = Image.new("L", (CARD_W, CARD_H), int(255 * theme.fullbg_blend))
            blended = Image.composite(dark, bg, alpha_arr)
            card.paste(blended)
        except Exception as e:
            print(f"  [ostrzeżenie] {e}")

    # Gradient pionowy — zmniejszona intensywność (max_alpha=160 zamiast 230)
    overlay = vertical_gradient_overlay(
        CARD_W, CARD_H, theme.overlay_color, max_alpha=160
    )
    card_rgba = card.convert("RGBA")
    card_rgba.alpha_composite(overlay)
    card = card_rgba.convert("RGB")

    draw = ImageDraw.Draw(card)
    PAD_X, PAD_Y = 60, 44

    y_logo = draw_logo(card, logo_path, PAD_X, PAD_Y)
    draw = ImageDraw.Draw(card)

    # Wyśrodkowany cudzysłów
    draw_quote_mark(draw, CARD_W // 2 - 30, 130, (*theme.accent, 140))

    # Wyśrodkowany tekst z cieniem dla kontrastu
    wrapped = textwrap.wrap(truncate_text(text, 160), width=44)[:4]
    font_text = load_font(30, bold=False)
    total_h = len(wrapped) * 46
    y_start = (CARD_H - total_h) // 2
    for line in wrapped:
        bbox = draw.textbbox((0, 0), line, font=font_text)
        lw = bbox[2] - bbox[0]
        draw_shadow_text(
            draw,
            ((CARD_W - lw) // 2, y_start),
            line,
            font_text,
            theme.text_primary,
            shadow_offset=3,
            shadow_alpha=200,
            shadow_base=theme.shadow_color,
        )
        y_start += 46

    # Autor wyśrodkowany (z cieniem)
    font_author = load_font(18, bold=True)
    autor_str = f"— {author}"
    bbox = draw.textbbox((0, 0), autor_str, font=font_author)
    aw = bbox[2] - bbox[0]
    draw_shadow_text(
        draw,
        ((CARD_W - aw) // 2, CARD_H - PAD_Y - 52),
        autor_str,
        font_author,
        theme.text_primary,
        shadow_offset=2,
        shadow_base=theme.shadow_color,
    )

    # Motto kursywą + brand wyśrodkowane
    font_tag = load_font_italic(12)
    bbox = draw.textbbox((0, 0), TAGLINE_MOTTO, font=font_tag)
    tw = bbox[2] - bbox[0]
    draw.text(
        ((CARD_W - tw) // 2, CARD_H - PAD_Y - 30),
        TAGLINE_MOTTO,
        font=font_tag,
        fill=theme.tagline_color,
    )
    font_brand = load_font(11)
    bbox = draw.textbbox((0, 0), TAGLINE_BRAND, font=font_brand)
    bw = bbox[2] - bbox[0]
    draw.text(
        ((CARD_W - bw) // 2, CARD_H - PAD_Y - 12),
        TAGLINE_BRAND,
        font=font_brand,
        fill=theme.tagline_color,
    )

    draw.rectangle([(0, CARD_H - 5), (CARD_W, CARD_H)], fill=theme.accent)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(str(output_path), "PNG", optimize=True)
    print(
        f"  ✓ {output_path.name}  [fullbg | {photo.name if photo else 'brak zdjęcia'}]"
    )


def render_minimal(
    text: str,
    author: str,
    photos_dir: Path,
    logo_path: Path,
    output_path: Path,
    theme: ColorTheme = SNE_RED,
) -> None:
    """Czyste tło, gruby pionowy pasek akcentowy, duża typografia.
    Zdjęcie prześwituje przez dekoracyjne okręgi w tle."""
    card = Image.new("RGB", (CARD_W, CARD_H), theme.panel_bg)
    draw = ImageDraw.Draw(card)
    PAD_X, PAD_Y = 80, 44

    # Trzy ramy akcentowe (bez okręgów — zastąpione obrazem)
    draw.rectangle([(0, 0), (CARD_W, 5)], fill=theme.accent)
    draw.rectangle([(0, CARD_H - 5), (CARD_W, CARD_H)], fill=theme.accent)
    draw.rectangle([(0, 0), (8, CARD_H)], fill=theme.accent)

    # Okręgi dekoracyjne — zdjęcie prześwituje przez nie
    circles = [(900, 100, 200), (1050, 500, 140), (200, 500, 100)]
    photo = random_photo(photos_dir)
    if photo:
        try:
            bg = Image.open(photo).convert("RGB")
            scale = max(CARD_W / bg.width, CARD_H / bg.height)
            bg = bg.resize(
                (int(bg.width * scale), int(bg.height * scale)), Image.LANCZOS
            )
            x_off = (bg.width - CARD_W) // 2
            y_off = (bg.height - CARD_H) // 2
            bg = bg.crop((x_off, y_off, x_off + CARD_W, y_off + CARD_H))

            # Pełne tło z 20% opacity
            full_alpha = Image.new("L", (CARD_W, CARD_H), int(255 * 0.20))
            card.paste(bg, (0, 0), full_alpha)

            # W kółkach — 95% opacity (prawie pełna widoczność)
            for cx, cy, r in circles:
                circle_mask = Image.new("L", (CARD_W, CARD_H), 0)
                cm_draw = ImageDraw.Draw(circle_mask)
                cm_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=int(255 * 0.95))
                card.paste(bg, (0, 0), circle_mask)
        except Exception as e:
            print(f"  [ostrzeżenie] Nie można załadować zdjęcia {photo}: {e}")
    else:
        for cx, cy, r in circles:
            bbox = [cx - r, cy - r, cx + r, cy + r]
            draw.ellipse(
                bbox,
                fill=(*theme.overlay_color, 0),
                outline=(*theme.accent, 40),
                width=1,
            )

    # Obramowanie okręgów akcentem
    draw = ImageDraw.Draw(card)
    for cx, cy, r in circles:
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r], outline=(*theme.accent, 80), width=2
        )

    y = draw_logo(card, logo_path, PAD_X, PAD_Y)
    draw = ImageDraw.Draw(card)

    # Cudzysłów dekoracyjny — wyżej, nie zlewa się z tekstem
    draw_quote_mark(draw, PAD_X - 6, y - 10, (*theme.accent,), size=80)
    y += 80

    wrapped = textwrap.wrap(truncate_text(text, 220), width=42)[:5]
    font_text = load_font(30, bold=False)
    line_h = 44
    for line in wrapped:
        draw.text((PAD_X, y), line, font=font_text, fill=theme.text_primary)
        y += line_h

    sep_y = min(y + 18, CARD_H - 100)
    draw.line([(PAD_X, sep_y), (PAD_X + 80, sep_y)], fill=theme.accent, width=4)

    draw.text(
        (PAD_X, CARD_H - PAD_Y - 54),
        f"— {author}",
        font=load_font(18, bold=True),
        fill=theme.text_primary,
    )
    draw.text(
        (PAD_X, CARD_H - PAD_Y - 32),
        TAGLINE_MOTTO,
        font=load_font_italic(12),
        fill=theme.tagline_color,
    )
    draw.text(
        (PAD_X, CARD_H - PAD_Y - 14),
        TAGLINE_BRAND,
        font=load_font(11),
        fill=theme.tagline_color,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(str(output_path), "PNG", optimize=True)
    print(
        f"  ✓ {output_path.name}  [minimal | {photo.name if photo else 'brak zdjęcia'}]"
    )


def render_stat(
    text: str,
    author: str,
    photos_dir: Path,
    logo_path: Path,
    output_path: Path,
    theme: ColorTheme = SNE_RED,
) -> None:
    """Prostokątna ramka, wewnątrz zdjęcie, na zdjęciu wyśrodkowany tekst z cieniem."""
    card = Image.new("RGB", (CARD_W, CARD_H), theme.base_bg)
    draw = ImageDraw.Draw(card)
    PAD_X, PAD_Y = 60, 44

    # Ramy akcentowe na krawędziach całej karty
    draw.rectangle([(0, 0), (CARD_W, 5)], fill=theme.accent)
    draw.rectangle([(0, CARD_H - 5), (CARD_W, CARD_H)], fill=theme.accent)
    draw.rectangle([(0, 0), (8, CARD_H)], fill=theme.accent)
    draw.rectangle([(CARD_W - 8, 0), (CARD_W, CARD_H)], fill=theme.accent)

    # Wymiary wewnętrznego prostokąta z ramką
    FRAME_BORDER = 6
    FRAME_L, FRAME_T = PAD_X - 20, 70
    FRAME_R, FRAME_B = CARD_W - PAD_X + 20, CARD_H - 70
    INNER_L = FRAME_L + FRAME_BORDER
    INNER_T = FRAME_T + FRAME_BORDER
    INNER_R = FRAME_R - FRAME_BORDER
    INNER_B = FRAME_B - FRAME_BORDER
    INNER_W = INNER_R - INNER_L
    INNER_H = INNER_B - INNER_T

    # Zdjęcie wewnątrz ramki
    photo = random_photo(photos_dir)
    if photo:
        try:
            bg = Image.open(photo).convert("RGB")
            scale = max(INNER_W / bg.width, INNER_H / bg.height)
            bg = bg.resize(
                (int(bg.width * scale), int(bg.height * scale)), Image.LANCZOS
            )
            x_off = (bg.width - INNER_W) // 2
            y_off = (bg.height - INNER_H) // 2
            bg = bg.crop((x_off, y_off, x_off + INNER_W, y_off + INNER_H))
            # Lekkie przyciemnienie zdjęcia dla czytelności tekstu
            dark = Image.new("RGB", (INNER_W, INNER_H), theme.overlay_color)
            alpha_arr = Image.new("L", (INNER_W, INNER_H), int(255 * 0.45))
            bg = Image.composite(dark, bg, alpha_arr)
            card.paste(bg, (INNER_L, INNER_T))
        except Exception as e:
            print(f"  [ostrzeżenie] {e}")
            card.paste(
                Image.new("RGB", (INNER_W, INNER_H), theme.panel_bg), (INNER_L, INNER_T)
            )
    else:
        card.paste(
            Image.new("RGB", (INNER_W, INNER_H), theme.panel_bg), (INNER_L, INNER_T)
        )

    # Ramka akcentowa dokoła zdjęcia
    draw = ImageDraw.Draw(card)
    draw.rectangle(
        [FRAME_L, FRAME_T, FRAME_R, FRAME_B], outline=theme.accent, width=FRAME_BORDER
    )

    y = draw_logo(card, logo_path, PAD_X, PAD_Y)
    draw = ImageDraw.Draw(card)

    # Wyśrodkowany cudzysłów na zdjęciu
    draw_quote_mark(draw, CARD_W // 2 - 25, INNER_T + 10, (*theme.accent,), size=64)

    # Wyśrodkowany tekst z cieniem na zdjęciu
    short = truncate_text(text, 160)
    wrapped = textwrap.wrap(short, width=46)[:4]
    font_text = load_font(28, bold=False)
    total_h = len(wrapped) * 42
    y_text = INNER_T + (INNER_H - total_h) // 2 + 20
    for line in wrapped:
        bbox = draw.textbbox((0, 0), line, font=font_text)
        lw = bbox[2] - bbox[0]
        draw_shadow_text(
            draw,
            ((CARD_W - lw) // 2, y_text),
            line,
            font_text,
            theme.text_primary,
            shadow_offset=3,
            shadow_alpha=210,
            shadow_base=theme.shadow_color,
        )
        y_text += 42

    # Autor z cieniem
    font_author = load_font(18, bold=True)
    autor_str = f"— {author}"
    bbox = draw.textbbox((0, 0), autor_str, font=font_author)
    aw = bbox[2] - bbox[0]
    draw_shadow_text(
        draw,
        ((CARD_W - aw) // 2, CARD_H - PAD_Y - 52),
        autor_str,
        font_author,
        theme.text_primary,
        shadow_offset=2,
        shadow_base=theme.shadow_color,
    )
    font_tag = load_font_italic(12)
    bbox = draw.textbbox((0, 0), TAGLINE_MOTTO, font=font_tag)
    tw = bbox[2] - bbox[0]
    draw.text(
        ((CARD_W - tw) // 2, CARD_H - PAD_Y - 30),
        TAGLINE_MOTTO,
        font=font_tag,
        fill=theme.tagline_color,
    )
    font_brand = load_font(11)
    bbox = draw.textbbox((0, 0), TAGLINE_BRAND, font=font_brand)
    bw = bbox[2] - bbox[0]
    draw.text(
        ((CARD_W - bw) // 2, CARD_H - PAD_Y - 12),
        TAGLINE_BRAND,
        font=font_brand,
        fill=theme.tagline_color,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(str(output_path), "PNG", optimize=True)
    print(f"  ✓ {output_path.name}  [stat | {photo.name if photo else 'brak zdjęcia'}]")


RENDERERS = {
    LAYOUT_GRADIENT: render_gradient,
    LAYOUT_GRADIENT_RTL: render_gradient_right,
    LAYOUT_FULLBG: render_fullbg,
    LAYOUT_MINIMAL: render_minimal,
    LAYOUT_STAT: render_stat,
}


def render_card(
    text: str,
    author: str,
    photos_dir: Path,
    logo_path: Path,
    output_path: Path,
    layout: str | None = None,
    theme_name: str = "red",
) -> None:
    layout = layout or random.choice(ALL_LAYOUTS)
    theme = THEMES.get(theme_name, SNE_RED)
    RENDERERS[layout](text, author, photos_dir, logo_path, output_path, theme)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Generuj karty ze świadectwami SNE")
    parser.add_argument(
        "--testimonials", "-t", type=Path, help="Plik .md ze świadectwami"
    )
    parser.add_argument(
        "--photos", "-p", type=Path, required=True, help="Katalog ze zdjęciami tła"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("output/testimonial_cards"),
        help="Katalog wyjściowy",
    )
    parser.add_argument(
        "--logo",
        type=Path,
        default=Path("images/logotyp/sne_kwadrat.png"),
        help="Ścieżka do logotypu SNE",
    )
    parser.add_argument(
        "--count",
        "-n",
        type=int,
        default=1,
        help="Liczba kart do wygenerowania (tryb losowy)",
    )
    parser.add_argument(
        "--layout",
        choices=ALL_LAYOUTS,
        default=None,
        help="Wymuszony layout (domyślnie: losowy)",
    )
    parser.add_argument(
        "--theme",
        choices=list(THEMES.keys()),
        default="red",
        help="Motyw kolorystyczny: red / dark / light",
    )
    parser.add_argument("--author", default=None, help="Autor świadectwa (tryb ręczny)")
    parser.add_argument("--text", default=None, help="Tekst świadectwa (tryb ręczny)")
    parser.add_argument(
        "--seed", type=int, default=None, help="Seed losowania dla powtarzalności"
    )
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    if not args.photos.is_dir():
        print(f"BŁĄD: Katalog ze zdjęciami nie istnieje: {args.photos}")
        raise SystemExit(1)

    logo_path = args.logo
    if not logo_path.exists():
        print(
            f"  [ostrzeżenie] Logo nie znaleziono pod {logo_path} — zostanie użyty tekst zastępczy."
        )

    # Tryb ręczny: --author + --text
    if args.author and args.text:
        out = args.output / "custom_card.png"
        render_card(
            args.text, args.author, args.photos, logo_path, out, args.layout, args.theme
        )
        return

    # Tryb losowy z pliku świadectw
    if not args.testimonials:
        parser.error("Podaj --testimonials lub oba: --author i --text")

    testimonials = parse_testimonials(args.testimonials)
    if not testimonials:
        print("BŁĄD: Nie znaleziono świadectw w podanym pliku.")
        raise SystemExit(1)

    print(f"Znaleziono {len(testimonials)} świadectw. Generuję {args.count} kart…")

    sample = random.choices(testimonials, k=args.count)
    layouts = [args.layout or random.choice(ALL_LAYOUTS) for _ in range(args.count)]

    for i, (entry, layout) in enumerate(zip(sample, layouts), start=1):
        slug = re.sub(r"[^\w]", "_", entry["author"].lower())[:20]
        out_path = args.output / f"{i:02d}_{slug}.png"
        render_card(
            entry["text"],
            entry["author"],
            args.photos,
            logo_path,
            out_path,
            layout,
            args.theme,
        )

    print(f"\nGotowe! Wygenerowano {args.count} kart w: {args.output}")


if __name__ == "__main__":
    main()
