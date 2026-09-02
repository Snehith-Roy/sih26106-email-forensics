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
    logging.info(f"MaxMind GeoLite2 loaded from {_mmdb_path}")
except Exception as e:
    _reader = None
    logging.error(f"CRITICAL: GeoLite2-City.mmdb not found at {_mmdb_path}: {e}")
    logging.error("Geolocation will NOT be available. Download from:")
    logging.error("  https://dev.maxmind.com/geoip/geolite2-free-geolocation-data")

def geolocate_ip(ip: str) -> dict:
    if not _reader:
        raise RuntimeError(
            f"MaxMind GeoLite2-City.mmdb not loaded. Cannot geolocate IP {ip}. "
            "Download from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data "
            "and place in backend/models_store/"
        )
    try:
        r = _reader.city(ip)
        return {
            "country": r.country.name,
            "city": r.city.name,
            "latitude": r.location.latitude,
            "longitude": r.location.longitude,
            "accuracy_radius_km": r.location.accuracy_radius,
        }
    except Exception as e:
        logging.warning(f"GeoIP lookup failed for {ip}: {e}")
        return {"country": None, "city": None, "latitude": None, "longitude": None}
