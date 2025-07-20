import plotly.graph_objs as go
import plotly.io as pio
from gcdesign.groutuls.groutuls import get_grout_matrix_failure_plot_vals



def shear_capacity_plotter(leg_od, leg_t, pile_od, pile_t, sk_height, sk_spacing, grout_E, grout_strength):


    h_over_s = sk_height / sk_spacing
    min_sk_spacing, max_sk_spacing = 0.01, 5000

    # get the shear capacity and grout matrix failure plot details
    fbks, fbk_limits, h_over_s_vals, f_bk_actual, hs_limit = get_grout_matrix_failure_plot_vals(leg_od, leg_t,
          pile_od, pile_t,sk_height, grout_E, grout_strength, max_sk_spacing, min_sk_spacing, sk_spacing)

    # create plotly fig
    fig = go.Figure()

    # Add fbks trace
    fig.add_trace(go.Scatter(x=h_over_s_vals, y=fbks,
        mode='lines',
        name='Fbk',
        line=dict(color='blue'),
        marker=dict(symbol='circle', size=6)
    ))

    # Add fbk_limits trace
    fig.add_trace(go.Scatter(x=h_over_s_vals, y=fbk_limits,
        mode='lines',
        name='Fbk limit (grout matrix failure)',
        line=dict(color='red'),
        marker=dict(symbol='x', size=6)
    ))

    # Add fbks trace
    colour = "green" if h_over_s < hs_limit else "red"
    fig.add_trace(go.Scatter(x=[h_over_s], y=[f_bk_actual],
        mode='markers',
        name='GC h/s design',
        marker=dict(symbol='circle', size=16, color=colour)
    ))
    # annotate the actual GC h/s value
    fig.add_annotation(x=h_over_s, y=f_bk_actual,
        text=f"h/s = {h_over_s:.3f}",
        showarrow=True, arrowhead=2,
        ax=30,  ay=-40,  # x and y offsets
        bgcolor="white", bordercolor="black",
        borderwidth=1, font=dict(size=12)
    )

    # Add vertical line at hs_limit
    fig.add_vline(x=hs_limit,
        line=dict(color="red", dash="dash"),
        annotation_text=f"h/s limit (>{round(hs_limit, 4)}=grout matrix failure)",
        annotation_position="top right"
    )

    # Add shaded rectangle to the right of hs_limit
    fig.add_shape(type="rect", x0=hs_limit, x1=max(h_over_s_vals),
        y0=0, y1=max(fbks + fbk_limits),  # y-axis upper limit
        fillcolor="rgba(200,200,200,0.3)",  # light gray transparent fill
        line=dict(width=0),
        layer="below"
    )

    # Update layout
    fig.update_layout(
        title='GC shear capacity (h/s capacity limit)',
        xaxis_title='h/s',
        yaxis_title='Fbk (MPa)',
        legend=dict(x=0.05, y=0.95),
        template='plotly_white',
    )

    # Show the plot
    # fig.show()

    gc_shrcap_plot_json = pio.to_json(fig)
    return gc_shrcap_plot_json
