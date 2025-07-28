import numpy as np
import random
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


def jacket_plotter(jkt_obj: Jacket, lat: float, msl: float, splash_lower: float, splash_upper: float, show_tower: bool, twr_obj: Tower=None):

    if twr_obj is not None:
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
    bay_horizontals = jkt_obj.bay_horizontals
    xjt_elevs = jkt_obj.xjt_elevs

    jkt_line_clr = "red" if not jkt_obj.joint_objs else "rgba(0, 0, 0, 0)"

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
                             mode='lines', line=dict(color=jkt_line_clr), name='jacket'))
    fig.add_trace(go.Scatter(x=[tp_width / 2, batter_1_width / 2, jacket_footprint / 2, jacket_footprint / 2],
                             y=[tp_btm, batter_1_elev, batter_2_elev, -water_depth + stickup],
                             mode='lines', line=dict(color=jkt_line_clr), showlegend=False))

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
        # add some elevation data text
        fig.add_trace(go.Scatter(x=[-2 * water_levels_x_ext * jacket_footprint], y=[this_kjt_elev], mode='text',
                                 text=[f'k{k_this} EL {this_kjt_elev}'],
                                 textposition='top right', textfont=dict(color='grey'), showlegend=False))

        # plot a horizontal brace between this k joint elevation
        if bay_horizontals[idx]:
            fig.add_trace(go.Scatter(x=[-this_kjt_width / 2, this_kjt_width / 2], y=[this_kjt_elev, this_kjt_elev],
                                     mode='lines', line=dict(color=jkt_line_clr), showlegend=False))


        # as we are plotting a diagonal brace from this k joints to next, at the last k joint we cant go any further!
        if idx == len(kjt_elevs) - 1:
            break

        next_kjt_width = kjt_widths[f"kjt_{k_next}"]
        next_kjt_elev = kjt_elevs[f"kjt_{k_next}"]
        # do one brace at a time
        fig.add_trace(go.Scatter(x=[-this_kjt_width / 2, next_kjt_width / 2], y=[this_kjt_elev, next_kjt_elev],
                                 mode='lines', line=dict(color=jkt_line_clr), showlegend=False))
        fig.add_trace(go.Scatter(x=[this_kjt_width / 2, -next_kjt_width / 2], y=[this_kjt_elev, next_kjt_elev],
                                 mode='lines', line=dict(color=jkt_line_clr), showlegend=False))

    # X BRACE elevations
    for xidx, (xjt, xjt_elev) in enumerate(xjt_elevs.items()):
        # add a dotted line from the k joint
        fig.add_shape(type='line', x0=-xof, x1=-1.5 * water_levels_x_ext * jacket_footprint,
                      y0=xjt_elev, y1=xjt_elev, line=dict(color='grey', dash="dot"), showlegend=False)
        # add some text
        fig.add_trace(go.Scatter(x=[-1.5 * water_levels_x_ext * jacket_footprint], y=[xjt_elev], mode='text',
                                 text=[f'x{xidx+1} EL {xjt_elev:.1f}'],
                                 textposition='top right', textfont=dict(color='grey'), showlegend=False))

    # jacket batter
    # add a dotted line from the batter elevations
    batter_1_elev, batter_1_width = jkt_obj.batter_1_elev, jkt_obj.batter_1_width
    # only plot the batter elevation line if 2 batter angles
    if not jkt_obj.single_batter:
        fig.add_shape(type='line', x0=xof + batter_1_width / 2, x1=2 * water_levels_x_ext * jacket_footprint,
                      y0=batter_1_elev, y1=batter_1_elev, line=dict(color='grey', dash="dot"), showlegend=False)
        # add some elevation data text
        fig.add_trace(go.Scatter(x=[2 * water_levels_x_ext * jacket_footprint], y=[batter_1_elev], mode='text',
                                 text=[f'batter 1 EL{batter_1_elev}'], textposition='top left', textfont=dict(color='grey'), showlegend=False))
    # second batter i.e. where legs go vertical to go into piles
    batter_2_elev, batter_2_width = jkt_obj.batter_2_elev, jkt_obj.batter_2_width
    fig.add_shape(type='line', x0=xof + batter_2_width / 2, x1=2 * water_levels_x_ext * jacket_footprint,
                  y0=batter_2_elev, y1=batter_2_elev, line=dict(color='grey', dash="dot"), showlegend=False)
    # add some elevation data text
    fig.add_trace(go.Scatter(x=[2 * water_levels_x_ext * jacket_footprint], y=[batter_2_elev], mode='text',
                             text=[f'batter 2 EL{batter_2_elev}'], textposition='top left', textfont=dict(color='grey'), showlegend=False))

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

    # plot jacket sections (2D plotting)
    fig = leg_object_plotting(fig, jkt_obj.leg_objs)  # plot the Leg sections
    fig = leg_object_plotting(fig, jkt_obj.brace_a_objs)  # plot the Brace a sections
    fig = leg_object_plotting(fig, jkt_obj.brace_b_objs)  # plot the Brace b sections
    fig = leg_object_plotting(fig, jkt_obj.brace_hz_objs)  # plot the Brace horizontal sections
    fig, Dc = jnt_object_plotting(fig, jkt_obj.joint_objs)  # plot k and x joints (last so that colours plot nicely ontop of legs)

    # Pile stickups
    pile_width = 200 if Dc is None else Dc + 500  # pile plot width
    for x_center in [-jacket_footprint / 2, jacket_footprint / 2]:
        x0, x1 = x_center - pile_width / 2, x_center + pile_width / 2
        y0, y1 = -water_depth, -water_depth + stickup
        fig.add_trace(go.Scatter(x=[x0, x1, x1, x0, x0], y=[y0, y0, y1, y1, y0], fill='toself', fillcolor='#444444',
            line=dict(color='#444444'), mode='lines', name='pile stickup<br>(indicative)' if x_center < 0 else None, showlegend=(x_center < 0)
        ))
    fig.add_shape(type='line', x0=xof + x1, x1=2 * water_levels_x_ext * jacket_footprint,
                  y0=y1, y1=y1, line=dict(color='grey', dash="dot"), showlegend=False)
    # add some elevation data text
    fig.add_trace(go.Scatter(x=[2 * water_levels_x_ext * jacket_footprint], y=[y1], mode='text',
                             text=[f'pile top EL{y1}'], textposition='top left', textfont=dict(color='grey'), showlegend=False))

    # labels and title
    fig.update_layout(yaxis_title='elevation rel LAT [mm]', yaxis=dict(scaleanchor="x", scaleratio=1), legend=dict(x=1, y=1))
    # Show the plot
    # fig.show()

    # Convert the plot to JSON
    plot_json = pio.to_json(fig)

    return plot_json


