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
header_h = 39
row_h = 66

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
        cell_fill = HexColor("#FFF4E8") if name == "POMARAŃCZOWA" and idx == 1 else WHITE
        rounded_rect(c, x, y, day_w, row_h, cell_fill, 7)
        size = 11.3 if len(duty) > 35 else 12.5
        centered_lines(c, duty, x, y, day_w, row_h, size=size, leading=15)
    y -= row_h + gap

notes_y = 25
notes_h = y - notes_y - 5
rounded_rect(c, margin_x, notes_y, PAGE_W - 2 * margin_x, notes_h, HexColor("#E9EEF1"), 8)
c.setFillColor(NAVY)
c.circle(margin_x + 20, notes_y + notes_h - 22, 9, fill=1, stroke=0)
c.setFont("DejaVu-Bold", 12)
c.setFillColor(WHITE)
c.drawCentredString(margin_x + 20, notes_y + notes_h - 26, "i")

note_lines = [
    "PIĄTEK: po kolacji wspólnie sprzątają grupy czerwona, żółta i niebieska.",
    "SOBOTA: grupa zielona odpowiada za podsumowanie oraz przerwy kawowe.",
    "NIEDZIELA: żółta przygotowuje przerwy kawowe; niebieska sprząta po posiłkach i kawie; zielona pomaga po przerwie kawowej.",
]
c.setFillColor(TEXT)
for idx, line in enumerate(note_lines):
    c.setFont("DejaVu-Bold" if idx == 0 else "DejaVu", 10.5)
    c.drawString(margin_x + 39, notes_y + notes_h - 27 - idx * 21, line)

c.showPage()
c.save()
print(OUTPUT)
