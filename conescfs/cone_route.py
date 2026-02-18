import copy

import numpy as np
from flask import Flask, request, jsonify, render_template, url_for
# local
from conescfs.coneplotter import cone_scfs_plot
from conescfs.scfprocess import cone_scf_single, cone_scf_sweep, tt_scf_process, cone_tt_scf_process
from conescfs.thktransitionscfs import calc_scf_thickness_transition

app = Flask(__name__)

@app.route('/conescfs', methods=['GET', 'POST'])
def cone_route():

    if request.method == 'POST':

        # Only parse JSON for POST
        if not request.is_json:
            return jsonify({"error": "Unsupported Media Type, expecting JSON"}), 415

        data = request.get_json()

        # Convert numeric fields automatically
        for k, v in data.items():
            try:
                data[k] = float(v)
            except (TypeError, ValueError):  # Leave non-numeric values unchanged
                pass

        # Extract form values
        # cone geom
        radius_tubular = data.get("radius_tubular")
        thickness_tubular = data.get("thickness_tubular")
        thickness_cone = data.get("thickness_cone")
        alpha = data.get("alpha")
        junction_type = data.get("cone_junction")  # "small" or "large"
        cone_x_axis_vary = data.get("cone_x_axis_vary")
        # thickness transition stuff
        transition_side = data.get("transition_side")
        scf_weld_type = data.get("scf_weld_type")
        weld_width = data.get('weld_width')
        # scf taper ratio only allows a dropdown box of allowable values
        scf_taper_ratio = float(data["scf_taper_ratio"]) if data.get("scf_taper_ratio") in (3., 4., 5., 6.) else None
        delta_m = data.get('delta_m')
        delta_0 = data.get('delta_0')
        scf_inclusion = data.get('scf_inclusion')  # "yes_multiply", "yes_linear_add", "no"
        # print(data)

        # add the images to the site based on inputs--------------------------------------------------------------------
        f_cone_img, f_tt_img = get_cone_and_tt_imgs(junction_type, transition_side, scf_weld_type,
                                                    thickness_transition=abs(thickness_cone-thickness_tubular))

        # cone SCF processing-------------------------------------------------------------------------------------------
        # using the minimum thickness of either the cone and tube, gives governing SCFs at the critical loc i.e.
        # at small diameter junction, the outside SCFs are larger, and at large diameter junction, the inside SCFs are larger
        use_minimum_t = True
        if "yes" in scf_inclusion:
            if use_minimum_t:
                thickness_tubular_override = min(thickness_tubular, thickness_cone)
                thickness_cone_override = min(thickness_tubular, thickness_cone)
            else:
                thickness_tubular_override = max(thickness_tubular, thickness_cone)
                thickness_cone_override = max(thickness_tubular, thickness_cone)
        else:
            thickness_tubular_override, thickness_cone_override = thickness_tubular, thickness_cone

        cone_scf_numeric_fields = {"radius_tubular": radius_tubular, "thickness_tubular": thickness_tubular_override,
            "thickness_cone": thickness_cone_override, "alpha": alpha}

        base_val = cone_scf_numeric_fields[cone_x_axis_vary]
        x_arr = np.linspace(base_val * 0.5, base_val * 1.5, 21)  # +/- 50% of the nominal value

        single_results = cone_scf_single(radius_tubular, thickness_tubular_override, thickness_cone_override, alpha, junction_type)
        sweep_results = cone_scf_sweep(junction_type, cone_x_axis_vary, x_arr, cone_scf_numeric_fields)

        # single (one off) SCF results---------------------
        # --- Section 3 ---
        scf_tube_in = single_results["sect3"]["tube_in"]
        scf_cone_in = single_results["sect3"]["cone_in"]
        scf_tube_out = single_results["sect3"]["tube_out"]
        scf_cone_out = single_results["sect3"]["cone_out"]

        # --- App F ---
        scf_tube_in_appf = single_results["appf17"]["tube_in"]
        scf_cone_in_appf = single_results["appf17"]["cone_in"]
        scf_tube_out_appf = single_results["appf17"]["tube_out"]
        scf_cone_out_appf = single_results["appf17"]["cone_out"]

        # sweep results SCF curves-----------------------
        # --- Section 3 curves ---
        scf_tube_ins = sweep_results["sect3"]["tube_in"]
        scf_cone_ins = sweep_results["sect3"]["cone_in"]
        scf_tube_outs = sweep_results["sect3"]["tube_out"]
        scf_cone_outs = sweep_results["sect3"]["cone_out"]

        # --- App F curves ---
        scf_tube_in_appfs = sweep_results["appf17"]["tube_in"]
        scf_cone_in_appfs = sweep_results["appf17"]["cone_in"]
        scf_tube_out_appfs = sweep_results["appf17"]["tube_out"]
        scf_cone_out_appfs = sweep_results["appf17"]["cone_out"]

        # thickness transition SCF processing--------------------------------------------------------------------------
        # scfs inside and outside
        scf_inside_tt, scf_outside_tt = tt_scf_process(thickness_tubular, thickness_cone, radius_tubular,
                                                       transition_side, weld_width, delta_m, delta_0, scf_taper_ratio,
                                                       scf_weld_type)

        # Cone and thickness transition SCFs----------------------------------------------------------------------------
        cone_tt_single_results = cone_tt_scf_process(single_results, scf_inside_tt, scf_outside_tt, scf_inclusion)
        scf_tube_in_tt = cone_tt_single_results["sect3"]["tube_in_tt"]
        scf_cone_in_tt = cone_tt_single_results["sect3"]["cone_in_tt"]
        scf_tube_out_tt = cone_tt_single_results["sect3"]["tube_out_tt"]
        scf_cone_out_tt = cone_tt_single_results["sect3"]["cone_out_tt"]

        # --- App F ---
        scf_tube_in_appf_tt = cone_tt_single_results["appf17"]["tube_in_tt"]
        scf_cone_in_appf_tt = cone_tt_single_results["appf17"]["cone_in_tt"]
        scf_tube_out_appf_tt = cone_tt_single_results["appf17"]["tube_out_tt"]
        scf_cone_out_appf_tt = cone_tt_single_results["appf17"]["cone_out_tt"]

        # plot the inside SCFs (outside and inside curves)---------------------------------------------------------------
        conescfs_plot_json_in = cone_scfs_plot(x_arr.tolist(), scf_tube_ins, scf_tube_in_appfs, scf_cone_ins, scf_cone_in_appfs, junction_type, cone_x_axis_vary, "INSIDE")
        conescfs_plot_json_out = cone_scfs_plot(x_arr.tolist(), scf_tube_outs, scf_tube_out_appfs, scf_cone_outs, scf_cone_out_appfs, junction_type, cone_x_axis_vary, "OUTSIDE")

        # scf messages re. implementation approach
        scf_msgs = get_scf_implementation_msgs(scf_inclusion, thickness_tubular_override)


        # Return results as JSON
        return jsonify({"status": "success",
                        # images
                        "cone_scf_img": url_for("static", filename=f_cone_img),
                        "tt_scf_img": url_for("static", filename=f_tt_img),
                        "cone_junction": junction_type,
                        "scf_inclusion": scf_inclusion,
                        # Cone SCFs=======================================
                        # DNV section 3 SCFs
                        "scf_tube_in": scf_tube_in,
                        "scf_cone_in": scf_cone_in,
                        "scf_tube_out": scf_tube_out,
                        "scf_cone_out": scf_cone_out,
                        # app F SCFs
                        "scf_tube_in_appf": scf_tube_in_appf,
                        "scf_cone_in_appf": scf_cone_in_appf,
                        "scf_tube_out_appf": scf_tube_out_appf,
                        "scf_cone_out_appf": scf_cone_out_appf,
                        # thickness transition SCFs===========================
                        "scf_inside_tt":  scf_inside_tt,
                        "scf_outside_tt": scf_outside_tt,
                        # Cone SCFs including thickness transition SCFS
                        # ===================================================
                        # DNV section 3 SCFs
                        "scf_tube_in_tt": scf_tube_in_tt,
                        "scf_cone_in_tt": scf_cone_in_tt,
                        "scf_tube_out_tt": scf_tube_out_tt,
                        "scf_cone_out_tt": scf_cone_out_tt,
                        # app F SCFs
                        "scf_tube_in_appf_tt": scf_tube_in_appf_tt,
                        "scf_cone_in_appf_tt": scf_cone_in_appf_tt,
                        "scf_tube_out_appf_tt": scf_tube_out_appf_tt,
                        "scf_cone_out_appf_tt": scf_cone_out_appf_tt,
                        # plot============================================
                        "conescfs_plot_json_in": conescfs_plot_json_in,
                        "conescfs_plot_json_out": conescfs_plot_json_out,
                        "scf_msgs": scf_msgs
                        })


    # GET request
    else:
        # Provide default values to render form
        default_data = {
            "cone_junction": "large",
            "radius_tubular": 850,
            "thickness_tubular": 85,
            "thickness_cone": 37,
            "alpha": 1.72,
            'weld_width': 75,
            'scf_taper_ratio': 4,
            'delta_m': 4,
            'delta_0': 1.85,
            "transition_side": "outside",
            # images
            "cone_scf_img": url_for("static", filename="conescfs_tts/cone_large_junction.png"),
            "tt_scf_img": url_for("static", filename="conescfs_tts/fig3_12a_and_12b.png"),
        }

        return render_template("conescfs.html", **default_data)


