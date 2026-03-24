import plotly.graph_objects as go
import plotly.io as pio
import numpy as np


def wind_speed_to_color(speed, max_speed=40):
    """
    Maps wind speed to a meteorological-style color scale:
    blue → green → yellow → red → deep purple
    """
    # Normalize
    norm = np.clip(speed / max_speed, 0, 1)

    # Define color stops
    stops = [
        (0.0, (0, 0, 255)),      # Blue
        (0.25, (0, 255, 0)),     # Green
        (0.5, (255, 255, 0)),    # Yellow
        (0.75, (255, 0, 0)),     # Red
        (1.0, (106, 0, 218))     # Deep purple
    ]

    # Find which segment norm falls in
    for i in range(len(stops)-1):
        if stops[i][0] <= norm <= stops[i+1][0]:
            t = (norm - stops[i][0]) / (stops[i+1][0] - stops[i][0])
            r = int(stops[i][1][0] + t * (stops[i+1][1][0] - stops[i][1][0]))
            g = int(stops[i][1][1] + t * (stops[i+1][1][1] - stops[i][1][1]))
            b = int(stops[i][1][2] + t * (stops[i+1][1][2] - stops[i][1][2]))
            return f"rgb({r},{g},{b})"

    return f"rgb{stops[-1][1]}"

def plot_wind_arrow(wind_speed, wind_direction, max_speed=25, shaft_width=4, head_width=8, arrow_length_scale=0.7):
    """
    Plots a filled wind arrow centered at (0,0) with meteorological color scale.
    """
    theta = np.radians(wind_direction)
    L = 10 * arrow_length_scale
    shaft_length = L * 0.6

    # Arrow polygon local coordinates
    x = np.array([
        -shaft_width/2, shaft_width/2, shaft_width/2,
        head_width/2, 0, -head_width/2, -shaft_width/2
    ])
    y = np.array([
        0, 0, shaft_length,
        shaft_length, L, shaft_length, shaft_length
    ])

    # Shift to center
    centroid_x = np.mean(x)
    centroid_y = np.mean(y)
    x_centered = x - centroid_x
    y_centered = y - centroid_y

    # Rotate
    x_rot = x_centered * np.cos(theta) - y_centered * np.sin(theta)
    y_rot = x_centered * np.sin(theta) + y_centered * np.cos(theta)

    x_rot = x_rot.tolist()  # ADD THIS
    y_rot = y_rot.tolist()  # ADD THIS

    # Color from meteorological scale
    color = wind_speed_to_color(wind_speed, max_speed)

    # Plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_rot,
        y=y_rot,
        mode='lines',
        fill='toself',
        fillcolor=color,
        line=dict(color=color, width=1),
        hoverinfo='skip',
        showlegend=False
    ))

    fig.update_layout(
        width=50,
        height=50,
        margin=dict(l=0, r=0, t=0, b=0, pad=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            range=[-10, 10],
            visible=False,
            showgrid=False,
            zeroline=False,
            scaleanchor="y"
        ),
        yaxis=dict(
            range=[-10, 10],
            visible=False,
            showgrid=False,
            zeroline=False
        ),
        showlegend=False
    )

    # fig.show()
    pio_json = pio.to_json(fig)
    return pio_json


# Example usage
if __name__ == "__main__":
    # Low, medium, high, max
    for ws in [5, 12, 18, 25]:
        plot_wind_arrow(wind_speed=ws, wind_direction=60)