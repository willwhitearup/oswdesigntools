import numpy as np

""" implements uls check calculations
"""

STEEL_E = 210000  # MPa

def axial(leg_od, leg_t, pile_od, pile_t, n_sks, sk_spacing, sk_height, fz, grout_E, grout_strength):
    """ implements design check under axial load only

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

    pile_ir = rp - tp
    if pile_ir <= rj:
        return 999.

    # design load per unit length, C.1.4.2
    fv1shk = fz / (2 * np.pi * rj * n)
    # nominal thickness of grout
    tg = rp - tp - rj
    # radial stiffness parameter, C.1.4.3
    k = ((2 * rj / tj) + (2 * rp / tp)) ** -1 + (eg / es) * ((2 * rp - 2 * tp) / tg) ** -1
    # interface shear capacity in the grouted connection with shear keys, C.1.4.3
    fbk = (((800 / (2 * (rj * 1e3)) + 140 * (h / s) ** 0.8)) * (k ** 0.6) * ((fck / 1e6) ** 0.3)) * mpa_to_pa
    # codified fbk_limit
    fbk_limit = (0.75 - 1.4 * (h / s)) * ((fck / mpa_to_pa) ** 0.5) * mpa_to_pa
    # design capacity per unit length, C.1.4.5
    fv1shcapd = fbk * s / gamma

    if fbk > fbk_limit and not np.allclose(fbk, fbk_limit): # np.allclose to avoid float rounding issues
        fv1shcapd = fbk_limit * s / gamma

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

    # conversion back from Pa to MPa
    pnom = pnom / mpa_to_pa  # convert back from Pa to MPa
    le = le / mm_to_m
    return pnom, le


def fbk_vs_grout_matrix_failure(leg_od, leg_t, pile_od, pile_t, sk_spacing, sk_height, grout_E, grout_strength):
    """ get vals for grout matrix failure plot
    """
    mm_to_m = 1e-3
    mpa_to_pa = 1e6
    rj = (leg_od / 2) * mm_to_m
    tj = leg_t * mm_to_m
    rp = (pile_od / 2) * mm_to_m
    tp = pile_t * mm_to_m
    es, eg = STEEL_E * mpa_to_pa, grout_E * mpa_to_pa
    fck = grout_strength * mpa_to_pa
    h, s = sk_height * mm_to_m, sk_spacing * mm_to_m

    pile_ir = rp - tp
    if pile_ir <= rj:
        return 999., 999.
    # nominal thickness of grout
    tg = rp - tp - rj
    # radial stiffness parameter, C.1.4.3
    k = ((2 * rj / tj) + (2 * rp / tp)) ** -1 + (eg / es) * ((2 * rp - 2 * tp) / tg) ** -1
    # interface shear capacity in the grouted connection with shear keys, C.1.4.3
    fbk = (((800 / (2 * (rj * 1e3)) + 140 * (h / s) ** 0.8)) * (k ** 0.6) * ((fck / 1e6) ** 0.3)) * mpa_to_pa
    # codified fbk_limit
    fbk_limit = (0.75 - 1.4 * (h / s)) * ((fck / mpa_to_pa) ** 0.5) * mpa_to_pa
    return fbk, fbk_limit


def get_grout_matrix_failure_plot_vals(leg_od, leg_t, pile_od, pile_t, sk_height, grout_E, grout_strength,
                                       max_sk_spacing, min_sk_spacing, sk_spacing_actual):
    """calculate shear capacity, fbk, and shear capacity grout matrix failure limit ,fbk_limit

    Create array of h/s vals and fbk vals for plotting
    """
    Pa_to_mpa = 1e-6
    # first work out actual f_bk (shear capacity)
    fbka, fbk_limita = fbk_vs_grout_matrix_failure(leg_od, leg_t, pile_od, pile_t, sk_spacing_actual, sk_height, grout_E, grout_strength)
    f_bk_actual = fbk_limita*Pa_to_mpa if fbka*Pa_to_mpa > fbk_limita*Pa_to_mpa else fbka*Pa_to_mpa

    # then create a range
    max_sk_spacing2 = max(max_sk_spacing, sk_spacing_actual)
    sk_spacings = np.linspace(max_sk_spacing2, min_sk_spacing, num=5000)
    h_over_s_vals = []
    fbks, fbk_limits = [], []
    gmf_flag = False
    hs_limit = None
    for idx, sk_spacing in enumerate(sk_spacings):
        fbk, fbk_limit = fbk_vs_grout_matrix_failure(leg_od, leg_t, pile_od, pile_t, sk_spacing, sk_height, grout_E, grout_strength)
        fbks.append(fbk*Pa_to_mpa)
        fbk_limits.append(fbk_limit*Pa_to_mpa)
        h_over_s = sk_height / sk_spacing
        h_over_s_vals.append(sk_height / sk_spacing)

        if fbk * Pa_to_mpa >= fbk_limit * Pa_to_mpa and gmf_flag is False:
            hs_limit = h_over_s
            gmf_flag = True


        if hs_limit is not None and h_over_s > 2 * hs_limit and h_over_s > sk_height / sk_spacing_actual:
            break

    return fbks, fbk_limits, h_over_s_vals, f_bk_actual, hs_limit
