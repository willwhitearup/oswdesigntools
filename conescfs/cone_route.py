import numpy as np
from flask import Flask, request, jsonify, render_template
# local
from conescfs.coneplotter import cone_scfs_plot
from conescfs.scfprocess import cone_scf_single, cone_scf_sweep

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

        numeric_inputs = {
            "radius_tubular": radius_tubular,
            "thickness_tubular": thickness_tubular,
            "thickness_cone": thickness_cone,
            "alpha": alpha
        }

        base_val = numeric_inputs[cone_x_axis_vary]
        x_arr = np.linspace(base_val * 0.5, base_val * 1.5, 21)

        single_results = cone_scf_single(radius_tubular, thickness_tubular, thickness_cone, alpha, junction_type)
        sweep_results = cone_scf_sweep(junction_type, cone_x_axis_vary, x_arr, numeric_inputs)

        # single (one off) SCF results----------------------------------------------------------
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

        # sweep results SCF curves----------------------------------------------------------
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

        # plot the inside SCFs (outside and inside curves)
        conescfs_plot_json_in = cone_scfs_plot(x_arr.tolist(), scf_tube_ins, scf_tube_in_appfs, scf_cone_ins, scf_cone_in_appfs, junction_type, cone_x_axis_vary, "INSIDE")
        conescfs_plot_json_out = cone_scfs_plot(x_arr.tolist(), scf_tube_outs, scf_tube_out_appfs, scf_cone_outs, scf_cone_out_appfs, junction_type, cone_x_axis_vary, "OUTSIDE")

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
                        "conescfs_plot_json_in": conescfs_plot_json_in,
                        "conescfs_plot_json_out": conescfs_plot_json_out
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