def get_cone_and_tt_imgs(junction_type, transition_side, scf_weld_type, thickness_transition):

    # get correct cone image
    if junction_type == "small":
        f_cone_img = "conescfs_tts/cone_small_junction.png"
    else:
        f_cone_img = "conescfs_tts/cone_large_junction.png"

    # now thkness transition
    if np.isclose(thickness_transition, 0.):
        f_tt_img = "conescfs_tts/fig3_8.png"
    elif transition_side == "outside" and scf_weld_type == "single_sided":
        f_tt_img = "conescfs_tts/fig3_12a_and_12b.png"
    elif transition_side == "inside" and scf_weld_type == "single_sided":
        f_tt_img = "conescfs_tts/fig3_12c_and_12d.png"
    elif transition_side == "outside" and scf_weld_type == "double_sided":
        f_tt_img = "conescfs_tts/fig3_11_b.png"
    elif transition_side == "inside" and scf_weld_type == "double_sided":
        f_tt_img = "conescfs_tts/fig3_11_b_edited_tt_on_inside.png"  # this is a monopile usually :-)
    else:
        f_tt_img = "conescfs_tts/tt_todo.png"  # what image for this??!?

    return f_cone_img, f_tt_img

def get_scf_implementation_msgs(scf_inclusion, thickness_tubular_override):
    scf_msgs = {}
    if scf_inclusion == "yes_multiply":
        scf_msgs["1"] = "Cone SCFs and thickness transition SCFs are multiplied."
    elif scf_inclusion == "yes_linear_add":
        scf_msgs["1"] = "Cone SCFs and thickness transition SCFs are linearly summed (e.g. 1.2 + 1.4 = 1.6)."
    else:
        scf_msgs["1"] = "Cone SCFs are not combined with thickness transition SCFs."

    if "yes" in scf_inclusion:
        scf_msgs["2"] = (
            f"Cone SCFs are calculated assuming a single thickness only; the minimum thickness of cone and tubular thicknesses ({thickness_tubular_override}) is used. "
            f"This approach isolates the SCF to be from the bending induced by the cone angle only i.e. SCF from bending induced from centre line eccentricity between adjacent sections is NOT considered.")
        scf_msgs["3"] = (
            "Thickness transition SCFs consider both the geometric effect (sharp corner between 2 plates of different thickness) and the SCF from "
            "bending induced from centre line eccentricity between adjacent sections.")
        scf_msgs["4"] = ("This approach is used to avoid double counting the SCF induced from bending due to the "
                         "centre line eccentricity i.e. this effect can be removed from the Cone SCF calculation but not be from the thickness transition SCF calculation.")

    return scf_msgs
