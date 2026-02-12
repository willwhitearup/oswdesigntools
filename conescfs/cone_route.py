import copy

import numpy as np
from flask import Flask, request, jsonify, render_template

from conescfs.coneplotter import cone_scfs_plot
from conescfs.scfs import calc_cone_scfs_sect3, calc_cone_scfs_appf17

app = Flask(__name__)

@app.route('/conescfs', methods=['GET', 'POST'])
def cone_route():

    if request.method == 'POST':

        # Only parse JSON for POST
        if not request.is_json:
            return jsonify({"error": "Unsupported Media Type, expecting JSON"}), 415

        data = request.get_json()

        # Convert numeric fields automatically
        numeric_fields = ["radius_tubular", "thickness_tubular", "thickness_cone", "alpha"]
        for field in numeric_fields:
            if field in data and data[field] != "":
                data[field] = float(data[field])

        print("Converted data:", data)

        # Extract values
        radius_tubular = data.get("radius_tubular")
        thickness_tubular = data.get("thickness_tubular")
        thickness_cone = data.get("thickness_cone")
        alpha = data.get("alpha")
        junction_type = data.get("cone_junction")  # "small" or "large"
        cone_x_axis_vary = data.get("cone_x_axis_vary")

        # Cone SCFs DNV
        scf_tube_in, scf_cone_in, scf_tube_out, scf_cone_out = calc_cone_scfs_sect3(radius_tubular, thickness_tubular, thickness_cone, alpha, junction_type)
        scf_tube_in_appf, scf_cone_in_appf, scf_tube_out_appf, scf_cone_out_appf = calc_cone_scfs_appf17(radius_tubular, thickness_tubular, thickness_cone, alpha, junction_type)

        print(scf_tube_in, scf_cone_in, scf_tube_out, scf_cone_out)
        print(scf_tube_in_appf, scf_cone_in_appf, scf_tube_out_appf, scf_cone_out_appf)
        print("X axis vary", cone_x_axis_vary)

        # Map all numeric inputs into a dict
        numeric_inputs = {
            "radius_tubular": radius_tubular,
            "thickness_tubular": thickness_tubular,
            "thickness_cone": thickness_cone,
            "alpha": alpha
        }

        # Figure out which one is varying
        x_axis_vary = cone_x_axis_vary  # e.g., 'radius_tubular'

        # Base value of the variable to vary
        base_val = numeric_inputs[x_axis_vary]

        # Create array for X-axis: +/- 20% around base
        x_arr = np.linspace(base_val * 0.8, base_val * 1.2, 10)

        # Initialize results
        scf_tube_ins, scf_cone_ins, scf_tube_outs, scf_cone_outs = [], [], [], []
        scf_tube_in_appfs, scf_cone_in_appfs, scf_tube_out_appfs, scf_cone_out_appfs = [], [], [], []

        # Loop dynamically, replacing only the chosen variable
        for x in x_arr:
            # Prepare arguments for calc function
            args = numeric_inputs.copy()
            args[x_axis_vary] = x  # override the varying one

            scf_tube_in, scf_cone_in, scf_tube_out, scf_cone_out = calc_cone_scfs_sect3(args["radius_tubular"], args["thickness_tubular"],
                                                                                        args["thickness_cone"], args["alpha"],junction_type)


            scf_tube_in_appf, scf_cone_in_appf, scf_tube_out_appf, scf_cone_out_appf = calc_cone_scfs_appf17(args["radius_tubular"], args["thickness_tubular"],
                                                                                        args["thickness_cone"], args["alpha"],junction_type)

            # store all SCFs
            scf_tube_ins.append(scf_tube_in)
            scf_cone_ins.append(scf_cone_in)
            scf_tube_outs.append(scf_tube_out)
            scf_cone_outs.append(scf_cone_out)

            scf_tube_in_appfs.append(scf_tube_in_appf)
            scf_cone_in_appfs.append(scf_cone_in_appf)
            scf_tube_out_appfs.append(scf_tube_out_appf)
            scf_cone_out_appfs.append(scf_cone_out_appf)

        # plot the inside SCFs
        conescfs_plot_json = cone_scfs_plot(x_arr.tolist(), scf_tube_ins, scf_tube_in_appfs, scf_cone_ins, scf_cone_in_appfs, junction_type, x_axis_vary, "INSIDE")
        # plot the outside SCFS
        # todo

        # Return results as JSON
        return jsonify({"status": "success",
                        "cone_junction": junction_type,
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
                        # plot
                        "conescfs_plot_json": conescfs_plot_json
        })


    # GET request
    else:
        # Provide default values to render form
        default_data = {
            "radius_tubular": 850,
            "thickness_tubular": 85,
            "thickness_cone": 37,
            "alpha": 1.72,
            "cone_junction": "large"
        }

        return render_template("conescfs.html", **default_data)
