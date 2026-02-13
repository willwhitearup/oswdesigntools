import numpy as np
import random
import plotly.graph_objs as go
import plotly.io as pio


def cone_scfs_plot(xvals: list, scf_tube_ins, scf_tube_in_appfs, scf_cone_ins, scf_cone_in_appfs,
                   junction: str, xaxis_label:str, loc: str):


    # Create main curve
    trace_curve_1 = go.Scatter(x=xvals, y=scf_tube_ins, mode='lines', name='Section3 (Tube-side)', line=dict(color='red'))
    trace_curve_2 = go.Scatter(x=xvals, y=scf_tube_in_appfs, mode='lines', name='AppF17 (Tube-side)', line=dict(color='red', dash='dash'))
    trace_curve_3 = go.Scatter(x=xvals, y=scf_cone_ins, mode='lines', name='Section3 (Cone-side)', line=dict(color='green'))
    trace_curve_4 = go.Scatter(x=xvals, y=scf_cone_in_appfs, mode='lines', name='AppF17 (Cone-side)', line=dict(color='green', dash='dash'))

    # get the y axis
    all_y = scf_tube_ins + scf_tube_in_appfs + scf_cone_ins + scf_cone_in_appfs
    y_min, y_max = min(all_y), max(all_y)
    y_lower = 0 if y_min >= 0 else y_min * 1.2
    y_upper = y_max * 1.2

    layout = go.Layout(
        title=f' {loc.upper()} SCFs: {junction.upper()} diameter junction',
        xaxis=dict(title=f'{xaxis_label}', showgrid=True, gridcolor='lightgray'),
        yaxis=dict(title='SCF', showgrid=True, gridcolor='lightgray', range=[y_lower, y_upper]),
        #legend=dict(x=0.7, y=0.95),
        hovermode='closest',
        template='plotly_white'
    )

    fig = go.Figure(data=[trace_curve_1, trace_curve_2, trace_curve_3, trace_curve_4], layout=layout)
    conescfs_plot_json = pio.to_json(fig)
    return conescfs_plot_json

if __name__ == "__main__":
    _ = cone_scfs_plot([0, 1, 2], [1, 2, 3], [1.5, 2.5, 3.5])



