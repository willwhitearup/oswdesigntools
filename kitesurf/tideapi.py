import requests
import pandas as pd



def get_tides_api(lat, lon):
    url = "https://marine-api.open-meteo.com/v1/marine"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "sea_level_height_msl",
    }

    r = requests.get(url, params=params, verify=False)
    r.raise_for_status()  # optional, will raise error if request fails
    data = r.json()

    hourly_data = data["hourly"]
    df = pd.DataFrame({
        "time": pd.to_datetime(hourly_data["time"]),
        "sea_level_msl": hourly_data["sea_level_height_msl"]
    })

    # Local MSL at Weston-super-Mare (meters)
    local_msl = 6.2

    # Adjust sea level to actual water height
    df["water_level"] = df["sea_level_msl"] + local_msl

    # Calculate daily min/max
    # Function to get daily min/max and their times
    df = df.groupby(df["time"].dt.date).apply(
        lambda x: pd.Series({
            "tide_min": x["water_level"].min(),
            "tide_max": x["water_level"].max(),
            "tide_min_time": x.loc[x["water_level"].idxmin(), "time"],
            "tide_max_time": x.loc[x["water_level"].idxmax(), "time"]
        })
    ).reset_index().rename(columns={"time": "date"})
    return df

if __name__ == "__main__":
    # Open-Meteo Marine API example — free tides
    lat = 51.3460
    lon = -2.9760

    daily_summary = get_tides_api(lat, lon)
    print(daily_summary)
