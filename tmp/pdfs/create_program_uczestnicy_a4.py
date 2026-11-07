from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path("/home/spasz/python/teachings")
OUTPUT = ROOT / "output/pdf/KAMCh_2026_program_dla_uczestnikow_A4.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

PAGE_W, PAGE_H = landscape(A4)
WHITE = HexColor("#FFFFFF")
NAVY = HexColor("#17324D")
TEXT = HexColor("#253442")
MUTED = HexColor("#65717D")
ECRU = HexColor("#F4F0E7")
EUCHARIST = HexColor("#FFF1C9")
MEAL = HexColor("#FCE8D4")
ENDING = HexColor("#E7EFF5")

days = [
    (
        "PIĄTEK",
        "6 LISTOPADA",
        HexColor("#B94A48"),
        [
            ("17.00", "Recepcja"),
            ("17.30", "Powitanie"),
            ("17.45", "Lodołamacz"),
            ("18.00", "Blok programowy"),
            ("18.50", "Oczekiwania i kolacja"),
            ("19.20", "Sprzątanie po kolacji"),
            ("19.35", "Konferencja i blok programowy"),
            ("21.00", "Zakończenie"),
        ],
    ),
    (
        "SOBOTA",
        "7 LISTOPADA",
        HexColor("#D5A92E"),
        [
            ("08.30", "Modlitwa osobista"),
            ("09.00", "Praca w grupach i kawa"),
            ("09.30", "Animacja"),
            ("09.45", "Podsumowanie"),
            ("10.00", "Modlitwa wspólnotowa"),
            ("10.30", "Konferencja"),
            ("11.15", "Przerwa na kawę i blok programowy"),
            ("12.20", "Przerwa"),
            ("12.30", "Eucharystia"),
            ("13.30", "Obiad"),
            ("14.30", "Konferencja i blok programowy"),
            ("15.30", "Przerwa"),
            ("15.45", "Konferencja"),
            ("16.45", "Przerwa na kawę"),
            ("17.00", "Blok modlitewny"),
            ("18.30", "Kolacja"),
            ("19.00", "Konferencja"),
            ("20.30", "Zakończenie"),
        ],
    ),
    (
        "NIEDZIELA",
        "8 LISTOPADA",
        HexColor("#2F7657"),
        [
            ("08.00", "Modlitwa osobista"),
            ("08.30", "Praca w grupach i kawa"),
            ("09.00", "Animacja"),
            ("09.15", "Podsumowanie"),
            ("09.30", "Blok programowy"),
            ("10.30", "Msza Święta"),
            ("11.30", "Przerwa na kawę"),
            ("12.00", "Konferencja i blok programowy"),
            ("13.00", "Świadectwa"),
            ("13.20", "Wizja SNE"),
            ("14.00", "Zakończenie"),
        ],
    ),
]


def wrap_text(text, font_name, font_size, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def row_color(label):
    lowered = label.lower()
    if "eucharystia" in lowered or "msza" in lowered:
        return EUCHARIST
    if "kolacja" in lowered or "obiad" in lowered:
        return MEAL
    if label == "Zakończenie":
        return ENDING
    return ECRU


c = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H))
c.setTitle("KAMCh 2026 - program dla uczestników")
c.setAuthor("SNE Lubecko")
c.setFillColor(WHITE)
c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

c.setFillColor(NAVY)
c.setFont("DejaVu-Bold", 21)
c.drawString(22, PAGE_H - 34, "PROGRAM KURSU KAMCh")
c.setFillColor(MUTED)
c.setFont("DejaVu", 10.5)
c.drawRightString(PAGE_W - 22, PAGE_H - 32, "6-8 listopada 2026  •  Lubecko")

margin_x = 22
column_gap = 9
column_w = (PAGE_W - 2 * margin_x - 2 * column_gap) / 3
column_top = PAGE_H - 55
header_h = 42
content_bottom = 20

for day_index, (day_name, date_label, accent, entries) in enumerate(days):
    x = margin_x + day_index * (column_w + column_gap)
    c.setFillColor(accent)
    c.roundRect(x, column_top - header_h, column_w, header_h, 8, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("DejaVu-Bold", 15)
    c.drawString(x + 12, column_top - 18, day_name)
    c.setFont("DejaVu-Bold", 8.2)
    c.drawRightString(x + column_w - 12, column_top - 17, date_label)

    rows_top = column_top - header_h - 5
    available_h = rows_top - content_bottom
    row_gap = 2
    row_h = min(34, (available_h - row_gap * (len(entries) - 1)) / len(entries))
    time_size = 8.6 if len(entries) > 15 else 10.2
    item_size = 8.4 if len(entries) > 15 else 10.1
    leading = 10 if len(entries) > 15 else 12.2
    time_w = 42

    y = rows_top - row_h
    for time_value, label in entries:
        c.setFillColor(row_color(label))
        c.roundRect(x, y, column_w, row_h, 5, fill=1, stroke=0)

        c.setFillColor(NAVY)
        c.setFont("DejaVu-Bold", time_size)
        c.drawString(x + 9, y + row_h / 2 - time_size * 0.34, time_value)

        text_x = x + time_w + 9
        text_w = column_w - time_w - 18
        lines = wrap_text(label, "DejaVu-Bold", item_size, text_w)
        c.setFillColor(TEXT)
        c.setFont("DejaVu-Bold", item_size)
        baseline = y + row_h / 2 + (len(lines) - 1) * leading / 2 - item_size * 0.34
        for line_index, line in enumerate(lines[:2]):
            c.drawString(text_x, baseline - line_index * leading, line)

        y -= row_h + row_gap

c.showPage()
c.save()
print(OUTPUT)
