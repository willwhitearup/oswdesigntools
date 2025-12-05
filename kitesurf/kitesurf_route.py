from flask import Flask, jsonify, request, render_template, session
from kitesurf.forecaster import get_good_week_forecast
from kitesurf.kitespots import get_lat_lon_for_location, get_loc_data_for_location
from kitesurf.whatsapp_notifier import  send_whatsapp_message

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

        use_defaults = form_data.get("use_defaults", False)
        loc_data = get_loc_data_for_location(loc)

        if not use_defaults:
            if "custom_loc_data" in form_data:
                custom = form_data["custom_loc_data"]
                # override
                loc_data = {
                    "wind_direction": custom["wind_direction"],
                    "wind_speed": custom["wind_speed"],
                    "tide_window": custom["tide_window"],
                    "wind_gust_limit": custom["wind_gust_limit"]
                }
                # store in session to persist
                session.setdefault("user_loc_data", {})
                session["user_loc_data"][loc] = loc_data
                session.modified = True
            # If previously saved overrides exist → load them
            elif "user_loc_data" in session and loc in session["user_loc_data"]:
                loc_data = session["user_loc_data"][loc]

        # get the lat lon of location and then store all in df
        lat, lon = get_lat_lon_for_location(loc)
        df = get_good_week_forecast(lat, lon, loc_data)

        # --- WhatsApp Alert Logic ---
        if len(df) >= 1:
            unique_dates = df['datetime'].dt.date.unique()
            formatted_dates = [f"{date.strftime('%A')} {date.day} {date.strftime('%B')}" for date in unique_dates]
            message_body = f"{loc} is psyching off in the next week!!! Go on the following days: {', '.join(formatted_dates)}"
            send_whatsapp_message(message_body)

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

    # If user overrides exist for default location, load those
    if "user_loc_data" in session and default_loc in session["user_loc_data"]:
        default_loc_data = session["user_loc_data"][default_loc]

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