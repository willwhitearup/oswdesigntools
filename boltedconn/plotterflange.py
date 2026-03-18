import plotly.graph_objs as go
import numpy as np
import plotly.io as pio
from boltedconn.flange import BoltedFlange

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
    b = flange_obj.b
    bolt_size = flange_obj.bolt_obj.bolt_size
    n_bolts = flange_obj.n_bolts
    # radius between flange and wall thickness
    r = flange_height / 8.5
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
    # vertical dim lines
    vert_line_annotation(fig, flange_length * 0.1, 0, -total_height, "total height")
    vert_line_annotation(fig, -flange_length * 1.075, 0, -flange_height, "t")
    # horz dim lines
    horz_line_annotation(fig, -total_height * 1.2, -flange_length , 0, "flange length")
    horz_line_annotation(fig, flange_height / 3, -flange_length, -b_star, "a")  # a
    horz_line_annotation(fig, flange_height / 3, -b_star, 0, "b*")
    horz_line_annotation(fig, flange_height / 6, -wall_thk/2-b, -wall_thk/2, "b")
    horz_line_annotation(fig, -total_height * 1.1, 0, -wall_thk, "wall thk")
    horz_line_annotation(fig, -flange_height * 1.2, -b_star-hole_diameter/2, -b_star + hole_diameter/2, "hole diameter")

    # fig size / extent and layout
    fig.update_layout(
        title=f'L-flange diagram {n_bolts} x {bolt_size} bolts',
        width=800,  # adjust figure width
        height=800,  # adjust figure height (square looks nice)
        xaxis=dict(range=[-flange_length * 1.2, flange_length * 0.2], scaleanchor='y', title='X (mm)'),
        yaxis=dict(range=[-total_height * 1.2, flange_height * 0.5], title='Y (mm)'),
        showlegend=False)

    #fig.show()

    return pio.to_json(fig)

# add dimension lines to flange
###
####
def horz_line_annotation(fig, line_y_dim, min_x, max_x, annotation_text):
    # horz dim line
    fig.add_trace(go.Scatter(x=[min_x, max_x], y=[line_y_dim, line_y_dim], mode="lines", line=dict(color="black", width=2), showlegend=False))
    # Left and right tick mark
    fig.add_trace(go.Scatter(x=[max_x, max_x], y=[line_y_dim - 5, line_y_dim + 5], mode="lines", line=dict(color="black", width=2), showlegend=False))
    fig.add_trace(go.Scatter(x=[min_x, min_x], y=[line_y_dim - 5, line_y_dim + 5], mode="lines", line=dict(color="black", width=2), showlegend=False))
    # text annotation
    fig.add_annotation(x=(min_x + max_x) / 2, y=line_y_dim, text=annotation_text, showarrow=False, font=dict(size=12, color="black"), bgcolor="white", bordercolor="black", borderpad=2)
    return None

def vert_line_annotation(fig, line_x_dim, min_y, max_y, annotation_text):
    # Vertical dimension line
    fig.add_trace(go.Scatter(x=[line_x_dim, line_x_dim], y=[min_y, max_y], mode="lines", line=dict(color="black", width=2), showlegend=False))
    # Top tick Bottom tick
    fig.add_trace(go.Scatter(x=[line_x_dim - 5, line_x_dim + 5], y=[max_y, max_y], mode="lines", line=dict(color="black", width=2), showlegend=False))
    fig.add_trace(go.Scatter(x=[line_x_dim - 5, line_x_dim + 5], y=[min_y, min_y], mode="lines", line=dict(color="black", width=2), showlegend=False))
    # Label in middle
    fig.add_annotation(x=line_x_dim,  y=(min_y + max_y) / 2, text=annotation_text, showarrow=False, font=dict(size=12, color="black"), bgcolor="white", bordercolor="black", borderpad=2)
    return None


if __name__ == "__main__":

    l_flange_plotter(
        wall_thk=50,
        flange_length=300,
        flange_height=200,
        total_height=500,
        hole_diameter=76,
        b_star=150
    )