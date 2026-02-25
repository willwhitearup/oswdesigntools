import copy
import math
import numpy as np
from flask import Flask, render_template, flash, jsonify, request, session
# local
from boltedconn.boltuls import bolt_connection_uls_strength_check
from boltedconn.plotterflange import l_flange_plotter
from boltedconn.plotterutils import bolted_connection_utils_plot


app = Flask(__name__)

@app.route('/boltedconn', methods=['GET', 'POST'])
def boltedconn_route():

    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON received'}), 400

        print("****************")
        print(data)

        # ================= DESIGN / ASSESS MODE =================
        bolt_assess = data["bolt_assess"]

        # ================= GEOMETRY =================
        mp_outer_diameter = float(data["mp_outer_diameter"])
        mp_wall_thk = float(data["mp_wall_thk"])

        # flange geometry
        flange_height = float(data["flange_height"])
        flange_length = float(data["flange_length"])
        bolt_size = data.get("bolt_size")  # used in assess mode
        # Optional values
        n_bolts = data.get("n_bolts")
        n_bolts = int(n_bolts) if n_bolts else None
        b_star = data.get("b_star")
        b_star = float(b_star) if b_star else None

        # ================= MATERIALS =================
        bolt_steel_grade = data["bolt_steel_grade"]
        flange_steel_grade = data["flange_steel_grade"]
        tower_steel_grade = data["tower_steel_grade"]

        # ================= LOADING =================
        ULS_axial_force = float(data["ULS_axial_force"])  # N
        ULS_bending_moment = float(data["ULS_bending_moment"])  # Nmm

        # ================= OPTIMISATION INPUTS =================
        opt_bolt_size = data.get("opt_bolt_size")  # used in design mode
        bolt_target_util = float(data.get("bolt_target_util", 0.95))
        maintain_a_b_ratio_1_25 = bool(data.get("maintain_a_b_ratio_1_25", False))

        # plot options
        x_axis_vary = data.get("x_axis_vary_bolt")

        if bolt_assess == "assess":
            # Build kwargs dynamically
            numeric_fields = {
                "flange_height": flange_height,
                "flange_length": flange_length,
                "n_bolts": n_bolts
            }

            # do the assessment
            flange_obj = bolt_connection_uls_strength_check(mp_outer_diameter, mp_wall_thk,
                                                      bolt_steel_grade, flange_steel_grade, tower_steel_grade,
                                                      ULS_bending_moment, ULS_axial_force,
                                                      flange_height, flange_length, bolt_size, n_bolts, b_star)

            # flange outline diagram plot
            flange_plot_json = l_flange_plotter(flange_obj)
            # util plot
            bolt_util_plot_json = bolt_util_plotter_process(numeric_fields, x_axis_vary, bolt_steel_grade, flange_steel_grade, tower_steel_grade,
                                                            ULS_bending_moment, ULS_axial_force, bolt_size, b_star, mp_outer_diameter, mp_wall_thk,
                                                            flange_obj.n_bolts_max)

        # Design mode i.e. optimisation
        elif bolt_assess == "design":
            a = 1  # todo

        return jsonify({'message': 'success',
                        "flange_plot_json": flange_plot_json,
                        "bolt_sector_force": flange_obj.bolt_sector_force,
                        "Fu_A":  flange_obj.Fu_A,
                        "Fu_B": flange_obj.Fu_B,
                        "Fu_D": flange_obj.Fu_D,
                        "Fu_E": flange_obj.Fu_E,
                        "Fu_governing": flange_obj.failure_mode_governing,
                        "flange_util": flange_obj.util,
                        "a_b_ratio": flange_obj.a_b_ratio,
                        "n_bolts_ass": flange_obj.n_bolts,  # nbolts assessed
                        "TobinagaIshiharaFlag": flange_obj.TobinagaIshiharaFlag,
                        "bolt_util_plot_json": bolt_util_plot_json  # results json plot
                        })



    # GET request
    else:
        # Provide default values to render form
        default_data = {
            "mp_outer_diameter": 7500.,
            "mp_wall_thk": 100.,
            "flange_height": 200.,
            "flange_length": 400.,
            "n_bolts": 130,
            "b_star": 210.,
            "ULS_axial_force": 17.305e6,  # N above the flange
            "ULS_bending_moment": 557e9,  # Nmm
            "bolt_target_util": 0.95,
            "maintain_a_b_ratio_1_25": True,
            "bolt_size": "M90"
        }

        return render_template("boltedconn.html", **default_data)



def bolt_util_plotter_process(numeric_fields, x_axis_vary, bolt_steel_grade, flange_steel_grade, tower_steel_grade,
                              ULS_bending_moment, ULS_axial_force, bolt_size, b_star, mp_outer_diameter, mp_wall_thk, n_bolts_max):
    """plot the x varying input vs FuA, FuB etc.

    todo: special plot if nBolts varies as need to cap the max no. of bolts on x-axis
    """
    maintain_a_b_ratio_1_25 = False
    base_val = numeric_fields[x_axis_vary]
    xlim = 0.5
    if x_axis_vary == "n_bolts":
        num_points = n_bolts_max - int(base_val * (1 - xlim)) + 1
        x_arr = np.linspace(int(base_val * (1 - xlim)), n_bolts_max, num_points)  # +/- 50% of nominal
    else:
        x_arr = np.linspace(base_val * (1 - xlim), base_val * (1 + xlim), 21)  # +/- 50% of nominal

    Fu_As, Fu_Bs, Fu_Ds, Fu_Es = [], [], [], []
    F_actuals = []
    for x in x_arr:
        kwargs = copy.deepcopy(numeric_fields)
        # Overwrite the varying parameter
        kwargs[x_axis_vary] = x

        # call function with numeric fields unpacked, other args explicitly
        flange_obj = bolt_connection_uls_strength_check(mp_outer_diameter, mp_wall_thk,
                                                             bolt_steel_grade, flange_steel_grade, tower_steel_grade,
                                                             ULS_bending_moment, ULS_axial_force,
                                                             kwargs["flange_height"],
                                                             kwargs["flange_length"],
                                                             bolt_size, kwargs["n_bolts"], b_star)

        if flange_obj.util is None or math.isinf(flange_obj.util):
            Fu_A, Fu_B, Fu_D, Fu_E = 0., 0., 0., 0.
        else:
            Fu_A, Fu_B, Fu_D, Fu_E = flange_obj.Fu_A, flange_obj.Fu_B, flange_obj.Fu_D, flange_obj.Fu_E

        Fu_As.append(Fu_A)
        Fu_Bs.append(Fu_B)
        Fu_Ds.append(Fu_D)
        Fu_Es.append(Fu_E)
        F_actuals.append(flange_obj.bolt_sector_force)

    bolt_util_plot_json = bolted_connection_utils_plot(x_arr.tolist(), x_axis_vary, Fu_As, Fu_Bs, Fu_Ds, Fu_Es,
                                                       F_actuals)

    return bolt_util_plot_json