import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function RelayMap({ geolocation, originIp }) {
  if (!geolocation?.latitude) {
    return <p style={{ color: "#6b7280" }}>No origin IP resolved.</p>;
  }
  const pos = [geolocation.latitude, geolocation.longitude];
  return (
    <MapContainer center={pos} zoom={4} style={{ height: 320, width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Marker position={pos}>
        <Popup>
          Origin IP: {originIp}
          <br />
          {geolocation.city}, {geolocation.country}
        </Popup>
      </Marker>
    </MapContainer>
  );
}
