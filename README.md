# README

__Čiko__

(For English use translator or learn Czech. Your choice.)

Když skončil omnivore, aplikace na agregaci RSS feedů, newsletterů a článků uložených k přečtení při brouzdání na internetu (pomocí rozšíření prohlížeče), zklamalo mě to. Místo self-hostování si omnivoru, jsem se rozhodl naprgat si vlastní věc. Výsledkem je Django aplikace + pár skriptů pospojovaných izolepou. Ale funguje to (většinou). Narozdíl od omnivoru to taky umí počítat, kolik jsem toho za den přečetl (+-). 

__Jak to funguje?__  
- jako každá Django aplikace

__Co to umí?__  
- zobrazovat články získané z RSS feedů
- zobrazovat články uložené přes Pocket
- ukládat označené pasáže z textu (aka výpisky z četby)
- spočítat, kolik jsem toho za den přečetl

__Pro koho to je?__  
Pro mě. To stačí.  

__Proč se to jmenuje Čiko?__  
[Proto](https://cs.wikipedia.org/wiki/Willy_Fog_na_cest%C4%9B_kolem_sv%C4%9Bta).

__Jak to spustit?__
```
source .env/bin/activate
cd django
python manage.py runserver
```

__Jak se to updatuje?__

Při změně modelu/DB:

```
python manage.py makemigrations
python manage.py migrate
```