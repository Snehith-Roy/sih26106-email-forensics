export default function EmailDetails({ parsed, origin }) {
  if (!parsed) return null;

  const fields = [
    { label: "From", value: `${parsed.from_name} <${parsed.from_address}>` },
    { label: "To", value: parsed.to_addresses?.join(", ") },
    { label: "Subject", value: parsed.subject },
    { label: "Date", value: parsed.date },
  ];

  const hops = origin?.unverified_self_reported_hops || [];

  return (
    <div style={{ marginTop: 24 }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>
        Parsed Email
      </h2>
      <table style={{ width: "100%", fontSize: 14, borderCollapse: "collapse" }}>
        <tbody>
          {fields.map((f) => (
            <tr key={f.label} style={{ borderBottom: "1px solid #e5e7eb" }}>
              <td style={{ padding: "6px 12px 6px 0", fontWeight: 600, color: "#6b7280", whiteSpace: "nowrap" }}>
                {f.label}
              </td>
              <td style={{ padding: "6px 0", color: "#111827" }}>{f.value}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {hops.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>
            Relay Hops
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {hops.map((hop, i) => (
              <div
                key={i}
                style={{
                  padding: "8px 12px",
                  background: "#f9fafb",
                  borderRadius: 6,
                  fontSize: 13,
                  borderLeft: `3px solid ${hop.ip ? "#f59e0b" : "#dc2626"}`,
                }}
              >
                <span style={{ fontWeight: 600 }}>Hop {i + 1}:</span>{" "}
                {hop.host || <em style={{ color: "#dc2626" }}>unverified</em>}
                {hop.ip && (
                  <span style={{ color: "#6b7280", marginLeft: 8 }}>({hop.ip})</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {origin?.trace_confidence && (
        <p style={{ marginTop: 8, fontSize: 12, color: "#9ca3af" }}>
          Trace confidence: {origin.trace_confidence}
        </p>
      )}
    </div>
  );
}
