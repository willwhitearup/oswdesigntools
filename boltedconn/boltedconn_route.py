import copy
import math
import numpy as np
from flask import Flask, render_template, flash, jsonify, request, session

from boltedconn.boltdata import BoltLibrary
# local
from boltedconn.boltuls import bolt_connection_uls_strength_check, flange_searching_geometry
from boltedconn.plotterflange import l_flange_plotter
from boltedconn.plotterutils import bolted_connection_utils_plot, bolt_util_plotter_process

app = Flask(__name__)

@app.route('/boltedconn', methods=['GET', 'POST'])
def boltedconn_route():

    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON received'}), 400

        print("****************")
        print(data)

        bolt_sizes = list(BoltLibrary._bolts.keys())
        bolt_sizes.sort(key=lambda x: int(x[1:]))  # removes 'M' prefix
        print(bolt_sizes)
        # ================= DESIGN / ASSESS MODE =================
        bolt_assess = data["bolt_assess"]

        # ================= GEOMETRY =================
        mp_outer_diameter = float(data["mp_outer_diameter"])
        mp_wall_thk = float(data["mp_wall_thk"])

        # flange geometry
        flange_height = float(data["flange_height"])
        flange_length = float(data["flange_length"])
        # bolt_size = data.get("bolt_size")  # used in assess mode
        bolt_size = data.get("bolt_size")

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
            # do the assessment
            flange_obj = bolt_connection_uls_strength_check(mp_outer_diameter, mp_wall_thk,
                                                            bolt_steel_grade, flange_steel_grade, tower_steel_grade, ULS_bending_moment, ULS_axial_force,
                                                            flange_height, flange_length, bolt_size, n_bolts, b_star)

            print(mp_outer_diameter, mp_wall_thk,
                                                            bolt_steel_grade, flange_steel_grade, tower_steel_grade, ULS_bending_moment, ULS_axial_force,
                                                            flange_height, flange_length, bolt_size, n_bolts, b_star)

            print("valid geom, convergence: ", flange_obj.valid_geom, flange_obj.Fu_convergence)
            print("n_bolts: ", n_bolts, flange_obj.n_bolts)
            # get a plot of the flange
            flange_plot_json = l_flange_plotter(flange_obj)

            if not flange_obj.valid_geom or not flange_obj.Fu_convergence:
                bolt_util_plot_json = None
            else:
                # util plot
                bolt_util_plot_json = bolt_util_plotter_process(x_axis_vary, bolt_steel_grade, flange_steel_grade, tower_steel_grade,
                                                                ULS_bending_moment, ULS_axial_force, bolt_size, b_star, mp_outer_diameter, mp_wall_thk,
                                                                flange_obj.n_bolts_max, flange_obj.flange_height, flange_obj.flange_length, flange_obj.n_bolts)

            # convert inf to a 0 for JS rendering
            if np.isinf(flange_obj.util) or np.isnan(flange_obj.util) or flange_obj.util is None:
                flange_obj.util = 0.

            return jsonify({'message': 'success',
                            "bolt_valid_geom_flag": flange_obj.valid_geom,
                            "Fu_convergence_flag": flange_obj.Fu_convergence,
                            "flange_plot_json": flange_plot_json,
                            "bolt_sector_force": flange_obj.bolt_sector_force,
                            "Fu_A":  flange_obj.Fu_A,
                            "Fu_B": flange_obj.Fu_B,
                            "Fu_D": flange_obj.Fu_D,
                            "Fu_E": flange_obj.Fu_E,
                            "Fu_governing": flange_obj.failure_mode_governing,
                            "flange_util": flange_obj.util,
                            "a_b_ratio": flange_obj.a_b_ratio,
                            "n_bolts_tried": n_bolts,  # nbolts tried
                            "n_bolts_ass": flange_obj.n_bolts,  # nbolts assessed
                            "n_bolts_max": flange_obj.n_bolts_max,  # nbolts max
                            "b_star": flange_obj.b_star,
                            "bolt_a": flange_obj.a,
                            "bolt_alpha": flange_obj.alpha,
                            "flange_net_mass": flange_obj.net_mass / 1000,
                            "TobinagaIshiharaFlag": flange_obj.TobinagaIshiharaFlag,
                            "bolt_util_plot_json": bolt_util_plot_json  # results json plot
                            })

        # Design mode i.e. optimisation
        elif bolt_assess == "design":
            incrs = 10
            flange_height_max = 1000
            flange_length_max = 1000

            df_optimal_res = flange_searching_geometry(mp_outer_diameter, mp_wall_thk, bolt_steel_grade, flange_steel_grade,
                                      tower_steel_grade,
                                      ULS_bending_moment, ULS_axial_force, maintain_a_b_ratio_1_25,
                                      bolt_target_util,
                                      flange_height_max,
                                      flange_length_max, incrs
                                      )

            df_optimal_res = df_optimal_res.to_dict(orient='records') if df_optimal_res is not None else []

            return jsonify({'message': 'success',
                            "df_optimal_res": df_optimal_res
                            })



    # GET request
    else:

        bolt_sizes = list(BoltLibrary._bolts.keys())
        bolt_sizes.sort(key=lambda x: int(x[1:]))  # sort numerically by size

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

        return render_template("boltedconn.html", bolt_sizes=bolt_sizes, **default_data)

