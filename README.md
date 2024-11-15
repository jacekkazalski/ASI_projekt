# s22393_CarPricePrediction
## Cel projektu
Celem projektu jest stworzenie modelu pozwalającego na przewidywanie ceny używanego samochodu na podstawie podanych prametrów.

Dataset zawiera ponad 90,000 rekordów ofert sprzedaży z popularnej strony z aukcjami samochodów.

Źródło danych: https://www.kaggle.com/datasets/wspirat/poland-used-cars-offers

## Analiza danych

Dataset zawiera 10 kolumn i 91523 wierszy, nie posiada brakujących wartości.
### Kolumny

| Nazwa | Opis | Przykład |
| ----- | ----- | ------- |
| brand | marka samochodu | alfa-romeo |
| model | nazwa konkretnego modelu | Alfa Romeo Spider 2.0-16 TSpark |
| price_in_pln | cena w PLN | 14700.0 |
| mileage | przebieg w kilometrach | 133 760 km |
| gearbox | rodzaj skrzyni biegów | manual |
| engine_capacity | pojemność silnika w cm3 | 1 970 cm3	 |
| fuel_type | rodzaj paliwa | Benzyna |
| city | miejscowość wystawienia oferty | Łask |
| voivodeship | województwo | Łódzkie |
| year | rok produkcji | 1998 |

4 kolumny to kolumny numeryczne – price_in_pln, mileage, engine_capacity, year.
2 kolumny to kolumny tekstowe – model, city
4 kolumny to kolumny kategoryczne – brand, gearbox, fuel_type, voivodship

Po wstępnym formatowaniu kolumn okazało się że dataset zawiera wiersze w których dane w poszczególnych kolumnach są pomieszane. Po ich usunięciu zostało 85677 wierszy.

Niektóre wartości w kolumnie voivodeship były nieprawidłowe. Po usunięciu wierszy zostało 85632 rekordów.
### Analiza zmiennych
- price_in_pln – ceny wahają się od 1111 do 2 599 000. Mediana to 46 500, ponad 75% cen jest poniżej 100 000 złotych.
- mileage – średni przebieg to 147 002 km, dużo wartości (ponad 6000) poniżej 10 czyli samochody nowe
- engine_capacity – średnia to 1893. Ponad 75% to silniki poniżej 2 litrów.
- year – średnia to 2013
- brand – 43 unikalne wartości
- model – 18021 unikalnych wartości
- gearbox
- fuel_type – 6 unikalnych wartości, wyraźna większośc to benzyna lub diesel
- city – 4353 unikalnych wartości, najpopularniejsze to duze miasta wojewódzkie jak Warszawa, Kraków czy Wrocław
- voivodship - 16 unikalnych wartości
