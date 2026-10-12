# Strona Regionalnego Centrum Alpha w Lubecku

Responsywna, statyczna strona przygotowana na podstawie bazy wiedzy w `issue_rca_lubecko`, materiałów fotograficznych i identyfikacji wizualnej Alpha.

## Podstrony

- `index.html` — strona główna;
- `czym-jest-alpha.html` — format, odbiorcy i najczęstsze pytania;
- `zacznij-alpha.html` — zakres wsparcia RCA;
- `historia.html` — historia Alpha w Lubecku i galeria;
- `odnowa-parafii.html` — interaktywny cykl odnowy parafii;
- `o-nas.html` — zespół RCA Lubecko;
- `kontakt.html` — kontakt i formularz przygotowujący wiadomość e-mail.

## Uruchomienie lokalne

Strona nie wymaga kompilacji ani instalowania zależności. Można otworzyć `index.html` bezpośrednio albo uruchomić prosty serwer HTTP w tym katalogu:

```bash
python3 -m http.server 4173
```

Następnie strona będzie dostępna pod adresem `http://127.0.0.1:4173/`.

## Ważne przed publikacją

- potwierdzić zgody na publikację wszystkich zdjęć i wizerunków;
- potwierdzić opisy ról członków zespołu;
- zdecydować, czy formularz ma pozostać odnośnikiem do programu pocztowego, czy zostać połączony z usługą obsługującą wysyłkę;
- podpiąć docelową domenę i uzupełnić adresy Open Graph oraz mapę witryny;
- ustalić, czy i gdzie publikować informacje o aktualnej edycji Alpha.

## Technologia

Strona korzysta z HTML, CSS i niewielkiej ilości JavaScriptu. Nie używa frameworka ani zewnętrznego systemu zarządzania treścią. Fonty Instrument Serif i Plus Jakarta Sans są pobierane z Google Fonts, a w razie braku połączenia używane są fonty zastępcze.

