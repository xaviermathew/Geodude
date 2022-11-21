def geocode(d, df):
    from geodude.query.scorer import get_candidates

    candidates = get_candidates(d, df)
    if len(candidates) > 0:
        g = candidates.iloc[0].geometry
        return g.x, g.y
