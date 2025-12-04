import requests
import pandas as pd

def get_sunrise_sunset_api(lat: float, lon: float) -> dict:
    """
    Returns a 7-day forecast of sunrise and sunset times for a given latitude and longitude.
    SSL verification is disabled (verify=False) — use only for testing.
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "sunrise,sunset",
        "timezone": "Europe/London",
    }

    r = requests.get(url, params=params, verify=False)
    r.raise_for_status()
    data = r.json()

    daily = data.get("daily", {})
    sun_times =  {
        "date": daily.get("time", []),
        "sunrise": daily.get("sunrise", []),
        "sunset": daily.get("sunset", []),
    }

    df = pd.DataFrame(sun_times)
    df["date"] = pd.to_datetime(df["date"])
    # df = df.drop(columns=["date"])
    df["sunrise"] = pd.to_datetime(df["sunrise"])
    df["sunset"] = pd.to_datetime(df["sunset"])
    return df

if __name__ == "__main__":
    lat = 51.3460
    lon = -2.9760

    sun_times = get_sunrise_sunset_api(lat, lon)
    print(sun_times)