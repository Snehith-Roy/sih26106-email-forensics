import { useState, useRef } from "react";
import { Upload, Activity, ShieldAlert } from "lucide-react";
import axios from "axios";

export default function UploadPanel({ onResult }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

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
      onResult(res.data);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || "Threat analysis failed. Please verify if the backend server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => !loading && fileInputRef.current?.click()}
        className={`
          relative overflow-hidden cursor-pointer group rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-300
          ${loading ? "border-blue-500/40 bg-blue-500/5 cursor-not-allowed" : ""}
          ${isDragActive ? "border-blue-500 bg-blue-500/10 shadow-glow-blue scale-[1.01]" : "border-cyber-border hover:border-blue-500/50 bg-cyber-card/20"}
        `}
      >
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept=".eml"
          onChange={(e) => e.target.files?.[0] && processFile(e.target.files[0])}
          disabled={loading}
        />

        {/* Scanning Light Line */}
        {loading && (
          <div className="absolute inset-x-0 top-0 h-1/2 bg-gradient-to-b from-blue-500/10 via-blue-500/20 to-transparent animate-scan border-b border-blue-500/40 pointer-events-none" />
        )}

        <div className="flex flex-col items-center justify-center space-y-4">
          {loading ? (
            <>
              <Activity className="h-12 w-12 text-blue-500 animate-pulse" />
              <div className="space-y-1">
                <p className="text-blue-400 font-mono text-sm tracking-wider animate-pulse">
                  [ ANALYZING EMAIL PATHWAY & SECURITY THREATS... ]
                </p>
                <p className="text-slate-500 text-[10px] font-mono">
                  Reading email metadata and tracing transit server routes
                </p>
              </div>
            </>
          ) : (
            <>
              <Upload className="h-12 w-12 text-slate-400 group-hover:text-blue-400 transition-colors duration-300" />
              <div>
                <p className="text-slate-200 font-medium">Drag and drop EML Email File here</p>
                <p className="text-slate-500 text-xs mt-1">or click to browse local files (.eml)</p>
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 flex items-start gap-3 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 font-mono text-xs">
          <ShieldAlert className="h-5 w-5 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold">EMAIL INGESTION ERROR</p>
            <p>{error}</p>
          </div>
        </div>
      )}
    </div>
  );
}
