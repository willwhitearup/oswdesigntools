from flask import Flask, render_template, session, request, jsonify
import json
import pandas as pd
from jktdesign.jacket import Jacket
from jktdesign.mass import calculate_jkt_mto
from jktdesign.plotter import jacket_plotter
from jktdesign.create2Dsections import (get_kjt_geom_form_data, create_2D_kjoint_data, get_xjt_geom_form_data,
                                        get_leg_geom_form_data, create_2D_xjoint_data, create_2D_leg_data,
                                        get_brace_geom_form_data, create_2D_brace_a_data, create_2D_brace_b_data,
                                        create_2D_brace_hz_data)

app = Flask(__name__)

@app.route('/jktsections', methods=['POST'])
def jacket_sections_plot():

    # get the plotly figure from plot_json
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON received'}), 400

    # get the form data back (input boxes)
    form_data = data.get('form_data', {})
    # print("form_data", form_data)

    # todo, only ID diameter refs done so far
    if form_data["joint_type_geometry"] != 'ID_constant':
        raise Exception("Joint2D sections have only been created using constant ID currently. Exiting...")

    kjt_geom_data = get_kjt_geom_form_data(form_data)
    xjt_geom_data = get_xjt_geom_form_data(form_data)
    leg_geom_data = get_leg_geom_form_data(form_data)
    brace_geom_data, brace_hz_geom_data = get_brace_geom_form_data(form_data)

    # get the original jacket data (from architect page)
    jkt_json_str = session.get('jkt_json', '{}')
    jkt_dict = json.loads(jkt_json_str)
    jkt_obj = create_jacket_from_session()

    # create the K-Joint 2DJoint objects
    kjt_2D_objs = create_2D_kjoint_data(kjt_geom_data)
    for kjt_2D_obj in kjt_2D_objs:
        jkt_obj.add_joint_obj(kjt_2D_obj, jt_type="kjt")

    extend_k1 = True  # set this option to True for time being
    jkt_obj.extend_k1_to_TP(extend_k1)
    # check if kjts are designed ok
    jkt_obj.kjt_warnings_check()

    # create the X-Joint 2DJoint objects
    xjt_2D_objs = create_2D_xjoint_data(xjt_geom_data)
    for xjt_2D_obj in xjt_2D_objs:
        jkt_obj.add_joint_obj(xjt_2D_obj, jt_type="xjt")

    # create the leg 2D sections (functionality for cones, kinks and straight legs)
    leg_objs = create_2D_leg_data(leg_geom_data, kjt_geom_data)
    for leg_obj in leg_objs:
        jkt_obj.add_leg_obj(leg_obj)

    # create the brace a 2D sections (spans kjts to xjts)
    brace_a_objs = create_2D_brace_a_data(brace_geom_data, kjt_geom_data, xjt_geom_data)
    for brace_a_obj in brace_a_objs:
        jkt_obj.add_brace_a_obj(brace_a_obj)

    # create the brace b 2D sections (spans xjts to kjts)
    brace_b_objs = create_2D_brace_b_data(brace_geom_data, kjt_geom_data, xjt_geom_data)
    for brace_b_obj in brace_b_objs:
        jkt_obj.add_brace_b_obj(brace_b_obj)

    # create bay horizontals 2D sections (spans kjts)
    brace_hz_objs = create_2D_brace_hz_data(brace_hz_geom_data, kjt_geom_data)
    for brace_hz_obj in brace_hz_objs:
        jkt_obj.add_brace_hz_obj(brace_hz_obj)

    # design warnings and errors and return to app
    warnings = jkt_obj.warnings

    # reconstruct the plot each time a new post is generated (so that the existing plot is not scattered with new data everytime a post request happens)
    updated_plot_json = jacket_plotter(jkt_obj, jkt_dict['lat'], jkt_dict['msl'], jkt_dict['splash_lower'], jkt_dict['splash_upper'], show_tower=False, twr_obj=None)

    # create mto dataframe
    df_mto = calculate_jkt_mto(jkt_obj)

    session['df_mto'] = df_mto.to_json()

    return jsonify({'message': 'Plot updated successfully',
                    'plot_json': updated_plot_json,
                    "warnings": warnings
                    })


@app.route('/jktsections', methods=['GET'])
def jacket_sections():
    """gets jkt_json data from architect.py and architect.html webpage
    """
    jkt_json_str = session.get('jkt_json', '{}')
    jkt_dict = json.loads(jkt_json_str)

    # create error message just so the page loads if user go theres initially
    if not jkt_dict:
        return render_template('jktsections.html',
                               error_message="Warning! First create your model on the Architect page before assigning sections!",
                               jkt_dict={}, plot_json={}, kjt_n_braces={})

    # get out some data to create the plotly figure
    lat, msl, splash_lower, splash_upper = jkt_dict['lat'], jkt_dict['msl'], jkt_dict['splash_lower'], jkt_dict['splash_upper']
    # create the jacket object
    jkt_obj = create_jacket_from_session()
    kjt_n_braces = jkt_obj.kjt_n_braces
    bay_horizontals = jkt_obj.bay_horizontals

    plot_json_str = jacket_plotter(jkt_obj, lat, msl, splash_lower, splash_upper, show_tower=False)
    plot_json = json.loads(plot_json_str)

    return render_template('jktsections.html', jkt_dict=jkt_dict,
                           plot_json=plot_json,
                           kjt_n_braces=kjt_n_braces,
                           bay_horizontals=bay_horizontals,
                           bay_horizontals_json=json.dumps(bay_horizontals))


def create_jacket_from_session():
    jkt_json_str = session.get('jkt_json', '{}')  # todo check on initial load
    jkt_dict = json.loads(jkt_json_str)

    return Jacket(
        jkt_dict['interface_elev'],
        jkt_dict['tp_width'],
        jkt_dict['tp_btm'],
        jkt_dict['tp_btm_k1_voffset'],
        jkt_dict['batter_1_theta'],
        jkt_dict['batter_1_elev'],
        jkt_dict['jacket_footprint'],
        jkt_dict['stickup'],
        jkt_dict['bay_heights'],
        jkt_dict['btm_vert_leg_length'],
        jkt_dict['water_depth'],
        jkt_dict['single_batter'],
        jkt_dict['bay_horizontals']
    )