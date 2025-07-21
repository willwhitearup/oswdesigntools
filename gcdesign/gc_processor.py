from gcdesign.groutuls.groutuls import axial, pnom_calc, axial_and_bending
from gcdesign.groutuls.groutvalidity import validity





def gc_processor(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing, fx, fy, fz, mx, my, grout_E, grout_strength):


    sk_axial_ur = axial(leg_od, leg_t, pile_od, pile_t, n_sks, sk_spacing, sk_height, fz, grout_E, grout_strength)
    sk_axbm_ur = axial_and_bending(leg_od, leg_t, pile_od, pile_t, n_sks, sk_spacing, sk_height, fz, grout_E, grout_strength, fx, fy,
                      mx, my, gc_length)
    pnom_top, pnom_btm, le = pnom_calc(leg_od, leg_t, pile_od, pile_t, grout_E, fx, fy, mx, my, gc_length)

    res = {"Pnom @ le from top [code calc]": pnom_top,
           "Pnom @ le from btm": pnom_btm,
           "SK UR axial only [code calc]": sk_axial_ur,
           "SK UR axial & bending": sk_axbm_ur
           }

    # do validity checks
    validity_chk_outcomes = validity(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing, le, max(pnom_top, pnom_btm))
    validity_chks = {}
    for chk in validity_chk_outcomes:
        chkpass = "PASS" if chk.result == True else "FAIL"
        chk_name = chk.name
        validity_chks[chk.reference] = (float(chk.value), chkpass, chk_name)

    return res, validity_chks, le