import plotly.graph_objs as go
import plotly.io as pio
import numpy as np
import copy
import math

def plotly_fig_plot(xvals: list, xaxis_label: str,
                    yvals: list, yvals2: list):

    # Create main curve
    trace_curve_1 = go.Scatter(x=xvals, y=yvals, mode='lines', name='y_vals1', line=dict(color='red'))
    trace_curve_2 = go.Scatter(x=xvals, y=yvals2, mode='lines', name='y_vals2', line=dict(color='blue'))


    layout = go.Layout(
        title=f'RRFs title 1',
        xaxis=dict(title=f'{xaxis_label}', showgrid=True, gridcolor='lightgray'),
        yaxis=dict(title='yaxis_label', showgrid=True, gridcolor='lightgray'),
        hovermode='closest',
        template='plotly_white'
    )

    fig = go.Figure(data=[trace_curve_1, trace_curve_2], layout=layout)
    fig.show()
    plot_json = pio.to_json(fig)
    return plot_json