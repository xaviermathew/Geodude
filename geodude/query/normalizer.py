import re

from scourgify.normalize import normalize_addr_dict
from scourgify.exceptions import AmbiguousAddressError, UnParseableAddressError
import usaddress


def normalize_address(d):
    try:
        nd = normalize_addr_dict(d)
    except (AmbiguousAddressError, UnParseableAddressError):
        d.pop('address_line_2')
        try:
            nd = normalize_addr_dict(d)
        except (AmbiguousAddressError, UnParseableAddressError):
            d['address_line_1'] = re.sub(r'(\d)\s+(\d)', r'\1-\2', d['address_line_1'])
            try:
                nd = normalize_addr_dict(d)
            except (AmbiguousAddressError, UnParseableAddressError):
                nd = d
    return {f'n_{k}': v for k, v in nd.items()}


def parse_address(d):
    a = ', '.join(filter(bool, [d['n_address_line_1'], d['n_address_line_2']]))
    try:
        parsed = usaddress.tag(a)[0]
    except usaddress.RepeatedLabelError:
        pass
    else:
        return {f'p_{k}': v for k, v in parsed.items()}
