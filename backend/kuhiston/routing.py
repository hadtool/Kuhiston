"""Навигация по дорогам/тропам через OSRM (PROJECT.md раздел 6, п. 3).

MVP-стратегия (см. DECISIONS.md и ISSUES.md): используем публичный OSRM
демо-сервер (router.project-osrm.org, данные OSM) через серверный прокси —
фронтенд не зависит от CORS и ключей. Если OSRM недоступен (таймаут/ошибка),
фолбэк — маршрут по прямой (haversine с поправочным коэффициентом 1.3).

Стабильный self-hosted OSRM (docker, данные OSM по Таджикистану) — отдельная
задача на машине основателя, для продакшена (см. ISSUES.md).
"""

import json
import math
import urllib.request

OSRM_BASE = "https://router.project-osrm.org"
PROFILES = {"driving", "foot", "bike"}
TIMEOUT = 6  # сек
FALLBACK_FACTOR = 1.3  # длина по прямой * 1.3 ≈ длина по дорогам


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def osrm_route(start, end, profile="driving"):
    """Запрашивает маршрут у OSRM.

    start/end — (lat, lng). Возвращает словарь:
        {distance_km, duration_min, geometry (GeoJSON LineString), source, profile}
    source == "osrm" или "fallback".
    При любой ошибке возвращает фолбэк по прямой (не бросает исключений).
    """
    if profile not in PROFILES:
        profile = "driving"
    s_lng, s_lat = start[1], start[0]
    e_lng, e_lat = end[1], end[0]
    coords = f"{s_lng},{s_lat};{e_lng},{e_lat}"
    url = f"{OSRM_BASE}/route/v1/{profile}/{coords}?overview=full&geometries=geojson"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("code") != "Ok" or not data.get("routes"):
            raise ValueError(data.get("code", "empty"))
        route = data["routes"][0]
        return {
            "distance_km": round(route["distance"] / 1000, 1),
            "duration_min": round(route["duration"] / 60),
            "geometry": route["geometry"],  # Feature geometry: LineString
            "source": "osrm",
            "profile": profile,
        }
    except Exception:
        # фолбэк: прямая линия
        straight = haversine_km(s_lat, s_lng, e_lat, e_lng)
        return {
            "distance_km": round(straight * FALLBACK_FACTOR, 1),
            "duration_min": round(straight * 15),  # грубо: 15 мин/км
            "geometry": {
                "type": "LineString",
                "coordinates": [[s_lng, s_lat], [e_lng, e_lat]],
            },
            "source": "fallback",
            "profile": profile,
        }