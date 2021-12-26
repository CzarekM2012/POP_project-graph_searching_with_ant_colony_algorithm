Repozytorium projektu z przedmiotu Przeszukiwanie i Optymalizacja.

Polecenie:
Projekt polega na zaplanowaniu racjonalnej kontroli tras intencji w sieci SDN
(Software Defined Networking), który dotyczy jednoczesnie sterowaniem sieciami Internetu Rzeczy (IoT). W tym celu, dla kazdej intencji w sieci wybieramy
zestaw dwóch sciezek, które sa rozłaczne tak bardzo jak to tylko mozliwe. Para ta
jest obliczana w taki sposób, aby zminimalizowac sredni wazony koszt sciezek poprzez załozenie, ze koszt jednej sciezki jest dany przez jej długosc, a koszt drugiej
scieżki przez jej zajetość (pojemność wyrażona w Gbps).W ten sposób otrzymujemy parę ścieżek, z których jedna minimalizuje czas transmisji, a druga minimalizuje prawdopodobienstwo straty. Funkcja celu powinna składac sie z trzech
elementów. Pierwszy z nich odpowiada za cel priorytetowy, którym jest minimalizacja liczby wspólnych krawedzi. Drugi element reprezentuje koszt scieżki X
(pierwsza scieżka), a trzeci element reprezentuje koszt sciezki Y (druga sciezka).
Zaproponwać funkcje kosztu oraz odpowiedni algorytm heurystyczny rozwiazujacy ten problem. Dane pobrac ze strony http://sndlib.zib.de/home.action, dla
sieci germany50. Literatura: DOI:10.1007/978-3-030-77970-2 40.
