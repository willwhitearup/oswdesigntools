import numpy as np
import random
import plotly.graph_objs as go
import plotly.io as pio


def gc_plotter(leg_od: float, leg_t: float, pile_od: float, pile_t: float, gc_length: float,
               n_sks: float, sk_width: float, sk_height: float, sk_spacing: float, elastic_length: float):

    # create plotly fig
    fig = go.Figure()

    # Leg dimensions
    leg_OR = leg_od / 2
    leg_IR = leg_OR - leg_t
    leg_xs = [leg_IR, leg_OR, leg_OR, leg_IR]
    leg_ys = [0, 0, -gc_length, -gc_length]

    ### leg ----------------------------------------------------------------------------
    for sign, show_legend in [(1, True), (-1, False)]:
        fig.add_trace(go.Scatter(x=[sign * x for x in leg_xs], y=leg_ys,
            mode="none", fill='toself', fillcolor="grey",
            line=dict(color="black"),
            name="leg",
            showlegend=False
        ))

    fig.add_trace(go.Scatter(x=[leg_OR, leg_OR, -leg_OR, -leg_OR], y=[-gc_length, -(gc_length+leg_t), -(gc_length+leg_t), -gc_length],
        mode="none", fill='toself', fillcolor="grey",
        line=dict(color="black"),
        name="gc_plate_btm",
        showlegend=False
    ))

    # Pile dimensions
    pile_OR = pile_od / 2
    pile_IR = pile_OR - pile_t

    pile_extension_factor = 1.25  # extend the pile below the btm of jacket by factor (for visualisation)
    pile_xs = [pile_IR, pile_OR, pile_OR, pile_IR]
    pile_ys = [0, 0, -gc_length, -gc_length]

    ### pile section------------------------------------------------------------
    for sign, show_legend in [(1, True), (-1, False)]:
        fig.add_trace(go.Scatter(x=[sign * x for x in pile_xs], y=[pile_extension_factor * y for y in pile_ys],
            mode="none", fill='toself', fillcolor="grey",
            line=dict(color="black"),
            name="pile",
            showlegend=False
        ))

    #### Jacket SKs (original + mirrored)--------------------------------------------------------
    sk_block_height = (n_sks - 1) * sk_spacing
    top_sk_elev = -gc_length / 2 + sk_block_height / 2
    sk_taper = sk_width / 4

    sk_elev = top_sk_elev
    for i in range(int(n_sks)):
        # Coordinates for one SK
        sk_xs = [leg_OR, leg_OR + sk_height, leg_OR + sk_height, leg_OR]
        sk_ys = [sk_elev + sk_width / 2, sk_elev + sk_width / 2 - sk_taper,
                 sk_elev - sk_width / 2 + sk_taper, sk_elev - sk_width / 2
                 ]

        # Add original SK (right side)
        fig.add_trace(go.Scatter(
            x=sk_xs,
            y=sk_ys,
            mode="none",
            fill='toself',
            fillcolor="green",
            line=dict(color="black"),
            name="leg_sks", showlegend=(i == 0)
        ))

        # Add mirrored SK (left side)
        fig.add_trace(go.Scatter(
            x=[-x for x in sk_xs],
            y=sk_ys,
            mode="none",
            fill='toself',
            fillcolor="green",
            line=dict(color="black"),
            name=f"sk_{i + 1} (mirror)",
            showlegend=False  # avoid duplicate legend
        ))

        # Move down to next SK elevation
        sk_elev -= sk_spacing


    #### Pile SKs (original + mirrored)--------------------------------------------------------
    n_pile_sks = n_sks + 1
    top_pile_sk_elev = top_sk_elev + 0.5 * sk_spacing
    pile_sk_elev = top_pile_sk_elev
    for i in range(n_pile_sks):
        # Coordinates for one SK
        sk_xs = [pile_IR, pile_IR, pile_IR - sk_height, pile_IR - sk_height]
        sk_ys = [pile_sk_elev + sk_width / 2, pile_sk_elev - sk_width / 2,
                 pile_sk_elev - sk_width / 2 + sk_taper, pile_sk_elev + sk_width / 2 - sk_taper]
        # Add original SK (right side)
        fig.add_trace(go.Scatter(x=sk_xs, y=sk_ys, mode="none", fill='toself',
            fillcolor="blue", line=dict(color="black"), name="pile_sks",  showlegend=(i == 0)))
        # Add mirrored SK (left side)
        fig.add_trace(go.Scatter(x=[-x for x in sk_xs], y=sk_ys, mode="none", fill='toself', fillcolor="blue",
            line=dict(color="black"), name=f"pile_sk_{i + 1} (mirror)", showlegend=False))
        # Move down to next pile SK elevation
        pile_sk_elev -= sk_spacing


    # Half elastic length exclusion region plot
    x_base = [-0.5 * (pile_od - 2 * pile_t), -0.5 * leg_od, -0.5 * leg_od, -0.5 * (pile_od - 2 * pile_t), -0.5 * (pile_od - 2 * pile_t)]
    y_coords_list = [[0, 0, -0.5 * elastic_length, -0.5 * elastic_length, 0],
                     [-gc_length, -gc_length, -gc_length + 0.5 * elastic_length, -gc_length + 0.5 * elastic_length, -gc_length]]

    for i, y_coords in enumerate(y_coords_list):
        for sign in [-1, 1]:  # left (-1) and right (1)
            fig.add_trace(go.Scatter(
                x=[sign * abs(x) for x in x_base], y=y_coords,
                fill='toself', fillcolor="rgba(255, 0, 0, 0.3)", line=dict(color="red", width=0),
                mode='lines', name='Half elastic length zone' if i == 0 and sign == -1 else None,
                showlegend=i == 0 and sign == -1))
    # end of half elastic zone length

    fig.update_layout(
        width=400,
        height=800,
        title='GC design',
        legend=dict(
            orientation='h',
            x=0.5,
            y=-0.2,
            xanchor='center',
            yanchor='top'
        ),
        xaxis=dict(
            range=[-0.5 * pile_od, 0.5 * pile_od],
            scaleanchor='y'  # Link x-axis scale to y-axis scale
        ),
        yaxis=dict(
            title='Elevation rel pile top (mm)',
            range=[-1.1 * gc_length, 0],
            scaleratio=1  # optional, ensure 1:1 ratio if needed
        )
    )

    #fig.show()

    gc_plot_json = pio.to_json(fig)
    return gc_plot_json


if __name__ == "__main__":
    leg_od, leg_t = 2000, 100
    pile_od, pile_t = 3000, 150
    gc_length = 10000
    n_sks, sk_width, sk_height, sk_spacing = 10, 80, 40, 500
    _ = gc_plotter(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing)



