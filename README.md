# README

__Čiko__

(For English use translator or learn Czech. Your choice.)

Když skončil omnivore, aplikace na agregaci RSS feedů, newsletterů a článků uložených k přečtení při brouzdání na internetu (pomocí rozšíření prohlížeče), zklamalo mě to. Místo self-hostování si omnivoru, jsem se rozhodl naprgat si vlastní věc. Výsledkem je Django aplikace + pár skriptů pospojovaných izolepou. Ale funguje to (většinou). Narozdíl od omnivoru to taky umí počítat, kolik jsem toho za den přečetl (+-). 

Jak to funguje?
- jako každá Django aplikace + `parse_pocket.py` stahuje věci uložené do Pocketu (protože se mi nechtělo dělat vlastní rozšíření prohlížeče)

Co to umí?
- ukládat a zobrazovat články získané z RSS feedů
- ukládat a zobrazovat články uložené přes Pocket
- ukládat označené pasáže z textu (aka výpisky z četby)

Pro koho to je?
Pro mě. To stačí.