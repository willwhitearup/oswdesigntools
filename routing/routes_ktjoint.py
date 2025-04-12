from flask import request, render_template, flash
from routing.core import create_plot, create_joint_plots
import numpy as np
from routing.scfs_kt_jts import KTJointSCFManager, ChordPropertyManager

# Define default values
DEFAULT_VALUES_KT = {'D_kt': 1000, 'T_kt': 20,
                     'dA_kt': 500, 'tA_kt': 15, 'thetaA_kt': 45,
                     'dB_kt': 500, 'tB_kt': 15, 'thetaB_kt': 90,
                     'dC_kt': 500, 'tC_kt': 15, 'thetaC_kt': 45,
                     'g_ab_kt': 75, 
                     'g_bc_kt': 75,
                     'L_kt': 5000, 'C_kt': 0.7,
                      # calculation options (strings)
                     'load_type_kt': 'balanced_axial_unbalanced_moment', 
                     'x_axis_desc_kt': 'D_kt', 
                     'scf_options_kt': 'scf_only'
                    }

def kt_joint_route():
    # plot data for brace a, brace b, brace c
    plot_data_a_cs_kt, plot_data_a_bs_kt = None, None
    plot_data_b_cs_kt, plot_data_b_bs_kt = None, None
    plot_data_c_cs_kt, plot_data_c_bs_kt = None, None
    show_table_kt = False
    ktjt_obj = None
    chord_props_obj_kt = None  # define a class for the joint calculated properties

    # Use default values if the request method is GET
    if request.method == 'GET':
        # chord
        d1 = DEFAULT_VALUES_KT['D_kt']
        thk1 = DEFAULT_VALUES_KT['T_kt']

        # brace A
        d2_a = DEFAULT_VALUES_KT['dA_kt']
        thk2_a = DEFAULT_VALUES_KT['tA_kt']
        theta_a = DEFAULT_VALUES_KT['thetaA_kt']

        # brace B
        d2_b = DEFAULT_VALUES_KT['dB_kt']
        thk2_b = DEFAULT_VALUES_KT['tB_kt']
        theta_b = DEFAULT_VALUES_KT['thetaB_kt']

        # brace C inputs
        d2_c = DEFAULT_VALUES_KT['dC_kt']
        thk2_c = DEFAULT_VALUES_KT['tC_kt']
        theta_c = DEFAULT_VALUES_KT['thetaC_kt']

        g_ab = DEFAULT_VALUES_KT['g_ab_kt']
        g_bc = DEFAULT_VALUES_KT['g_bc_kt']
        L = DEFAULT_VALUES_KT['L_kt']
        C = DEFAULT_VALUES_KT['C_kt']
        load_type = DEFAULT_VALUES_KT['load_type_kt']
        x_axis_desc = DEFAULT_VALUES_KT['x_axis_desc_kt']
        scf_options = DEFAULT_VALUES_KT['scf_options_kt']
    else:
        # chord inputs
        d1 = request.form.get('D_kt', DEFAULT_VALUES_KT['D_kt'])
        thk1 = request.form.get('T_kt', DEFAULT_VALUES_KT['T_kt'])
        # brace A inputs
        d2_a = request.form.get('dA_kt', DEFAULT_VALUES_KT['dA_kt'])
        thk2_a = request.form.get('tA_kt', DEFAULT_VALUES_KT['tA_kt'])
        theta_a = request.form.get('thetaA_kt', DEFAULT_VALUES_KT['thetaA_kt'])
        # brace B inputs
        d2_b = request.form.get('dB_kt', DEFAULT_VALUES_KT['dB_kt'])
        thk2_b = request.form.get('tB_kt', DEFAULT_VALUES_KT['tB_kt'])
        theta_b = request.form.get('thetaB_kt', DEFAULT_VALUES_KT['thetaB_kt'])

        # brace C inputs
        d2_c = request.form.get('dC_kt', DEFAULT_VALUES_KT['dC_kt'])
        thk2_c = request.form.get('tC_kt', DEFAULT_VALUES_KT['tC_kt'])
        theta_c = request.form.get('thetaC_kt', DEFAULT_VALUES_KT['thetaC_kt'])

        g_ab = request.form.get('g_ab_kt', DEFAULT_VALUES_KT['g_ab_kt'])  # gap
        g_bc = request.form.get('g_bc_kt', DEFAULT_VALUES_KT['g_bc_kt'])  # gap

        L = request.form.get('L_kt', DEFAULT_VALUES_KT['L_kt'])  # chord length and fixity
        C = request.form.get('C_kt', DEFAULT_VALUES_KT['C_kt'])
        load_type = request.form.get('load_type_kt', DEFAULT_VALUES_KT['load_type_kt'])  # update var names
        x_axis_desc = request.form.get('x_axis_desc_kt', DEFAULT_VALUES_KT['x_axis_desc_kt'])  # todo align var names
        scf_options = request.form.get('scf_options_kt', DEFAULT_VALUES_KT['scf_options_kt'])  # "scf_only" or "scf_stress_adjusted"

    try:
        # map the provided Flask app var names (key) to generic names (value) for Python use
        x_axis_desc_mapper = {"D_kt": "D", "T_kt": "T",
                              "dA_kt": "dA", "tA_kt": "tA",
                              "dB_kt": "dB", "tB_kt": "tB",
                              "dC_kt": "dC", "tC_kt": "tC",
                              "thetaA_kt": "thetaA",
                              "thetaB_kt": "thetaB",
                              "thetaC_kt": "thetaC",
                              "g_ab_kt": "g_ab",
                              "g_bc_kt": "g_bc",
                              "L_kt": "L", "C_kt": "C"
                              }

        x_axis_mapped = x_axis_desc_mapper[x_axis_desc]

        show_table_kt = True  # variable to indicate that SCFs can be presented in a data table
        # convert angles to radians
        theta_a_radians, theta_b_radians, theta_c_radians = np.radians(float(theta_a)), np.radians(float(theta_b)), np.radians(float(theta_c))

        # store all inputs in a dict and convert to floats
        input_fields = {"D": float(d1), "T": float(thk1),
                        "dA": float(d2_a), "tA": float(thk2_a), "thetaA": theta_a_radians,
                        "dB": float(d2_b), "tB": float(thk2_b), "thetaB": theta_b_radians,
                        "dC": float(d2_c), "tC": float(thk2_c), "thetaC": theta_c_radians,
                        "g_ab": float(g_ab),
                        "g_bc": float(g_bc),
                        "L": float(L),
                        "C": float(C)}

        # calculated values
        chord_props_obj_kt = None

        stress_adjusted = True if scf_options == "scf_stress_adjusted" else False

        ktjt_obj = KTJointSCFManager(x_axis_mapped, input_fields, stress_adjusted, joint_type="kt")
        ktjt_obj.get_joint_scfs(load_type)

        # convert theta angles back to radians for plotting
        ktjt_obj.convert_angles_to_degrees(x_axis_mapped)

        # get the plot data for a KT joint (no of brace attachments is 3)
        (plot_data_a_cs_kt, plot_data_a_bs_kt,
         plot_data_b_cs_kt, plot_data_b_bs_kt,
         plot_data_c_cs_kt, plot_data_c_bs_kt) = create_joint_plots(ktjt_obj, x_axis_mapped, stress_adjusted, no_braces=3)

    except Exception as e:
        flash(f"An error occurred: {e}")

    return render_template('kt_joint.html',
                           plot_data_a_cs_kt=plot_data_a_cs_kt, plot_data_a_bs_kt=plot_data_a_bs_kt,  # brace A (c-s and b-s)
                           plot_data_b_cs_kt=plot_data_b_cs_kt, plot_data_b_bs_kt=plot_data_b_bs_kt,  # brace B (c-s and b-s)
                           plot_data_c_cs_kt=plot_data_c_cs_kt, plot_data_c_bs_kt=plot_data_c_bs_kt,  # brace C (c-s and b-s)
                           show_table_kt=show_table_kt,
                           D_kt=d1, T_kt=thk1,  # chord
                           dA_kt=d2_a, tA_kt=thk2_a, thetaA_kt=theta_a, # brace A
                           dB_kt=d2_b, tB_kt=thk2_b, thetaB_kt=theta_b,  # brace B
                           dC_kt=d2_c, tC_kt=thk2_c, thetaC_kt=theta_c,  # brace C
                           g_ab_kt=g_ab,  # gap
                           g_bc_kt=g_bc,  # gap
                           L_kt=L, C_kt=C,
                           load_type_kt=load_type,
                           x_axis_desc_kt=x_axis_desc,
                           scf_options_kt=scf_options,
                           ktjt_obj=ktjt_obj,
                           chord_props_obj_kt=chord_props_obj_kt  # calculated values
                           )