import plotly.graph_objects as go
import numpy as np

def wind_speed_to_color(speed, max_speed=25):
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

    # fallback
    return f"rgb{stops[-1][1]}"

def plot_wind_arrow(wind_speed, wind_direction, max_speed=25, shaft_width=4, head_width=8, arrow_length_scale=0.7):
    """
    Plots a filled wind arrow centered at (0,0) with meteorological color scale.
    """
    theta = np.radians(wind_direction)
    L = wind_speed * arrow_length_scale
    shaft_length = L * 0.6
    head_length = L * 0.4

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
        line=dict(color=color),
        hoverinfo='skip'
    ))

    fig.update_layout(
        title=f"Wind Arrow: {wind_speed:.1f} m/s at {wind_direction}°",
        xaxis=dict(range=[-max_speed, max_speed], zeroline=False, showgrid=False),
        yaxis=dict(range=[-max_speed, max_speed], zeroline=False, showgrid=False),
        width=400,
        height=400,
        plot_bgcolor='white',
        showlegend=False
    )

    fig.show()


# Example usage
if __name__ == "__main__":
    # Low, medium, high, max
    for ws in [5, 12, 18, 25]:
        plot_wind_arrow(wind_speed=ws, wind_direction=60)