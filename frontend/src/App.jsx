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
    const handleDragEnter = (e) => {
      e.preventDefault();
      setIsDragActive(true);
    };

    const handleDragLeave = (e) => {
      e.preventDefault();
      if (e.clientX === 0 && e.clientY === 0) {
        setIsDragActive(false);
      }
    };

    const handleDragOver = (e) => {
      e.preventDefault();
    };

    const handleDrop = (e) => {
      e.preventDefault();
      setIsDragActive(false);
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        processFile(e.dataTransfer.files[0]);
      }
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
    if (!file.name.endsWith(".eml")) {
      setError("Invalid file type. Please upload a standard email file ending in .eml");
      return;
    }
    setError(null);
    setLoading(true);
    const form = new FormData();
    form.append("file", file);

    try {
      const res = await axios.post("/api/analyze", form);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || "Threat analysis failed. Please verify if the backend server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!result) return;
    setDownloading(true);
    try {
      const res = await axios.post("/api/reports/generate", result, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      const fileName = `forensic_report_${result.parsed.subject.replace(/[^a-z0-9]/gi, "_").toLowerCase()}.pdf`;
      link.setAttribute("download", fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Failed to download PDF report", err);
    } finally {
      setDownloading(false);
    }
  };

  // Provide initial mock values before file ingestion to keep layout rendered
  const displayScore = result ? result.risk_score.total_score : 0;
  const displayAuth = result ? result.auth : { spf_result: "none", dkim_result: "none", dmarc_result: "none" };
  const displayParsed = result ? result.parsed : {
    from_name: "Awaiting Scan Ingestion",
    from_address: "no-ingest@forensics.local",
    to_addresses: [],
    subject: "No active scan transaction",
    date: "-",
    body: "Please upload or drop a raw .eml file to inspect content.",
    received_chain: []
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-cyber-bg text-slate-100 overflow-hidden font-sans select-none">
      
      {/* Global Drag & Drop Overlay */}
      {isDragActive && (
        <div className="absolute inset-0 bg-cyber-bg/95 backdrop-blur-md z-[9999] border-4 border-dashed border-blue-500 flex flex-col items-center justify-center space-y-4 transition-all duration-300">
          <Upload className="h-16 w-16 text-blue-400 animate-bounce" />
          <h2 className="text-xl font-bold tracking-widest text-slate-200 uppercase font-mono">
            DROP EMAIL FILE (.eml) TO START THREAT SCANS
          </h2>
          <p className="text-slate-500 font-mono text-xs">
            Ingestion gateway active. Release to parse relay path.
          </p>
        </div>
      )}

      {/* Processing Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-cyber-bg/90 backdrop-blur-sm z-[9998] flex flex-col items-center justify-center space-y-4">
          <Activity className="h-12 w-12 text-blue-500 animate-pulse" />
          <div className="space-y-1 text-center font-mono">
            <p className="text-blue-400 text-sm tracking-wider animate-pulse">
              [ ANALYZING EMAIL PATHWAY & SECURITY THREATS... ]
            </p>
            <p className="text-slate-500 text-[10px]">
              Reading email metadata and tracing transit server routes
            </p>
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
            <p className="text-[9px] text-slate-500 font-mono tracking-widest uppercase">
              SIH26106 Threat Platform
            </p>
          </div>
        </div>


        {/* Action controls (exactly as mockup) */}
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 bg-blue-600/10 border border-blue-500/30 text-blue-400 hover:bg-blue-600/20 hover:border-blue-500/50 px-3 py-1.5 rounded-lg transition-all duration-300 text-[9px] font-mono cursor-pointer font-bold uppercase">
            <Upload className="h-3.5 w-3.5" />
            Upload Email (.eml)
            <input
              type="file"
              accept=".eml"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && processFile(e.target.files[0])}
            />
          </label>

          {result && (
            <button
              onClick={handleDownloadReport}
              disabled={downloading}
              className="flex items-center gap-1.5 bg-slate-900 border border-cyber-border/80 text-slate-300 hover:border-slate-500 px-3 py-1.5 rounded-lg transition-all duration-300 text-[9px] font-mono font-bold uppercase"
            >
              <Download className="h-3.5 w-3.5" />
              {downloading ? "Exporting..." : "Download PDF Report"}
            </button>
          )}
        </div>
      </header>

      {/* Main Workspace Grid Layout */}
      <main className="flex-1 grid grid-cols-4 grid-rows-3 gap-4 p-4 overflow-hidden">
        
        {/* Left Column: Severity assessment + standard checks (col-span-1 row-span-2) */}
        <section className="col-span-1 row-span-2 bg-[#0c1220]/80 border border-cyber-border/60 rounded-xl p-4 overflow-hidden flex flex-col justify-between h-full">
          <RiskGauge score={displayScore} auth={displayAuth} />
        </section>

        {/* Center Column: Geolocation Tracer (col-span-2 row-span-2) */}
        <section className="col-span-2 row-span-2 bg-[#0c1220]/80 border border-cyber-border/60 rounded-xl p-4 overflow-hidden flex flex-col h-full">
          <div className="flex items-center justify-between border-b border-cyber-border/40 pb-2 mb-2 shrink-0">
            <span className="text-[10px] text-slate-400 uppercase tracking-widest font-bold font-mono">Geographical Source IP Tracer</span>
            <span className="text-blue-400 text-[8px] tracking-wider uppercase font-mono">Origin Location Pin</span>
          </div>
          <div className="flex-1 w-full rounded-lg overflow-hidden">
            <RelayMap 
              geolocation={result?.origin?.geolocation} 
              originIp={result?.origin?.origin_ip} 
            />
          </div>
        </section>

        {/* Right Column: Metadata & Hops Timeline (col-span-1 row-span-2) */}
        <section className="col-span-1 row-span-2 bg-[#0c1220]/80 border border-cyber-border/60 rounded-xl p-4 overflow-hidden flex flex-col h-full justify-between">
          <div className="flex items-center justify-between border-b border-cyber-border/40 pb-2 shrink-0">
            <span className="text-[10px] text-slate-400 uppercase tracking-widest font-bold font-mono">Ingested Message Metadata</span>
            <span className="text-blue-400 text-[8px] tracking-wider uppercase font-mono">Details</span>
          </div>

          {/* Email Text details */}
          <div className="h-[38%] overflow-y-auto border-b border-cyber-border/40 py-1.5 space-y-1.5 font-mono text-[9px] pr-1">
            <div className="flex justify-between items-start gap-4 pb-1 border-b border-cyber-border/20">
              <span className="text-slate-500 shrink-0">THREAT STATUS:</span>
              <span className={`font-bold text-right ${result ? (displayScore >= 70 ? "text-rose-400" : "text-amber-400") : "text-slate-400"}`}>
                {result ? (displayScore >= 70 ? "Threat Detected" : "Suspicious Hops") : "Awaiting File Ingestion"}
              </span>
            </div>
            <div className="flex justify-between items-start gap-4 pb-1 border-b border-cyber-border/20">
              <span className="text-slate-500 shrink-0">SENDER:</span>
              <span className="text-slate-300 font-bold text-right break-all" title={displayParsed.from_address}>
                {displayParsed.from_address}
              </span>
            </div>
            <div className="flex justify-between items-start gap-4 pb-1 border-b border-cyber-border/20">
              <span className="text-slate-500 shrink-0">TRANSIT IP:</span>
              <span className="text-slate-300 text-right font-medium" title={result?.origin?.origin_ip || "-"}>
                {result?.origin?.origin_ip || "-"}
              </span>
            </div>
            <div className="flex justify-between items-start gap-4 pb-1 border-b border-cyber-border/20">
              <span className="text-slate-500 shrink-0">SUBJECT:</span>
              <span className="text-slate-300 font-bold text-right break-words" title={displayParsed.subject}>
                {displayParsed.subject}
              </span>
            </div>
            <div className="flex justify-between items-start gap-4">
              <span className="text-slate-500 shrink-0">RECEIVED AT:</span>
              <span className="text-slate-300 text-right break-words">{displayParsed.date}</span>
            </div>
          </div>

          {/* Forensic timeline hops list */}
          <div className="h-[58%] overflow-y-auto pt-2">
            <RelayTimeline 
              hops={displayParsed.received_chain} 
              trustBoundaryHop={result?.origin?.trust_boundary_hop} 
            />
          </div>
        </section>

        {/* Bottom Full-width Row: Campaign link graph (col-span-4 row-span-1) */}
        <section className="col-span-4 row-span-1 bg-[#0c1220]/80 border border-cyber-border/60 rounded-xl p-4 overflow-hidden flex flex-col h-full justify-between">
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
