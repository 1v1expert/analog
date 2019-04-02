def _rev_dict(choices):
    return {v: k for k, v in choices}


STRUCTURE_PRODUCT = (
    (0, 'name'),
    (1, 'class'),
    (2, 'subclass'),
    (3, 'vendor_code'),
    (4, 'manufacturer'),
    (5, 'attributes')
)

STRUCTURE_PRODUCT_REV_DICT = _rev_dict(STRUCTURE_PRODUCT)

