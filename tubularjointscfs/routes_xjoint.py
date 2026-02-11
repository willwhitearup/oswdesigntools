from flask import request, render_template, flash
import numpy as np

from tubularjointscfs.core import create_joint_plots
from tubularjointscfs.scfs_xty_jts import XTYJointSCFManager

# Define default values
DEFAULT_VALUES_X = {'Dx': 1000, 'Tx': 20, 'dax': 500, 'tax': 15, 'thetax': 45, 'Lx': 5000, 'Cx': 0.7,
                    # calculation options (strings)
                    'load_type_x': "balanced_forces", 'x_axis_desc_x': 'Dx', 'scf_options_x': 'scf_only'
                    }


def x_joint_route():
    plot_data_a_cs_x, plot_data_a_bs_x = None, None
    show_table_x = False
    xjt_obj = None

    # Use default values if the request method is GET
    if request.method == 'GET':
        # chord inputs and brace inputs
        d1 = DEFAULT_VALUES_X['Dx']
        thk1 = DEFAULT_VALUES_X['Tx']
        d2 = DEFAULT_VALUES_X['dax']
        thk2 = DEFAULT_VALUES_X['tax']
        theta = DEFAULT_VALUES_X['thetax']
        # other stuff
        L = DEFAULT_VALUES_X['Lx']
        C = DEFAULT_VALUES_X['Cx']
        load_type = DEFAULT_VALUES_X['load_type_x']
        x_axis_desc = DEFAULT_VALUES_X['x_axis_desc_x']
        scf_options = DEFAULT_VALUES_X['scf_options_x']
    else:
        # chord inputs and brace inputs
        d1 = request.form.get('Dx', DEFAULT_VALUES_X['Dx'])
        thk1 = request.form.get('Tx', DEFAULT_VALUES_X['Tx'])
        d2 = request.form.get('dax', DEFAULT_VALUES_X['dax'])
        thk2 = request.form.get('tax', DEFAULT_VALUES_X['tax'])
        theta = request.form.get('thetax', DEFAULT_VALUES_X['thetax'])
        # other stuff
        L = request.form.get('Lx', DEFAULT_VALUES_X['Lx'])  # chord length and fixity
        C = request.form.get('Cx', DEFAULT_VALUES_X['Cx'])
        load_type = request.form.get('load_type_x', DEFAULT_VALUES_X['load_type_x'])  # update var names
        x_axis_desc = request.form.get('x_axis_desc_x', DEFAULT_VALUES_X['x_axis_desc_x'])
        scf_options = request.form.get('scf_options_x', DEFAULT_VALUES_X['scf_options_x'])  # "scf_only" or "scf_stress_adjusted"

    try:
        show_table_x = True

        # map the provided Flask app var names (key) to generic names (value) for Python use
        x_axis_desc_mapper = {"Dx": "D", "Tx": "T", "dax": "d", "tax": "t", "thetax": "theta"}
        x_axis_mapped = x_axis_desc_mapper[x_axis_desc]

        # store all inputs in a dict and convert to floats
        input_fields = {"D": float(d1), "T": float(thk1), "d": float(d2), "t": float(thk2),
                        "theta": np.radians(float(theta)), "L":float(L), "C": float(C)}

        # get the plots and x joint object
        stress_adjusted = True if scf_options == "scf_stress_adjusted" else False
        # get scfs for the Joint type  # todo make Object a better name
        xjt_obj = XTYJointSCFManager(x_axis_mapped, input_fields, stress_adjusted, joint_type="x")
        xjt_obj.get_joint_scfs(load_type)
        # convert theta angles back to radians for plotting
        xjt_obj.convert_angles_to_degrees(x_axis_mapped)
        # make the plots
        plot_data_a_cs_x, plot_data_a_bs_x = create_joint_plots(xjt_obj, x_axis_mapped, stress_adjusted, no_braces=1)

    except Exception as e:
        flash(f"An error occurred: {e}")

    # when returning args to the Flask html, the var names must be unique and match the html var names (as global)
    return render_template('x_joint.html',
                           xjt_obj=xjt_obj,
                           plot_data_a_cs_x=plot_data_a_cs_x,
                           plot_data_a_bs_x=plot_data_a_bs_x,
                           show_table_x=show_table_x,
                           Dx=d1, Tx=thk1,  # chord
                           dax=d2, tax=thk2, thetax=theta,  # brace A
                           Lx=L, Cx=C,
                           load_type_x=load_type,
                           x_axis_desc_x=x_axis_desc,
                           scf_options_x=scf_options)