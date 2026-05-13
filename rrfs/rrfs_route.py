import copy
import math
import numpy as np
from flask import Flask, render_template, flash, jsonify, request, session

from rrfs.plotterrrfs import plotly_fig_plot
from rrfs.requations import axialrrf_x

app = Flask(__name__)


@app.route("/rrfs", methods=["GET", "POST"])
def rrfs_route():

    if request.method == "POST":

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON received'}), 400

        rrfs_assess = data.get("rrfs_assess")

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
        x_kt_lims = {"rrfs_beta": (0.4, 0.85), "rrfs_gamma": (10, 30), "rrfs_tau": (0.35, 0.85), "rrfs_theta": (30, 90)}

        rrf_result = axialrrf_x(beta, gamma, tau)

        x_kt_lims = {"rrfs_beta": (0.4, 0.85), "rrfs_gamma": (10, 30), "rrfs_tau": (0.35, 0.85), "rrfs_theta": (30, 90)}

        # get the RRF result
        rrf_result = axialrrf_x(beta, gamma, tau)

        # plot the range of RRFs based on x-axis variable
        rrf_vals = []
        if x_axis_vary in x_kt_lims:
            start, end = x_kt_lims[x_axis_vary]
            x_vals = np.linspace(start, end, 100).tolist()

            for x in x_vals:
                if x_axis_vary == "rrfs_beta":
                    rrf_vals.append(axialrrf_x(x, gamma, tau))
                elif x_axis_vary == "rrfs_gamma":
                    rrf_vals.append(axialrrf_x(beta, x, tau))
                elif x_axis_vary == "rrfs_tau":
                    rrf_vals.append(axialrrf_x(beta, gamma, x))
                elif x_axis_vary == "rrfs_theta":  # theta in X joints?? todo check
                    rrf_vals.append(axialrrf_x(beta, gamma, tau))  # if theta not in function, adjust later

            # now get the json of the plot # TODO - add in all of the different Axial, IPB & OPB RRFs for the X jnt
            plot_json = plotly_fig_plot(x_vals, x_axis_vary, rrf_vals, rrf_vals)



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