import React from "react";
import { ShieldCheck, ShieldAlert, Calendar, Server } from "lucide-react";

export default function RelayTimeline({ hops, trustBoundaryHop }) {
  if (!hops || hops.length === 0) {
    return <p className="text-slate-500 font-mono text-xs">No mail server transit hops resolved yet.</p>;
  }

  const sortedHops = [...hops].reverse();

  return (
    <div className="relative pl-6 border-l border-cyber-border space-y-6 font-mono text-[9px]">
      {sortedHops.map((hop) => {
        const isUntrusted = trustBoundaryHop === null || hop.hop < trustBoundaryHop;

        return (
          <div key={hop.hop} className="relative group">
            <div className="absolute -left-[31px] top-1.5 flex items-center justify-center">
              {isUntrusted ? (
                <div className="h-3 w-3 bg-rose-500 rounded-full border-4 border-cyber-bg shadow-glow-red animate-pulse" />
              ) : (
                <div className="h-3 w-3 bg-emerald-500 rounded-full border-4 border-cyber-bg shadow-glow-green" />
              )}
            </div>

            <div className={`
              border rounded-xl p-3 transition-all duration-300
              ${isUntrusted
                ? "bg-rose-500/5 border-rose-500/20 hover:border-rose-500/40 hover:shadow-glow-red"
                : "bg-emerald-500/5 border-emerald-500/20 hover:border-emerald-500/40 hover:shadow-glow-green"
              }
            `}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-slate-400">HOP #{hop.hop}</span>
                <span className={`flex items-center gap-1 text-[8px] font-bold tracking-wider uppercase ${isUntrusted ? "text-rose-400" : "text-emerald-400"}`}>
                  {isUntrusted ? (
                    <>
                      <ShieldAlert className="h-3 w-3 shrink-0" /> CLAIMED ORIGIN (UNVERIFIED)
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="h-3 w-3 shrink-0" /> VERIFIED SERVER NODE
                    </>
                  )}
                </span>
              </div>

              <div className="space-y-2">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <span className="text-slate-500 text-[8px] block uppercase mb-0.5">From Host (Sender Claim)</span>
                    <span className="text-slate-200 break-all flex items-center gap-1">
                      <Server className="h-3 w-3 text-slate-500 shrink-0" />
                      {hop.from || "Unknown Host"}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[8px] block uppercase mb-0.5">To Host (Recipient Gateway)</span>
                    <span className="text-slate-200 break-all flex items-center gap-1">
                      <Server className="h-3 w-3 text-slate-500 shrink-0" />
                      {hop.by || "Unknown Gateway"}
                    </span>
                  </div>
                </div>

                {hop.date && (
                  <div className="pt-1.5 border-t border-cyber-border/20 flex items-center gap-1 text-slate-500 text-[8px]">
                    <Calendar className="h-3 w-3 shrink-0" />
                    <span>Transit Time: {hop.date}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
