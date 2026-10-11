from pathlib import Path

from PIL import Image
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "infografiki" / "pelna_render"
OUTPUT_DIR = ROOT / "output" / "pdf"
TEMP_DIR = ROOT / "tmp" / "pdfs" / "kamch_infografiki_jpg"
OUTPUT_FILE = OUTPUT_DIR / "KAMCh_infografiki_pelna_mniejsza.pdf"


def main() -> None:
    slides = sorted(SOURCE_DIR.glob("slajd-*.png"))
    if len(slides) != 10:
        raise RuntimeError(f"Oczekiwano 10 slajdów, znaleziono {len(slides)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    page_width = 960
    page_height = 540
    pdf = canvas.Canvas(
        str(OUTPUT_FILE),
        pagesize=(page_width, page_height),
        pageCompression=1,
    )
    pdf.setTitle("KAMCh — infografiki kursu")
    pdf.setAuthor("SNE Lubecko")
    pdf.setSubject("Kurs Animacji Modlitwy Charyzmatycznej")

    for index, slide in enumerate(slides, start=1):
        jpg_path = TEMP_DIR / f"slajd-{index:02d}.jpg"
        with Image.open(slide) as image:
            image.convert("RGB").save(
                jpg_path,
                "JPEG",
                quality=85,
                optimize=True,
                progressive=True,
                subsampling=2,
            )
        pdf.drawImage(
            str(jpg_path),
            0,
            0,
            width=page_width,
            height=page_height,
            preserveAspectRatio=True,
            mask="auto",
        )
        pdf.showPage()

    pdf.save()
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
