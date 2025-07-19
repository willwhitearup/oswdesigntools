from flask import Flask, render_template, flash, jsonify, request, session

from gcdesign.gc_processor import gc_processor
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

        leg_od = float(form_data['jkt_od'])
        leg_t = float(form_data['jkt_thk'])
        pile_od = float(form_data['pile_od'])
        pile_t = float(form_data['pile_thk'])
        gc_length = float(form_data['gc_length'])
        n_sks = int(form_data['num_sks'])  # n sks integer
        sk_width = float(form_data['sk_width'])
        sk_height = float(form_data['sk_height'])
        sk_spacing = float(form_data['sk_spacing'])
        # grout materials
        grout_E = float(form_data['grout_E'])
        grout_strength = float(form_data['grout_strength'])
        # forces and moments
        fx = float(form_data['Fx'])
        fy = float(form_data['Fy'])
        fz = float(form_data['Fz'])
        mx = float(form_data['Mx'])
        my = float(form_data['My'])

        # pass to the gc processor for all the calcs
        res, validity_chks = gc_processor(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing, fx, fy, fz, mx, my, grout_E, grout_strength)
        # generate the plots
        gc_plot_json = gc_plotter(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing)
        bm_plot_json = bm_plotter(fx, fy, mx, my, gc_length, pile_od)

        return jsonify({'gc_message': 'Plot updated successfully',
                        'gc_plot_json': gc_plot_json,
                        'bm_plot_json': bm_plot_json,
                        "res": res,
                        "validity_chks": validity_chks
                        })

    # GET request – render with defaults
    defaults = get_gc_defaults()

    return render_template('gc.html',
                           defaults=defaults)


def get_gc_defaults():

    # test ones
    leg_od = 3580.
    leg_t = 80.
    pile_od = 4200.
    pile_t = 80.
    gc_length = 10050.
    n_sks = 14
    sk_width = 40.
    sk_height = 20.
    sk_spacing = 365.

    # Load conditions (N and Nmm)
    fx =-193900
    fy = -9539000
    fz = -32520000

    mx = -63769500 * 1e3  # Nmm
    my = 1025350 * 1e3  # Nmm

    grout_strength = 80. # MPa (N/mm2)
    grout_E = 38863.61  # MPa  (N/mm2)

    return {
        "leg_od": leg_od,
        "leg_t": leg_t,
        "pile_od": pile_od,
        "pile_t": pile_t,
        "gc_length": gc_length,
        "n_sks": n_sks,
        "sk_width": sk_width,
        "sk_height": sk_height,
        "sk_spacing": sk_spacing,
        "fx": fx,
        "fy": fy,
        "fz": fz,
        "mx": mx,
        "my": my,
        "grout_strength": grout_strength,
        "grout_E": grout_E
    }


