import React from "react";
import { ShieldCheck, ShieldAlert, ShieldAlert as ShieldWarning, CheckCircle, XCircle, AlertTriangle } from "lucide-react";

export default function AuthBadges({ auth }) {
  const getStatusConfig = (result) => {
    switch (result?.toLowerCase()) {
      case "pass":
        return {
          bg: "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
          icon: <CheckCircle className="h-5 w-5 text-emerald-400" />,
          label: "PASS",
        };
      case "fail":
        return {
          bg: "bg-rose-500/10 border-rose-500/30 text-rose-400",
          icon: <XCircle className="h-5 w-5 text-rose-400" />,
          label: "FAIL",
        };
      case "none":
        return {
          bg: "bg-amber-500/10 border-amber-500/30 text-amber-400",
          icon: <AlertTriangle className="h-5 w-5 text-amber-400" />,
          label: "NONE",
        };
      case "softfail":
      case "neutral":
        return {
          bg: "bg-amber-500/10 border-amber-500/25 text-amber-300",
          icon: <AlertTriangle className="h-5 w-5 text-amber-300" />,
          label: "NEUTRAL / SOFTFAIL",
        };
      default:
        return {
          bg: "bg-slate-500/10 border-slate-500/30 text-slate-400",
          icon: <AlertTriangle className="h-5 w-5 text-slate-400" />,
          label: "UNKNOWN",
        };
    }
  };

  const spf = getStatusConfig(auth.spf_result);
  const dkim = getStatusConfig(auth.dkim_result);
  const dmarc = getStatusConfig(auth.dmarc_result);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
      {/* SPF Card */}
      <div className={`border rounded-xl p-4 flex flex-col justify-between transition-all duration-300 ${spf.bg}`}>
        <div className="flex items-center justify-between mb-3">
          <span className="font-bold text-slate-400 tracking-wider">SPF RECORD</span>
          {spf.icon}
        </div>
        <div className="space-y-1">
          <p className="text-lg font-black">{spf.label}</p>
          <p className="text-[10px] text-slate-500">
            {auth.sender_publishes_spf ? "✓ Sender publishes valid SPF record" : "⚠️ Domain lacks published SPF record"}
          </p>
          {auth.spf_dns_lookup_count !== null && (
            <p className="text-[10px] text-slate-500">
              DNS Lookups: {auth.spf_dns_lookup_count} / 10 limit
            </p>
          )}
        </div>
      </div>

      {/* DKIM Card */}
      <div className={`border rounded-xl p-4 flex flex-col justify-between transition-all duration-300 ${dkim.bg}`}>
        <div className="flex items-center justify-between mb-3">
          <span className="font-bold text-slate-400 tracking-wider">DKIM SIGNATURE</span>
          {dkim.icon}
        </div>
        <div className="space-y-1">
          <p className="text-lg font-black">{dkim.label}</p>
          <p className="text-[10px] text-slate-500">
            {auth.dkim_independently_verified === true
              ? "✓ Cryptographically re-verified on-demand"
              : auth.dkim_independently_verified === false
              ? "⚠️ Signature mismatch or verification failed"
              : "⚠️ No cryptographic signature found"}
          </p>
        </div>
      </div>

      {/* DMARC Card */}
      <div className={`border rounded-xl p-4 flex flex-col justify-between transition-all duration-300 ${dmarc.bg}`}>
        <div className="flex items-center justify-between mb-3">
          <span className="font-bold text-slate-400 tracking-wider">DMARC POLICY</span>
          {dmarc.icon}
        </div>
        <div className="space-y-1">
          <p className="text-lg font-black">{dmarc.label}</p>
          <p className="text-[10px] text-slate-500">
            {auth.sender_publishes_dmarc
              ? `✓ Published Policy: p=${auth.dmarc_policy || "none"}`
              : "⚠️ No published DMARC record found"}
          </p>
          {auth.dmarc_policy === "none" && (
            <p className="text-[10px] text-amber-500 font-bold">
              ⚠️ Alert: p=none allows domain spoofing
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
