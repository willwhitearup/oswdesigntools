import plotly.graph_objs as go
import plotly.io as pio

def bolted_connection_utils_plot(xvals: list, xaxis_label,
                                 Fu_As: list, Fu_Bs, Fu_Ds, Fu_Es,
                                 F_actuals: list):

    # Helper to filter out 0 or None values
    def clean_list(ylist):
        return [y for y in ylist if y not in (0, None)]

    Fu_As = clean_list(Fu_As)
    Fu_Bs = clean_list(Fu_Bs)
    Fu_Ds = clean_list(Fu_Ds)
    Fu_Es = clean_list(Fu_Es)
    F_actuals = clean_list(F_actuals)

    # Optional: also filter xvals so they match the filtered y-values
    def clean_x_y(xvals, yvals):
        return [x for x, y in zip(xvals, yvals) if y not in (0, None)]

    xvals = clean_x_y(xvals, Fu_As)


    # Create main curve
    trace_curve_1 = go.Scatter(x=xvals, y=Fu_As, mode='lines', name='Fu_A', line=dict(color='red'))
    trace_curve_2 = go.Scatter(x=xvals, y=Fu_Bs, mode='lines', name='Fu_B', line=dict(color='blue'))
    trace_curve_3 = go.Scatter(x=xvals, y=Fu_Ds, mode='lines', name='Fu_D', line=dict(color='green'))
    trace_curve_4 = go.Scatter(x=xvals, y=Fu_Es, mode='lines', name='Fu_E', line=dict(color='purple'))
    # actual force applied
    trace_curve_5 = go.Scatter(x=xvals, y=F_actuals, mode='lines', name='Ultimate tension force (segment model)',
                               line=dict(color='gray', dash='dash'))

    # get the y axis
    all_y = Fu_As + Fu_Bs + Fu_Ds + Fu_Es
    print(all_y)
    y_min, y_max = min(all_y), max(all_y)
    y_lower = 0 if y_min >= 0 else y_min * 1.2
    y_upper = y_max * 1.2

    layout = go.Layout(
        title=f'Bolted connection failure modes',
        xaxis=dict(title=f'{xaxis_label}', showgrid=True, gridcolor='lightgray'),
        yaxis=dict(title='Resistance Force', showgrid=True, gridcolor='lightgray', range=[y_lower, y_upper]),
        #legend=dict(x=0.7, y=0.95),
        hovermode='closest',
        template='plotly_white'
    )

    fig = go.Figure(data=[trace_curve_1, trace_curve_2, trace_curve_3, trace_curve_4, trace_curve_5], layout=layout)
    #fig.show()
    plot_json = pio.to_json(fig)
    return plot_json
