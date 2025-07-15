import numpy as np
import random
import plotly.graph_objs as go
import plotly.io as pio


def jacket_plotter(leg_od: float, leg_t: float,
                   pile_od: float, pile_t: float, gc_length: float,
                   n_sks: float, sk_width: float, sk_height: float, sk_spacing: float):

    # create plotly fig
    fig = go.Figure()

    # Leg dimensions
    leg_OR = leg_od / 2
    leg_IR = leg_OR - leg_t
    leg_xs = [leg_IR, leg_OR, leg_OR, leg_IR]
    leg_ys = [0, 0, -gc_length, -gc_length]

    ### leg ----------------------------------------------------------------------------
    for sign, show_legend in [(1, True), (-1, False)]:
        fig.add_trace(go.Scatter(
            x=[sign * x for x in leg_xs],
            y=leg_ys,
            mode="none",
            fill='toself',
            fillcolor="grey",
            line=dict(color="black"),
            name="leg",
            showlegend=show_legend
        ))

    fig.add_trace(go.Scatter(
        x=[leg_OR, leg_OR, -leg_OR, -leg_OR],
        y=[-gc_length, -(gc_length+leg_t), -(gc_length+leg_t), -gc_length],
        mode="none",
        fill='toself',
        fillcolor="grey",
        line=dict(color="black"),
        name="gc_plate_btm",
        showlegend=True
    ))

    # Pile dimensions
    pile_OR = pile_od / 2
    pile_IR = pile_OR - pile_t

    pile_extension_factor = 1.25
    pile_xs = [pile_IR, pile_OR, pile_OR, pile_IR]
    pile_ys = [0, 0, -gc_length, -gc_length]

    ### pile section------------------------------------------------------------
    for sign, show_legend in [(1, True), (-1, False)]:
        fig.add_trace(go.Scatter(
            x=[sign * x for x in pile_xs],
            y=[pile_extension_factor * y for y in pile_ys],
            mode="none",
            fill='toself',
            fillcolor="brown",
            line=dict(color="black"),
            name="pile",
            showlegend=show_legend
        ))

    # Bottom of pile line and label
    bottom_y = -gc_length
    line_x_start = 1.05 * pile_OR + 10  # offset right of pile
    line_x_end = 2 * pile_OR  # extend further right

    fig.add_trace(go.Scatter(
        x=[line_x_start, line_x_end],
        y=[bottom_y, bottom_y],
        mode="lines",
        line=dict(color="grey", width=1, dash="dot"),
        showlegend=False
    ))

    fig.add_annotation(
        x=line_x_end + 2,
        y=bottom_y,
        text="bottom of connection",
        showarrow=False,
        font=dict(size=10, color="grey"),
        xanchor="left",
        yanchor="middle"
    )

    #### Jacket SKs (original + mirrored)--------------------------------------------------------
    sk_block_height = n_sks * sk_spacing
    top_sk_elev = -gc_length / 2 + sk_block_height / 2
    sk_taper = sk_width / 4

    for i in range(n_sks):
        # Coordinates for one SK
        sk_xs = [leg_OR, leg_OR + sk_height, leg_OR + sk_height, leg_OR]
        sk_ys = [
            top_sk_elev + sk_width / 2,
            top_sk_elev + sk_width / 2 - sk_taper,
            top_sk_elev - sk_width / 2 + sk_taper,
            top_sk_elev - sk_width / 2
        ]

        # Add original SK (right side)
        fig.add_trace(go.Scatter(
            x=sk_xs,
            y=sk_ys,
            mode="none",
            fill='toself',
            fillcolor="red",
            line=dict(color="black"),
            name=f"sk_{i + 1}",
            showlegend=True
        ))

        # Add mirrored SK (left side)
        fig.add_trace(go.Scatter(
            x=[-x for x in sk_xs],
            y=sk_ys,
            mode="none",
            fill='toself',
            fillcolor="red",
            line=dict(color="black"),
            name=f"sk_{i + 1} (mirror)",
            showlegend=False  # avoid duplicate legend
        ))

        # Move down to next SK elevation
        top_sk_elev -= sk_spacing


    #### Pile SKs (original + mirrored)--------------------------------------------------------
    n_pile_sks = n_sks + 1
    pile_sk_block_height = n_pile_sks * sk_spacing
    top_pile_sk_elev = -gc_length / 2 + pile_sk_block_height / 2

    for i in range(n_pile_sks):
        # Coordinates for one SK
        sk_xs = [pile_IR, pile_IR, pile_IR - sk_height, pile_IR - sk_height]
        sk_ys = [
            top_pile_sk_elev + sk_width / 2,
            top_pile_sk_elev - sk_width / 2,
            top_pile_sk_elev - sk_width / 2 + sk_taper,
            top_pile_sk_elev + sk_width / 2 - sk_taper
        ]

        # Add original SK (right side)
        fig.add_trace(go.Scatter(
            x=sk_xs,
            y=sk_ys,
            mode="none",
            fill='toself',
            fillcolor="blue",
            line=dict(color="black"),
            name=f"pile_sk_{i + 1}",
            showlegend=True
        ))

        # Add mirrored SK (left side)
        fig.add_trace(go.Scatter(
            x=[-x for x in sk_xs],
            y=sk_ys,
            mode="none",
            fill='toself',
            fillcolor="blue",
            line=dict(color="black"),
            name=f"pile_sk_{i + 1} (mirror)",
            showlegend=False  # avoid duplicate legend
        ))

        # Move down to next pile SK elevation
        top_pile_sk_elev -= sk_spacing



    fig.update_layout(
        yaxis_title='elevation rel LAT [mm]',
        yaxis=dict(scaleanchor="x", scaleratio=1),
        legend=dict(x=1, y=1)
    )

    fig.show()
    return pio.to_json(fig)


if __name__ == "__main__":
    leg_od, leg_t = 2000, 100
    pile_od, pile_t = 3000, 150
    gc_length = 10000
    n_sks, sk_width, sk_height, sk_spacing = 10, 80, 40, 500
    _ = jacket_plotter(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing)



