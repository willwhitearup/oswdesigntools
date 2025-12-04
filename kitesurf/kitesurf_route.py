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
        loc = form_data.get("location", "wsm")

        lat, lon = get_lat_lon_for_location(loc)
        loc_data = get_loc_data_for_location(loc)

        df = get_good_week_forecast(lat, lon, loc_data)

        return jsonify({
            "columns": list(df.columns),
            "rows": df.values.tolist(),
            "loc_data": loc_data
        })

    # --- GET request: render the page ---
    defaults = get_defaults()

    # use default location to pull loc_data
    default_loc = defaults["default_location"]
    default_loc_data = get_loc_data_for_location(default_loc)

    return render_template(
        'kitesurf.html',
        defaults=defaults,
        loc_data=default_loc_data
    )




def get_defaults():
    return {
        "locations": ["wsm", "brighton"],
        "default_location": "wsm"
    }