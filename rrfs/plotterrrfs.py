import plotly.graph_objects as go
import plotly.io as pio


def plotly_fig_plot(plot_title: str, xaxis_label: str, curves: list):
    """Create a Plotly line plot with one or more curves. The y-axis is the RRF.

    Parameters
    ----------
    plot_title : str
        Plot title displayed at the top of the figure.

    xaxis_label : str
        Label for the x-axis.

    curves : list
        List of dictionaries defining each curve.

        Each dictionary must contain:
            {
                "xvals": list,
                "yvals": list,
                "label": str
            }

    Returns
    -------
    plot_json : str
        Plotly figure converted to JSON format for frontend rendering.
    """

    # Create empty figure
    fig = go.Figure()

    # Add curves
    for curve in curves:

        fig.add_trace(
            go.Scatter(
                x=curve["xvals"],
                y=curve["yvals"],
                mode='lines',
                name=curve["label"]
            )
        )

    # Update layout
    fig.update_layout(
        title=plot_title,

        xaxis=dict(
            title=xaxis_label,
            showgrid=True,
            gridcolor='lightgray'
        ),

        yaxis=dict(
            title="RRF",
            showgrid=True,
            gridcolor='lightgray'
        ),

        hovermode='closest',
        template='plotly_white'
    )

    # fig.show()

    plot_json = pio.to_json(fig)

    return plot_json