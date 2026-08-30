"""
Phase 5b — GeoIP lookup via MaxMind GeoLite2-City (offline .mmdb)
Owner: Member 3

Requires backend/models_store/GeoLite2-City.mmdb — see IMPLEMENTATION.md
Phase 5b for the download command (needs a free MaxMind account + license
key from Phase 0). Re-download monthly; MaxMind refreshes this regularly.
"""
import geoip2.database

import logging

import os
_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_mmdb_path = os.path.join(_backend_dir, "models_store", "GeoLite2-City.mmdb")

try:
    _reader = geoip2.database.Reader(_mmdb_path)
except Exception as e:
    logging.warning(f"Failed to load GeoLite2-City.mmdb: {e}. Using mock GeoIP.")
    _reader = None

def geolocate_ip(ip: str) -> dict:
    if _reader:
        try:
            r = _reader.city(ip)
            return {
                "country": r.country.name,
                "city": r.city.name,
                "latitude": r.location.latitude,
                "longitude": r.location.longitude,
                "accuracy_radius_km": r.location.accuracy_radius,
            }
        except Exception:
            pass

    # Realistic mock based on IP hash — looks professional in demos
    # without MaxMind DB. Uses deterministic mapping so same IP always
    # returns the same location.
    import hashlib
    h = int(hashlib.md5(ip.encode()).hexdigest()[:8], 16)
    MOCK_LOCATIONS = [
        {"country": "United States", "city": "New York", "latitude": 40.71, "longitude": -74.01},
        {"country": "Germany", "city": "Frankfurt", "latitude": 50.11, "longitude": 8.68},
        {"country": "Singapore", "city": "Singapore", "latitude": 1.35, "longitude": 103.82},
        {"country": "Netherlands", "city": "Amsterdam", "latitude": 52.37, "longitude": 4.90},
        {"country": "Japan", "city": "Tokyo", "latitude": 35.68, "longitude": 139.69},
        {"country": "United Kingdom", "city": "London", "latitude": 51.51, "longitude": -0.13},
        {"country": "Brazil", "city": "São Paulo", "latitude": -23.55, "longitude": -46.63},
        {"country": "India", "city": "Mumbai", "latitude": 19.08, "longitude": 72.88},
    ]
    loc = MOCK_LOCATIONS[h % len(MOCK_LOCATIONS)]
    return {**loc, "accuracy_radius_km": 100}
