import json
import requests
import pandas as pd

with open("ocm_key.txt") as f:
    key = f.read().strip()

params = {
    "output": "json",
    "latitude": 12.9716,      # Bengaluru centre
    "longitude": 77.5946,
    "distance": 30,           # radius
    "distanceunit": "km",
    "maxresults": 5000,
    "compact": "false",       # keep names, not only IDs
    "verbose": "false",
    "key": key,
}
r = requests.get("https://api.openchargemap.io/v3/poi/", params=params, timeout=60)
r.raise_for_status()
data = r.json()
print("Stations:", len(data))

with open("data/raw/ocm_bengaluru.json", "w", encoding="utf8") as f:
    json.dump(data, f)

rows = []
for p in data:
    a = p.get("AddressInfo") or {}
    conns = p.get("Connections") or []
    powers = [c.get("PowerKW") for c in conns if c.get("PowerKW")]
    rows.append({
        "id": p.get("ID"),
        "title": a.get("Title"),
        "town": a.get("Town"),
        "lat": a.get("Latitude"),
        "lon": a.get("Longitude"),
        "operator": (p.get("OperatorInfo") or {}).get("Title"),
        "usage": (p.get("UsageType") or {}).get("Title"),
        "status": (p.get("StatusType") or {}).get("Title"),
        "points": p.get("NumberOfPoints"),
        "max_power_kw": max(powers) if powers else None,
        "connectors": "; ".join(sorted({(c.get("ConnectionType") or {}).get("Title") or "" for c in conns})),
    })
df = pd.DataFrame(rows)
df.to_csv("data/raw/ocm_bengaluru.csv", index=False)
print(df.head())