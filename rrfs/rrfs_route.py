import copy
import math
import numpy as np
from flask import Flask, render_template, flash, jsonify, request, session

from rrfs.plotterrrfs import plotly_fig_plot
from rrfs.requations import axialrrf_x, ipbrrf_x, opbrrf_x

app = Flask(__name__)

@app.route("/rrfs", methods=["GET", "POST"])
def rrfs_route():

    if request.method == "POST":

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON received'}), 400

        rrfs_assess = data.get("rrfs_assess")  # gets the Joint type (X, YT or K)

        beta = float(data.get("rrfs_beta"))
        gamma = float(data.get("rrfs_gamma"))
        tau = float(data.get("rrfs_tau"))
        theta = float(data.get("rrfs_theta"))
        zeta = float(data.get("rrfs_zeta"))
        # plot x-axis variation
        x_axis_vary = data.get("rrfs_x_axis_vary")

        print("Joint:", rrfs_assess)
        print("Beta:", beta)
        print("Gamma:", gamma)
        print("x_axis_vary:", x_axis_vary)

        # X JOINT =======================================================================
        rrf_x_jt_axial_result, rrf_x_jt_ipb_result, rrf_x_jt_opb_result, x_jt_plot_json = get_x_jt_RRFs_data(beta, gamma, tau, theta, x_axis_vary)

        # todo KT and Y JOINTS



        return jsonify({
            "success": True
        })

    return render_template(
        "rrfs.html",

        rrfs_assess="rrfs-x",

        beta=0.8,
        gamma=20,
        tau=0.5,
        theta=45,
        zeta=0.1,

        x_axis_vary="beta"
    )


def get_x_jt_RRFs_data(beta: float,
                       gamma: float,
                       tau: float,
                       theta: float,
                       x_axis_vary: str):

    # Single-point results
    rrf_x_jt_axial_result = axialrrf_x(beta, gamma, tau)
    rrf_x_jt_ipb_result = ipbrrf_x(beta, gamma, tau)
    rrf_x_jt_opb_result = opbrrf_x(beta, gamma, tau)

    x_jt_lims = {"rrfs_beta": (0.4, 0.85), "rrfs_gamma": (10, 30), "rrfs_tau": (0.35, 0.85), "rrfs_theta": (30, 90)
                 }

    if x_axis_vary in x_jt_lims:
        start, end = x_jt_lims[x_axis_vary]
        x_vals = np.linspace(start, end, 100).tolist()
        # Store RRF results
        rrf_x_jt_axial_results, rrf_x_jt_ipb_results, rrf_x_jt_opb_results = [], [], []

        for x in x_vals:
            # Current parameter set
            params = {"rrfs_beta": beta, "rrfs_gamma": gamma, "rrfs_tau": tau, "rrfs_theta": theta}
            # Update the varying parameter
            params[x_axis_vary] = x
            # Short aliases
            beta_i = params["rrfs_beta"]
            gamma_i = params["rrfs_gamma"]
            tau_i = params["rrfs_tau"]
            # Calculate RRFs
            rrf_x_jt_axial_results.append(axialrrf_x(beta_i, gamma_i, tau_i))
            rrf_x_jt_ipb_results.append(ipbrrf_x(beta_i, gamma_i, tau_i))
            rrf_x_jt_opb_results.append(opbrrf_x(beta_i, gamma_i, tau_i))

        # Plot curves
        x_jt_plot_curves = [
            {
                "xvals": x_vals,
                "yvals": rrf_x_jt_axial_results,
                "label": "Axial RRF"
            },
            {
                "xvals": x_vals,
                "yvals": rrf_x_jt_ipb_results,
                "label": "IPB RRF"
            },
            {
                "xvals": x_vals,
                "yvals": rrf_x_jt_opb_results,
                "label": "OPB RRF"
            }
        ]

        # Generate plot
        x_jt_plot_json = plotly_fig_plot(plot_title="X joint", xaxis_label=x_axis_vary, curves=x_jt_plot_curves)

    return rrf_x_jt_axial_result, rrf_x_jt_ipb_result, rrf_x_jt_opb_result, x_jt_plot_json