def jnt_object_plotting(fig, joint_objs):
    """plot k and x joint objects
    """
    Dc = None
    for jidx, joint_obj in enumerate(joint_objs):
        if joint_obj.jt_type == "kjt":
            clr, line_clr = "rgba(255, 0, 200, 0.4)", "rgb(180, 0, 140)"
            Dc = joint_obj.Dc  # get diameter of last K joint in the jacket and return it
        elif joint_obj.jt_type == "xjt":
            clr, line_clr = "rgba(180, 30, 200, 0.4)", "rgb(120, 20, 160)"
        kinked_can = joint_obj.kinked_can
        for idx, (k, v) in enumerate(joint_obj.joint_poly_coords_transf.items()):
            # kinked Can section plotting logic...
            if k == "can" and kinked_can:
                can_poly_coords = v
                for pidx, (x, y) in enumerate(can_poly_coords):
                    show_in_legend = not joint_obj.mirror and idx == 0 and pidx == 0
                    name = joint_obj.jt_name if show_in_legend else None
                    fig.add_trace(
                        go.Scatter(x=x, y=y, line=dict(color=clr), name=name,
                                   mode="none", fill='toself', fillcolor=clr,
                                   showlegend=show_in_legend
                                   ))
                    # line around polygon plot
                    fig.add_trace(go.Scatter(x=x + [x[0]], y=y + [y[0]], mode="lines", line=dict(color=line_clr),
                                             showlegend=False))

            # all other polygons e.g. stubs of the Joint (including normal non-kinked Can, are just rectangles)
            else:
                x, y = v[0], v[1]

                show_in_legend = not joint_obj.mirror and idx == 0
                name = joint_obj.jt_name if show_in_legend else None

                # plot the polygon (use toself as polygon not closed)
                fig.add_trace(go.Scatter(x=x, y=y, line=dict(color=clr), name=name,
                                         mode="none", fill='toself', fillcolor=clr,
                                         showlegend=show_in_legend
                                         ))
                # line outline of polygon (with line, repeated first point)
                fig.add_trace(go.Scatter(x=x + [x[0]], y=y + [y[0]], mode="lines", line=dict(color=line_clr), showlegend=False))

    return fig, Dc


