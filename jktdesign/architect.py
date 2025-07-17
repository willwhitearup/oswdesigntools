from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from jktdesign.jacket import Jacket
from jktdesign.plotter import jacket_plotter
from jktdesign.tower import Tower
import uuid
import json


app = Flask(__name__)

# some sensible inputs
BATTER_1_THETA_MIN, BATTER_1_THETA_MAX, BATTER_1_THETA_STEP = 60, 90, 0.2
JACKET_FOOTPRINT_MIN, JACKET_FOOTPRINT_MAX, JACKET_FOOTPRINT_STEP = 5000, 60000, 200
STICKUP_MIN, STICKUP_MAX, STICKUP_STEP = 0., 25000, 100

@app.route('/architect', methods=['GET', 'POST'])
def jacket_architect():
    if request.method == 'POST':
        try:
            show_tower = request.form.get('show_tower') == 'on'
            single_batter = request.form.get('single_batter') == 'on'
            # Handle tower inputs with fallback to defaults
            if show_tower:
                rna_cog = float(request.form.get('rna_cog', 0))
                moment_interface_del = float(request.form.get('moment_interface_del', 0))
                shear_interface_del = float(request.form.get('shear_interface_del', 0))
            else:
                session_data = json.loads(session.get('jkt_json', '{}'))
                rna_cog = session_data.get('rna_cog', 999)
                moment_interface_del = session_data.get('moment_interface_del', 999)
                shear_interface_del = session_data.get('shear_interface_del', 999)

            if single_batter:
                batter_1_theta, batter_1_elev = None, None
            else:
                batter_1_theta = float(request.form['batter_1_theta'])
                batter_1_elev = float(request.form['batter_1_elev'])

            water_depth = float(request.form['water_depth'])
            msl = float(request.form['msl'])
            splash_lower, splash_upper = float(request.form['splash_lower']), float(request.form['splash_upper'])

            interface_elev = float(request.form['interface_elev'])
            tp_btm, tp_width = float(request.form['tp_btm']), float(request.form['tp_width'])

            jacket_footprint = float(request.form['jacket_footprint'])
            stickup = float(request.form['stickup'])
            tp_btm_k1_voffset = float(request.form['tp_btm_k1_voffset'])
            btm_vert_leg_length = float(request.form['btm_vert_leg_length'])
            n_bays = int(request.form['n_bays'])
            # Collect bay heights dynamically
            bay_heights = [float(request.form[f'bay_height_{i}']) for i in range(1, n_bays + 1)]
            # collect bay horizontals dynamically
            bay_horizontals = [f'bay_horizontal_{i}' in request.form for i in range(1, n_bays + 1)]
            bay_horizontals.insert(0, False)  # artificially insert a False to indicate the top k brace has no horizontal

            # clear session data if the n bays is altered by the User----------------------
            session_data = json.loads(session.get('jkt_json', '{}'))
            old_n_bays = session_data.get('n_bays')
            # Clear session if n_bays changed
            if old_n_bays is not None and old_n_bays != n_bays:
                session.clear()
            # end of session clearing-----------------------------------

            # Create objects
            jkt_obj = Jacket(interface_elev, tp_width, tp_btm, tp_btm_k1_voffset, batter_1_theta, batter_1_elev,
                             jacket_footprint, stickup, bay_heights, btm_vert_leg_length, water_depth, single_batter, bay_horizontals)

            twr_obj = Tower(rna_cog, interface_elev, moment_interface_del, shear_interface_del)
            lat = 0.

            # get jkt and twr dicts
            jkt_dict = {k: v for k, v in jkt_obj.__dict__.items() if v is not None}
            twr_dict = {"show_tower": show_tower, "rna_cog": rna_cog, "moment_interface_del": moment_interface_del,
                        "shear_interface_del": shear_interface_del}

            # create a session dict
            session_data = {**jkt_dict, **twr_dict}
            session_data['msl'] = msl  # add water levels info into the session
            session_data['lat'] = lat
            session_data['splash_lower'] = splash_lower
            session_data['splash_upper'] = splash_upper
            session_json = json.dumps(session_data)
            session['jkt_json'] = session_json

            # Plot jacket
            plot_json = jacket_plotter(jkt_obj, lat, msl, splash_lower, splash_upper, show_tower, twr_obj)
            # return for the POST request-------------------------------------
            return jsonify({'plot_json': plot_json,
                            "batter_2_theta": jkt_obj.batter_2_theta,
                            "batter_1_theta": jkt_obj.batter_1_theta,
                            "batter_1_elev_min": jkt_obj.batter_1_elevation_min,
                            "batter_1_elev_max": jkt_obj.batter_1_elevation_max,
                            "batter_1_theta_min": BATTER_1_THETA_MIN,
                            "batter_1_theta_max": BATTER_1_THETA_MAX,
                            "batter_1_theta_step": BATTER_1_THETA_STEP,
                            "jacket_footprint_min": JACKET_FOOTPRINT_MIN,
                            "jacket_footprint_max": JACKET_FOOTPRINT_MAX,
                            "jacket_footprint_step": JACKET_FOOTPRINT_STEP,
                            "stickup_min": STICKUP_MIN,
                            "stickup_max": STICKUP_MAX,
                            "stickup_step": STICKUP_STEP,
                            "bay_heights": bay_heights
                            })

        except Exception as e:
            flash(f"An error occurred: {e}")
            return jsonify({'error': f"An error occurred: {e}"}), 400

    # GET requests------------------------------------------------------------------------------------
    # on initial load get the defaults, otherwise use the session dict
    if 'jkt_json' in session:
        defaults = json.loads(session.get('jkt_json', '{}'))
    else:
        # jacket wireframe defaults
        defaults = get_default_config()

    # Calculate batter_2_theta
    jkt_obj = Jacket(defaults['interface_elev'], defaults['tp_width'], defaults['tp_btm'], defaults['tp_btm_k1_voffset'],
                     defaults['batter_1_theta'], defaults['batter_1_elev'], defaults['jacket_footprint'], defaults['stickup'],
                     defaults['bay_heights'], defaults['btm_vert_leg_length'], defaults['water_depth'],
                     defaults['single_batter'], defaults['bay_horizontals'])

    # return for the GET---------------
    return render_template('architect.html',
                           defaults=defaults,
                           batter_1_elev_min=jkt_obj.batter_1_elevation_min,
                           batter_1_elev_max=jkt_obj.batter_1_elevation_max,
                           batter_1_theta=round(jkt_obj.batter_1_theta, 3),
                           batter_2_theta=round(jkt_obj.batter_2_theta, 3),
                           batter_1_theta_min=BATTER_1_THETA_MIN,
                           batter_1_theta_max=BATTER_1_THETA_MAX,
                           batter_1_theta_step=BATTER_1_THETA_STEP,
                           jacket_footprint_min=JACKET_FOOTPRINT_MIN,
                           jacket_footprint_max=JACKET_FOOTPRINT_MAX,
                           jacket_footprint_step=JACKET_FOOTPRINT_STEP,
                           stickup_min=STICKUP_MIN,
                           stickup_max=STICKUP_MAX,
                           stickup_step=STICKUP_STEP
                           )


