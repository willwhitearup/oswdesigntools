from flask import Flask, render_template, flash, jsonify, request, session

from gcdesign.plotterbm import bm_plotter
from gcdesign.plottergc import gc_plotter

app = Flask(__name__)

@app.route('/gc', methods=['GET', 'POST'])
def gc_route():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON received'}), 400

        form_data = data.get('form_data', {})
        print(form_data)

        # test for layout
        leg_od, leg_t = 2000, 100
        pile_od, pile_t = 3000, 150
        gc_length = 10000
        n_sks, sk_width, sk_height, sk_spacing = 10, 80, 40, 500
        gc_plot_json = gc_plotter(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing)

        fx, fy = 1.1E+07, 2.6E+06
        mx, my = 2.9E+07, -1.2E+08
        gc_length, gc_radius = 10000, 3000
        bm_plot_json = bm_plotter(fx, fy, mx, my, gc_length, gc_radius)

        return jsonify({'gc_message': 'Plot updated successfully',
                        'gc_plot_json': gc_plot_json,
                        'bm_plot_json': bm_plot_json
                        })

    # If GET request
    return render_template('gc.html')

