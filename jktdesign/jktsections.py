from flask import Flask, render_template, session, request, jsonify
import json
from jktdesign.jacket import Jacket
from jktdesign.plotter import jacket_plotter
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)

@app.route('/jktsections', methods=['POST'])
def jacket_sections_plot():

    # get the plotly figure from plot_json
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON received'}), 400

    # get the form data back (input boxes)
    form_data = data.get('form_data', {})
    print(form_data)

    # get the original jacket data (from architect page
    jkt_json_str = session.get('jkt_json', '{}')
    jkt_dict = json.loads(jkt_json_str)
    lat, msl, splash_lower = jkt_dict['lat'], jkt_dict['msl'], jkt_dict['splash_lower']

    # get the plot back in its current form and make updates!
    plot_json = data.get('plot_json')
    # print(plot_json)
    fig = go.Figure(plot_json)
    fig.add_trace(go.Scatter(x=[0, 5000], y=[0,5000], mode='markers', name='New Point', marker=dict(size=20), showlegend=True))
    updated_plot_json = pio.to_json(fig)  # convert it back to json to feed back

    return jsonify({'message': 'Plot updated successfully',
                    'plot_json': updated_plot_json
                    })


@app.route('/jktsections', methods=['GET'])
def jacket_sections():
    """gets jkt_json data from architect.py and architect.html webpage
    """
    jkt_json_str = session.get('jkt_json', '{}')
    jkt_dict = json.loads(jkt_json_str)
    # get out some data to create the plotly figure
    lat, msl, splash_lower, splash_upper = jkt_dict['lat'], jkt_dict['msl'], jkt_dict['splash_lower'], jkt_dict['splash_upper']
    # create the jacket object
    jkt_obj = create_jacket_from_session()
    plot_json_str = jacket_plotter(jkt_obj, lat, msl, splash_lower, splash_upper, show_tower=False)
    plot_json = json.loads(plot_json_str)
    return render_template('jktsections.html', jkt_dict=jkt_dict, plot_json=plot_json)


def create_jacket_from_session():
    jkt_json_str = session.get('jkt_json', '{}')
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