from collections import Counter
import functools
import operator

from thefuzz import fuzz
import pandas as pd

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
keys_all_match = [
    'n_state',
    'n_postal_code',
]
keys_any_match = [
    'n_city',
    'p_AddressNumber',
    'p_StreetName'
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
    from geodude.query.normalizer import normalize_address, parse_address

    d = normalize_address(d)
    parsed = parse_address(d)
    if parsed is not None:
        d.update(parsed)
    all_match_filters = []
    for key in keys_all_match:
        if d[key]:
            all_match_filters.append(getattr(df, key) == d[key])
    any_match_filters = []
    for key in keys_any_match:
        if d[key]:
            any_match_filters.append(getattr(df, key) == d[key])

    filters = None
    if all_match_filters:
        filters = functools.reduce(operator.and_, all_match_filters)
    if any_match_filters:
        if filters is None:
            filters = functools.reduce(operator.or_, any_match_filters)
        else:
            filters = filters & functools.reduce(operator.or_, any_match_filters)
    candidates = df[filters]
    candidates['score'] = candidates.progress_apply(lambda row: score_candidates(row, d), axis=1).progress_apply(pd.Series)
    # candidates['score'] = candidates['score'] / candidates['score'].max()
    return candidates.sort_values('score', ascending=False)[:max_results]
