# Geodude
Toy geocoder

* Why is this called what it is? [Pokémon](https://www.pokemon.com/us/pokedex/geodude)

## Usage
```python
>>> from geodude.geodude import geocode
>>> from geodude.ingest.openaddresses import ingest_cities
>>> df = ingest_cities()

>>> # exact match
>>> geocode({
...     'address_line_1': '54 MACON STREET',
...     'address_line_2': '',
...     'city': 'New York City',
...     'state': 'New York',
...     'postal_code': '11216'
... }, df)
[{'number': '54',
  'street': 'MACON ST',
  'postcode': '11216',
  'city': 'New York City',
  'region': 'New York',
  'accuracy_type': 'parcel',
  'score': 300.0,
  'lat_long': (-73.9489084, 40.6810246)}]

>>> # street number not present in data
>>> geocode({
...     'address_line_1': '5400 MACON STREET',
...     'address_line_2': '',
...     'city': 'New York City',
...     'state': 'New York',
...     'postal_code': '11216'
... }, df)
[{'street': 'MACON ST',
  'postcode': '11216',
  'city': 'New York City',
  'region': 'New York',
  'accuracy_type': 'street_center',
  'score': 0.9,
  'lat_long': (-73.94388640762713, 40.681734969491515)}]

>>> # street number + name not present in data
>>> geocode({
...     'address_line_1': '5400 MACONSET STREET',
...     'address_line_2': '',
...     'city': 'New York City',
...     'state': 'New York',
...     'postal_code': '11216'
... }, df)
[{'postcode': '11216',
  'city': 'New York City',
  'region': 'New York',
  'accuracy_type': 'zip5',
  'score': 0.75,
  'lat_long': (-73.94936157047428, 40.680576926737395)}]
```
