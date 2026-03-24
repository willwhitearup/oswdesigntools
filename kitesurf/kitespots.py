# https://www.gps-coordinates.net/

KITESPOTS = {
    "wsm": {"lat_lon": (51.334260370651116, -2.9853119878062206),
               "tide_window": ("high", 3),  # 3 hours either side of high tide.
                "wind_direction": (195, 10),  # degrees, wind direction allowable (from)
                "wind_speed": (15, 35),
                "wind_gust_limit": 15},
    "brighton": {"lat_lon": (50.81967021596384,-0.14270713755812015),
                 "tide_window": ("low", 2),
                 "wind_direction": (105, 285),
                 "wind_speed": (15, 35),
                "wind_gust_limit": 15},
    "sauntonsands": {"lat_lon": (51.10381285137496,-4.222697576060517),
                 "tide_window": ("low", 3),
                 "wind_direction": (180, 2.5),
                 "wind_speed": (15, 35),
                 "wind_gust_limit": 15},
    "porthcawl": {"lat_lon": (51.48900928676906,-3.7255750707983637),
                     "tide_window": ("low", 3),
                     "wind_direction": (150, 330),
                     "wind_speed": (15, 35),
                     "wind_gust_limit": 15},
    "pentewan": {"lat_lon": (50.288185628372474,-4.782024815343533),
                  "tide_window": ("low", 3),
                  "wind_direction": (20, 200),
                  "wind_speed": (15, 35),
                  "wind_gust_limit": 15},
    "exmouthBeach": {"lat_lon": (50.61510341294092,-3.413637544769994),
                 "tide_window": ("low", 3),
                 "wind_direction": (140, 290),
                 "wind_speed": (15, 35),
                 "wind_gust_limit": 15},
    "exmouthDuckpond": {"lat_lon": (50.62156377585369,-3.4210925979483187),
                     "tide_window": ("high", 4),
                     "wind_direction": (270, 359),
                     "wind_speed": (15, 35),
                     "wind_gust_limit": 15},
    "southEndonSea_EastBeach": {"lat_lon": (51.53122189505167,0.8022566271774867),
                        "tide_window": ("low", 3),
                        "wind_direction": (50, 225),
                        "wind_speed": (15, 35),
                        "wind_gust_limit": 15}

}


def get_lat_lon_for_location(loc):
    lat, lon = KITESPOTS[loc]["lat_lon"]
    return lat, lon


def get_loc_data_for_location(loc):
    return KITESPOTS[loc]