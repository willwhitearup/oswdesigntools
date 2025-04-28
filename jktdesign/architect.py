from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from jktdesign.jacket import Jacket
from jktdesign.plotter import jacket_plotter
from jktdesign.tower import Tower

app = Flask(__name__)

# some sensible inputs
BATTER_1_THETA_MIN, BATTER_1_THETA_MAX, BATTER_1_THETA_STEP = 60, 90, 0.2
JACKET_FOOTPRINT_MIN, JACKET_FOOTPRINT_MAX, JACKET_FOOTPRINT_STEP = 5000, 60000, 200
STICKUP_MIN, STICKUP_MAX, STICKUP_STEP = 0., 25000, 100

@app.route('/architect', methods=['GET', 'POST'])
def jacket_architect():
    if request.method == 'POST':
        try:
            # print(request.form)
            show_tower = request.form.get('show_tower') == 'on'
            single_batter = request.form.get('single_batter') == 'on'

            if show_tower:
                rna_cog = float(request.form['rna_cog'])
                moment_interface_del = float(request.form['moment_interface_del'])
                shear_interface_del = float(request.form['shear_interface_del'])
            else:
                rna_cog = 999
                moment_interface_del = 999
                shear_interface_del = 999

            if single_batter:
                batter_1_theta = None
                batter_1_elev = None
            else:
                batter_1_theta = float(request.form['batter_1_theta'])
                batter_1_elev = float(request.form['batter_1_elev'])

            water_depth = float(request.form['water_depth'])
            msl = float(request.form['msl'])
            splash_lower = float(request.form['splash_lower'])
            splash_upper = float(request.form['splash_upper'])

            interface_elev = float(request.form['interface_elev'])
            tp_btm = float(request.form['tp_btm'])
            tp_width = float(request.form['tp_width'])

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

            # Create objects
            jkt_obj = Jacket(interface_elev, tp_width, tp_btm, tp_btm_k1_voffset, batter_1_theta, batter_1_elev,
                             jacket_footprint, stickup, bay_heights, btm_vert_leg_length, water_depth, single_batter, bay_horizontals)

            twr_obj = Tower(rna_cog, interface_elev, moment_interface_del, shear_interface_del)
            # Plot jacket
            lat = 0.
            plot_json = jacket_plotter(twr_obj, jkt_obj, lat, msl, splash_lower, splash_upper, show_tower)

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
                            "stickup_step": STICKUP_STEP
                            })

        except Exception as e:
            flash(f"An error occurred: {e}")
            return jsonify({'error': f"An error occurred: {e}"}), 400

    # Default values for GET request
    defaults = {
        'water_depth': 62800,
        'msl': 2200,
        'splash_lower': -6110,
        'splash_upper': 12580,
        'rna_cog': 250000,
        'interface_elev': 42150,
        'tp_btm': 33150,
        'tp_width': 19300,
        'moment_interface_del': 121587000000,
        'shear_interface_del': 1198000,
        'show_tower': True,
        'jacket_footprint': 36000,
        'stickup': 4000,
        'tp_btm_k1_voffset': 1000,
        'btm_vert_leg_length': 5030,
        'n_bays': 4,
        'batter_1_theta': 86,
        'batter_1_elev': -9700,
        'single_batter': False
    }

    # Calculate default bay heights
    bay_height_value = ((defaults['tp_btm'] - defaults['tp_btm_k1_voffset']) - (
                -defaults['water_depth'] + defaults['stickup'] + defaults['tp_btm_k1_voffset'])) / defaults['n_bays']

    defaults['bay_heights'] = ','.join([str(bay_height_value)] * defaults['n_bays'])

    defaults['bay_horizontals'] = [False] * defaults['n_bays']
    # Calculate batter_2_theta
    jkt_obj = Jacket(defaults['interface_elev'], defaults['tp_width'], defaults['tp_btm'], defaults['tp_btm_k1_voffset'],
                     defaults['batter_1_theta'], defaults['batter_1_elev'], defaults['jacket_footprint'], defaults['stickup'],
                     [bay_height_value] * defaults['n_bays'], defaults['btm_vert_leg_length'], defaults['water_depth'],
                     defaults['single_batter'], defaults['bay_horizontals'])

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


if __name__ == "__main__":
    app.run(debug=True)
