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

    session['jktsections_form_data'] = form_data

    section_alignment = form_data.get("section_alignment", "ID_constant")
    section_definition = form_data.get("section_definition", "by_OD")

    kjt_geom_data = get_kjt_geom_form_data(form_data)
    xjt_geom_data = get_xjt_geom_form_data(form_data)
    leg_geom_data = get_leg_geom_form_data(form_data)
    brace_geom_data, brace_hz_geom_data = get_brace_geom_form_data(form_data)
    cone_taper = float(form_data.get("cone_taper", 4.))

    # get the original jacket data (from architect page)
    jkt_json_str = session.get('jkt_json', '{}')
    jkt_dict = json.loads(jkt_json_str)
    jkt_obj = create_jacket_from_session()  # define the jkt object from the 1D session (only at this point)


    jkt_obj.set_cone_taper_ratio(cone_taper)  # set the cone taper ratio (used if sections are different sizes)
    jkt_obj.set_tubular_section_alignment(section_alignment)  # set tubular sections alignment (by ID or by mid Dia # not by OD for jackets)

    # create the K-Joint 2DJoint objects
    kjt_2D_objs = create_2D_kjoint_data(kjt_geom_data, section_definition)
    for kjt_2D_obj in kjt_2D_objs:
        jkt_obj.add_joint_obj(kjt_2D_obj, jt_type="kjt")

    extend_k1 = True  # set this option to True for time being (extends k1 to underside of TP)
    jkt_obj.extend_k1_to_TP(extend_k1)
    # check if kjts are designed ok
    jkt_obj.kjt_warnings_check()

    # create the X-Joint 2DJoint objects
    xjt_2D_objs = create_2D_xjoint_data(xjt_geom_data, section_definition)
    for xjt_2D_obj in xjt_2D_objs:
        jkt_obj.add_joint_obj(xjt_2D_obj, jt_type="xjt")

    # create the leg 2D sections (functionality for cones, kinks and straight legs)
    leg_objs = create_2D_leg_data(leg_geom_data, kjt_geom_data, section_definition)
    for leg_obj in leg_objs:
        jkt_obj.add_leg_obj(leg_obj)

    # create the brace a 2D sections (spans kjts to xjts)
    brace_a_objs = create_2D_brace_a_data(brace_geom_data, kjt_geom_data, xjt_geom_data, section_definition)
    for brace_a_obj in brace_a_objs:
        jkt_obj.add_brace_a_obj(brace_a_obj)

    # create the brace b 2D sections (spans xjts to kjts)
    brace_b_objs = create_2D_brace_b_data(brace_geom_data, kjt_geom_data, xjt_geom_data, section_definition)
    for brace_b_obj in brace_b_objs:
        jkt_obj.add_brace_b_obj(brace_b_obj)

    # create bay horizontals 2D sections (spans kjts)
    brace_hz_objs = create_2D_brace_hz_data(brace_hz_geom_data, kjt_geom_data, section_definition)
    for brace_hz_obj in brace_hz_objs:
        jkt_obj.add_brace_hz_obj(brace_hz_obj)

    # design warnings and errors and return to app
    warnings = jkt_obj.warnings

    # reconstruct the plot each time a new post is generated (so that the existing plot is not scattered with new data everytime a post request happens)
    updated_plot_json = jacket_plotter(jkt_obj, jkt_dict['lat'], jkt_dict['msl'], jkt_dict['splash_lower'], jkt_dict['splash_upper'], show_tower=False, twr_obj=None)

    # create mto dataframe
    df_mto = calculate_jkt_mto(jkt_obj)
    session['df_mto'] = df_mto.to_json()

    msg = 'Plot updated (with warnings and/or errors)' if warnings else 'Plot updated successfully'
    return jsonify({'message': msg,
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
    jkt_obj = create_jacket_from_session()  # initially try to create the jacket obj from session object
    kjt_n_braces = jkt_obj.kjt_n_braces
    bay_horizontals = jkt_obj.bay_horizontals

    plot_json_str = jacket_plotter(jkt_obj, lat, msl, splash_lower, splash_upper, show_tower=False)
    plot_json = json.loads(plot_json_str)

    # try first to use the session dict
    if 'jktsections_form_data' in session:
        defaults_sct = session.get('jktsections_form_data', '{}')
    else:  # on initial load use some defaults
        # jacket wireframe defaults
        defaults_sct = get_default_sct_config(jkt_obj)


    return render_template('jktsections.html', jkt_dict=jkt_dict,
                           plot_json=plot_json,
                           kjt_n_braces=kjt_n_braces,
                           bay_horizontals=bay_horizontals,
                           bay_horizontals_json=json.dumps(bay_horizontals),
                           defaults_sct=defaults_sct)


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

def get_default_sct_config(jkt_obj):

    kjt_n_braces = jkt_obj.kjt_n_braces
    k_jt_d, k_jt_stub_d, t = 2000, 1000, 99
    x_jt_d, x_jt_stub_d = 1000, 1000
    section_definition, section_alignment = "by_OD", "ID_constant"
    cone_taper = 4.
    defaults_sct = {}

    for k_jt, n_braces in kjt_n_braces.items():
        idx = k_jt.split("_")[1]
        # k jt defaults
        defaults_sct[f"{k_jt}_can_d"] = k_jt_d
        defaults_sct[f"{k_jt}_can_t"] = t
        defaults_sct[f"{k_jt}_stub_1_d"] = k_jt_stub_d
        defaults_sct[f"{k_jt}_stub_2_d"] = k_jt_stub_d
        defaults_sct[f"{k_jt}_stub_3_d"] = k_jt_stub_d
        defaults_sct[f"{k_jt}_stub_1_t"] = t
        defaults_sct[f"{k_jt}_stub_2_t"] = t
        defaults_sct[f"{k_jt}_stub_3_t"] = t
        # leg defaults
        defaults_sct[f"leg_{idx}_t"] = t
        # x jts
        defaults_sct[f"xjt_{idx}_can_d"] = x_jt_d
        defaults_sct[f"xjt_{idx}_can_t"] = t
        defaults_sct[f"xjt_{idx}_stub_d"] = x_jt_d
        defaults_sct[f"xjt_{idx}_stub_t"] = t
        # bay braces
        defaults_sct[f"bay_{idx}_t"] = t
        defaults_sct[f"bay_hz_{idx}_t"] = t

    defaults_sct["cone_taper"] = cone_taper
    defaults_sct["section_definition"] = section_definition
    defaults_sct["section_alignment"] = section_alignment

    return defaults_sct