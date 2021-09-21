# gvp
This is a wrapper for the new internal api of Gymnázium na Vítězné pláni introduced around the start of 2021. It supports getting articles, contacts and more.

# installation
```
pip install gvp
```

# usage
It is recommended to just import the `gvp` module directly.

Everything has docstrings and is annotated, you can just look at the source code to understand it best.

## examples
Get a list of articles:
```py
articles = gvp.articles()
print(articles)
# [<Article id=3686 author='HORYNA' title='Jak na burzu učebnic'>,
#  <Article id=3685 author='SUCHANKOVA' title='Mensa seminář'>,
#  <Article id=3684 author='SUCHANKOVA' title='Přednášky - MUP Autumn Academy 2021'>,
#  <Article id=3683 author='HORYNA' title='Výsledky testování'>,
#  ...]
```

Get a list of all teacher contacts
```py
contacts = gvp.contacts()
print(contacts)
# [<Contact name='Mgr. Adámková Lenka' description=None>,
#  <Contact name='Mb Babiera Jose' description=None>,
#  <Contact name='Mgr. Bártová Irena' description='třídní učitelka 6.B'>,
#  <Contact name='Mgr. Birhanzl Ingrid' description='třídní učitelka 3.C'>,
#  ...]
```

Get a list of all static files
```py
files = gvp.static_files()
print(files)
# [<StaticFile id=2 title='Kontakty'>,
#  <StaticFile id=3 title='Ochrana osobních údajů'>,
#  <StaticFile id=4 title='Učební plán'>,
#  <StaticFile id=5 title='Roční plán'>,
#  ...]
```

Search for a specific article/static page/comment
```py
results = gvp.search('Gymázium na Vítězné pláni')
print(results)
# [<SearchResult category='static' title='Spolek rodičů'>,
#  <SearchResult category='articles' title='Fotografie a video z akademie (aktualizováno)'>,
#  ...]

results = gvp.search('Gymázium na Vítězné pláni', category='articles')
print(results)
# [<SearchResult category='articles' title='Fotografie a video z akademie (aktualizováno)'>,
#  <SearchResult category='articles' title='Studentská odborná soutěž 2013/2014'>,
#  ...]

print(results[0].complete())
# <Article id=1610 author='Petr Urbančík' title='Fotografie a video z akademie (aktualizováno)'>
```