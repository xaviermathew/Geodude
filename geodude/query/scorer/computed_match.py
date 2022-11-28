import operator

from thefuzz import fuzz
import pandas as pd

street_loose_match_keys = [
    'p_StreetName',
]
street_exact_match_keys = street_loose_match_keys + [
    'p_StreetNamePreModifier',
    'p_StreetNamePreDirectional',
    'p_StreetNamePreType',
    'p_StreetNamePostType',
    'p_StreetNamePostDirectional',
]
line1_loose_match_keys = [
    'p_AddressNumber',
]
line1_exact_match_keys = line1_loose_match_keys + [
    'p_AddressNumberPrefix',
    'p_AddressNumberSuffix',
]

state_match_keys = [
    'n_state',
]
city_match_keys = [
    'n_city',
] + state_match_keys
zip5_match_keys = [
    'n_postal_code',
] + city_match_keys
street_match_keys = street_loose_match_keys + zip5_match_keys
parcel_match_keys = line1_loose_match_keys + street_match_keys

accuracy_type_parcel = 'parcel'
accuracy_type_street_center = 'street_center'
accuracy_type_zip5 = 'zip5'
accuracy_type_city = 'city'
accuracy_type_state = 'state'


def score_parcel_match_candidates(row, d):
    matches = 0.0
    for key in line1_exact_match_keys + street_exact_match_keys:
        lhs = getattr(row, key)
        rhs = d.get(key)
        if lhs is not None and rhs is not None:
            # print(key, lhs, rhs)
            matches += fuzz.ratio(lhs, rhs)
    return matches


def compute_centroid(df):
    return df.dissolve().centroid


def compute_street_center(df):
    return compute_centroid(df)


def get_candidates(d, df, max_results=10):
    from geodude.query.scorer.utils import _get_candidates, filter_df

    parsed, candidates = _get_candidates(d, df)
    matches = filter_df(candidates, parsed, parcel_match_keys, operator.and_)
    if len(matches) > 0:
        matches['score'] = matches.progress_apply(lambda row: score_parcel_match_candidates(row, parsed), axis=1) \
                                  .progress_apply(pd.Series)
        matches['accuracy_type'] = accuracy_type_parcel
        matches['lat_long'] = matches['geometry']
        return matches.sort_values('score', ascending=False)[:max_results]
    else:
        matches = filter_df(candidates, parsed, street_match_keys, operator.and_)
        if len(matches) > 0:
            matches['lat_long'] = compute_street_center(matches)
            matches = matches[:1]
            matches['score'] = 0.9
            matches['accuracy_type'] = accuracy_type_street_center
            return matches
        else:
            matches = filter_df(candidates, parsed, zip5_match_keys, operator.and_)
            if len(matches) > 0:
                matches['lat_long'] = compute_centroid(matches)
                matches = matches[:1]
                matches['score'] = 0.75
                matches['accuracy_type'] = accuracy_type_zip5
                return matches
            else:
                matches = filter_df(candidates, parsed, city_match_keys, operator.and_)
                if len(matches) > 0:
                    matches['lat_long'] = compute_centroid(matches)
                    matches = matches[:1]
                    matches['score'] = 0.5
                    matches['accuracy_type'] = accuracy_type_city
                    return matches
                else:
                    matches = filter_df(candidates, parsed, state_match_keys, operator.and_)
                    if len(matches) > 0:
                        matches['lat_long'] = compute_centroid(matches)
                        matches = matches[:1]
                        matches['score'] = 0.25
                        matches['accuracy_type'] = accuracy_type_state
                        return matches
