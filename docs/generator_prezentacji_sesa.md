# Generator prezentacji SESA

Generator zamienia jedną deklarację YAML oraz gotowe obrazy na dwa pliki:

- Markdown zgodny z Obsidianem;
- prezentację PowerPoint z edytowalnymi tytułami, podtytułami i slajdem końcowym.

## Użycie

```bash
scripts/generate_sesa_presentation.sh sciezka/do/prezentacja.yaml
```

Opcjonalnie można wskazać katalog podglądów:

```bash
scripts/generate_sesa_presentation.sh sciezka/do/prezentacja.yaml \
  --preview-dir /tmp/podglad-prezentacji
```

Po poprawnym wykonaniu skrypt wypisuje JSON ze ścieżkami do YAML-a, Markdownu, PPTX-a i podglądów oraz liczbą slajdów.

## Schemat YAML

Pełny przykład znajduje się w `scripts/sesa_presentation.example.yaml`.

```yaml
version: 1
title: "Tytuł prezentacji"
source: "nazwa_pliku_zrodlowego"
date: "2026-11-09"
status: "propozycja"

output:
  markdown: "nazwa_pliku_zrodlowego_prezentacja.md"
  pptx: "nazwa_pliku_zrodlowego_prezentacja.pptx"

slides:
  - type: illustration
    title: "Tytuł slajdu"
    subtitle: "Jedno zdanie streszczające punkt."
    image: "01_ilustracja.jpg"

  - type: key_sentence
    title: "Zdanie kluczowe"
    text: "Dokładne zdanie podsumowujące ze źródła."
```

Ścieżki w `output` i `image` są rozwiązywane względem katalogu YAML-a. Generator wymaga dokładnie jednego slajdu `key_sentence`, zawsze na końcu.

## Odpowiedzialność generatora

Generator:

- sprawdza strukturę YAML-a;
- tworzy Markdown i PPTX z tej samej deklaracji;
- osadza obrazy w prezentacji;
- buduje natywny slajd końcowy z żółtym pasem;
- renderuje PNG każdego slajdu i montaż całej prezentacji;
- uruchamia walidację struktury PPTX;
- usuwa własny katalog roboczy po zakończeniu.

Dobór punktów nauczania oraz generowanie i ocena ilustracji nadal należą do procesu opisanego w `.github/prompts/prezentacja-sesa.prompt.md`.
