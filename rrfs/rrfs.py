import copy
import math
import numpy as np
from flask import Flask, render_template, flash, jsonify, request, session

from rrfs.requations import axialrrf_x

app = Flask(__name__)


@app.route("/rrfs", methods=["GET", "POST"])
def rrfs_route():

    if request.method == "POST":

        # Joint type
        rrfs_assess = request.form.get("rrfs_assess")

        # Geometry inputs
        beta = request.form.get("rrfs_beta", type=float)
        gamma = request.form.get("rrfs_gamma", type=float)
        tau = request.form.get("rrfs_tau", type=float)
        theta = request.form.get("rrfs_theta", type=float)
        zeta = request.form.get("rrfs_zeta", type=float)

        # Placeholder logic
        print("POST request received")

        print("Joint:", rrfs_assess)
        print("Beta:", beta)
        print("Gamma:", gamma)
        print("Tau:", tau)
        print("Theta:", theta)
        print("Zeta:", zeta)

        x_axial_rrf = axialrrf_x(beta, gamma, tau)

        return render_template(
            "rrfs.html",

            rrfs_assess=rrfs_assess,
            beta=beta,
            gamma=gamma,
            tau=tau,
            theta=theta,
            zeta=zeta,

            message="POST request processed"
        )

    # Default GET request
    return render_template(
        "rrfs.html",

        rrfs_assess="rrfs-x",
        beta=0.8,
        gamma=20,
        tau=0.5,
        theta=45,
        zeta=0.1,

        message="RRFs placeholder page"
    )