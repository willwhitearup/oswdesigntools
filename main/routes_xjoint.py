from flask import request, render_template, flash
import numpy as np

from main.core import create_plot
from main.scfs_xjts import XJointSCFManager

# Define default values
DEFAULT_VALUES_X = {'Dx': 1000, 'Tx': 20, 'dax': 500, 'tax': 15, 'thetax': 45, 'Lx': 5000, 'Cx': 0.7,
                    # calculation options (strings)
    'load_type_x': "balanced_forces", 'x_axis_desc_x': 'Dx', 'scf_options_x': 'scf_only'
                    }


def x_joint_route():
    plot_data_a_csx, plot_data_a_bsx = None, None
    show_table = False
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
        load_type_x = DEFAULT_VALUES_X['load_type_x']
        x_axis_desc_x = DEFAULT_VALUES_X['x_axis_desc_x']
        scf_options_x = DEFAULT_VALUES_X['scf_options_x']
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
        load_type_x = request.form.get('load_type_x', DEFAULT_VALUES_X['load_type_x'])  # update var names
        x_axis_desc_x = request.form.get('x_axis_desc_x', DEFAULT_VALUES_X['x_axis_desc_x'])  # todo align var names
        scf_options_x = request.form.get('scf_options_x', DEFAULT_VALUES_X['scf_options_x'])  # "scf_only" or "scf_stress_adjusted"

    try:
        show_table = True

        # convert angles to radians
        theta_radians = np.radians(float(theta))

        # store all inputs in a dict and convert to floats
        input_fields = {"Dx": float(d1), "Tx": float(thk1), "dax": float(d2), "tax": float(thk2),
                        "thetax": theta_radians, "Lx":float(L), "Cx": float(C)}

        stress_adjusted = True if scf_options_x == "scf_stress_adjusted" else False

        xjt_obj = XJointSCFManager(x_axis_desc_x, input_fields, stress_adjusted)
        xjt_obj.get_joint_scfs(load_type_x)

        # brace A plots
        # chord side
        plot_data_a_csx = create_plot(xjt_obj.params, {("axial crown", "red", "-"): xjt_obj.scf_a_axial_chord_crowns,
                                                      ("axial saddle", "orange", "-"): xjt_obj.scf_a_axial_chord_saddles,
        #                                               ("IPB crown", "blue", "-"): xjt_obj.scf_ipb_a_chord_crowns,
        #                                               ("OPB saddle", "green", "-"): xjt_obj.scf_opb_a_chord_saddles,
        #                                               ("axial crown stress_adjusted", "red", "--"): xjt_obj.scf_a_axial_chord_crowns_adj,
        #                                               ("axial saddle stress_adjusted", "orange", "--"): xjt_obj.scf_a_axial_chord_saddles_adj,
        #                                               ("IPB crown stress_adjusted", "blue", "--"): xjt_obj.scf_ipb_a_chord_crowns_adj,
        #                                               ("OPB saddle stress_adjusted", "green", "--"): xjt_obj.scf_opb_a_chord_saddles_adj
                                                       },
                                      x_axis_desc_x, stress_adjusted=stress_adjusted)  # chordside
        #
        # brace side
        plot_data_a_bsx = create_plot(xjt_obj.params, {("axial crown", "red", "-"): xjt_obj.scf_a_axial_brace_crowns,
                                                      ("axial saddle", "orange", "-"): xjt_obj.scf_a_axial_brace_saddles,
        #                                               ("IPB crown", "blue", "-"): xjt_obj.scf_ipb_a_brace_crowns,
        #                                               ("OPB saddle", "green", "-"): xjt_obj.scf_opb_a_brace_saddles,
        #                                               ("axial crown stress_adjusted", "red", "--"): xjt_obj.scf_a_axial_brace_crowns_adj,
        #                                               ("axial saddle stress_adjusted", "orange", "--"): xjt_obj.scf_a_axial_brace_saddles_adj,
        #                                               ("IPB crown stress_adjusted", "blue", "--"): xjt_obj.scf_ipb_a_brace_crowns_adj,
        #                                               ("OPB saddle stress_adjusted", "green", "--"): xjt_obj.scf_opb_a_brace_saddles_adj
                                                       },
                                      x_axis_desc_x, stress_adjusted=stress_adjusted)  # braceside




    except Exception as e:
        flash(f"An error occurred: {e}")


    return render_template('x_joint.html',
                           xjt_obj=xjt_obj,
                           plot_data_a_csx=plot_data_a_csx,
                           plot_data_a_bsx=plot_data_a_bsx,
                           show_table=show_table,
                           Dx=d1, Tx=thk1,  # chord
                           dax=d2, tax=thk2, thetax=theta, # brace A
                           Lx=L, Cx=C,
                           load_type_x=load_type_x,
                           x_axis_desc_x=x_axis_desc_x,
                           scf_options_x=scf_options_x)