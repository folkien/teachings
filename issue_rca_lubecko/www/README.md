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
- metadane kanoniczne i Open Graph wskazują `https://alpha.lubecko.pl/`; jeśli nowa strona trafi pod inny adres, trzeba zaktualizować je przed publikacją;
- ustalić, czy i gdzie publikować informacje o aktualnej edycji Alpha.
- potwierdzić zakres zgód na ponowne wykorzystanie świadectw wraz z imieniem i wiekiem; ich źródłem są publiczne posty SNE Lubecko, ale nowa strona jest osobnym miejscem publikacji.
- po 22 października zaktualizować albo usunąć ze strony głównej zaproszenie na pierwsze spotkania 11. edycji.

## Archiwum wydarzeń i świadectw

Podstrona `historia.html` korzysta z uporządkowanych danych z [[../facebook_alpha_archiwum]]. Pełna baza obejmuje chronologię działań, godziny spotkań, dane liczbowe i 117 świadectw. Na stronie wykorzystano tylko krótki wybór, aby zachować czytelność; dawne numery telefonów i niepotwierdzone daty nie zostały opublikowane.

## Redakcja zdjęć

Wybrane fotografie zostały skopiowane z roboczego katalogu `/home/spasz/Obrazy/alpha/`, zmniejszone i zapisane jako WebP w `assets/photos/`. Oryginały nie zostały zmienione.

- strona główna pokazuje przede wszystkim własne edycje Alpha w Lubecku;
- pozostałe podstrony wykorzystują różne zdjęcia, bez przypadkowego powtarzania tych samych kadrów;
- galeria na stronie historii pokazuje Lubecko oraz miejsca, którym RCA towarzyszyło: Koszęcin, Olszynę, Zawadzkie, Legnicę, Gliwice i Jelenią Górę;
- nazwy plików w `assets/photos/` opisują miejsce albo funkcję zdjęcia, aby później można było łatwo rozbudować galerię lub przygotować mapę działań RCA.

## Technologia

Strona korzysta z HTML, CSS i niewielkiej ilości JavaScriptu. Nie używa frameworka ani zewnętrznego systemu zarządzania treścią. Fonty Instrument Serif i Plus Jakarta Sans są pobierane z Google Fonts, a w razie braku połączenia używane są fonty zastępcze.
