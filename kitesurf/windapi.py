import requests
import certifi

import requests
import pandas as pd

def get_wind_forecast(lat: float, lon: float) -> dict:
    """
    Returns a dict with hourly wind forecast for the next 7 days
    for a given latitude and longitude.
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wind_speed_10m,wind_gusts_10m,wind_direction_10m",
        "timezone": "Europe/London",
    }

    r = requests.get(url, params=params, verify=False)  # verify uses system certs or certifi
    r.raise_for_status()
    data = r.json()

    hourly = data.get("hourly", {})

    # return only the wind-related hourly data
    winddata = {
        "time": hourly.get("time", []),
        "wind_speed": hourly.get("wind_speed_10m", []),
        "wind_gusts": hourly.get("wind_gusts_10m", []),
        "wind_direction": hourly.get("wind_direction_10m", []),
    }

    df = pd.DataFrame(winddata)

    # Convert 'time' to datetime
    df["datetime"] = pd.to_datetime(df["time"])
    df.drop(columns=["time"], inplace=True)
    # Create separate columns
    df["date"] = df["datetime"].dt.date
    #df["hour"] = df["datetime"].dt.hour
    return df


if __name__ == "__main__":
    lat = 51.3460
    lon = -2.9760

    df = get_wind_forecast(lat, lon)
    print(df)