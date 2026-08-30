export default function NlpAnalysis({ nlp }) {
  if (!nlp) return null;

  const rows = [
    {
      label: "ML Phishing Probability",
      value: `${(nlp.ml_phishing_probability * 100).toFixed(1)}%`,
      bar: nlp.ml_phishing_probability,
      color: nlp.ml_phishing_probability >= 0.7 ? "#dc2626" : nlp.ml_phishing_probability >= 0.4 ? "#f59e0b" : "#16a34a",
    },
    {
      label: "Urgency Score",
      value: nlp.urgency_score.toFixed(2),
      bar: nlp.urgency_score,
      color: nlp.urgency_score >= 0.7 ? "#dc2626" : "#f59e0b",
    },
    {
      label: "Impersonation Score",
      value: nlp.impersonation_score.toFixed(2),
      bar: nlp.impersonation_score,
      color: nlp.impersonation_score >= 0.5 ? "#dc2626" : "#16a34a",
    },
    {
      label: "Display Name Mismatch",
      value: nlp.display_name_mismatch ? "Yes" : "No",
      bar: nlp.display_name_mismatch ? 1 : 0,
      color: nlp.display_name_mismatch ? "#dc2626" : "#16a34a",
    },
  ];

  return (
    <div style={{ marginTop: 24 }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>
        NLP Analysis
      </h2>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {rows.map((r) => (
          <div key={r.label} style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ width: 200, fontSize: 14, color: "#374151" }}>{r.label}</span>
            <div style={{ flex: 1, height: 8, background: "#e5e7eb", borderRadius: 4, overflow: "hidden" }}>
              <div style={{ width: `${r.bar * 100}%`, height: "100%", background: r.color, borderRadius: 4 }} />
            </div>
            <span style={{ width: 80, fontSize: 14, fontWeight: 600, textAlign: "right" }}>{r.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
