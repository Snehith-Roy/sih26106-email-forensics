"""
Phase 5b — GeoIP lookup via MaxMind GeoLite2-City (offline .mmdb)
Owner: Member 3

Requires backend/models_store/GeoLite2-City.mmdb — see IMPLEMENTATION.md
Phase 5b for the download command (needs a free MaxMind account + license
key from Phase 0). Re-download monthly; MaxMind refreshes this regularly.
"""
import geoip2.database

import logging

try:
    _reader = geoip2.database.Reader("backend/models_store/GeoLite2-City.mmdb")
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

    # Mock return if no DB or lookup fails
    return {
        "country": "MockCountry", 
        "city": "MockCity", 
        "latitude": 0.0,
        "longitude": 0.0, 
        "accuracy_radius_km": 10
    }
