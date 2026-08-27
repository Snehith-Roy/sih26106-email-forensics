import { useState } from "react";
import axios from "axios";

export default function UploadPanel({ onResult }) {
  const [loading, setLoading] = useState(false);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    const form = new FormData();
    form.append("file", file);
    const res = await axios.post("/api/analyze", form);
    onResult(res.data);
    setLoading(false);
  }

  return (
    <div style={{ padding: 16, border: "2px dashed #d1d5db", borderRadius: 12, textAlign: "center" }}>
      <input type="file" accept=".eml" onChange={handleUpload} />
      {loading && <p style={{ fontSize: 14, color: "#6b7280", marginTop: 8 }}>Analyzing…</p>}
    </div>
  );
}
