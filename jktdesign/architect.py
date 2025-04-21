from flask import Flask, render_template, request, jsonify
import numpy as np
from jktdesign.jacket import Jacket
from jktdesign.plotter import jacket_plotter
from jktdesign.tower import Tower

app = Flask(__name__)


@app.route('/architect', methods=['GET', 'POST'])
def jacket_architect():
    if request.method == 'POST':
        try:
            water_depth = float(request.form['water_depth'])
            msl = float(request.form['msl'])
            splash_lower = float(request.form['splash_lower'])
            splash_upper = float(request.form['splash_upper'])
            rna_cog = float(request.form['rna_cog'])
            interface_elev = float(request.form['interface_elev'])
            tp_btm = float(request.form['tp_btm'])
            tp_width = float(request.form['tp_width'])
            moment_interface_del = float(request.form['moment_interface_del'])
            shear_interface_del = float(request.form['shear_interface_del'])
            show_tower = request.form.get('show_tower') == 'on'
            jacket_footprint = float(request.form['jacket_footprint'])
            stickup = float(request.form['stickup'])
            tp_btm_k1_voffset = float(request.form['tp_btm_k1_voffset'])
            btm_vert_leg_length = float(request.form['btm_vert_leg_length'])
            n_bays = int(request.form['n_bays'])

            # Collect bay heights dynamically
            bay_heights = [float(request.form[f'bay_height_{i}']) for i in range(1, n_bays + 1)]
            batter_1_theta = float(request.form['batter_1_theta'])
            batter_1_elev = float(request.form['batter_1_elev'])

            # Create objects
            jkt_obj = Jacket(interface_elev, tp_width, tp_btm, tp_btm_k1_voffset, batter_1_theta, batter_1_elev,
                             jacket_footprint, stickup, bay_heights, btm_vert_leg_length, water_depth)
            twr_obj = Tower(rna_cog, interface_elev, moment_interface_del, shear_interface_del)

            batter_2_theta = jkt_obj.batter_2_theta

            # Plot jacket
            lat = 0.
            plot_json = jacket_plotter(twr_obj, jkt_obj, lat, msl, splash_lower, splash_upper, show_tower)

            return jsonify({'plot_json': plot_json})

        except KeyError as e:
            return f"Missing form field: {e}", 400

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
        'batter_1_elev': -9700
    }

    # Calculate default bay heights
    bay_height_value = ((defaults['tp_btm'] - defaults['tp_btm_k1_voffset']) - (
                -defaults['water_depth'] + defaults['stickup'] + defaults['tp_btm_k1_voffset'])) / defaults['n_bays']

    defaults['bay_heights'] = ','.join([str(bay_height_value)] * defaults['n_bays'])



    # Calculate min and max values for the slider
    batter_1_elev_min = -50000
    batter_1_elev_max = 20000
    # Calculate batter_2_theta
    jkt_obj = Jacket(defaults['interface_elev'], defaults['tp_width'], defaults['tp_btm'], defaults['tp_btm_k1_voffset'],
                     defaults['batter_1_theta'], defaults['batter_1_elev'], defaults['jacket_footprint'], defaults['stickup'],
                     [bay_height_value] * defaults['n_bays'], defaults['btm_vert_leg_length'], defaults['water_depth'])
    batter_2_theta = jkt_obj.batter_2_theta

    return render_template('architect.html', defaults=defaults,
                           batter_1_elev_min=batter_1_elev_min, batter_1_elev_max=batter_1_elev_max,
                           batter_2_theta=batter_2_theta)


if __name__ == "__main__":
    app.run(debug=True)
