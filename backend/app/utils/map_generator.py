from pathlib import Path

import folium


def generate_map_html(
    analysis_id: str,
    locations: list[dict],
    output_dir: str = "reports",
) -> str:
    if not locations:
        m = folium.Map(location=[39.0, 35.0], zoom_start=6)
    else:
        first = locations[0]
        m = folium.Map(
            location=[first["latitude"], first["longitude"]],
            zoom_start=10,
        )

    color_map = {
        "exif_gps": "green",
        "ip_geo": "blue",
        "visual_estimate": "orange",
        "social_checkin": "purple",
    }

    for loc in locations:
        color = color_map.get(loc.get("source", ""), "red")
        folium.Marker(
            [loc["latitude"], loc["longitude"]],
            popup=f"{loc.get('source', 'unknown')} — {loc.get('address', '')}",
            icon=folium.Icon(color=color),
        ).add_to(m)

    out_path = Path(output_dir) / f"{analysis_id}_map.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(out_path))
    return str(out_path)