def leg_object_plotting(fig, leg_objs):
    """plot leg and brace sections
    """
    for leg_obj in leg_objs:
        leg_name = leg_obj.leg_name
        if leg_obj.member_type == "LEG":

            clr = "rgba(30, 140, 255, 0.4)"  # brighter, more azure-like fill
            line_clr = "rgb(20, 100, 230)"

            cone_clr, cone_line_clr = "rgba(135, 206, 250, 0.6)", "rgb(0, 0, 128)"  # LightSkyBlue with 60% opacity

            show_in_legend = not leg_obj.mirror
            name = leg_name if show_in_legend else None
        elif leg_obj.member_type == "BRC":
            clr, line_clr = "rgba(50, 205, 50, 0.4)", "rgb(50, 205, 50)"
            cone_clr, cone_line_clr = "rgba(135, 206, 250, 0.6)", "rgb(0, 0, 128)"  # LightSkyBlue with 60% opacity
            show_in_legend = ("aR" not in leg_name) and ("bL" not in leg_name) and ("bR" not in leg_name)
            name = leg_name.replace("_aL", "") if show_in_legend else None
        else:
            continue  # skip if unknown member_type

        # Plot leg_a polygons
        for aidx, (x, y) in enumerate(leg_obj.leg_a_poly_coords):
            show_legend = show_in_legend and aidx == 0
            leg_name_to_use = name if show_legend else None
            fig.add_trace(go.Scatter(
                x=x, y=y, line=dict(color=clr), name=leg_name_to_use,
                mode="none", fill='toself', fillcolor=clr, showlegend=show_legend
            ))
            fig.add_trace(go.Scatter(x=x + [x[0]], y=y + [y[0]], mode="lines",line=dict(color=line_clr), showlegend=False
            ))

        # Plot leg_b polygons if present
        leg_b_poly_coords = leg_obj.leg_b_poly_coords
        if leg_b_poly_coords is not None:
            for (x, y) in leg_b_poly_coords:
                fig.add_trace(go.Scatter(
                    x=x, y=y, line=dict(color=clr), name=None,
                    mode="none", fill='toself', fillcolor=clr, showlegend=False
                ))
                fig.add_trace(go.Scatter(
                    x=x + [x[0]], y=y + [y[0]], mode="lines",
                    line=dict(color=line_clr), showlegend=False
                ))

        # Plot cone polygon if present
        cone_poly_coords = leg_obj.cone_poly_coords
        if cone_poly_coords is not None:

            x, y = cone_poly_coords[0], cone_poly_coords[1]
            fig.add_trace(go.Scatter(x=x, y=y, line=dict(color=cone_clr), name=(name + " cone" if name else None),
                                     mode="none", fill='toself', fillcolor=cone_clr,
                                     showlegend=show_in_legend))
            fig.add_trace(go.Scatter(x=x + [x[0]], y=y + [y[0]], mode="lines", line=dict(color=cone_line_clr), showlegend=False
            ))

    return fig
