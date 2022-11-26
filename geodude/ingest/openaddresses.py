import os
import re

import geopandas as gd
import pandas as pd
from scourgify.normalize import normalize_addr_dict
from scourgify.exceptions import AmbiguousAddressError, UnParseableAddressError
import usaddress


def normalize_address(row):
    address_line_1 = (row.number + ' ' + row.street).strip()
    d = {
        'address_line_1': address_line_1,
        'address_line_2': row.unit,
        'city': row.city,
        'state': row.region,
        'postal_code': row.postcode
    }
    try:
        nd = normalize_addr_dict(d)
    except (AmbiguousAddressError, UnParseableAddressError):
        d.pop('address_line_2')
        try:
            nd = normalize_addr_dict(d)
        except (AmbiguousAddressError, UnParseableAddressError):
            d['address_line_1'] = re.sub(r'(\d)\s+(\d)', r'\1-\2', address_line_1)
            try:
                nd = normalize_addr_dict(d)
            except (AmbiguousAddressError, UnParseableAddressError):
                nd = d
    if nd.get('address_line_2') is None and row.unit:
        nd['address_line_2'] = 'UNIT ' + row.unit
    return nd


def parse_address(row):
    a = ', '.join(filter(lambda x: x and not pd.isnull(x), [row.n_address_line_1, row.n_address_line_2]))
    try:
        d = usaddress.tag(a)[0]
    except usaddress.RepeatedLabelError:
        if row.street.count(' ') == 1:
            street, street_suffix = row.street.split()
        else:
            street = row.street
            street_suffix = None
        d = {
            'AddressNumber': row.number,
            'StreetName': street,
            'StreetNamePostType': street_suffix,
            'SubaddressType': 'UNIT',
            'SubaddressIdentifier': row.unit,
        }
    for k in usaddress.LABELS:
        if k != 'NotAddress' and k not in d:
            d[k] = None
    return d


def ingest_cities():
    base_dir = 'data/openaddresses/cities/'
    df_set = []
    for fname in os.listdir(base_dir):
        if not fname.endswith('.geojson'):
            continue
        df = gd.read_file(os.path.join(base_dir, fname))
        df = df.drop(columns=['hash', 'id', 'district'])
        country, state, city = fname.split('-')[0].split('_', 2)
        df['city'] = city
        df['region'] = state

        n_address_df = df[['number', 'street', 'unit', 'city', 'region', 'postcode']]\
            .progress_apply(normalize_address, axis=1)\
            .progress_apply(pd.Series)
        df[['n_address_line_1', 'n_address_line_2', 'n_city', 'n_state', 'n_postal_code']] = n_address_df

        p_address_df = df[['number', 'street', 'unit', 'n_address_line_1', 'n_address_line_2']]\
            .progress_apply(parse_address, axis=1)\
            .progress_apply(pd.Series)
        df[[f'p_{col}' for col in p_address_df.columns]] = p_address_df

        df_set.append(df)

    if df_set:
        return pd.concat(df_set)


def ingest_states():
    raise NotImplementedError
