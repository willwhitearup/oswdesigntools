import numpy as np
import plotly.graph_objects as go
import plotly.io as pio


def map_plot(lat, lon, wind_start, wind_end):
    wind_start = wind_start % 360
    wind_end = wind_end % 360
    if wind_end < wind_start:
        wind_end += 360

    radius_km = 1

    # convert radius to degrees
    radius_deg = radius_km / 111

    # generate arc
    bearings = np.linspace(wind_start, wind_end, 200) % 360
    theta = np.radians(90 - bearings)

    # arc coordinates
    arc_lats = lat + radius_deg * np.sin(theta)
    arc_lons = lon + radius_deg * np.cos(theta) / np.cos(np.radians(lat))

    # close sector
    sector_lats = np.concatenate(([lat], arc_lats, [lat]))
    sector_lons = np.concatenate(([lon], arc_lons, [lon]))
    # sector_lats = np.concatenate(([lat], arc_lats, [lat, lat]))
    # sector_lons = np.concatenate(([lon], arc_lons, [lon, lon]))

    fig = go.Figure()

    # centre marker
    fig.add_trace(go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode='markers',
        marker=dict(size=12)
    ))

    # sector overlay
    fig.add_trace(go.Scattermapbox(
        lat=sector_lats,
        lon=sector_lons,
        mode='lines',
        fill='toself',
        fillcolor='rgba(0,0,255,0.3)',
        line=dict(color='rgba(0,0,255,0.7)', width=2)
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=lat, lon=lon),
            zoom=12,
            layers=[
                dict(
                    sourcetype='geojson',
                    source={
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [list(zip(sector_lons, sector_lats))]
                        }
                    },
                    type='fill',
                    color='rgba(0,100,255,0.3)',
                    line=dict(width=0)
                )
            ]
        ),
        margin=dict(l=0, r=0, t=0, b=0),   # 👈 critical
        paper_bgcolor="rgba(0,0,0,0)",     # 👈 remove white frame
        plot_bgcolor="rgba(0,0,0,0)"       # 👈 remove inner bg
    )


    #fig.show()
    pio_json = pio.to_json(fig)

    return pio_json



if __name__ == "__main__":
    lat, lon = 51.3460, -2.9760
    wind_start, wind_end = 180, 359
    pio_json = map_plot(lat, lon, wind_start, wind_end)