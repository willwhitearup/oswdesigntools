import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

from jktdesign.jacket import Jacket
from jktdesign.tower import Tower


def c_o_a_targetline(pt1, pt2, tp_btm, tp_width, c_o_a_LAT):
    vector_x, vector_y = pt1[0] - pt2[0],  pt1[1] - pt2[1]
    length = np.sqrt(vector_x**2 + vector_y**2)
    l2 = np.sqrt((0 - 0.5*tp_width) ** 2 + (c_o_a_LAT - tp_btm) ** 2)
    normalized_vector_x, normalized_vector_y = vector_x / length, vector_y / length
    x4 = pt1[0] + l2 * normalized_vector_x
    y4 = pt1[1] + l2 * normalized_vector_y
    return x4, y4


def jacket_plotter(twr_obj: Tower, jkt_obj: Jacket, lat: float, msl: float, splash_lower: float, splash_upper: float, show_tower: bool):

    # tower object
    rna_cog = twr_obj.rna_cog
    interface_elev = twr_obj.interface_elev
    c_o_a_LAT = twr_obj.c_o_a_LAT

    # jacket object
    tp_width = jkt_obj.tp_width
    tp_btm = jkt_obj.tp_btm
    batter_1_width = jkt_obj.batter_1_width
    batter_1_elev = jkt_obj.batter_1_elev
    jacket_footprint = jkt_obj.jacket_footprint
    batter_2_elev = jkt_obj.batter_2_elev
    water_depth = jkt_obj.water_depth
    stickup = jkt_obj.stickup
    kjt_elevs = jkt_obj.kjt_elevs
    kjt_widths = jkt_obj.kjt_widths
    xjt_elevs = jkt_obj.xjt_elevs

    # Create the plot
    fig = go.Figure()

    # WATER LEVELS------------------------------------------------------------------------------------------
    water_levels_x_ext = 1  # multiplier on the jacket footprint
    # LAT
    fig.add_shape(type='line', x0=-water_levels_x_ext*jacket_footprint, x1=water_levels_x_ext*jacket_footprint, y0=lat, y1=lat, line=dict(color='blue', dash='dash'), showlegend=False)
    fig.add_trace(go.Scatter(x=[1 * jacket_footprint], y=[lat], mode='text', text=['LAT'], textposition='top right', textfont=dict(color='blue'), showlegend=False))
    # MSL
    fig.add_shape(type='line', x0=-water_levels_x_ext*jacket_footprint, x1=water_levels_x_ext*jacket_footprint, y0=msl, y1=msl, line=dict(color='grey', dash='dash'), showlegend=False)
    fig.add_trace(go.Scatter(x=[1.2 * jacket_footprint], y=[msl], mode='text', text=['MSL'], textposition='top right', textfont=dict(color='grey'), showlegend=False))
    # splash lower
    fig.add_shape(type='line', x0=-water_levels_x_ext*jacket_footprint, x1=water_levels_x_ext*jacket_footprint, y0=splash_lower, y1=splash_lower, line=dict(color='dodgerblue', dash='dash'), showlegend=False)
    fig.add_trace(go.Scatter(x=[1 * jacket_footprint], y=[splash_lower], mode='text', text=['splash_lower'], textposition='top right', textfont=dict(color='dodgerblue'), showlegend=False))
    # splash upper
    fig.add_shape(type='line', x0=-water_levels_x_ext*jacket_footprint, x1=water_levels_x_ext*jacket_footprint, y0=splash_upper, y1=splash_upper, line=dict(color='dodgerblue', dash='dash'), showlegend=False)
    fig.add_trace(go.Scatter(x=[1 * jacket_footprint], y=[splash_upper], mode='text', text=['splash_upper'], textposition='top right', textfont=dict(color='dodgerblue'), showlegend=False))

    # MUDLINE----------------------------------------------------------------------------------------------
    fig.add_shape(type='line', x0=-water_levels_x_ext*jacket_footprint, x1=water_levels_x_ext*jacket_footprint, y0=-water_depth, y1=-water_depth, line=dict(color='brown'), showlegend=False)
    fig.add_trace(go.Scatter(x=[1 * jacket_footprint], y=[-water_depth], mode='text', text=['mudline'], textposition='top right', textfont=dict(color='brown'), showlegend=False))

    # JKT LEGS
    fig.add_trace(go.Scatter(x=[-tp_width / 2, -batter_1_width / 2, -jacket_footprint / 2, -jacket_footprint / 2],
                             y=[tp_btm, batter_1_elev, batter_2_elev, -water_depth + stickup],
                             mode='lines', line=dict(color='red'), name='jacket'))
    fig.add_trace(go.Scatter(x=[tp_width / 2, batter_1_width / 2, jacket_footprint / 2, jacket_footprint / 2],
                             y=[tp_btm, batter_1_elev, batter_2_elev, -water_depth + stickup],
                             mode='lines', line=dict(color='red'), showlegend=False))

    xof = 1500  # dotted lines to be slightly offset from the plot
    # JKT BRACES----------------------------------------------------------------------------------------------
    for idx, (kjt, this_kjt_elev) in enumerate(kjt_elevs.items()):

        # get the k numbering
        k_this, k_next = idx + 1, idx + 2

        # get the elevation of the current k joint and add some info to the plot figure
        this_kjt_width = kjt_widths[f"kjt_{k_this}"]

        # add a dotted line from the k joint
        fig.add_shape(type='line', x0=-xof - this_kjt_width / 2, x1=-2 * water_levels_x_ext * jacket_footprint,
                      y0=this_kjt_elev, y1=this_kjt_elev, line=dict(color='grey', dash="dot"), showlegend=False)
        # add some text
        fig.add_trace(go.Scatter(x=[-2 * water_levels_x_ext * jacket_footprint], y=[this_kjt_elev], mode='text',
                                 text=[f'k{k_this} EL {this_kjt_elev}'],
                                 textposition='top right', textfont=dict(color='grey'), showlegend=False))


        if idx == len(kjt_elevs) - 1:
            break

        next_kjt_width = kjt_widths[f"kjt_{k_next}"]
        next_kjt_elev = kjt_elevs[f"kjt_{k_next}"]
        # do one brace at a time
        fig.add_trace(go.Scatter(x=[-this_kjt_width / 2, next_kjt_width / 2], y=[this_kjt_elev, next_kjt_elev],
                                 mode='lines', line=dict(color='red'), showlegend=False))
        fig.add_trace(go.Scatter(x=[this_kjt_width / 2, -next_kjt_width / 2], y=[this_kjt_elev, next_kjt_elev],
                                 mode='lines', line=dict(color='red'), showlegend=False))

    # X BRACE elevations
    for xidx, (xjt, xjt_elev) in enumerate(xjt_elevs.items()):
        # add a dotted line from the k joint
        fig.add_shape(type='line', x0=-xof, x1=-1.5 * water_levels_x_ext * jacket_footprint,
                      y0=xjt_elev, y1=xjt_elev, line=dict(color='grey', dash="dot"), showlegend=False)
        # add some text
        fig.add_trace(go.Scatter(x=[-1.5 * water_levels_x_ext * jacket_footprint], y=[xjt_elev], mode='text',
                                 text=[f'x{idx+1} EL {xjt_elev:.1f}'],
                                 textposition='top right', textfont=dict(color='grey'), showlegend=False))


    # Pile stickups
    fig.add_trace(go.Scatter(x=[-jacket_footprint / 2, -jacket_footprint / 2], y=[-water_depth, -water_depth + stickup],
                             mode='lines', name='stickup', line=dict(color='black', width=5)))
    fig.add_trace(go.Scatter(x=[jacket_footprint / 2, jacket_footprint / 2], y=[-water_depth, -water_depth + stickup],
                             mode='lines', line=dict(color='black', width=5), showlegend=False))

    # Tower and TP----------------------------------------------------------------------------------------------
    if show_tower:
        # TP box-----------------------------------------------------------------------------------------------------
        fig.add_trace(go.Scatter(x=[-tp_width/2, -tp_width/2, tp_width/2, tp_width/2, -tp_width/2],
                                 y=[tp_btm, interface_elev, interface_elev, tp_btm, tp_btm],
                                 fill='toself', line=dict(color='rgba(0,0,0,0)'), fillcolor='purple', opacity=0.7, name='TP'))

        # RNA and tower----------------------------------------------------------------------------------------------
        fig.add_trace(go.Scatter(x=[0], y=[rna_cog], mode='markers', marker=dict(color='black'), name='RNA'))
        fig.add_trace(go.Scatter(x=[0, 0], y=[interface_elev, rna_cog], mode='lines', line=dict(color='black'), showlegend=False))
        fig.add_trace(go.Scatter(x=[0], y=[c_o_a_LAT], mode='markers', marker=dict(symbol='star', color='black', size=15), name='WTG CoA'))
        # add the CoA target line
        x4, y4 = c_o_a_targetline([-tp_width / 2, tp_btm], [-batter_1_width / 2, batter_1_elev], tp_btm, tp_width, c_o_a_LAT)
        x5, y5 = c_o_a_targetline([tp_width / 2, tp_btm], [batter_1_width / 2, batter_1_elev], tp_btm, tp_width, c_o_a_LAT)
        fig.add_trace(go.Scatter(x=[-tp_width / 2, x4], y=[tp_btm, y4], mode='lines', line=dict(color='red', dash="dash"), name='WTG CoA target'))
        fig.add_trace(go.Scatter(x=[tp_width / 2, x5], y=[tp_btm, y5], mode='lines', line=dict(color='red', dash="dash"), showlegend=False))

    else:
        # TP btm line only--------------------------------------------------------------------------------------------------
        fig.add_trace(go.Scatter(x=[-tp_width/2, tp_width/2], y=[tp_btm, tp_btm], line=dict(color='purple'), name='TP btm width'))

    # Add labels and title
    water_levels_x_ext=0.1
    fig.update_layout(
        yaxis_title='elevation rel LAT [mm]',
        #xaxis=dict(range=[-water_levels_x_ext * jacket_footprint, water_levels_x_ext * jacket_footprint]),  #set the x-axis extents
        yaxis=dict(scaleanchor="x", scaleratio=1),
        legend=dict(x=1, y=1)
    )
    # Show the plot
    # fig.show()

    # Convert the plot to JSON
    plot_json = pio.to_json(fig)

    return plot_json