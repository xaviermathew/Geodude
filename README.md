# Geodude
Toy geocoder

* Why is this called what it is? [Pokémon](https://www.pokemon.com/us/pokedex/geodude)

## Usage
```python
>>> from geodude.geodude import geocode
>>> from geodude.ingest.openaddresses import ingest_cities

>>> df = ingest_cities()
>>> geocode({
...     'address_line_1': '54 MACON STREET',
...     'address_line_2': '',
...     'city': 'New York City',
...     'state': 'New York',
...     'postal_code': '11216'
... }, df)
(-73.9489084, 40.6810246)
```
