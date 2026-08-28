export default function ScoreBreakdown({ breakdown }) {
  if (!breakdown || Object.keys(breakdown).length === 0) return null;

  const maxScore = Math.max(...Object.values(breakdown), 1);

  const labelMap = {
    ml_phishing_probability: "ML Phishing Probability",
    urgency_score: "Urgency Score",
    impersonation_score: "Impersonation Score",
    display_name_mismatch: "Display Name Mismatch",
    auth_fail: "Auth Failures",
    mx_mismatch: "MX Mismatch",
    spf_fail: "SPF Fail",
    dkim_fail: "DKIM Fail",
    dmarc_fail: "DMARC Fail",
    domain_age: "Domain Age",
    ip_abuse: "IP Abuse Score",
    geo_risk: "Geo Risk",
    relay_anomaly: "Relay Anomaly",
    attachment_risk: "Attachment Risk",
  };

  const sorted = Object.entries(breakdown).sort((a, b) => b[1] - a[1]);

  return (
    <div style={{ marginTop: 24 }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>
        Score Breakdown
      </h2>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {sorted.map(([key, val]) => (
          <div key={key} style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ width: 200, fontSize: 13, color: "#374151" }}>
              {labelMap[key] || key}
            </span>
            <div style={{ flex: 1, height: 8, background: "#e5e7eb", borderRadius: 4, overflow: "hidden" }}>
              <div
                style={{
                  width: `${(val / maxScore) * 100}%`,
                  height: "100%",
                  background: val >= 15 ? "#dc2626" : val >= 5 ? "#f59e0b" : "#16a34a",
                  borderRadius: 4,
                }}
              />
            </div>
            <span style={{ width: 50, fontSize: 13, fontWeight: 600, textAlign: "right", color: "#374151" }}>
              +{val}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
