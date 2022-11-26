from collections import Counter

from thefuzz import fuzz
import pandas as pd

from geodude.query.scorer.utils import _get_candidates

keys_h = [
    'p_AddressNumber',
    'p_StreetName',
    'n_address_line_1',
]
keys_m = [
    'p_AddressNumberPrefix',
    'p_AddressNumberSuffix',
    'n_postal_code',
    'n_city',
    'n_address_line_2',
]
keys_l = [
    'p_StreetNamePreModifier',
    'p_StreetNamePreDirectional',
    'p_StreetNamePreType',
    'p_StreetNamePostType',
    'p_StreetNamePostDirectional',
]
priorities = [
    (8, keys_h),
    (4, keys_m),
    (1, keys_l),
]


def score_candidates(row, d):
    matches = Counter()
    for weight, keys in priorities:
        for key in keys:
            lhs = getattr(row, key)
            rhs = d.get(key)
            if lhs is not None and rhs is not None:
                # print(key, lhs, rhs)
                matches[weight] += fuzz.ratio(lhs, rhs)
    return sum([w * c for w, c in matches.items()])


def get_candidates(d, df, max_results=10):
    parsed, candidates = _get_candidates(d, df)
    candidates['score'] = candidates.progress_apply(lambda row: score_candidates(row, parsed), axis=1) \
                                    .progress_apply(pd.Series)
    candidates['accuracy_type'] = 'best_match'
    candidates['lat_long'] = candidates.geometry
    # candidates['score'] = candidates['score'] / candidates['score'].max()
    return candidates.sort_values('score', ascending=False)[:max_results]
