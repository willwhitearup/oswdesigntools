import pandas as pd
from kitesurf.sunhoursapi import get_sunrise_sunset_api
from kitesurf.tideapi import get_tides_api
from kitesurf.windapi import get_wind_forecast


def get_good_week_forecast(lat, lon, loc_data):

    df_sun_times = get_sunrise_sunset_api(lat, lon)
    df_tide_times = get_tides_api(lat, lon)
    df_wind_forecast = get_wind_forecast(lat, lon)

    filtered_list = []
    for date, data in df_wind_forecast.groupby("date"):
        # extract stuff from data to filter
        time = data["datetime"]
        forecast_wind_speed = data["wind_speed"]
        forecast_wind_direction = data["wind_direction"]
        forecast_wind_gust = data["wind_gusts"]

        # filter day time hours (light)
        sun_date = df_sun_times[df_sun_times["date"].dt.date == date]
        sunrise, sunset = sun_date["sunrise"].iloc[0], sun_date["sunset"].iloc[0]
        light_hours_allow = (time >= sunrise) & (time <=sunset)

        # filter tide times
        tide_date = df_tide_times[df_tide_times["date"] == date]
        tide_time = tide_date["tide_min_time"].iloc[0] if loc_data["tide_window"][0] == "low" else tide_date["tide_max_time"].iloc[0]
        tide_lim_min = tide_time - pd.Timedelta(hours=loc_data["tide_window"][1])
        tide_lim_max = tide_time + pd.Timedelta(hours=loc_data["tide_window"][1])
        tide_hours_allow = (time >= tide_lim_min) & (time <=tide_lim_max)

        # add in high and low tide times
        data["tide_low_time"] = tide_date["tide_min_time"].iloc[0].hour
        data["tide_high_time"] = tide_date["tide_max_time"].iloc[0].hour

        # filter wind direction
        wind_direction_allow = (forecast_wind_direction >= loc_data["wind_direction"][0]) & (forecast_wind_direction <= loc_data["wind_direction"][1])
        # filter wind speeds
        wind_speed_allow = (forecast_wind_speed >= loc_data["wind_speed"][0]) & (forecast_wind_speed <= loc_data["wind_speed"][1])
        # filter wind gusts
        gusting = forecast_wind_gust - forecast_wind_speed
        wind_gusts_allow = (gusting <= loc_data["wind_gust_limit"])

        #### apply all the masks
        mask = light_hours_allow & tide_hours_allow & wind_direction_allow & wind_speed_allow & wind_gusts_allow
        filtered_list.append(data[mask])

    df = pd.concat(filtered_list, ignore_index=True)
    df.drop(columns="date", inplace=True)
    col_order = ["datetime", "wind_speed", "wind_direction", "wind_gusts", "tide_low_time", "tide_high_time"]
    df = df[col_order]
    return df

if __name__ == "__main__":
    # wsm
    lat = 51.3460
    lon = -2.9760
    loc_data = {"tide_window": ("high", 3),  # 3 hours either side of high tide.
                "wind_direction": (180, 330), # wind direction is from and this is the allowable wind direction window
                "wind_speed": (5, 50),
                "wind_gust_limit": 15}

    df = get_good_week_forecast(lat, lon, loc_data)
    # Show all columns
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 1000)
    print(df)
    a=1
