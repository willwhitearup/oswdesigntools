from gcdesign.groutuls.groutuls import axial, pnom_calc
from gcdesign.groutuls.groutvalidity import validity





def gc_processor(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing, fx, fy, fz, mx, my, grout_E, grout_strength):


    sk_axial_ur = axial(leg_od, leg_t, pile_od, pile_t, n_sks, sk_spacing, sk_height, fz, grout_E, grout_strength)
    pnom = pnom_calc(leg_od, leg_t, pile_od, pile_t, grout_E, fx, fy, mx, my)

    res = {"pnom": pnom,
           "SK_axial_UR": sk_axial_ur}

    # do validity checks
    validity_chk_outcomes = validity(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing)
    validity_chks = {}
    for chk in validity_chk_outcomes:
        chkpass = "PASS" if chk.result == True else "FAIL"
        validity_chks[chk.reference] = (float(chk.value), chkpass)

    return res, validity_chks