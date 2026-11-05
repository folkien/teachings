from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path("/home/spasz/python/teachings")
OUTPUT = ROOT / "output/pdf/KAMCh_2026_plan_poslug_A4_poziomo.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
pdfmetrics.registerFont(TTFont("DejaVu", FONT))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_BOLD))

PAGE_W, PAGE_H = landscape(A4)
BG = HexColor("#F7F4ED")
NAVY = HexColor("#17324D")
TEXT = HexColor("#253442")
MUTED = HexColor("#5D6874")
WHITE = HexColor("#FFFFFF")

groups = [
    ("CZERWONA", HexColor("#B94A48"), WHITE, [
        "Wspólne sprzątanie\npo kolacji",
        "Sprzątanie\npo posiłkach",
        "Liturgia\n+ modlitwa za kurs",
    ]),
    ("ŻÓŁTA", HexColor("#E4B93F"), HexColor("#3F3211"), [
        "Wspólne sprzątanie\npo kolacji",
        "Liturgia\n+ modlitwa za kurs",
        "Przygotowanie\nprzerw kawowych",
    ]),
    ("NIEBIESKA", HexColor("#347AA5"), WHITE, [
        "Wspólne sprzątanie\npo kolacji",
        "Animacje",
        "Sprzątanie po posiłkach\ni kawie",
    ]),
    ("POMARAŃCZOWA", HexColor("#D7792D"), HexColor("#2E2419"), [
        "Modlitwa za kurs",
        "Przygotowanie stołów\ni posiłków",
        "Podsumowanie",
    ]),
    ("ZIELONA", HexColor("#2F7657"), WHITE, [
        "Przygotowanie podsumowania\nna sobotę",
        "Podsumowanie\ni przerwy kawowe",
        "Animacje + pomoc\nw sprzątaniu\npo przerwie kawowej",
    ]),
]


def rounded_rect(c, x, y, w, h, fill, radius=6):
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=0)


def centered_lines(c, text, x, y, w, h, size=13, leading=17, color=TEXT, bold=True):
    lines = text.split("\n")
    c.setFillColor(color)
    c.setFont("DejaVu-Bold" if bold else "DejaVu", size)
    baseline = y + h / 2 + (len(lines) - 1) * leading / 2 - size * 0.35
    for index, line in enumerate(lines):
        c.drawCentredString(x + w / 2, baseline - index * leading, line)


def wrap_text(text, font, size, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def legend_card(c, x, y, w, h, title, body):
    rounded_rect(c, x, y, w, h, WHITE, 6)
    c.setFillColor(NAVY)
    c.setFont("DejaVu-Bold", 8.8)
    c.drawString(x + 11, y + h - 17, title.upper())
    lines = wrap_text(body, "DejaVu", 7.4, w - 22)
    c.setFillColor(TEXT)
    c.setFont("DejaVu", 7.4)
    start_y = y + h - 31
    for idx, line in enumerate(lines[:7]):
        c.drawString(x + 11, start_y - idx * 9.6, line)


c = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H))
c.setTitle("KAMCh 2026 - plan posług grup")
c.setAuthor("SNE Lubecko")
c.setFillColor(BG)
c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

margin_x = 22
top = PAGE_H - 20
gap = 5
group_w = 128
day_w = (PAGE_W - 2 * margin_x - group_w - 3 * gap) / 3
header_h = 35
row_h = 58

rounded_rect(c, margin_x, top - header_h, PAGE_W - 2 * margin_x, header_h, NAVY, 7)
headers = [
    (margin_x, group_w, "GRUPA"),
    (margin_x + group_w + gap, day_w, "PIĄTEK"),
    (margin_x + group_w + 2 * gap + day_w, day_w, "SOBOTA"),
    (margin_x + group_w + 3 * gap + 2 * day_w, day_w, "NIEDZIELA"),
]
for x, width, label in headers:
    centered_lines(c, label, x, top - header_h, width, header_h, size=15, leading=17, color=WHITE)

y = top - header_h - gap - row_h
for name, color, name_color, duties in groups:
    rounded_rect(c, margin_x, y, group_w, row_h, color, 7)
    group_size = 12 if name == "POMARAŃCZOWA" else 14
    centered_lines(c, name, margin_x, y, group_w, row_h, size=group_size, leading=15, color=name_color)
    for idx, duty in enumerate(duties):
        x = margin_x + group_w + gap + idx * (day_w + gap)
        rounded_rect(c, x, y, day_w, row_h, WHITE, 7)
        size = 11.3 if len(duty) > 35 else 12.5
        centered_lines(c, duty, x, y, day_w, row_h, size=size, leading=15)
    y -= row_h + gap

c.setFillColor(NAVY)
c.setFont("DejaVu-Bold", 11)
c.drawString(margin_x, y - 8, "CO OZNACZAJĄ POSŁUGI?")

legend = [
    (
        "Animacje",
        "Przygotowanie jednej lub dwóch zabaw, które poruszą ciało i umysł oraz pomogą uczestnikom się obudzić. Trzeba uwzględnić warunki sali. Najlepiej ok. 10 minut, maksymalnie 15 minut.",
    ),
    (
        "Liturgia i modlitwa za kurs",
        "Przygotowanie liturgii Eucharystii i posługa podczas niej. Ponadto grupa znajduje przynajmniej jeden czas wolny na wspólną modlitwę za kurs.",
    ),
    (
        "Przygotowanie stołów i posiłków",
        "Nałożenie zastawy, przygotowanie stołów pod posiłek oraz pomoc przy rozłożeniu i wydawaniu posiłku.",
    ),
    (
        "Podsumowanie",
        "Przygotowanie 15-minutowego podsumowania poprzedniego dnia i omówionych tematów. Forma może być różna, np. reportaż, pantomima, teatr lub prezentacja.",
    ),
    (
        "Przerwy kawowe",
        "Przygotowanie kawy i przekąsek w sposób estetyczny i kreatywny, tak aby uczestnikom było miło. Należy też dbać o uzupełnianie stołu.",
    ),
    (
        "Sprzątanie po posiłkach i kawie",
        "Zebranie talerzy i kubków, ich umycie oraz przetarcie i uporządkowanie stołów po posiłku lub przerwie kawowej.",
    ),
]

legend_gap = 7
legend_w = (PAGE_W - 2 * margin_x - 2 * legend_gap) / 3
legend_h = 86
legend_bottom = 20
for idx, (title, body) in enumerate(legend):
    col = idx % 3
    row = 1 - idx // 3
    lx = margin_x + col * (legend_w + legend_gap)
    ly = legend_bottom + row * (legend_h + legend_gap)
    legend_card(c, lx, ly, legend_w, legend_h, title, body)

c.showPage()
c.save()
print(OUTPUT)
