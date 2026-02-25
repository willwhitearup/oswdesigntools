import plotly.graph_objs as go
import numpy as np
import plotly.io as pio

from boltedconn.boltdata import Bolt
from boltedconn.flange import BoltedFlange


# wall_thk: float,
# flange_length: float,
# flange_thickness: float,
# total_height: float,
# hole_diameter: float,
# b_star: float
def l_flange_plotter(flange_obj: BoltedFlange):
    """
    Single L-flange profile.
    Origin (0,0) at top outer diameter.
    """

    wall_thk = flange_obj.wall_thickness
    flange_length = flange_obj.flange_length
    flange_height = flange_obj.flange_height
    total_height = flange_obj.total_height
    hole_diameter = flange_obj.bolt_obj.hole_diameter
    b_star = flange_obj.b_star

    # radius between flange and wall thickness
    r = flange_height / 8
    n_arc_pts: int = 12  # smoothness of radius

    # ============================================================
    # 1) Vertical leg down to fillet
    xs_leg = [0, 0, -wall_thk, -wall_thk]
    ys_leg = [0, -total_height, -total_height, -flange_height - r]

    # ============================================================
    # 2) Internal fillet (quarter circle)

    cx = -wall_thk - r
    cy = -flange_height - r
    theta = np.linspace(0, np.pi / 2, n_arc_pts)
    xs_arc = list(cx + r * np.cos(theta))
    ys_arc = list(cy + r * np.sin(theta))

    # ============================================================
    # 3) From fillet to first bolt-hole edge
    xs_to_hole = [-b_star + hole_diameter / 2, -b_star + hole_diameter / 2, 0]
    ys_to_hole = [-flange_height, 0, 0]

    # 4) Outer flange section beyond bolt hole
    xs_outer = [-b_star - hole_diameter / 2, -flange_length, -flange_length, -b_star - hole_diameter / 2, -b_star - hole_diameter / 2]
    ys_outer = [-flange_height, -flange_height, 0, 0, -flange_height]

    # ============================================================
    # 5) Close first filled region explicitly
    xs_part1 = xs_leg + xs_arc + xs_to_hole + [xs_leg[0]]
    ys_part1 = ys_leg + ys_arc + ys_to_hole + [ys_leg[0]]

    # ============================================================
    # 6) Create figure
    fig = go.Figure()

    # add traces to figure
    flange_colour = "#EF553B"  # steel red
    edge_colour = "#B22222"
    # First filled region (left side of bolt hole)
    fig.add_trace(go.Scatter(x=xs_part1, y=ys_part1, mode="lines", fill="toself", fillcolor=flange_colour,
            line=dict(color=edge_colour, width=2), showlegend=False))

    # Second filled region (right side of bolt hole)
    fig.add_trace(go.Scatter(x=xs_outer, y=ys_outer, mode="lines", fill="toself", fillcolor=flange_colour,
            line=dict(color=edge_colour, width=2), showlegend=False))

    # bolt axis dotted line
    fig.add_trace(go.Scatter(x=[-b_star, -b_star], y=[flange_height / 3, -flange_height * 4 / 3],
                             mode="lines", line=dict(color="black", width=2, dash="dot"), showlegend=False))

    ## annotations
    fig = flange_t_annotation(fig, flange_length, flange_height)
    fig = b_star_annotation(fig, flange_height, b_star)
    fig = flange_height_annotation(fig, total_height)
    fig = flange_length_annotation(fig, total_height, flange_length)
    fig = hole_diameter_annotation(fig, b_star, flange_height, hole_diameter)

    # fig size / extent and layout
    fig.update_layout(
        width=800,  # adjust figure width
        height=800,  # adjust figure height (square looks nice)
        xaxis=dict(range=[-flange_length * 1.2, flange_length * 0.2], scaleanchor='y', title='X (mm)'),
        yaxis=dict(range=[-total_height * 1.2, flange_height * 0.5], title='Y (mm)'),
        showlegend=False)

    # fig.show()

    return pio.to_json(fig)


def flange_length_annotation(fig, total_height, flange_length):

    y_dim = - 1.075 * total_height

    # dim line
    fig.add_trace(go.Scatter(x=[0, -flange_length], y=[y_dim, y_dim], mode="lines", line=dict(color="black", width=2), showlegend=False))

    # text annotation
    fig.add_annotation(x=-flange_length / 2, y=y_dim, ax=-flange_length, ay=y_dim, text="flange length", showarrow=False,
                       font=dict(size=12, color="black"), bgcolor="white", bordercolor="black", borderpad=2)

    # Left and right tick mark
    fig.add_trace(go.Scatter(x=[0, 0], y=[y_dim - 3, y_dim + 3], mode="lines", line=dict(color="black", width=2), showlegend=False))
    fig.add_trace(go.Scatter(x=[-flange_length, -flange_length], y=[y_dim - 5, y_dim + 5], mode="lines", line=dict(color="black", width=2), showlegend=False))

    return fig



