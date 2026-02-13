from conescfs.scfs import calc_cone_scfs_sect3, calc_cone_scfs_appf17


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
    """Returns SCFs over ±50% variation of selected variable.
    """

    keys = ["tube_in", "cone_in", "tube_out", "cone_out"]

    results = {"x": x_arr, "sect3": {k: [] for k in keys}, "appf17": {k: [] for k in keys}
               }

    for x in x_arr:
        args = numeric_inputs.copy()
        args[cone_x_axis_vary] = x

        sect3_vals = calc_cone_scfs_sect3(args["radius_tubular"], args["thickness_tubular"], args["thickness_cone"],
            args["alpha"], junction_type
        )

        appf_vals = calc_cone_scfs_appf17(args["radius_tubular"], args["thickness_tubular"], args["thickness_cone"],
            args["alpha"], junction_type
        )

        for key, val in zip(keys, sect3_vals):
            results["sect3"][key].append(val)

        for key, val in zip(keys, appf_vals):
            results["appf17"][key].append(val)

    return results
