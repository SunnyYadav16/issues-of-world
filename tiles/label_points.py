"""One label point per state, guaranteed inside its largest polygon, from the Survey of India file.
Run: uv run --with pyarrow --with shapely python tiles/label_points.py
Output: apps/web/src/map/stateLabels.json (derived data; regenerate if SOI_States.parquet changes)."""
import json
import pyarrow.parquet as pq
import shapely

# Long official names crowd the map; the full name is always in the panel and the state list.
SHORT = {38: "DNH & DD"}

rows = pq.read_table("tiles/SOI_States.parquet").to_pylist()
features = []
for r in rows:
    if r["State_LGD"] == 0:  # inter-state "DISPUTED" slivers are not states
        continue
    geom = shapely.from_wkb(r["geometry"])
    parts = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    main = max(parts, key=lambda p: p.area)
    pt = main.representative_point()
    features.append({
        "type": "Feature",
        "properties": {"lgd": r["State_LGD"], "name": SHORT.get(r["State_LGD"], r["STATE_C"]), "area": round(geom.area, 3)},
        "geometry": {"type": "Point", "coordinates": [round(pt.x, 4), round(pt.y, 4)]},
    })
json.dump({"type": "FeatureCollection", "features": features}, open("apps/web/src/map/stateLabels.json", "w"), separators=(",", ":"))
print(len(features), "label points")
