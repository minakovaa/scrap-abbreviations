# Scrap Russian and Bulgarian abbreviations and create dictionary

Scrap abbreviations for Russian and Bulgarian languages and then create Bg-Ru dictionary for abbreviation translation. 

In `scrap-ru-abbr.py`  there is asynchronous scrapping abbreviations for Russian language.

In `scrap-bg-abbr.py` there is asynchronous scrapping abbreviations for Bulgarian language.

Source language is Bulgarian. Abbreviations scrapped from website 
- https://frazite.com/

Target language is Russian. Abbreviations scrapped from website
- http://netler.ru/slovari/abbreviature.htm

Abbreviations mapped by their embeddings using [sentence_transformers](https://github.com/UKPLab/sentence-transformers) library.
Script for generation mapping in `map-abbreviations.py` file. 


