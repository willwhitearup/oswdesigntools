from flask import Flask, jsonify, request, render_template
from kitesurf.forecaster import get_good_week_forecast
from kitesurf.kitespots import get_lat_lon_for_location, get_loc_data_for_location

app = Flask(__name__)

@app.route('/kitesurf', methods=['GET', "POST"])
def kitesurf_route():

    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON received'}), 400

        form_data = data.get('form_data', {})
        # Get location from query param, default to "wsm" if not provided
        loc = form_data.get("location")

        lat, lon = get_lat_lon_for_location(loc)
        loc_data = get_loc_data_for_location(loc)

        df = get_good_week_forecast(lat, lon, loc_data)

        return jsonify({
            "columns": list(df.columns),
            "rows": df.values.tolist()
        })

    # GET request – render with defaults
    defaults = get_defaults()

    return render_template('kitesurf.html', defaults=defaults)




def get_defaults():
    return {
        "locations": ["wsm", "brighton"],
        "default_location": "wsm"
    }