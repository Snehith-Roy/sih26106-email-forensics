import React, { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix Leaflet marker icon asset resolution issues in Vite
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

const DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});
L.Marker.prototype.options.icon = DefaultIcon;

// Helper to center the map viewport dynamically when coordinates change
function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom());
    }
  }, [center, zoom, map]);
  return null;
}

export default function RelayMap({ geolocation, originIp }) {
  const hasCoords = geolocation?.latitude !== undefined && geolocation?.longitude !== undefined;
  
  // Default coordinates (e.g. World center) if no file is ingested
  const mapCenter = hasCoords ? [geolocation.latitude, geolocation.longitude] : [20, 0];
  const zoomLevel = hasCoords ? 4 : 2;

  // Mocking the receiving MTA gateway (e.g. central mail protection server in Frankfurt, DE)
  // to draw a glowing path connection line to the origin IP
  const receiverCoords = [50.1109, 8.6821]; 
  const tracerPath = hasCoords ? [receiverCoords, [geolocation.latitude, geolocation.longitude]] : [];

  return (
    <div className="relative h-full w-full rounded-lg overflow-hidden border border-cyber-border/60">
      <MapContainer 
        center={mapCenter} 
        zoom={zoomLevel} 
        style={{ height: "100%", width: "100%", background: "#080c14" }}
        zoomControl={true}
      >
        {/* Sleek Dark CartoDB Map Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {hasCoords && (
          <>
            {/* Glowing origin marker */}
            <Marker position={[geolocation.latitude, geolocation.longitude]}>
              <Popup>
                <div className="font-mono text-[10px] text-slate-200">
                  <p className="font-bold text-amber-400">RESOLVED ATTACK ORIGIN</p>
                  <p className="mt-1">IP: {originIp}</p>
                  <p>Location: {geolocation.city || "Unknown City"}, {geolocation.country || "Unknown Country"}</p>
                </div>
              </Popup>
            </Marker>

            {/* Glowing tracer connection line */}
            <Polyline 
              positions={tracerPath} 
              pathOptions={{ 
                color: "#f59e0b", 
                weight: 2, 
                dashArray: "6, 6",
                lineCap: "round"
              }} 
            />
          </>
        )}

        <MapController center={mapCenter} zoom={zoomLevel} />
      </MapContainer>
    </div>
  );
}
