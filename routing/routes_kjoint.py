from flask import request, render_template, flash
from routing.core import create_joint_plots
import numpy as np
from routing.scfs_kt_jts import KTJointSCFManager, ChordPropertyManager

# Define default values
DEFAULT_VALUES_K = {'D': 1000, 'T': 20, 'dA': 500, 'tA': 15, 'thetaA': 45,
                    'dB': 500, 'tB': 15, 'thetaB': 45, 'g_ab': 75, 'L': 5000, 'C': 0.7,
                    # calculation options (strings)
                    'load_type': 'balanced_axial_unbalanced_moment', 'x_axis_desc': 'D', 'scf_options': 'scf_only'
                    }

def k_joint_route():
    # plot data for brace a
    plot_data_a_cs, plot_data_a_bs = None, None
    # plot data for brace b
    plot_data_b_cs,plot_data_b_bs = None, None
    show_table = False
    kjt_obj = None
    chord_props_obj = None  # define a class for the joint calculated properties

    # Use default values if the request method is GET
    if request.method == 'GET':
        d1 = DEFAULT_VALUES_K['D']
        thk1 = DEFAULT_VALUES_K['T']
        d2_a = DEFAULT_VALUES_K['dA']
        thk2_a = DEFAULT_VALUES_K['tA']
        theta_a = DEFAULT_VALUES_K['thetaA']
        d2_b = DEFAULT_VALUES_K['dB']
        thk2_b = DEFAULT_VALUES_K['tB']
        theta_b = DEFAULT_VALUES_K['thetaB']
        g_ab = DEFAULT_VALUES_K['g_ab']
        L = DEFAULT_VALUES_K['L']
        C = DEFAULT_VALUES_K['C']
        load_type = DEFAULT_VALUES_K['load_type']
        x_axis_desc = DEFAULT_VALUES_K['x_axis_desc']
        scf_options = DEFAULT_VALUES_K['scf_options']
    else:
        # chord inputs
        d1 = request.form.get('D', DEFAULT_VALUES_K['D'])
        thk1 = request.form.get('T', DEFAULT_VALUES_K['T'])
        # brace A inputs
        d2_a = request.form.get('dA', DEFAULT_VALUES_K['dA'])
        thk2_a = request.form.get('tA', DEFAULT_VALUES_K['tA'])
        theta_a = request.form.get('thetaA', DEFAULT_VALUES_K['thetaA'])
        # brace B inputs
        d2_b = request.form.get('dB', DEFAULT_VALUES_K['dB'])
        thk2_b = request.form.get('tB', DEFAULT_VALUES_K['tB'])
        theta_b = request.form.get('thetaB', DEFAULT_VALUES_K['thetaB'])
        g_ab = request.form.get('g_ab', DEFAULT_VALUES_K['g_ab'])  # gap
        L = request.form.get('L', DEFAULT_VALUES_K['L'])  # chord length and fixity
        C = request.form.get('C', DEFAULT_VALUES_K['C'])
        load_type = request.form.get('load_type', DEFAULT_VALUES_K['load_type'])  # update var names
        x_axis_desc = request.form.get('x_axis_desc', DEFAULT_VALUES_K['x_axis_desc'])  # todo align var names
        scf_options = request.form.get('scf_options', DEFAULT_VALUES_K['scf_options'])  # "scf_only" or "scf_stress_adjusted"

    try:
        show_table = True  # variable to indicate that SCFs can be presented in a data table
        # convert angles to radians
        theta_a_radians, theta_b_radians = np.radians(float(theta_a)), np.radians(float(theta_b))

        # store all inputs in a dict and convert to floats
        input_fields = {"D": float(d1), "T": float(thk1), "dA": float(d2_a), "tA": float(thk2_a),
                        "thetaA": theta_a_radians, "dB": float(d2_b), "tB": float(thk2_b),
                        "thetaB": theta_b_radians, "g_ab": float(g_ab), "L":float(L), "C": float(C)}

        # calculated values
        chord_props_obj = ChordPropertyManager(input_fields["L"], input_fields["D"], input_fields["T"])

        stress_adjusted = True if scf_options == "scf_stress_adjusted" else False

        kjt_obj = KTJointSCFManager(x_axis_desc, input_fields, stress_adjusted)
        kjt_obj.get_joint_scfs(load_type)

        # convert theta angles back to radians for plotting
        kjt_obj.convert_angles_to_degrees(x_axis_desc)

        # get the plot data for a K joint (no of brace attachments is 2
        plot_data_a_cs, plot_data_a_bs, plot_data_b_cs, plot_data_b_bs = create_joint_plots(kjt_obj, x_axis_desc, stress_adjusted, no_braces=2)


    except Exception as e:
        flash(f"An error occurred: {e}")

    return render_template('k_joint.html',
                           plot_data_a_cs=plot_data_a_cs, plot_data_a_bs=plot_data_a_bs,  # brace A (c-s and b-s)
                           plot_data_b_cs=plot_data_b_cs, plot_data_b_bs=plot_data_b_bs,  # brace B (c-s and b-s)
                           show_table=show_table,
                           D=d1, T=thk1,  # chord
                           dA=d2_a, tA=thk2_a, thetaA=theta_a, # brace A
                           dB=d2_b, tB=thk2_b, thetaB=theta_b,  # brace B
                           g_ab=g_ab,  # gap
                           L=L, C=C,
                           load_type=load_type,
                           x_axis_desc=x_axis_desc,
                           scf_options=scf_options,
                           kjt_obj=kjt_obj,
                           chord_props_obj=chord_props_obj  # calculated values
                           )