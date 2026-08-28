export default function AuthBadges({ auth }) {
  if (!auth) return null;

  const checks = [
    { label: "SPF", value: auth.spf_result },
    { label: "DKIM", value: auth.dkim_result },
    { label: "DMARC", value: auth.dmarc_result },
  ];

  return (
    <div style={{ marginTop: 24 }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>
        Authentication Results
      </h2>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        {checks.map((c) => {
          const pass = c.value === "pass";
          return (
            <div
              key={c.label}
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                fontWeight: 600,
                fontSize: 14,
                color: "#fff",
                background: pass ? "#16a34a" : "#dc2626",
              }}
            >
              {c.label}: {c.value}
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 10, fontSize: 13, color: "#6b7280" }}>
        DKIM independently verified:{" "}
        {auth.dkim_independently_verified === null
          ? "N/A"
          : auth.dkim_independently_verified
          ? "Yes"
          : "No"}{" "}
        · Sender publishes SPF: {auth.sender_publishes_spf ? "Yes" : "No"} ·
        Sender publishes DMARC: {auth.sender_publishes_dmarc ? "Yes" : "No"}
      </div>
    </div>
  );
}
