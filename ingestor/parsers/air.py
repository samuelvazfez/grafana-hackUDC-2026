"""Parsers para Open-Meteo: Air Quality, Forecast y Polen."""

def parse_air_quality(raw_results):
    rows = []
    for item in raw_results:
        lat, lon, idx = item.get("_lat"), item.get("_lon"), item.get("_idx")
        current = item.get("current", {})
        time_str = current.get("time")
        if not time_str:
            continue
        rows.append({
            "time": time_str, "lat": lat, "lon": lon, "coord_index": idx,
            "european_aqi": current.get("european_aqi"),
            "pm10": current.get("pm10"),
            "pm2_5": current.get("pm2_5"),
            "uv_index": current.get("uv_index")
        })
    return rows


def parse_forecast(raw_results):
    rows = []
    for item in raw_results:
        lat, lon, idx = item.get("_lat"), item.get("_lon"), item.get("_idx")
        hourly = item.get("hourly", {})
        times = hourly.get("time", [])
        for i, t in enumerate(times):
            rows.append({
                "time": t, "lat": lat, "lon": lon, "coord_index": idx,
                "temperature": _safe_get(hourly, "temperature_2m", i),
                "apparent_temperature": _safe_get(hourly, "apparent_temperature", i),
                "precipitation_probability": _safe_get(hourly, "precipitation_probability", i),
                "precipitation": _safe_get(hourly, "precipitation", i),
                "wind_speed": _safe_get(hourly, "wind_speed_10m", i),
                "wind_gusts": _safe_get(hourly, "wind_gusts_10m", i),
                "visibility": _safe_get(hourly, "visibility", i),
                "cloud_cover": _safe_get(hourly, "cloud_cover", i),
                "is_day": _safe_get(hourly, "is_day", i),
            })
    return rows


def parse_pollen(raw_results):
    rows = []
    for item in raw_results:
        lat, lon, idx = item.get("_lat"), item.get("_lon"), item.get("_idx")
        hourly = item.get("hourly", {})
        times = hourly.get("time", [])
        for i, t in enumerate(times):
            rows.append({
                "time": t, "lat": lat, "lon": lon, "coord_index": idx,
                "grass_pollen": _safe_get(hourly, "grass_pollen", i),
                "birch_pollen": _safe_get(hourly, "birch_pollen", i),
                "olive_pollen": _safe_get(hourly, "olive_pollen", i),
                "alder_pollen": _safe_get(hourly, "alder_pollen", i),
                "ragweed_pollen": _safe_get(hourly, "ragweed_pollen", i),
            })
    return rows


def _safe_get(hourly, key, idx):
    arr = hourly.get(key, [])
    if idx < len(arr):
        return arr[idx]
    return None
