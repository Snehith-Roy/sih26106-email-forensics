import React from "react";
import { Check, X, AlertTriangle, Shield } from "lucide-react";

export default function RiskGauge({ score, auth }) {
  const radius = 70;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getTheme = (val) => {
    if (val >= 70) {
      return {
        color: "text-rose-500",
        stroke: "url(#gaugeRed)",
        bg: "bg-rose-500/10",
        label: "Critical Threat",
        border: "border-rose-500/30",
        glow: "shadow-glow-red",
      };
    }
    if (val >= 40) {
      return {
        color: "text-amber-500",
        stroke: "url(#gaugeAmber)",
        bg: "bg-amber-500/10",
        label: "Suspicious Risk",
        border: "border-amber-500/30",
        glow: "shadow-glow-amber",
      };
    }
    return {
      color: "text-emerald-500",
      stroke: "url(#gaugeGreen)",
      bg: "bg-emerald-500/10",
      label: "Safe / Legitimate",
      border: "border-emerald-500/30",
      glow: "shadow-glow-green",
    };
  };

  const theme = getTheme(score);

  const getAuthBadge = (res) => {
    const val = res?.toLowerCase();
    if (val === "pass") {
      return {
        border: "border-emerald-500/30 bg-emerald-500/5 text-emerald-400",
        icon: <div className="h-5 w-5 rounded-full border border-emerald-500/50 flex items-center justify-center bg-emerald-500/10"><Check className="h-3 w-3" /></div>,
        label: "VERIFIED"
      };
    }
    if (val === "fail") {
      return {
        border: "border-rose-500/30 bg-rose-500/5 text-rose-400",
        icon: <div className="h-5 w-5 rounded-full border border-rose-500/50 flex items-center justify-center bg-rose-500/10"><X className="h-3 w-3" /></div>,
        label: "FAILED"
      };
    }
    return {
      border: "border-amber-500/30 bg-amber-500/5 text-amber-400",
      icon: <div className="h-5 w-5 rounded-full border border-amber-500/50 flex items-center justify-center bg-amber-500/10"><AlertTriangle className="h-3 w-3" /></div>,
      label: "MISSING"
    };
  };

  const spf = getAuthBadge(auth?.spf_result);
  const dkim = getAuthBadge(auth?.dkim_result);
  const dmarc = getAuthBadge(auth?.dmarc_result);

  return (
    <div className="flex flex-col h-full justify-between select-none">
      <div className="flex items-center justify-between border-b border-cyber-border/40 pb-2">
        <span className="text-[10px] text-slate-400 uppercase tracking-widest font-bold font-mono">Threat Severity Meter</span>
        <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
      </div>

      {/* Circle Gauge */}
      <div className="flex-1 flex flex-col items-center justify-center relative py-2">
        <div className="relative w-40 h-40 flex items-center justify-center">
          <div className={`absolute inset-4 rounded-full bg-cyber-bg/60 blur-lg transition-all duration-700 ${theme.bg}`} />

          <svg className="w-full h-full transform -rotate-90">
            <defs>
              <linearGradient id="gaugeGreen" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#059669" />
                <stop offset="100%" stopColor="#10b981" />
              </linearGradient>
              <linearGradient id="gaugeAmber" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#d97706" />
                <stop offset="100%" stopColor="#fbbf24" />
              </linearGradient>
              <linearGradient id="gaugeRed" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#dc2626" />
                <stop offset="100%" stopColor="#f87171" />
              </linearGradient>
            </defs>
            <circle
              cx="80"
              cy="80"
              r={radius}
              stroke="#162235"
              strokeWidth={strokeWidth}
              fill="transparent"
            />
            <circle
              cx="80"
              cy="80"
              r={radius}
              stroke={theme.stroke}
              strokeWidth={strokeWidth}
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
          </svg>

          <div className="absolute flex flex-col items-center justify-center font-mono">
            <div className="text-3xl font-black tracking-tighter text-slate-100">
              {score}<span className="text-xs text-slate-500 font-normal">/100</span>
            </div>
            <span className="text-[8px] text-slate-500 tracking-widest mt-0.5 uppercase">Risk Level</span>
          </div>
        </div>

        <div className={`mt-2 font-mono font-bold tracking-widest text-[9px] px-3 py-1 rounded border flex items-center gap-1.5 ${theme.color} ${theme.bg} ${theme.border}`}>
          <Shield className="h-3 w-3 shrink-0" />
          {theme.label.toUpperCase()}
        </div>
      </div>

      {/* Authentication Checks Grid */}
      <div className="grid grid-cols-3 gap-2 pt-3 border-t border-cyber-border/40 font-mono text-[8px]">
        {/* SPF Card */}
        <div className={`border rounded-lg p-2 flex flex-col items-center justify-between text-center transition-all ${spf.border}`}>
          <span className="text-slate-400 font-semibold mb-1 block uppercase tracking-wider">Sender SPF</span>
          {spf.icon}
          <span className="text-[7px] font-bold mt-1 text-slate-500 uppercase">{spf.label}</span>
        </div>

        {/* DKIM Card */}
        <div className={`border rounded-lg p-2 flex flex-col items-center justify-between text-center transition-all ${dkim.border}`}>
          <span className="text-slate-400 font-semibold mb-1 block uppercase tracking-wider">DKIM Sig</span>
          {dkim.icon}
          <span className="text-[7px] font-bold mt-1 text-slate-500 uppercase">{dkim.label}</span>
        </div>

        {/* DMARC Card */}
        <div className={`border rounded-lg p-2 flex flex-col items-center justify-between text-center transition-all ${dmarc.border}`}>
          <span className="text-slate-400 font-semibold mb-1 block uppercase tracking-wider">DMARC Policy</span>
          {dmarc.icon}
          <span className="text-[7px] font-bold mt-1 text-slate-500 uppercase">{dmarc.label}</span>
        </div>
      </div>
    </div>
  );
}
