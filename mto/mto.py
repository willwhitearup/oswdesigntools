from flask import render_template, Flask, session, request
import json
import pandas as pd
# local imports
from jktdesign.jacket import Jacket
import io

app = Flask(__name__)

@app.route('/mto')
def gen_mto():
    num_legs = request.args.get('num_legs', '3')
    total_mass_sum = 0  # default in case no data
    df_json = session.get('df_mto')
    if df_json:
        df = pd.read_json(io.StringIO(df_json))
        df = df.reset_index()  # move index into a column named 'index'
        df["total mass [t]"] = df["unit mass [t]"] * float(num_legs)

        df = df.round({"total mass [t]": 4,
                       "unit mass [t]": 4})

        total_mass_sum = df["total mass [t]"].sum().round(5)

        data = df.to_dict(orient='records')
        columns = df.columns.tolist()


    else:
        data, columns = [], []
    return render_template('mto.html', data=data, columns=columns, total_mass_sum=total_mass_sum, num_legs=num_legs)

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