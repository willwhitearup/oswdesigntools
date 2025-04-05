from flask import request, render_template, flash
import numpy as np

from routing.core import create_plot, create_joint_plots
from routing.scfs_xty_jts import XTYJointSCFManager

# Define default values
DEFAULT_VALUES_TY = {'D_ty': 1000, 'T_ty': 20, 'd_ty': 500, 't_ty': 15, 'theta_ty': 45, 'L_ty': 5000, 'C_ty': 0.7,
                    # calculation options (strings)
                    'load_type_ty': "balanced_forces", 'x_axis_desc_ty': 'D_ty', 'scf_options_ty': 'scf_only'
                    }

def ty_joint_route():
    plot_data_a_cs_ty, plot_data_a_bs_ty = None, None
    show_table_ty = False
    tyjt_obj = None

    # Use default values if the request method is GET
    if request.method == 'GET':
        # chord inputs and brace inputs
        d1 = DEFAULT_VALUES_TY['D_ty']
        thk1 = DEFAULT_VALUES_TY['T_ty']
        d2 = DEFAULT_VALUES_TY['d_ty']
        thk2 = DEFAULT_VALUES_TY['t_ty']
        theta = DEFAULT_VALUES_TY['theta_ty']
        # other stuff
        L_ty = DEFAULT_VALUES_TY['L_ty']
        C_ty = DEFAULT_VALUES_TY['C_ty']
        load_type = DEFAULT_VALUES_TY['load_type_ty']
        x_axis_desc = DEFAULT_VALUES_TY['x_axis_desc_ty']
        scf_options = DEFAULT_VALUES_TY['scf_options_ty']
    else:
        # chord inputs and brace inputs
        d1 = request.form.get('D_ty', DEFAULT_VALUES_TY['D_ty'])
        thk1 = request.form.get('T_ty', DEFAULT_VALUES_TY['T_ty'])
        d2 = request.form.get('d_ty', DEFAULT_VALUES_TY['d_ty'])
        thk2 = request.form.get('t_ty', DEFAULT_VALUES_TY['t_ty'])
        theta = request.form.get('theta_ty', DEFAULT_VALUES_TY['theta_ty'])
        # other stuff
        L_ty = request.form.get('L_ty', DEFAULT_VALUES_TY['L_ty'])  # chord length and fixity
        C_ty = request.form.get('C_ty', DEFAULT_VALUES_TY['C_ty'])
        load_type = request.form.get('load_type_ty', DEFAULT_VALUES_TY['load_type_ty'])  # update var names
        x_axis_desc = request.form.get('x_axis_desc_ty', DEFAULT_VALUES_TY['x_axis_desc_ty'])
        scf_options = request.form.get('scf_options_ty', DEFAULT_VALUES_TY['scf_options_ty'])  # "scf_only" or "scf_stress_adjusted"

    try:
        show_table_ty = True

        # map the provided Flask app var names (key) to generic names (value) for Python use
        x_axis_desc_mapper = {"D_ty": "D", "T_ty": "T", "d_ty": "d", "t_ty": "t", "theta_ty": "theta"}
        x_axis_mapped = x_axis_desc_mapper[x_axis_desc]

        # store all inputs in a dict and convert to floats
        input_fields = {"D": float(d1), "T": float(thk1), "d": float(d2), "t": float(thk2),
                        "theta": np.radians(float(theta)), "L":float(L_ty), "C": float(C_ty)}

        # get the plots and x joint object
        stress_adjusted = True if scf_options == "scf_stress_adjusted" else False
        # get scfs for the Joint type  # todo make Object a better name
        tyjt_obj = XTYJointSCFManager(x_axis_mapped, input_fields, stress_adjusted, joint_type="ty")
        tyjt_obj.get_joint_scfs(load_type)
        # convert theta angles back to radians for plotting
        tyjt_obj.convert_angles_to_degrees(x_axis_mapped)
        # make the plots
        plot_data_a_cs_ty, plot_data_a_bs_ty = create_joint_plots(tyjt_obj, x_axis_mapped, stress_adjusted, no_braces=1)

    except Exception as e:
        flash(f"An error occurred: {e}")

    # when returning args to the Flask html, the var names must be unique and match the html var names (as global)
    return render_template('ty_joint.html',
                           tyjt_obj=tyjt_obj,
                           plot_data_a_cs_ty=plot_data_a_cs_ty,
                           plot_data_a_bs_ty=plot_data_a_bs_ty,
                           show_table_ty=show_table_ty,
                           D_ty=d1, T_ty=thk1,  # chord
                           d_ty=d2, t_ty=thk2, theta_ty=theta,  # brace A
                           L_ty=L_ty, C_ty=C_ty,
                           load_type_ty=load_type,
                           x_axis_desc_ty=x_axis_desc,
                           scf_options_ty=scf_options)