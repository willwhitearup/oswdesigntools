import plotly.graph_objs as go
import plotly.io as pio
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



def create_plotly_plot(xvals, yvals_dict, x_label, y_label="SCF", plot_title=None, stress_adjusted=False):
    """Creates and shows a Plotly interactive plot.

    Args:
        xvals (list or array): X-axis values.
        yvals_dict (dict): Dictionary with keys as (label, color, linestyle) and values as y-values.
        x_label (str): X-axis label.
        y_label (str, optional): Y-axis label. Defaults to "SCF".
        plot_title (str, optional): Title of the plot.
        stress_adjusted (bool, optional): Whether to plot dashed lines. Defaults to False.
    """
    fig = go.Figure()

    for (label, color, linestyle), yvals in yvals_dict.items():
        if not stress_adjusted and linestyle == "--":
            continue

        line_dash = "dash" if linestyle == "--" else "solid"

        fig.add_trace(go.Scatter(
            x=xvals,
            y=yvals,
            mode='lines+markers',
            name=label,
            line=dict(color=color, dash=line_dash),
            marker=dict(symbol='circle')
        ))

    fig.update_layout(
        title=plot_title or "",
        xaxis_title=x_label,
        yaxis_title=y_label,
        template="plotly_white",
        legend=dict(bordercolor="Black", borderwidth=1),
        margin=dict(l=40, r=20, t=50, b=40)
    )

    # fig.show()
    plot_json = pio.to_json(fig)
    return plot_json


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
    if no_braces not in [1, 2, 3]:
        raise Exception(f"No. of joint braces ({no_braces}) not allowed. Up to 3 braces currently allowed")

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


    plot_data_a_cs_json = create_plotly_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_a_chord_crowns,
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


    plot_data_a_bs_json = create_plotly_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_a_brace_crowns,
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

    # 2 brace e.g. K joint
    if no_braces > 1:

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

        plot_data_b_cs_json = create_plotly_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_b_chord_crowns,
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

        plot_data_b_bs_json = create_plotly_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_b_brace_crowns,
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


    # 3 braces for KT joint only
    if no_braces > 2:

        # brace C plots
        # chord side
        plot_data_c_cs = create_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_c_chord_crowns,
                                                     ("axial saddle", "orange", "-"): jt_obj.scf_axial_c_chord_saddles,
                                                     ("IPB crown", "blue", "-"): jt_obj.scf_ipb_c_chord_crowns,
                                                     ("OPB saddle", "green", "-"): jt_obj.scf_opb_c_chord_saddles,
                                                     ("axial crown stress_adjusted", "red",
                                                       "--"): jt_obj.scf_axial_c_chord_crowns_adj,
                                                     ("axial saddle stress_adjusted", "orange",
                                                       "--"): jt_obj.scf_axial_c_chord_saddles_adj,
                                                     ("IPB crown stress_adjusted", "blue",
                                                       "--"): jt_obj.scf_ipb_c_chord_crowns_adj,
                                                     ("OPB saddle stress_adjusted", "green",
                                                       "--"): jt_obj.scf_opb_c_chord_saddles_adj
                                                     },
                                     x_axis_desc, stress_adjusted=stress_adjusted)  # chordside

        # brace side
        plot_data_c_bs = create_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_c_brace_crowns,
                                                     ("axial saddle", "orange", "-"): jt_obj.scf_axial_c_brace_saddles,
                                                     ("IPB crown", "blue", "-"): jt_obj.scf_ipb_c_brace_crowns,
                                                     ("OPB saddle", "green", "-"): jt_obj.scf_opb_c_brace_saddles,
                                                     ("axial crown stress_adjusted", "red",
                                                       "--"): jt_obj.scf_axial_c_brace_crowns_adj,
                                                     ("axial saddle stress_adjusted", "orange",
                                                       "--"): jt_obj.scf_axial_c_brace_saddles_adj,
                                                     ("IPB crown stress_adjusted", "blue",
                                                       "--"): jt_obj.scf_ipb_c_brace_crowns_adj,
                                                     ("OPB saddle stress_adjusted", "green",
                                                       "--"): jt_obj.scf_opb_c_brace_saddles_adj
                                                     },
                                     x_axis_desc, stress_adjusted=stress_adjusted)  # braceside

        plot_objs.append(plot_data_c_cs)
        plot_objs.append(plot_data_c_bs)

    return plot_objs


