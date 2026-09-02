import { useState, useEffect } from "react";
import RiskGauge from "./components/RiskGauge.jsx";
import RelayTimeline from "./components/RelayTimeline.jsx";
import RelayMap from "./components/RelayMap.jsx";
import CampaignGraph from "./components/CampaignGraph.jsx";
import { Download, Globe, AlertTriangle, ShieldCheck, Mail, Calendar, User, Search, Terminal, Upload, Activity, ShieldAlert } from "lucide-react";
import axios from "axios";

export default function App() {
  const [result, setResult] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Global window drag & drop event handling
  useEffect(() => {
    const handleDragEnter = (e) => { e.preventDefault(); setIsDragActive(true); };
    const handleDragLeave = (e) => { e.preventDefault(); if (e.clientX === 0 && e.clientY === 0) setIsDragActive(false); };
    const handleDragOver = (e) => { e.preventDefault(); };
    const handleDrop = (e) => {
      e.preventDefault(); setIsDragActive(false);
      if (e.dataTransfer.files && e.dataTransfer.files[0]) processFile(e.dataTransfer.files[0]);
    };
    window.addEventListener("dragenter", handleDragEnter);
    window.addEventListener("dragleave", handleDragLeave);
    window.addEventListener("dragover", handleDragOver);
    window.addEventListener("drop", handleDrop);
    return () => {
      window.removeEventListener("dragenter", handleDragEnter);
      window.removeEventListener("dragleave", handleDragLeave);
      window.removeEventListener("dragover", handleDragOver);
      window.removeEventListener("drop", handleDrop);
    };
  }, []);

  const processFile = async (file) => {
    if (!file.name.endsWith(".eml")) { setError("Invalid file type. Please upload a .eml file"); return; }
    setError(null); setLoading(true);
    const form = new FormData(); form.append("file", file);
    try { const res = await axios.post("/api/analyze", form); setResult(res.data); }
    catch (err) { setError(err.response?.data?.detail || "Analysis failed. Is the backend running?"); }
    finally { setLoading(false); }
  };

  const handleDownloadReport = async () => {
    if (!result) return; setDownloading(true);
    try {
      const res = await axios.post("/api/reports/generate", result, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a"); link.href = url;
      link.download = `forensic_report_${result.parsed.subject.replace(/[^a-z0-9]/gi, "_").toLowerCase()}.pdf`;
      document.body.appendChild(link); link.click(); link.remove();
    } catch (err) { console.error("PDF download failed", err); }
    finally { setDownloading(false); }
  };

  const displayScore = result ? result.risk_score.total_score : 0;
  const displayAuth = result ? result.auth : { spf_result: "none", dkim_result: "none", dmarc_result: "none" };
  const displayParsed = result ? result.parsed : {
    from_name: "Awaiting Scan", from_address: "no-file@forensics.local", to_addresses: [],
    subject: "Upload a .eml file to begin", date: "-", body: "", received_chain: []
  };
  const nlp = result?.nlp || {};
  const breakdown = result?.risk_score?.breakdown || {};
  const maxBreakdown = Math.max(...Object.values(breakdown), 1);

  return (
    <div className="h-screen w-screen flex flex-col bg-cyber-bg text-slate-100 overflow-hidden font-sans select-none">
      {/* Global Drag & Drop Overlay */}
      {isDragActive && (
        <div className="absolute inset-0 bg-cyber-bg/95 backdrop-blur-md z-[9999] border-4 border-dashed border-blue-500 flex flex-col items-center justify-center space-y-4 transition-all duration-300">
          <Upload className="h-16 w-16 text-blue-400 animate-bounce" />
          <h2 className="text-xl font-bold tracking-widest text-slate-200 uppercase font-mono">DROP EMAIL FILE (.eml)</h2>
          <p className="text-slate-500 font-mono text-xs">Ingestion gateway active. Release to parse relay path.</p>
        </div>
      )}

      {/* Processing Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-cyber-bg/90 backdrop-blur-sm z-[9998] flex flex-col items-center justify-center space-y-4">
          <Activity className="h-12 w-12 text-blue-500 animate-pulse" />
          <div className="space-y-1 text-center font-mono">
            <p className="text-blue-400 text-sm tracking-wider animate-pulse">[ ANALYZING EMAIL PATHWAY... ]</p>
            <p className="text-slate-500 text-[10px]">Reading metadata and tracing transit routes</p>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="h-14 shrink-0 border-b border-cyber-border/80 bg-[#0c1220]/90 backdrop-blur-md flex items-center justify-between px-6 z-40">
        <div className="flex items-center gap-3">
          <div className="h-7 w-7 rounded bg-gradient-to-br from-blue-600 to-blue-400 flex items-center justify-center shadow-glow-blue">
            <Terminal className="h-4 w-4 text-white" />
          </div>
          <div>
            <h1 className="text-xs font-black tracking-widest uppercase bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
              Email Forensic & Threat Intelligence Platform
            </h1>
            <p className="text-[9px] text-slate-500 font-mono tracking-widest uppercase">SIH26106 Threat Platform</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {result && <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />}
          <label className="flex items-center gap-1.5 bg-blue-600/10 border border-blue-500/30 text-blue-400 hover:bg-blue-600/20 hover:border-blue-500/50 px-3 py-1.5 rounded-lg transition-all duration-300 text-[9px] font-mono cursor-pointer font-bold uppercase">
            <Upload className="h-3.5 w-3.5" /> Upload Email (.eml)
            <input type="file" accept=".eml" className="hidden" onChange={(e) => e.target.files?.[0] && processFile(e.target.files[0])} />
          </label>
          {result && (
            <button onClick={handleDownloadReport} disabled={downloading}
              className="flex items-center gap-1.5 bg-slate-900 border border-cyber-border/80 text-slate-300 hover:border-slate-500 px-3 py-1.5 rounded-lg transition-all duration-300 text-[9px] font-mono font-bold uppercase">
              <Download className="h-3.5 w-3.5" /> {downloading ? "Exporting..." : "Download PDF Report"}
            </button>
          )}
        </div>
      </header>

      {/* Main Workspace Grid Layout */}
      <main className="flex-1 grid grid-cols-4 grid-rows-3 gap-3 p-3 overflow-hidden">
        {/* Left: Gauge + Auth */}
        <section className="col-span-1 row-span-2 bg-[#0c1220]/80 border border-cyber-border/60 rounded-xl p-4 overflow-hidden flex flex-col justify-between h-full">
          <RiskGauge score={displayScore} auth={displayAuth} />
        </section>

        {/* Center: Map with relay simulation */}
        <section className="col-span-2 row-span-2 bg-[#0c1220]/80 border border-cyber-border/60 rounded-xl p-3 overflow-hidden flex flex-col h-full">
          <div className="flex items-center justify-between border-b border-cyber-border/40 pb-2 mb-2 shrink-0">
            <span className="text-[10px] text-slate-400 uppercase tracking-widest font-bold font-mono">Email Relay Path Simulation</span>
            <span className="text-blue-400 text-[8px] tracking-wider uppercase font-mono flex items-center gap-1">
              <Globe className="h-3 w-3" /> Live Trace
            </span>
          </div>
          <div className="flex-1 w-full rounded-lg overflow-hidden">
            <RelayMap
              geolocation={result?.origin?.geolocation}
              originIp={result?.origin?.origin_ip}
              receivedChain={displayParsed.received_chain}
              trustBoundaryHop={result?.origin?.trust_boundary_hop}
            />
          </div>
        </section>

        {/* Right: Metadata + Timeline + NLP + Score Breakdown */}
        <section className="col-span-1 row-span-2 bg-[#0c1220]/80 border border-cyber-border/60 rounded-xl p-4 overflow-hidden flex flex-col h-full justify-between">
          <div className="flex items-center justify-between border-b border-cyber-border/40 pb-2 mb-2 shrink-0">
            <span className="text-[10px] text-slate-400 uppercase tracking-widest font-bold font-mono">Forensic Analysis</span>
            <span className="text-blue-400 text-[8px] tracking-wider uppercase font-mono">Details</span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {/* Metadata */}
            <div className="space-y-1.5 font-mono text-[9px]">
              {[
                ["THREAT", result ? (displayScore >= 70 ? "Threat Detected" : displayScore >= 40 ? "Suspicious" : "Safe") : "Awaiting File",
                  result ? (displayScore >= 70 ? "text-rose-400" : displayScore >= 40 ? "text-amber-400" : "text-emerald-400") : "text-slate-500"],
                ["SENDER", displayParsed.from_address, "text-slate-300"],
                ["ORIGIN IP", result?.origin?.origin_ip || "Unresolved", "text-slate-300"],
                ["SUBJECT", displayParsed.subject, "text-slate-300"],
                ["DATE", displayParsed.date, "text-slate-400"],
              ].map(([k, v, cls]) => (
                <div key={k} className="flex justify-between items-start gap-2 pb-1 border-b border-cyber-border/15">
                  <span className="text-slate-500 shrink-0">{k}:</span>
                  <span className={`${cls} font-bold text-right break-all`} title={v}>{v}</span>
                </div>
              ))}
            </div>

            {/* NLP Signals */}
            {result && (
              <div>
                <div className="text-[9px] text-slate-500 uppercase tracking-widest font-bold font-mono mb-2">NLP Signals</div>
                {[
                  ["ML Phishing", nlp.ml_phishing_probability || 0, nlp.ml_phishing_probability >= 0.7 ? "bg-rose-500" : nlp.ml_phishing_probability >= 0.4 ? "bg-amber-500" : "bg-emerald-500", nlp.ml_phishing_probability >= 0.7 ? "text-rose-400" : nlp.ml_phishing_probability >= 0.4 ? "text-amber-400" : "text-emerald-400"],
                  ["Urgency", nlp.urgency_score || 0, nlp.urgency_score >= 0.5 ? "bg-rose-500" : "bg-amber-500", nlp.urgency_score >= 0.5 ? "text-rose-400" : "text-amber-400"],
                  ["Impersonation", nlp.impersonation_score || 0, nlp.impersonation_score >= 0.5 ? "bg-rose-500" : "bg-emerald-500", nlp.impersonation_score >= 0.5 ? "text-rose-400" : "text-emerald-400"],
                ].map(([label, val, barCls, txtCls]) => (
                  <div key={label} className="flex items-center gap-2 mb-1.5">
                    <span className="text-[8px] text-slate-500 w-20 shrink-0 uppercase tracking-wider">{label}</span>
                    <div className="flex-1 h-1 bg-cyber-bg rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all duration-1000 ${barCls}`} style={{ width: `${val * 100}%` }} />
                    </div>
                    <span className={`text-[9px] font-bold w-10 text-right ${txtCls}`}>{(val * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            )}

            {/* Score Breakdown */}
            {result && Object.keys(breakdown).length > 0 && (
              <div>
                <div className="text-[9px] text-slate-500 uppercase tracking-widest font-bold font-mono mb-2">Score Breakdown</div>
                {Object.entries(breakdown)
                  .sort((a, b) => b[1] - a[1])
                  .map(([key, val]) => {
                    const cl = val >= 15 ? "bg-rose-500" : val >= 5 ? "bg-amber-500" : "bg-emerald-500";
                    const tx = val >= 15 ? "text-rose-400" : val >= 5 ? "text-amber-400" : "text-emerald-400";
                    const name = key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
                    return (
                      <div key={key} className="flex items-center gap-2 mb-1">
                        <span className="text-[7px] text-slate-500 w-24 shrink-0 uppercase tracking-wider">{name}</span>
                        <div className="flex-1 h-1 bg-cyber-bg rounded-full overflow-hidden">
                          <div className={`h-full rounded-full transition-all duration-1000 ${cl}`} style={{ width: `${(val / maxBreakdown) * 100}%` }} />
                        </div>
                        <span className={`text-[8px] font-bold w-8 text-right ${tx}`}>+{val}</span>
                      </div>
                    );
                  })}
              </div>
            )}

            {/* Relay Timeline */}
            <div>
              <div className="text-[9px] text-slate-500 uppercase tracking-widest font-bold font-mono mb-2">Relay Hop Trace</div>
              <RelayTimeline hops={displayParsed.received_chain} trustBoundaryHop={result?.origin?.trust_boundary_hop} />
            </div>
          </div>
        </section>

        {/* Bottom: Campaign */}
        <section className="col-span-4 row-span-1 bg-[#0c1220]/80 border border-cyber-border/60 rounded-xl p-3 overflow-hidden flex flex-col h-full justify-between">
          <CampaignGraph currentAnalysis={result} />
        </section>
      </main>

      {/* Global Error Banner */}
      {error && (
        <div className="absolute bottom-4 right-4 z-50 max-w-sm flex items-start gap-3 p-4 rounded-xl bg-rose-950 border border-rose-500/50 text-rose-300 font-mono text-xs shadow-glow-red">
          <ShieldAlert className="h-5 w-5 shrink-0 mt-0.5" />
          <div>
            <p className="font-bold uppercase tracking-wider">Forensic Alert</p>
            <p className="text-[10px] text-slate-400 mt-1">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-slate-400 hover:text-slate-100 font-bold ml-2">×</button>
        </div>
      )}
    </div>
  );
}
