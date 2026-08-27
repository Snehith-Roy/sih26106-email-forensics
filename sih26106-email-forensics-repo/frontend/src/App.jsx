import { useState } from "react";
import UploadPanel from "./components/UploadPanel.jsx";
import RiskGauge from "./components/RiskGauge.jsx";
import RelayMap from "./components/RelayMap.jsx";

export default function App() {
  const [result, setResult] = useState(null);

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <h1>SIH26106 — Email Forensics Dashboard</h1>
      <UploadPanel onResult={setResult} />

      {result && (
        <div style={{ display: "flex", gap: 32, marginTop: 24 }}>
          <RiskGauge score={result.risk_score.total_score} />
          <RelayMap
            geolocation={result.origin.geolocation}
            originIp={result.origin.origin_ip}
          />
        </div>
      )}
    </div>
  );
}