def tubular_second_moment_of_area(outer_diameter: float, thk: float):
    r2 = outer_diameter / 2
    r1 = r2 - thk
    return (np.pi / 4.) * (r2 ** 4 - r1 ** 4)

def tubular_cross_section_area(outer_diameter: float, thk: float):
    r2 = outer_diameter / 2
    r1 = r2 - thk
    return np.pi * (r2 ** 2. - r1 ** 2.)


# todo convert everything to json plots at some point!
def create_joint_plots_json(jt_obj, x_axis_desc, stress_adjusted, no_braces):
    """creates the plotting objects for Flask site

    Args:
        jt_obj:
        x_axis_desc:
        stress_adjusted:
        no_braces:

    Returns:
        plot_objs, list, of plot objects
    """
    if no_braces not in [1, 2, 3]:
        raise Exception(f"No. of joint braces ({no_braces}) not allowed. Up to 3 braces currently allowed")

    # brace A plots
    # chord side
    plot_data_a_cs_json = create_plotly_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_a_chord_crowns,
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
    plot_data_a_bs_json = create_plotly_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_a_brace_crowns,
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


    plot_objs = [plot_data_a_cs_json, plot_data_a_bs_json]

    # 2 brace e.g. K joint
    if no_braces > 1:

        # brace B plots
        # chord side
        plot_data_b_cs_json = create_plotly_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_b_chord_crowns,
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
        plot_data_b_bs_json = create_plotly_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_b_brace_crowns,
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

        plot_objs.append(plot_data_b_cs_json)
        plot_objs.append(plot_data_b_bs_json)


    # 3 braces for KT joint only
    if no_braces > 2:

        # brace C plots
        # chord side

        plot_data_c_cs_json = create_plotly_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_c_chord_crowns,
                                                     ("axial saddle", "orange", "-"): jt_obj.scf_axial_c_chord_saddles,
                                                     ("IPB crown", "blue", "-"): jt_obj.scf_ipb_c_chord_crowns,
                                                     ("OPB saddle", "green", "-"): jt_obj.scf_opb_c_chord_saddles,
                                                     ("axial crown stress_adjusted", "red",
                                                       "--"): jt_obj.scf_axial_c_chord_crowns_adj,
                                                     ("axial saddle stress_adjusted", "orange",
                                                       "--"): jt_obj.scf_axial_c_chord_saddles_adj,
                                                     ("IPB crown stress_adjusted", "blue",
                                                       "--"): jt_obj.scf_ipb_c_chord_crowns_adj,
                                                     ("OPB saddle stress_adjusted", "green",
                                                       "--"): jt_obj.scf_opb_c_chord_saddles_adj
                                                     },
                                     x_axis_desc, stress_adjusted=stress_adjusted)  # chordside


        # brace side
        plot_data_c_bs_json = create_plotly_plot(jt_obj.params, {("axial crown", "red", "-"): jt_obj.scf_axial_c_brace_crowns,
                                                     ("axial saddle", "orange", "-"): jt_obj.scf_axial_c_brace_saddles,
                                                     ("IPB crown", "blue", "-"): jt_obj.scf_ipb_c_brace_crowns,
                                                     ("OPB saddle", "green", "-"): jt_obj.scf_opb_c_brace_saddles,
                                                     ("axial crown stress_adjusted", "red",
                                                       "--"): jt_obj.scf_axial_c_brace_crowns_adj,
                                                     ("axial saddle stress_adjusted", "orange",
                                                       "--"): jt_obj.scf_axial_c_brace_saddles_adj,
                                                     ("IPB crown stress_adjusted", "blue",
                                                       "--"): jt_obj.scf_ipb_c_brace_crowns_adj,
                                                     ("OPB saddle stress_adjusted", "green",
                                                       "--"): jt_obj.scf_opb_c_brace_saddles_adj
                                                     },
                                     x_axis_desc, stress_adjusted=stress_adjusted)  # braceside

        plot_objs.append(plot_data_c_cs_json)
        plot_objs.append(plot_data_c_bs_json)

    return plot_objs