def get_default_config():

    tp_btm_k1_voffset = 1000
    water_depth = 62800
    stickup = 4000
    tp_btm = 33150
    n_bays = 2

    # Calculate jacket height
    seafloor_elevation = -water_depth + stickup + tp_btm_k1_voffset
    jacket_height = (tp_btm - tp_btm_k1_voffset) - seafloor_elevation
    bay_height = jacket_height / n_bays

    return {
        'water_depth': water_depth,
        'msl': 2200,
        'splash_lower': -6110,
        'splash_upper': 12580,
        'rna_cog': 250000,
        'interface_elev': 42150,
        'tp_btm': tp_btm,
        'tp_width': 19300,
        'moment_interface_del': 121587000000,
        'shear_interface_del': 1198000,
        'show_tower': True,
        'jacket_footprint': 36000,
        'stickup': stickup,
        'tp_btm_k1_voffset': tp_btm_k1_voffset,
        'btm_vert_leg_length': 5030,
        'n_bays': n_bays,
        'batter_1_theta': 86,
        'batter_1_elev': -18500,
        'single_batter': False,
        'bay_horizontals': [True] + [False] * (n_bays - 1),
        'bay_heights': [bay_height] * n_bays,
    }

if __name__ == "__main__":
    app.run(debug=True)
