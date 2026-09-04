import React, { useEffect, useRef } from "react";
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

// Custom div icons for colored markers
const createDivIcon = (color, size = 16) =>
  L.divIcon({
    className: "",
    html: `<div style="width:${size}px;height:${size}px;background:${color};border-radius:50%;border:2px solid #060a12;box-shadow:0 0 12px ${color}80;animation:${color === "#ef4444" ? "nodePulse 2s infinite" : "none"}"></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });

function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) map.setView(center, zoom || map.getZoom());
  }, [center, zoom, map]);
  return null;
}

export default function RelayMap({ geolocation, originIp, receivedChain, trustBoundaryHop }) {
  const hasCoords = geolocation?.latitude != null;
  const hops = (receivedChain || []).slice().reverse();
  const bnd = trustBoundaryHop;

  // Receiver location (Frankfurt — Google mail gateway)
  const receiver = [50.1109, 8.6821];

  // Generate simulated coordinates for hops when no origin IP
  const fakeCoords = hops.map((h, i) => {
    const t = i / (hops.length || 1);
    const targetLat = hasCoords ? geolocation.latitude : 35.68;
    const targetLng = hasCoords ? geolocation.longitude : 139.69;
    const lat = receiver[0] + (targetLat - receiver[0]) * t + Math.sin(i * 2.1) * 5;
    const lng = receiver[1] + (targetLng - receiver[1]) * t + Math.cos(i * 1.7) * 8;
    return [lat, lng];
  });

  const mapCenter = hasCoords
    ? [geolocation.latitude, geolocation.longitude]
    : hops.length > 0
    ? fakeCoords[Math.floor(fakeCoords.length / 2)]
    : [25, 0];

  const zoomLevel = hasCoords ? 4 : hops.length > 0 ? 3 : 2;

  // Build path for polyline
  const pathPoints = hasCoords ? [receiver, [geolocation.latitude, geolocation.longitude]] : [receiver, ...fakeCoords];

  return (
    <div className="relative h-full w-full rounded-lg overflow-hidden border border-cyber-border/60">
      <MapContainer center={mapCenter} zoom={zoomLevel} style={{ height: "100%", width: "100%", background: "#060a12" }} zoomControl={false}>
        <TileLayer
          attribution='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://openstreetmap.org/">OSM</a>'
          url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png?api_key=cb1_2xbk_1_5274a8e2177f21f737d3aaf9"
        />

        {/* Receiver marker (green) */}
        <Marker position={receiver} icon={createDivIcon("#10b981", 14)}>
          <Popup>
            <div style={{ fontFamily: "monospace", fontSize: 11 }}>
              <b style={{ color: "#10b981" }}>TRUSTED GATEWAY</b>
              <br />
              mx.google.com
              <br />
              Frankfurt, DE
            </div>
          </Popup>
        </Marker>

        {/* Origin marker (red) if resolved */}
        {hasCoords && (
          <Marker position={[geolocation.latitude, geolocation.longitude]} icon={createDivIcon("#ef4444", 20)}>
            <Popup>
              <div style={{ fontFamily: "monospace", fontSize: 11 }}>
                <b style={{ color: "#ef4444" }}>RESOLVED ORIGIN</b>
                <br />
                IP: {originIp}
                <br />
                {geolocation.city || "Unknown"}, {geolocation.country || "Unknown"}
              </div>
            </Popup>
          </Marker>
        )}

        {/* Hop markers when no origin IP */}
        {!hasCoords &&
          fakeCoords.map((coord, i) => {
            const hop = hops[i];
            const u = bnd === null || hop.hop < bnd;
            const color = u ? "#ef4444" : "#10b981";
            return (
              <Marker key={hop.hop} position={coord} icon={createDivIcon(color, 12)}>
                <Popup>
                  <div style={{ fontFamily: "monospace", fontSize: 10 }}>
                    <b>Hop #{hop.hop}</b> {u ? "(Unverified)" : "(Verified)"}
                    <br />
                    {hop.from || "Unknown"}
                  </div>
                </Popup>
              </Marker>
            );
          })}

        {/* Path polyline */}
        <Polyline
          positions={pathPoints}
          pathOptions={{
            color: hasCoords ? "#f59e0b" : "#64748b",
            weight: 2,
            dashArray: "8, 8",
            opacity: hasCoords ? 0.7 : 0.4,
          }}
        />

        <MapController center={mapCenter} zoom={zoomLevel} />
      </MapContainer>

      {/* Map info overlay */}
      <div className="absolute bottom-2 left-2 bg-[#0a101eee] border border-cyber-border/40 rounded-lg p-2.5 font-mono z-[1000] backdrop-blur-md">
        {hasCoords ? (
          <>
            <div className="text-blue-400 font-bold text-[11px]">{originIp}</div>
            <div className="text-slate-400 text-[10px]">
              {geolocation.city}, {geolocation.country}
            </div>
          </>
        ) : (
          <>
            <div className="text-amber-400 font-bold text-[10px]">PATH SIMULATED</div>
            <div className="text-slate-500 text-[9px]">{hops.length} hops traced from relay chain</div>
          </>
        )}
      </div>

      {/* Status badge */}
      <div
        className="absolute top-2 right-2 rounded-md px-2.5 py-1 text-[7px] font-bold tracking-wider uppercase font-mono z-[1000] backdrop-blur-md flex items-center gap-1.5"
        style={{
          border: `1px solid ${hasCoords ? "#10b98130" : "#f59e0b30"}`,
          color: hasCoords ? "#10b981" : "#f59e0b",
          background: hasCoords ? "#10b98108" : "#f59e0b08",
        }}
      >
        <div
          className="w-1.5 h-1.5 rounded-full"
          style={{
            background: hasCoords ? "#10b981" : "#f59e0b",
            animation: "blink 2s infinite",
          }}
        />
        {hasCoords ? "ORIGIN RESOLVED" : "SIMULATED PATH"}
      </div>
    </div>
  );
}
