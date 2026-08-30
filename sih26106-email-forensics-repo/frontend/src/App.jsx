import { useState } from "react";
import UploadPanel from "./components/UploadPanel.jsx";
import RiskGauge from "./components/RiskGauge.jsx";
import RelayMap from "./components/RelayMap.jsx";
import AuthBadges from "./components/AuthBadges.jsx";
import NlpAnalysis from "./components/NlpAnalysis.jsx";
import ScoreBreakdown from "./components/ScoreBreakdown.jsx";
import EmailDetails from "./components/EmailDetails.jsx";

export default function App() {
  const [result, setResult] = useState(null);

  const riskLabel =
    !result
      ? ""
      : result.risk_score.total_score >= 70
      ? "HIGH RISK — Likely Phishing"
      : result.risk_score.total_score >= 40
      ? "MEDIUM RISK — Suspicious"
      : "LOW RISK — Likely Legitimate";

  const riskColor =
    !result
      ? "#000"
      : result.risk_score.total_score >= 70
      ? "#dc2626"
      : result.risk_score.total_score >= 40
      ? "#f59e0b"
      : "#16a34a";

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 20 }}>
        SIH26106 — Email Forensics Dashboard
      </h1>
      <UploadPanel onResult={setResult} />

      {result && (
        <>
          {/* Risk score + Map row */}
          <div style={{ display: "flex", gap: 32, marginTop: 24, alignItems: "flex-start" }}>
            <div style={{ textAlign: "center" }}>
              <RiskGauge score={result.risk_score.total_score} />
              <p style={{ marginTop: 8, fontWeight: 600, fontSize: 14, color: riskColor }}>
                {riskLabel}
              </p>
            </div>
            <div style={{ flex: 1 }}>
              <RelayMap
                geolocation={result.origin.geolocation}
                originIp={result.origin.origin_ip}
              />
            </div>
          </div>

          {/* Auth badges */}
          <AuthBadges auth={result.auth} />

          {/* NLP + Score Breakdown side by side */}
          <div style={{ display: "flex", gap: 32, marginTop: 24 }}>
            <div style={{ flex: 1 }}>
              <NlpAnalysis nlp={result.nlp} />
            </div>
            <div style={{ flex: 1 }}>
              <ScoreBreakdown breakdown={result.risk_score.breakdown} />
            </div>
          </div>

          {/* Email details */}
          <EmailDetails parsed={result.parsed} origin={result.origin} />
        </>
      )}
    </div>
  );
}
