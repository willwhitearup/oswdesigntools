def get_lat_lon_for_location(loc):
    if loc == "wsm":
        lat, lon = 51.3460, -2.9760
    if loc == "brighton":
        lat, lon = 50.82838, -0.13947
    return lat, lon


def get_loc_data_for_location(loc):
    if loc == "wsm":
        loc_data = {"tide_window": ("high", 3),  # 3 hours either side of high tide.
                    "wind_direction": (180, 330),
                    # wind direction is from and this is the allowable wind direction window
                    "wind_speed": (5, 50),
                    "wind_gust_limit": 15}

    if loc == "brighton":
        loc_data = {"tide_window": ("high", 3),  # 3 hours either side of high tide.
                    "wind_direction": (90, 270),
                    # wind direction is from and this is the allowable wind direction window
                    "wind_speed": (5, 50),
                    "wind_gust_limit": 15}
    return loc_data