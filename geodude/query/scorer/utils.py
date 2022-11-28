import functools
import operator

from geodude.query.scorer.computed_match import (
    accuracy_type_parcel, accuracy_type_street_center, accuracy_type_zip5,
    accuracy_type_city, accuracy_type_state
)

keys_all_match = [
    'n_state',
    'n_postal_code',
]
keys_any_match = [
    'n_city',
    'p_AddressNumber',
    'p_StreetName'
]

accuracy_type_state_fields = ['region', 'accuracy_type', 'score', 'lat_long']
accuracy_type_city_fields = ['city'] + accuracy_type_state_fields
accuracy_type_zip5_fields = ['postcode'] + accuracy_type_city_fields
accuracy_type_street_center_fields = ['street'] + accuracy_type_zip5_fields
accuracy_type_parcel_fields = ['number'] + accuracy_type_street_center_fields
accuracy_type__field__map = {
    accuracy_type_parcel: accuracy_type_parcel_fields,
    accuracy_type_street_center: accuracy_type_street_center_fields,
    accuracy_type_zip5: accuracy_type_zip5_fields,
    accuracy_type_city: accuracy_type_city_fields,
    accuracy_type_state: accuracy_type_state_fields,
}


def get_df_filter(df, d, keys, combiner):
    filters = []
    for key in keys:
        if d[key] is not None:
            filters.append(getattr(df, key) == d[key])
    merged = functools.reduce(combiner, filters)
    return merged


def filter_df(df, d, keys, combiner):
    merged = get_df_filter(df, d, keys, combiner)
    return df[merged]


def _get_candidates(d, df):
    from geodude.query.normalizer import normalize_address, parse_address

    d = normalize_address(d)
    parsed = parse_address(d)
    if parsed is not None:
        d.update(parsed)

    filtered = filter_df(df, d, keys_all_match, operator.and_)
    filtered = filter_df(filtered, d, keys_any_match, operator.or_)
    return d, filtered


def candidates_to_dict(df):
    accuracy_type = df.iloc[0]['accuracy_type']
    keys = accuracy_type__field__map[accuracy_type]
    df = df[keys]
    df['lat_long'] = df.lat_long.progress_apply(lambda row: (row.x, row.y))
    return df.to_dict('records')
