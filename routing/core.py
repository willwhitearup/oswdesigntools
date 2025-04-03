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


def tubular_second_moment_of_area(outer_diameter: float, thk: float):
    r2 = outer_diameter / 2
    r1 = r2 - thk
    return (np.pi / 4.) * (r2 ** 4 - r1 ** 4)

def tubular_cross_section_area(outer_diameter: float, thk: float):
    r2 = outer_diameter / 2
    r1 = r2 - thk
    return np.pi * (r2 ** 2. - r1 ** 2.)