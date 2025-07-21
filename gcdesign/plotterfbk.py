import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

def skspacing_vs_fbk_plot(leg_od, leg_t, pile_od, pile_t, sk_height, sk_spacing, grout_E, grout_strength):

    rj, tj = leg_od / 2, leg_t
    rp, tp = pile_od / 2, pile_t
    eg, es = grout_E, 210000
    fck = grout_strength
    h = sk_height
    my_s = sk_spacing
    tg = rp - tp - rj

    # Calculate k
    k = ((2 * rj / tj) + (2 * rp / tp)) ** -1 + (eg / es) * ((2 * rp - 2 * tp) / tg) ** -1

    # s values from 20 to max(my_s, 800)
    max_s = max(my_s, 800)
    s_values = np.linspace(20, max_s, 50)

    # Calculate fbk for all s
    fbk_values = (((800 / (2 * rj)) + 140 * (h / s_values) ** 0.8) * (k ** 0.6) * (fck ** 0.3))
    fbk_limit_values = (0.75 - 1.4 * (h / s_values)) * (fck ** 0.5)

    # Calculate fbk at my_s
    fbk_my_s = (((800 / (2 * rj)) + 140 * (h / my_s) ** 0.8) * (k ** 0.6) * (fck ** 0.3))

    # Create main curve
    trace_curve = go.Scatter(
        x=s_values.tolist(),
        y=fbk_values.tolist(),
        mode='lines',
        name='fbk vs s'
    )

    # Create grout matrix failure curve
    trace_curve_gmf = go.Scatter(
        x=s_values.tolist(),
        y=fbk_limit_values.tolist(),
        mode='lines',
        name='fbk grout matrix failure vs s',
        line=dict(color='rgba(255, 0, 0, 0.3)', width=2, dash='dash')
    )


    # Horizontal line from (0, fbk_my_s) to (my_s, fbk_my_s)
    trace_hline = go.Scatter(
        x=[0, my_s],
        y=[fbk_my_s, fbk_my_s],
        mode='lines',
        line=dict(color='green', dash='dash'),
        name=f'fbk={fbk_my_s:.2f} @ s={my_s}'
    )

    layout = go.Layout(
        title='SK spacing vs shear capacity (fbk) [valid if within grout matrix failure limit]',
        xaxis=dict(title='SK spacing (mm)', showgrid=True, gridcolor='lightgray'),
        yaxis=dict(title='Fbk (MPa)', showgrid=True, gridcolor='lightgray'),
        legend=dict(x=0.7, y=0.95),
        hovermode='closest',
        template='plotly_white'
    )

    fig = go.Figure(data=[trace_curve, trace_curve_gmf, trace_hline], layout=layout)

    fig.add_shape(
        type='line',
        x0=my_s,
        x1=my_s,
        y0=0,
        y1=1,
        xref='x',
        yref='paper',
        line=dict(color='green', dash='dash'),
    )

    gc_fbk_plot_json = pio.to_json(fig)
    return gc_fbk_plot_json
