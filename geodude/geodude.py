def geocode(d, df):
    from geodude.query.scorer import get_candidates
    from geodude.query.scorer.utils import candidates_to_dict

    candidates = get_candidates(d, df)
    return candidates_to_dict(candidates)
