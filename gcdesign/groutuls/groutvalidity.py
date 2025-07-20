# imports
from collections import namedtuple

"""
todo: checks units todo!
# todo

"""
# namedtuple for storing DNVGL-ST-0126 validity checks
DNVLimit = namedtuple('DNVLimit', ['result', 'name', 'message', 'reference', 'value', 'limit'])


def validity(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing, le, pnom):
    """ performs checks on the validity of the inputs to DNVGL-ST-0126, Appendix C

        Args:
            rj, float, outer radius jacket leg, units: m
            tj, float, wall thickness of jacket leg, units: m
            rp, float, outer radius of pile, units: m
            tp, float, wall thickness of pile, units: m
            n, int, number of effective shear keys
            h, float, shear key height, units: m
            w, float, shear key width, units: m
            s, float, shear key spacing, units: m
            lfree_top, float, length of top grouted connection without sks, units: m
            lfree_btm, float, length of bottom grouted connection without sks, units: m

        Returns list of checks, each item is a DNVLimit namedtuple
    """
    rj = leg_od / 2
    tj = leg_t
    rp = pile_od / 2
    tp = pile_t
    n = n_sks  # on the jacket leg
    h = sk_height
    w = sk_width
    s = sk_spacing

    sk_region_length = (n - 1) * s
    lfree_top = (gc_length - sk_region_length) / 2
    lfree_btm = lfree_top
    # pile
    pile_sk_region_length = n * s
    # holder for check outcomes
    outcomes = []
    # calculations of grouted connection geometry
    # nominal thickness of grout
    tg = rp - tp - rj
    # length of shear key area
    lsk = (n - 1) * s
    # full length of grouted section
    flen = lsk + lfree_top + lfree_btm
    # effective length of the grouted section
    lg = flen - 2.0 * tg
    # outer diameter of the grouted connection
    dg = 2.0 * (rj + tg)
    # C.1.4.6, Vertical distance between shear keys for pre installed pile
    limit = min(0.8 * ((rp * tp)) ** 0.5, 0.8 * ((rj * tj)) ** 0.5)
    if s >= limit:
        outcomes.append(DNVLimit(True, 's min limit', 'Vertical distance between shear keys is ok', 'C.1.4.6', s, limit))
    else:
        outcomes.append(DNVLimit(False, 's min limit', 'Vertical distance between shear keys is too small', 'C.1.4.6', s, limit))

    # C.1.4.7, Geometry of shear keys
    # shear key height
    limit = 0.005
    if h >= limit:
        outcomes.append(DNVLimit(True, 'SK h>=5mm', 'Shear key height is large enough', 'C.1.4.7', h, limit))
    else:
        outcomes.append(DNVLimit(False, 'SK h>=5mm', 'Shear key height is too small', 'C.1.4.7', h, limit))

    # shear key width
    if  1.5 <= w/h <= 3.0:
        outcomes.append(DNVLimit(True, 'SK w/h limits', 'Shear key width is within range 1.5 <= w/h <= 3.0', 'C.1.4.7', w, 1.5))
    elif w/h > 3.0:
        outcomes.append(DNVLimit(False, 'SK w/h limits', 'Shear key width is too large', 'C.1.4.7', w, 3.0))
    else:
        outcomes.append(DNVLimit(False, 'SK w/h limits', 'Shear key width is too small', 'C.1.4.7', w, 1.5))

    # shear key spacing
    if (h / s) <= 0.1:
        outcomes.append(DNVLimit(True, 'SK h/s<=0.1', 'Shear key height/spacing ratio is ok', 'C.1.4.7', h / s, 0.1))
    else:
        outcomes.append(DNVLimit(False, 'SK h/s<=0.1', 'Shear key height/spacing ratio is too large', 'C.1.4.7', h / s, 0.1))

    # jacket leg geometry, for pre-installed piles
    value = (h / (2 * rj))
    if value <= 0.012:
        outcomes.append(DNVLimit(True, 'SK h/DL<=12mm', 'Shear key height to jacket leg outer diameter ratio is ok', 'C.1.4.7', value, 0.012))
    else:
        outcomes.append(DNVLimit(False, 'SK h/DL<=12mm', 'Shear key height to jacket leg outer diameter ratio is too large', 'C.1.4.7', value, 0.012))

    # pre-installed pile
    value = lg / (2 * rj)
    if  1 <= value <= 10.0:
        outcomes.append(DNVLimit(True, 'Lg/Djl limit', 'Grout length to jacket leg outer diameter ratio is within range 1.0 <= ... <= 10.0', 'C.1.4.8', value, 1.0))
    elif value > 10.0:
        outcomes.append(DNVLimit(False, 'Lg/Djl limit', 'Grout length to jacket leg outer diameter ratio is too large', 'C.1.4.8', value, 10.0))
    else:
        outcomes.append(DNVLimit(False, 'Lg/Djl limit', 'Grout length to jacket leg outer diameter ratio is too small', 'C.1.4.8', value, 1.0))

    # C.1.4.9, Grout dimensions
    value = dg / tg
    if  10.0 <= value <= 45.0:
        outcomes.append(DNVLimit(True, 'Dg/tg limit', 'Grout dimension ratio Dg/tg is within range 10.0 <= ... <= 45.0', 'C.1.4.9', value, 10.0))
    elif value > 45.0:
        outcomes.append(DNVLimit(False, 'Dg/tg limit', 'Grout dimension ratio Dg/tg is too large', 'C.1.4.9', value, 45.0))
    else:
        outcomes.append(DNVLimit(False, 'Dg/tg limit', 'Grout dimension ratio Dg/tg is too small', 'C.1.4.9', value, 10.0))

    # pre-installed pile
    value = rj / tj
    if  10.0 <= value <= 30.0:
        outcomes.append(DNVLimit(True, 'Rjl/tjl limit', 'Jacket leg geometry ratio is within range 10.0 <= ... <= 30.0', 'C.1.4.10', value, 10.0))
    elif value > 30.0:
        outcomes.append(DNVLimit(False, 'Rjl/tjl limit', 'Jacket leg geometry ratio is too large', 'C.1.4.10', value, 30.0))
    else:
        outcomes.append(DNVLimit(False, 'Rjl/tjl limit', 'Jacket leg geometry ratio is too small', 'C.1.4.10', value, 10.0))

    # pre-installed pile
    value = rp / tp
    if  15.0 <= value <= 70.0:
        outcomes.append(DNVLimit(True, 'Rp/tp limit', 'Pile geometry ratio is within range 15.0 <= ... <= 70.0', 'C.1.4.11', value, 15.0))
    elif value > 70.0:
        outcomes.append(DNVLimit(False, 'Rp/tp limit', 'Pile geometry ratio is too large', 'C.1.4.11', value, 70.0))
    else:
        outcomes.append(DNVLimit(False, 'Rp/tp limit', 'Pile geometry ratio is too small', 'C.1.4.11', value, 15.0))


    # other separate chks

    # grout annulus 40mm
    value = (rp - tp) - rj
    if value <= 40:
        outcomes.append(DNVLimit(False, 'tg>=40mm', 'Grout annulus', '6.2.1.12', value, 40))
    else:
        outcomes.append(DNVLimit(True, 'tg>=40mm', 'Grout annulus', '6.2.1.12', value, 40))

    # sks within half elastic range
    pile_sk_free_len_total = gc_length - pile_sk_region_length
    value = 0.5 * pile_sk_free_len_total
    if pile_sk_free_len_total <= le:
        outcomes.append(DNVLimit(False, 'SK > (le/2) from end', 'SKs in 0.5 * le', 'C.1.4.13', value, 99))
    else:
        outcomes.append(DNVLimit(True, 'SK > (le/2) from end', 'SKs in 0.5 * le', 'C.1.4.13', value, 99))

    # pnom checks
    value = pnom
    if pnom > 1.5:
        outcomes.append(DNVLimit(False, 'Pnom<=1.5 MPa', 'Pnom<=1.5 MPa', '6.5.4.6', value, 99))
    else:
        outcomes.append(DNVLimit(True, 'Pnom<=1.5 MPa', 'Pnom<=1.5 MPa', '6.5.4.6', value, 99))

    # return list of outcomes (DNVLimit namedtuples)
    return outcomes
