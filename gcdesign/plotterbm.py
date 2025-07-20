import numpy as np
import plotly.graph_objs as go
import plotly.io as pio


def create_cylinder(radius: float, length: float):
    theta = np.linspace(0, 2*np.pi, 20)
    z = np.linspace(0, -length, 2)  # from 0 down to -length
    theta_grid, z_grid = np.meshgrid(theta, z)
    x = radius * np.cos(theta_grid)
    y = radius * np.sin(theta_grid)
    z = z_grid
    return x.flatten(), y.flatten(), z.flatten()


def contraflexure_components(fx, fy, mx, my):
    z_x = mx / fy if fy != 0 else None
    z_y = -my / fx if fx != 0 else None
    return z_x, z_y


def label_bm_lines(fig, x, y, text_var, lengths):
    top_idx, bottom_idx = -1, 0  # first and last element
    # Top label
    fig.add_trace(go.Scatter3d(x=[x[top_idx]], y=[y[top_idx]], z=[lengths[top_idx]],
        mode='text', text=[f"{text_var[top_idx]:.2f}"], textposition='top center', showlegend=False))
    # Bottom label
    fig.add_trace(go.Scatter3d(x=[x[bottom_idx]], y=[y[bottom_idx]], z=[lengths[bottom_idx]],
        mode='text', text=[f"{text_var[bottom_idx]:.2f}"], textposition='top center', showlegend=False))
    return fig


def bm_plotter(fx: float, fy: float, mx: float, my: float, gc_length: float, pile_od: float):

    print(fx, fy, mx, my, gc_length, pile_od)

    lengths = np.linspace(0, -gc_length, 5)  # Z-axis goes down
    mx_t = mx - fy * lengths  # Bending about x-axis due to lateral fy
    my_t = my + fx * lengths   # Bending about y-axis due to lateral fx
    m_res = np.sqrt(mx_t ** 2 + my_t ** 2)  # Bending resultant

    fig = go.Figure()

    # scaling for gc length and moments
    maxx, maxy = max(abs(mx_t)), max(abs(my_t))

    max_total = max(maxy, maxx)

    # Res Moment
    fig.add_trace(go.Scatter3d(x=mx_t.tolist(), y=my_t.tolist(), z=lengths.tolist(),
        mode='lines+markers',
        name='Moment resultant (Nmm)',
        marker=dict(size=4),
        line=dict(width=4, color='red')
    ))

    fig = label_bm_lines(fig, mx_t, my_t, m_res, lengths)

    # Moment about X axis
    fig.add_trace(go.Scatter3d(x=mx_t.tolist(), y=np.zeros_like(lengths).tolist(), z=lengths.tolist(),
        mode='lines+markers',
        name='Moment about X',
        marker=dict(size=4),
        line=dict(width=4, dash='dash', color='green')
    ))

    fig = label_bm_lines(fig, mx_t, np.zeros(len(mx_t)), mx_t, lengths)

    # Moment about Y axis
    fig.add_trace(go.Scatter3d(x=np.zeros_like(lengths).tolist(), y=my_t.tolist(), z=lengths.tolist(),
        mode='lines+markers',
        name='Moment about Y',
        marker=dict(size=4),
        line=dict(width=4, dash='dash', color='orange')
    ))

    fig = label_bm_lines(fig, np.zeros(len(my_t)), my_t, my_t, lengths)

    # contraflexure label
    z_x, z_y = contraflexure_components(fx, fy, mx, my)
    xloc = "ABOVE" if z_x >= 0 else "BELOW"
    yloc = "ABOVE" if z_y >= 0 else "BELOW"

    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[z_x],
        mode='markers',
        name=f'X Moment CONTRAFLEXURE @z={round(abs(z_x), 2)}mm {xloc} top of connection',
        marker=dict(size=14, color='green', symbol='diamond')
    ))

    # Moment about Y axis
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[float(z_y)],
        mode='markers',
        name=f'Y Moment CONTRAFLEXURE @z={round(abs(z_y), 2)}mm {yloc} top of connection',
        marker=dict(size=14, color='orange', symbol='diamond')
    ))

    # add a grouted connection tube !
    pile_radius = pile_od / 2
    x_cyl, y_cyl, z_cyl = create_cylinder(radius=pile_radius, length=gc_length)
    # Scale tube radius independently by scaling x_cyl and y_cyl:
    scaling_factor = 0.25
    tube_scale = (scaling_factor / max(x_cyl)) * max_total
    x_cyl_scaled = x_cyl * tube_scale
    y_cyl_scaled = y_cyl * tube_scale
    fig.add_trace(go.Mesh3d(x=x_cyl_scaled.tolist(), y=y_cyl_scaled.tolist(), z=z_cyl.tolist(),
        alphahull=0,
        opacity=0.2,
        color='green',
        name='GC (diameter) not to scale'
    ))

    camera_scale = 1.5

    axis_scale_x = maxx / max_total
    axis_scale_y = maxy / max_total
    axis_scale = max(axis_scale_x, axis_scale_y)

    max_z = max(0.1 * gc_length, z_y, z_x)
    min_z = min(-1.1 * gc_length, z_y, z_x)
    # change the axis and scaling
    fig.update_layout(
        width=500,  # narrower width
        height=800,  # taller height, for skyscraper-like shape
        scene=dict(
            xaxis_title='x', yaxis_title='y', zaxis_title='z',
            aspectmode='manual',
            xaxis=dict(range=[-max_total * 1.1, max_total* 1.1]),
            yaxis=dict(range=[-max_total* 1.1, max_total* 1.1]),
            zaxis=dict(range=[min_z, max_z]),
            aspectratio=dict(x=axis_scale, y=axis_scale, z=2),  # Treat Z as equal length to X/Y
            camera=dict(eye=dict(x=camera_scale, y=camera_scale, z=camera_scale),)
        ),
        legend=dict(
            orientation="h",  # horizontal legend
            yanchor="top",
            y=-0.2,  # position legend below the plot (negative y)
            xanchor="center",
            x=0.5,  # centered horizontally
            bgcolor='rgba(255,255,255,0.8)',  # optional background
        ),
        title='GC bending moment diagram'
    )

    # fig.show()
    bm_plot_json = pio.to_json(fig)
    return bm_plot_json


if __name__ == "__main__":
    fx, fy = 1.1E+07, 2.6E+06
    mx, my = 2.9E+07, -1.2E+08
    gc_length, pile_od = 10000, 4200

    # leg_od = 3580.
    # leg_t = 80.
    # pile_od = 4200.
    # pile_t = 80.
    # gc_length = 10050.
    # n_sks = 14
    # sk_width = 40.
    # sk_height = 20.
    # sk_spacing = 365.
    #
    # # Load conditions (N and Nmm)
    fx =-193900
    fy = -9539000
    fz = -32520000

    mx = -63769500 * 1e3  # Nmm
    my = 1025350 * 1e3  # Nmm
    #
    # grout_strength = 80. # MPa (N/mm2)
    # grout_E = 38863.61  # MPa  (N/mm2)
    fx, fy, mx, my, gc_length, pile_od = -193900.0, -9539000.0, -63769500000.0, 1025350000.0, 10050.0, 4200.0
    bm_plotter(fx, fy, mx, my, gc_length, pile_od)