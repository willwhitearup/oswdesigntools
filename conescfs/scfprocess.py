from conescfs.scfs import calc_cone_scfs_sect3, calc_cone_scfs_appf17
from conescfs.thktransitionscfs import calc_scf_thickness_transition


def cone_scf_single(radius_tubular, thickness_tubular, thickness_cone, alpha, junction_type):
    """Returns SCFs for a single geometry.
    """
    sect3_vals = calc_cone_scfs_sect3(radius_tubular, thickness_tubular, thickness_cone, alpha, junction_type)
    appf_vals = calc_cone_scfs_appf17(radius_tubular, thickness_tubular, thickness_cone, alpha, junction_type)

    keys = ["tube_in", "cone_in", "tube_out", "cone_out"]

    return {"sect3": dict(zip(keys, sect3_vals)),
            "appf17": dict(zip(keys, appf_vals))
            }


def cone_scf_sweep(junction_type, cone_x_axis_vary, x_arr, numeric_inputs):
    """Returns SCFs over ±X% variation of selected variable.
    """

    keys = ["tube_in", "cone_in", "tube_out", "cone_out"]
    results = {"x": x_arr, "sect3": {k: [] for k in keys}, "appf17": {k: [] for k in keys}}

    for x in x_arr:
        args = numeric_inputs.copy()
        args[cone_x_axis_vary] = x

        sect3_vals = calc_cone_scfs_sect3(args["radius_tubular"], args["thickness_tubular"], args["thickness_cone"],
            args["alpha"], junction_type)

        appf_vals = calc_cone_scfs_appf17(args["radius_tubular"], args["thickness_tubular"], args["thickness_cone"],
            args["alpha"], junction_type)

        for key, val in zip(keys, sect3_vals):
            results["sect3"][key].append(val)

        for key, val in zip(keys, appf_vals):
            results["appf17"][key].append(val)

    return results

def tt_scf_process(thickness_tubular, thickness_cone, radius_tubular, transition_side, weld_width, delta_m, delta_0,
                   scf_taper_ratio, scf_weld_type):

    thk_diff = abs(thickness_tubular - thickness_cone)

    # thicker tube than cone
    if thickness_tubular >= thickness_cone:

        thickness_thick_member, thickness_thin_member = thickness_tubular, thickness_cone

        if transition_side == "inside":  # i.e. outer diameter is flush
            diameter_thick_member = radius_tubular * 2
            diameter_thin_member = radius_tubular * 2
        elif transition_side == "outside":
            diameter_thick_member = radius_tubular * 2
            diameter_thin_member = radius_tubular * 2 - 2 * thk_diff


    # thicker cone than tube
    elif thickness_cone > thickness_tubular:

        thickness_thick_member, thickness_thin_member = thickness_cone, thickness_tubular

        if transition_side == "inside":  # i.e. outer diameter is flush
            diameter_thick_member = radius_tubular * 2
            diameter_thin_member = radius_tubular * 2

        elif transition_side == "outside":
            diameter_thick_member = radius_tubular * 2 + 2 * thk_diff
            diameter_thin_member = radius_tubular * 2

    # calculate weld width
    scf_inside_tt, scf_outside_tt = calc_scf_thickness_transition(diameter_thick_member, diameter_thin_member,
                                                                  thickness_thick_member, thickness_thin_member, weld_width,
                                                                  delta_m, delta_0, scf_taper_ratio, scf_weld_type,
                                                                  transition_side)

    return scf_inside_tt, scf_outside_tt


def cone_tt_scf_process(single_results, scf_inside_tt, scf_outside_tt, scf_inclusion):

    cone_tt_single_results = {}
    for k, v in single_results.items():
        cone_tt_single_results[k] = {}
        for loc, cone_scf in v.items():
            if loc.endswith("_in"):
                if scf_inclusion == "yes_multiply":
                    cone_tt_scf = cone_scf * scf_inside_tt
                elif scf_inclusion == "yes_linear_add":
                    cone_tt_scf = cone_scf + (scf_inside_tt - 1.)
                else:
                    cone_tt_scf = cone_scf

            elif loc.endswith("_out"):
                if scf_inclusion == "yes_multiply":
                    cone_tt_scf = cone_scf * scf_outside_tt
                elif scf_inclusion == "yes_linear_add":
                    cone_tt_scf = cone_scf + (scf_outside_tt - 1.)
                else:
                    cone_tt_scf = cone_scf

            else:
                raise ValueError(f"Unexpected SCF key: {loc}")
            cone_tt_single_results[k][f"{loc}_tt"] = cone_tt_scf

    return cone_tt_single_results


