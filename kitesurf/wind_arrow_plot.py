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
    """Plots a filled wind arrow centered at (0,0) with meteorological color scale."""
    L = 10 * arrow_length_scale
    shaft_length = L * 0.6
    half = L / 2 + 0.5
    theta = np.radians(180 - wind_direction)

    x = np.array([-shaft_width/2, shaft_width/2, shaft_width/2, head_width/2, 0, -head_width/2, -shaft_width/2])
    y = np.array([0, 0, shaft_length, shaft_length, L, shaft_length, shaft_length])

    x -= np.mean(x)
    y -= np.mean(y)

    x_rot = (x * np.cos(theta) - y * np.sin(theta)).tolist()
    y_rot = (x * np.sin(theta) + y * np.cos(theta)).tolist()

    color = wind_speed_to_color(wind_speed, max_speed)

    fig = go.Figure(go.Scatter(
        x=x_rot, y=y_rot,
        mode='lines', fill='toself',
        fillcolor=color, line=dict(color=color, width=1),
        hoverinfo='skip', showlegend=False
    ))
    arr_size = 25  # change the wind arrow figure size
    fig.update_layout(
        width=arr_size, height=arr_size,
        margin=dict(l=0, r=0, t=0, b=0, pad=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(range=[-half, half], visible=False, showgrid=False, zeroline=False, scaleanchor="y"),
        yaxis=dict(range=[-half, half], visible=False, showgrid=False, zeroline=False)
    )

    return pio.to_json(fig)


# Example usage
if __name__ == "__main__":
    # Low, medium, high, max
    _ = plot_wind_arrow(wind_speed=5, wind_direction=60)