def b_star_annotation(fig, flange_thickness, b_star):

    # b* annotation
    y_dim = flange_thickness / 4  # position above the flange

    # dim line
    fig.add_trace(go.Scatter(x=[0, -b_star], y=[y_dim, y_dim], mode="lines", line=dict(color="black", width=2), showlegend=False))

    # text annotation
    fig.add_annotation(x=-b_star / 2, y=y_dim, ax=-b_star, ay=y_dim, text="b*", showarrow=False,
                       font=dict(size=12, color="black"), bgcolor="white", bordercolor="black", borderpad=2)

    # Left and right tick mark
    fig.add_trace(go.Scatter(x=[0, 0], y=[y_dim - 5, y_dim + 5], mode="lines", line=dict(color="black", width=2), showlegend=False))
    fig.add_trace(go.Scatter(x=[-b_star, -b_star], y=[y_dim - 5, y_dim + 5], mode="lines", line=dict(color="black", width=2), showlegend=False))

    return fig


def hole_diameter_annotation(fig, b_star, flange_thickness, hole_diameter):

    # b* annotation
    y_dim = -flange_thickness * 1.2  # position above the flange
    xmin, xmax = -b_star - hole_diameter*0.5, -b_star + hole_diameter*0.5

    # dim line
    fig.add_trace(go.Scatter(x=[xmin, xmax], y=[y_dim, y_dim], mode="lines", line=dict(color="black", width=2), showlegend=False))

    # text annotation
    fig.add_annotation(x=-b_star, y=y_dim * 1.1, text="hole diameter", showarrow=False,
                       font=dict(size=12, color="black"), bgcolor="white", bordercolor="black", borderpad=2)

    # Left and right tick mark
    fig.add_trace(go.Scatter(x=[xmin, xmin], y=[y_dim - 5, y_dim + 5], mode="lines", line=dict(color="black", width=2), showlegend=False))
    fig.add_trace(go.Scatter(x=[xmax, xmax], y=[y_dim - 5, y_dim + 5], mode="lines", line=dict(color="black", width=2), showlegend=False))

    return fig


def flange_t_annotation(fig, flange_length, flange_thickness):

    x_dim = -flange_length-50  # position of vertical dimension line
    y_top = 0  # top of flange
    tick_size = 5  # length of horizontal ticks

    # Vertical dimension line
    fig.add_trace(go.Scatter(
        x=[x_dim, x_dim],
        y=[-flange_thickness, y_top],
        mode="lines",
        line=dict(color="black", width=2),
        showlegend=False
    ))

    # Top tick
    fig.add_trace(go.Scatter(
        x=[x_dim - tick_size, x_dim + tick_size],
        y=[y_top, y_top],
        mode="lines",
        line=dict(color="black", width=2),
        showlegend=False
    ))

    # Bottom tick
    fig.add_trace(go.Scatter(
        x=[x_dim - tick_size, x_dim + tick_size],
        y=[-flange_thickness, -flange_thickness],
        mode="lines",
        line=dict(color="black", width=2),
        showlegend=False
    ))

    # Label in middle
    fig.add_annotation(
        x=x_dim,  # slightly left of the line
        y=(y_top - flange_thickness) / 2,
        text="t",
        showarrow=False,
        font=dict(size=12, color="black"),
        bgcolor="white",
        bordercolor="black",
        borderpad=2
    )
    return fig


def flange_height_annotation(fig, total_height):
    x_offset = 60  # horizontal offset to left of flange
    y_top = 0
    y_bottom = -total_height
    tick_size = 5  # length of ticks

    # Vertical dimension line
    fig.add_trace(go.Scatter(
        x=[x_offset, x_offset],
        y=[y_bottom, y_top],
        mode="lines",
        line=dict(color="black", width=2),
        showlegend=False
    ))

    # Top tick
    fig.add_trace(go.Scatter(
        x=[x_offset - tick_size, x_offset + tick_size],
        y=[y_top, y_top],
        mode="lines",
        line=dict(color="black", width=2),
        showlegend=False
    ))

    # Bottom tick
    fig.add_trace(go.Scatter(
        x=[x_offset - tick_size, x_offset + tick_size],
        y=[y_bottom, y_bottom],
        mode="lines",
        line=dict(color="black", width=2),
        showlegend=False
    ))

    # Label in middle
    fig.add_annotation(
        x=x_offset,  # slight left offset for readability
        y=(y_top + y_bottom) / 2,
        text="total height",
        showarrow=False,
        font=dict(size=12, color="black"),
        bgcolor="white",
        bordercolor="black",
        borderpad=2
    )
    return fig

if __name__ == "__main__":

    l_flange_plotter(
        wall_thk=50,
        flange_length=300,
        flange_height=200,
        total_height=500,
        hole_diameter=76,
        b_star=150
    )