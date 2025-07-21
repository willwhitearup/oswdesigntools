from flask import Flask, render_template, flash, jsonify, request, session

from gcdesign.gc_processor import gc_processor
from gcdesign.plotterbm import bm_plotter
from gcdesign.plotterfbk import skspacing_vs_fbk_plot
from gcdesign.plottergc import gc_plotter
from gcdesign.plottergrtmtx import shear_capacity_plotter

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
        n_sks = int(float(form_data['num_sks']))  # n sks integer
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

        geom_warnings = []
        if leg_od >= pile_od - 2 * pile_t:
            geom_warnings.append(f"Error: leg OD {leg_od} exceeds pile ID {pile_od - 2 * pile_t}")
        if n_sks * sk_spacing >= gc_length:
            geom_warnings.append(f"Error: SK length ({n_sks * sk_spacing}) exceeds GC length ({gc_length})")


        # pass to the gc processor for all the calcs
        res, validity_chks, elastic_length = gc_processor(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width,
                                                          sk_height, sk_spacing, fx, fy, fz, mx, my, grout_E, grout_strength)

        # generate the plots
        gc_plot_json = gc_plotter(leg_od, leg_t, pile_od, pile_t, gc_length, n_sks, sk_width, sk_height, sk_spacing, elastic_length)
        bm_plot_json = bm_plotter(fx, fy, mx, my, gc_length, pile_od)
        gc_shrcap_plot_json = shear_capacity_plotter(leg_od, leg_t, pile_od, pile_t, sk_height, sk_spacing, grout_E, grout_strength)
        gc_fbk_plot_json = skspacing_vs_fbk_plot(leg_od, leg_t, pile_od, pile_t, sk_height, sk_spacing, grout_E, grout_strength)

        return jsonify({'gc_message': 'Plot updated successfully',
                        'gc_plot_json': gc_plot_json,
                        'bm_plot_json': bm_plot_json,
                        'gc_shrcap_plot_json': gc_shrcap_plot_json,
                        'gc_fbk_plot_json': gc_fbk_plot_json,
                        "res": res,
                        "validity_chks": validity_chks,
                        "geom_warnings": geom_warnings
                        })

    # GET request – render with defaults
    defaults = get_gc_defaults()

    return render_template('gc.html',
                           defaults=defaults)


def get_gc_defaults():

    # test ones
    leg_od = 3580.
    leg_t = 80.
    pile_od = 4250.
    pile_t = 85.
    gc_length = 11000.
    n_sks = 15
    sk_width = 44.
    sk_height = 22.
    sk_spacing = 370.

    # Load conditions (N and Nmm)
    fx = -100000.
    fy = -9000000.
    fz = -32000000.

    mx = 60000000 * 1e3  # Nmm
    my = -1000000 * 1e3  # Nmm

    grout_strength = 80.0 # MPa (N/mm2)
    grout_E = 38000.0  # MPa  (N/mm2)

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


