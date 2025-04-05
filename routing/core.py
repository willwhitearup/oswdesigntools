# from flask import flash, get_flashed_messages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import base64
import io



def create_plot(xvals, yvals_dict, x_label, y_label="SCF", plot_title=None, stress_adjusted=False):
    """colors, str, 'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'white'
    """
    plt.figure()

    # plot each data set onto same figure
    for (label, color, linestyle), yvals in yvals_dict.items():

        if stress_adjusted is False and linestyle == "--":
            pass
        else:
            plt.plot(xvals, yvals, color=color, marker='o', linestyle=linestyle, label=label)

    # plotting options
    plt.xlabel(f'{x_label}')
    plt.ylabel(f'{y_label}')
    plt.grid(True)  # grid on
    plt.legend()  # add legend
    if plot_title is not None:
        plt.title(f'{plot_title}')

    # Adjust the layout to fit within the figure area
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return plot_data


def create_joint_plots(jt_obj, x_axis_desc, stress_adjusted, no_braces):
    """creates the plotting objects for Flask site

    Args:
        jt_obj:
        x_axis_desc:
        stress_adjusted:
        no_braces:

    Returns:
        plot_objs, list, of plot objects
    """
    if no_braces not in [1, 2]:
        # todo: KT joints have 3 braces
        raise Exception(f"No. of joint braces ({no_braces}) not allowed. Only 1 or 2 braces currently allowed")

    # brace A plots
    # chord side
    plot_data_a_cs = create_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_a_chord_crowns,
                                                 ("axial saddle", "orange", "-"): jt_obj.scf_axial_a_chord_saddles,
                                                 ("IPB crown", "blue", "-"): jt_obj.scf_ipb_a_chord_crowns,
                                                 ("OPB saddle", "green", "-"): jt_obj.scf_opb_a_chord_saddles,
                                                 ("axial crown stress_adjusted", "red",
                                                   "--"): jt_obj.scf_axial_a_chord_crowns_adj,
                                                 ("axial saddle stress_adjusted", "orange",
                                                   "--"): jt_obj.scf_axial_a_chord_saddles_adj,
                                                 ("IPB crown stress_adjusted", "blue",
                                                   "--"): jt_obj.scf_ipb_a_chord_crowns_adj,
                                                 ("OPB saddle stress_adjusted", "green",
                                                   "--"): jt_obj.scf_opb_a_chord_saddles_adj
                                                 },
                                 x_axis_desc, stress_adjusted=stress_adjusted)  # chordside

    # brace side
    plot_data_a_bs = create_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_a_brace_crowns,
                                                 ("axial saddle", "orange", "-"): jt_obj.scf_axial_a_brace_saddles,
                                                 ("IPB crown", "blue", "-"): jt_obj.scf_ipb_a_brace_crowns,
                                                 ("OPB saddle", "green", "-"): jt_obj.scf_opb_a_brace_saddles,
                                                 ("axial crown stress_adjusted", "red",
                                                   "--"): jt_obj.scf_axial_a_brace_crowns_adj,
                                                 ("axial saddle stress_adjusted", "orange",
                                                   "--"): jt_obj.scf_axial_a_brace_saddles_adj,
                                                 ("IPB crown stress_adjusted", "blue",
                                                   "--"): jt_obj.scf_ipb_a_brace_crowns_adj,
                                                 ("OPB saddle stress_adjusted", "green",
                                                   "--"): jt_obj.scf_opb_a_brace_saddles_adj
                                                 },
                                 x_axis_desc, stress_adjusted=stress_adjusted)  # braceside

    plot_objs = [plot_data_a_cs, plot_data_a_bs]

    if no_braces == 2:

        # brace B plots
        # chord side
        plot_data_b_cs = create_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_b_chord_crowns,
                                                     ("axial saddle", "orange", "-"): jt_obj.scf_axial_b_chord_saddles,
                                                     ("IPB crown", "blue", "-"): jt_obj.scf_ipb_b_chord_crowns,
                                                     ("OPB saddle", "green", "-"): jt_obj.scf_opb_b_chord_saddles,
                                                     ("axial crown stress_adjusted", "red",
                                                       "--"): jt_obj.scf_axial_b_chord_crowns_adj,
                                                     ("axial saddle stress_adjusted", "orange",
                                                       "--"): jt_obj.scf_axial_b_chord_saddles_adj,
                                                     ("IPB crown stress_adjusted", "blue",
                                                       "--"): jt_obj.scf_ipb_b_chord_crowns_adj,
                                                     ("OPB saddle stress_adjusted", "green",
                                                       "--"): jt_obj.scf_opb_b_chord_saddles_adj
                                                     },
                                     x_axis_desc, stress_adjusted=stress_adjusted)  # chordside

        # brace side
        plot_data_b_bs = create_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_b_brace_crowns,
                                                     ("axial saddle", "orange", "-"): jt_obj.scf_axial_b_brace_saddles,
                                                     ("IPB crown", "blue", "-"): jt_obj.scf_ipb_b_brace_crowns,
                                                     ("OPB saddle", "green", "-"): jt_obj.scf_opb_b_brace_saddles,
                                                     ("axial crown stress_adjusted", "red",
                                                       "--"): jt_obj.scf_axial_b_brace_crowns_adj,
                                                     ("axial saddle stress_adjusted", "orange",
                                                       "--"): jt_obj.scf_axial_b_brace_saddles_adj,
                                                     ("IPB crown stress_adjusted", "blue",
                                                       "--"): jt_obj.scf_ipb_b_brace_crowns_adj,
                                                     ("OPB saddle stress_adjusted", "green",
                                                       "--"): jt_obj.scf_opb_b_brace_saddles_adj
                                                     },
                                     x_axis_desc, stress_adjusted=stress_adjusted)  # braceside

        plot_objs.append(plot_data_b_cs)
        plot_objs.append(plot_data_b_bs)



    return plot_objs


def tubular_second_moment_of_area(outer_diameter: float, thk: float):
    r2 = outer_diameter / 2
    r1 = r2 - thk
    return (np.pi / 4.) * (r2 ** 4 - r1 ** 4)

def tubular_cross_section_area(outer_diameter: float, thk: float):
    r2 = outer_diameter / 2
    r1 = r2 - thk
    return np.pi * (r2 ** 2. - r1 ** 2.)