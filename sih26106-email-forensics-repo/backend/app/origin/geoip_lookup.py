"""
Phase 5b — GeoIP lookup via MaxMind GeoLite2-City (offline .mmdb)
Owner: Member 3

Requires backend/models_store/GeoLite2-City.mmdb — see IMPLEMENTATION.md
Phase 5b for the download command (needs a free MaxMind account + license
key from Phase 0). Re-download monthly; MaxMind refreshes this regularly.
"""
import geoip2.database

_reader = geoip2.database.Reader("backend/models_store/GeoLite2-City.mmdb")


def geolocate_ip(ip: str) -> dict:
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
        return {"country": None, "city": None, "latitude": None,
                "longitude": None, "accuracy_radius_km": None}
