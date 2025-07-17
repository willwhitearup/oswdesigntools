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


def bm_plotter(fx: float, fy: float, mx: float, my: float, gc_length: float, gc_radius: float):

    lengths = np.linspace(0, -gc_length, 5)  # Z-axis goes down
    mx_t = mx - fy * lengths  # Bending about x-axis due to lateral fy
    my_t = my + fx * lengths   # Bending about y-axis due to lateral fx
    m_res = np.sqrt(mx_t ** 2 + my_t ** 2)  # Bending resultant

    fig = go.Figure()

    # scaling for gc length and moments
    maxx, maxy = max(abs(mx_t)), max(abs(my_t))

    max_total = max(maxy, maxx)
    axis_scale_x = maxx / max_total
    axis_scale_y = maxy / max_total

    # Res Moment
    fig.add_trace(go.Scatter3d(x=mx_t.tolist(), y=my_t.tolist(), z=lengths.tolist(),
        mode='lines+markers',
        name='Res',
        marker=dict(size=4),
        line=dict(width=4, color='red')
    ))

    fig = label_bm_lines(fig, mx_t, my_t, m_res, lengths)

    # Moment about X axis
    fig.add_trace(go.Scatter3d(x=mx_t.tolist(), y=np.zeros_like(lengths), z=lengths.tolist(),
        mode='lines+markers',
        name='Moment about X',
        marker=dict(size=4),
        line=dict(width=4, dash='dash', color='green')
    ))

    fig = label_bm_lines(fig, mx_t, np.zeros(len(mx_t)), mx_t, lengths)

    # Moment about Y axis
    fig.add_trace(go.Scatter3d(x=np.zeros_like(lengths), y=my_t.tolist(), z=lengths.tolist(),
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
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[z_y],
        mode='markers',
        name=f'Y Moment CONTRAFLEXURE @z={round(abs(z_y), 2)}mm {yloc} top of connection',
        marker=dict(size=14, color='orange', symbol='diamond')
    ))


    # add a grouted connection tube !
    x_cyl, y_cyl, z_cyl = create_cylinder(radius=gc_radius, length=gc_length)
    # Scale tube radius independently by scaling x_cyl and y_cyl:
    scaling_factor = 0.25
    tube_scale = (scaling_factor / max(x_cyl)) * max_total
    x_cyl_scaled = x_cyl * tube_scale
    y_cyl_scaled = y_cyl * tube_scale

    fig.add_trace(go.Mesh3d(x=x_cyl_scaled, y=y_cyl_scaled, z=z_cyl,
        alphahull=0,
        opacity=0.2,
        color='green',
        name='GC (diameter) not to scale'
    ))

    # change the axis and scaling
    fig.update_layout(
        scene=dict(
            xaxis_title='x',
            yaxis_title='y',
            zaxis_title='z',
            aspectmode='manual',
            xaxis=dict(range=[-maxx, maxx]),
            yaxis=dict(range=[-maxy, maxy]),
            zaxis=dict(range=[-1.2 * gc_length, 0.2 * gc_length]),
            aspectratio=dict(x=axis_scale_x, y=axis_scale_y, z=2),  # Treat Z as equal length to X/Y
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        title='GC bending moment diagram'
    )

    # fig.show()

    bm_plot_json = pio.to_json(fig)
    return bm_plot_json


if __name__ == "__main__":
    fx, fy = 1.1E+07, 2.6E+06
    mx, my = 2.9E+07, -1.2E+08
    gc_length, gc_radius = 10000, 3000
    bm_plotter(fx, fy, mx, my, gc_length, gc_radius)