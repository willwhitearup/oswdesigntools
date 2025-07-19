import numpy as np

""" implements uls check calculations
"""

STEEL_E = 210000  # MPa

def axial(leg_od, leg_t, pile_od, pile_t, n_sks, sk_spacing, sk_height, fz, grout_E, grout_strength):
    """ implements design check under axial load only

        As per section 2.7 of "Deep Cluster ULS.xmcd" Mathcad calculation

        Args:
            fz, numpy array of floats, axial load, units: N
            rj, float, outer radius jacket leg, units: m
            tj, float, wall thickness of jacket leg, units: m
            rp, float, outer radius of pile, units: m
            tp, float, wall thickness of pile, units: m
            n, int, number of effective shear keys
            es, float, elastic modulus of steel, units: Pa
            eg, float, elastic modulus of grout, units: Pa
            h, float, shear key height, units: m
            s, float, shear key spacing, units: m
            fck, float, defining characteristic compressive strength of 75mm cubes, units: Pa
            gamma, float, material factor, units: unitless
            
        Returns numpy array of floats of utilisations

        True
    """
    mm_to_m = 1e-3
    mpa_to_pa = 1e6

    rj = (leg_od / 2) * mm_to_m
    tj = leg_t * mm_to_m
    rp = (pile_od / 2) * mm_to_m
    tp = pile_t * mm_to_m
    n = n_sks
    es, eg = STEEL_E * mpa_to_pa, grout_E * mpa_to_pa
    fck = grout_strength * mpa_to_pa
    h, s = sk_height * mm_to_m, sk_spacing * mm_to_m
    gamma = 2  # material factor

    # design load per unit length, C.1.4.2
    fv1shk = fz / (2 * np.pi * rj * n)
    
    # nominal thickness of grout
    tg = rp - tp - rj
    
    # radial stiffness parameter, C.1.4.3
    k = ((2 * rj / tj) + (2 * rp / tp)) ** -1 + (eg / es) * ((2 * rp - 2 * tp) / tg) ** -1
    
    # interface shear capacity in the grouted connection with shear keys, C.1.4.3
    fbk = (((800 / (2 * (rj * 1e3)) + 140 * (h / s) ** 0.8)) * (k ** 0.6) * ((fck / 1e6) ** 0.3)) * mpa_to_pa
    
    # codified limit
    limit = (0.75 - 1.4 * (h / s)) * ((fck / mpa_to_pa) ** 0.5) * mpa_to_pa
    # design capacity per unit length, C.1.4.5
    fv1shcapd = fbk * s / gamma
    if fbk > limit and not np.allclose(fbk, limit): # np.allclose to avoid float rounding issues
        fv1shcapd = limit * s / gamma
    
    # utilisations
    util = fv1shk / fv1shcapd
    return np.absolute(util)


def pnom_calc(leg_od, leg_t, pile_od, pile_t, grout_E, fx, fy, mxo, myo):
    """ implements Pnom design check
        
        Args:
            rj, float, outer radius jacket leg, units: m
            tj, float, wall thickness of jacket leg, units: m
            rp, float, outer radius of pile, units: m
            tp, float, wall thickness of pile, units: m
            es, float, elastic modulus of steel, units: Pa
            eg, float, elastic modulus of grout, units: Pa
            fx, numpy array of floats, shear force, units: N
            fy, numpy array of floats, shear force, units: N
            mx, numpy array of floats, shear bending moment, units: Nm
            my, numpy array of floats, shear bending moment, units: Nm
            
        Returns numpy array of floats of pnom values: Pa
    """

    mm_to_m = 1e-3
    mpa_to_pa = 1e6
    Nmm_to_Nm = 1e-3

    rj = (leg_od / 2) * mm_to_m
    tj = leg_t * mm_to_m
    rp = (pile_od / 2) * mm_to_m
    tp = pile_t * mm_to_m

    es, eg = STEEL_E * mpa_to_pa, grout_E * mpa_to_pa

    mx, my = mxo * Nmm_to_Nm, myo * Nmm_to_Nm

    # nominal thickness of grout
    tg = rp - tp - rj
    
    # ratio of elastic modulus steel to elastic modulus grout
    m = es / eg
    
    # supporting spring stiffness, C.1.4.14
    krd = (4 * es * rj) / (tg * m + (rp ** 2 / tp) + (rj ** 2 / tj))
    
    # second moment of area of jacket leg
    ij = np.pi * ((2 * rj) ** 4 - (2 * rj - 2 * tj) ** 4) / 64

    # elastic length, C.1.4.13
    le = (4 * es * ij / krd) ** 0.25

    # total combined applied moment
    mtot = np.sqrt((mx - fy * le) ** 2 + (my + fx * le) ** 2)

    # maximum nominal radial contact pressure, C.1.4.15
    pnom = (le ** 2 * krd) * mtot / (8 * es * ij * rj)  # this is in Pa (as per the docstrings)
    pnom = pnom / mpa_to_pa  # convert back from MPa to Pa
    return pnom

