---
agent: agent
description: "Wzbogacenie szkicu nauczania - zaciągnięcie pasujących elementów z bazy wiedzy"
---

# Cel: Wzbogacenie aktualnego nauczania o materiał z bazy wiedzy

Wykonaj poniższe kroki dla wskazanego pliku nauczania z katalogu `konferencje_todo/`:

## Krok 1 – Analiza nauczania

Przeczytaj dokładnie cały plik nauczania. Zidentyfikuj:

- **Temat główny i słowa kluczowe** – czego dotyczy nauczanie?
- **Luki i słabe miejsca** – gdzie brakuje ilustracji, świadectwa, mocnej myśli, cytatu?
- **Ton i styl** – w jakim języku i rytmie jest napisane?
- **Struktura** – punkt wyjścia z życia, Słowo Boże, świadectwo, wezwanie?

## Krok 2 – Przeszukanie bazy wiedzy

Na podstawie tematu i luk przeszukaj następujące pliki w `wiedza/`:

| Plik | Szukaj |
|---|---|
| `wiedza/swiadectwa.md` | Świadectwa tematycznie powiązane z treścią nauczania |
| `wiedza/cytaty_wazne.md` | Cytaty i złote myśli wzmacniające główną tezę |
| `wiedza/cytaty_kk.md` | Dokumenty Kościoła pasujące do tematu |
| `wiedza/przyklady.md` | Analogie, anegdoty, obrazy z biznesu lub technologii |
| `wiedza/styl_pisania.md` | Styl autora – żeby wzbogacone fragmenty brzmiały spójnie |

Szukaj elementów, które:
- **pasują tematycznie** (słowa kluczowe, emocje, kontekst życiowy),
- **wypełniają konkretną lukę** w strukturze nauczania,
- **nie dublują** tego, co już jest w pliku.

## Krok 3 – Dobór i dopasowanie

Wybierz 3–7 najlepiej pasujących elementów (zróżnicowanych typem: świadectwo + cytat + przykład).

Dla każdego elementu oceń:
- **Gdzie** wstawić go do nauczania (np. po akapicie o X, przed wezwaniem)?
- **Jak** go wprowadzić, by brzmiał naturalnie i spójnie ze stylem autora?
- Jeśli fragment wymaga **lekkiej adaptacji stylistycznej** – dostosuj go (skróć, zmień formę, wstaw naturalne przejście), ale zachowaj pierwotny sens.

## Krok 4 – Wzbogacenie pliku nauczania

Dopisz wybrane elementy do pliku nauczania w odpowiednich miejscach.

Każdy wstawiony fragment powinien być oznaczony komentarzem źródłowym w formacie:

```
> [!source] Źródło: [[Nazwa_Pliku_Bazy_Wiedzy]]
```

umieszczonym bezpośrednio pod wstawionym fragmentem.

Nie przepisuj całego pliku – dopisuj i wstawiaj punktowo.

## Krok 5 – Weryfikacja spójności

Po wstwieniu elementów przejrzyj całość nauczania i sprawdź:

- Czy struktura jest zachowana (życie → Słowo → świadectwo → wezwanie)?
- Czy ton i rytm są spójne z resztą tekstu i szablonem stylu autora?
- Czy nauczanie nie jest przeładowane (maks. jeden przykład / jedno świadectwo na główny punkt)?
- Czy każdy wstawiony fragment ma oznaczenie źródła?

Jeśli cokolwiek zaburza spójność – usuń lub popraw wstawiony fragment.

## Podsumowanie

Zwróć krótkie podsumowanie w punktach:
- Jakie luki zidentyfikowano w nauczaniu
- Jakie elementy wybrano z bazy wiedzy i skąd
- W które miejsca pliku zostały wstawione
- Czy adaptowano styl i w jaki sposób
