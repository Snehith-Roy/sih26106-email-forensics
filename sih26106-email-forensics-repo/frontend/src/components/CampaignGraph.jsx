import React, { useState, useEffect } from "react";
import { Network, HelpCircle, Layers, Globe, ShieldAlert, AlertTriangle, Mail } from "lucide-react";
import axios from "axios";

export default function CampaignGraph({ currentAnalysis }) {
  const [campaignData, setCampaignData] = useState({ campaigns: [], total_analyzed: 0 });
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedNodeDetails, setSelectedNodeDetails] = useState(
    "Hover over any node in the network to inspect its threat indicator details and forensic significance."
  );

  useEffect(() => {
    fetchCampaigns();
  }, [currentAnalysis]);

  const fetchCampaigns = async () => {
    try {
      const res = await axios.get("/api/campaigns");
      setCampaignData(res.data);
    } catch (err) {
      console.error("Failed to fetch campaigns", err);
    }
  };

  const centerNode = { x: 260, y: 80, label: "Scan Ingest" };

  const nodes = [
    {
      id: 1,
      x: 380,
      y: 80,
      label: "Origin IP Address",
      val: currentAnalysis?.origin?.origin_ip || "185.220.101.5",
      desc: "The public IP address where this email originated. Traced to geolocalized coordinates and evaluated for historical spam/abuse reports.",
      color: "text-amber-400 stroke-amber-500",
      icon: <Globe size={14} className="text-amber-400" />
    },
    {
      id: 2,
      x: 320,
      y: 135,
      label: "SPF Authentication",
      val: currentAnalysis?.auth?.spf_result?.toUpperCase() || "SOFTFAIL",
      desc: "Sender Policy Framework checking whether the sending mail server is authorized in the sender's DNS record.",
      color: "text-rose-400 stroke-rose-500",
      icon: <ShieldAlert size={14} className="text-rose-400" />
    },
    {
      id: 3,
      x: 200,
      y: 135,
      label: "DKIM Verification",
      val: currentAnalysis?.auth?.dkim_result?.toUpperCase() || "FAIL",
      desc: "DomainKeys Identified Mail checking the cryptographic digital signature of the email headers and body to verify integrity.",
      color: "text-rose-400 stroke-rose-500",
      icon: <ShieldAlert size={14} className="text-rose-400" />
    },
    {
      id: 4,
      x: 140,
      y: 80,
      label: "Campaign Group",
      val: "Cluster CAMP-104",
      desc: "Identifies if this email belongs to a broader coordinated threat wave based on shared sending IP, domain registry dates, or subject matching.",
      color: "text-rose-400 stroke-rose-500",
      icon: <Layers size={14} className="text-rose-400" />
    },
    {
      id: 5,
      x: 200,
      y: 25,
      label: "Sender Domain",
      val: currentAnalysis?.parsed?.from_address?.split("@")[1] || "bank-corp.com",
      desc: "The domain name extracted from the sender email. Checked for domain registration age and MX hosting records.",
      color: "text-emerald-400 stroke-emerald-500",
      icon: <Globe size={14} className="text-emerald-400" />
    },
    {
      id: 6,
      x: 320,
      y: 25,
      label: "Urgency Indicators",
      val: currentAnalysis?.nlp?.urgency_score > 0.3 ? "Urgent Action Required" : "Normal Cues",
      desc: "Natural Language Processing threat score checking for high-urgency keywords, impersonation language, and financial wire patterns.",
      color: "text-amber-400 stroke-amber-500",
      icon: <AlertTriangle size={14} className="text-amber-400" />
    }
  ];

  const handleNodeHover = (node) => {
    if (node) {
      setHoveredNode(node.id);
      setSelectedNodeDetails(`${node.label.toUpperCase()}: ${node.val}. ${node.desc}`);
    } else {
      setHoveredNode(null);
      setSelectedNodeDetails(
        "Hover over any node in the network to inspect its threat indicator details and forensic significance."
      );
    }
  };

  return (
    <div className="flex flex-col h-full font-mono text-[9px] justify-between overflow-hidden select-none">
      
      {/* Card Header */}
      <div className="flex items-center justify-between border-b border-cyber-border/40 pb-1.5 shrink-0">
        <div className="flex items-center gap-1.5">
          <Network className="h-4 w-4 text-blue-400" />
          <span className="text-[9px] text-slate-300 uppercase tracking-widest font-bold">Related Campaign Correlation Map</span>
        </div>
        <div className="text-slate-500 text-[8px]">
          Correlated Threats: {campaignData.campaigns?.length || 0} | Analyzed Count: {campaignData.total_analyzed}
        </div>
      </div>

      {/* Main Grid Content */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4 mt-2 overflow-hidden h-full">
        
        {/* Interactive SVG Network */}
        <div className="md:col-span-2 relative flex items-center justify-center bg-cyber-bg/50 rounded-lg border border-cyber-border/30 overflow-hidden h-full max-h-[170px]">
          <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(to_right,#1f2d47_1px,transparent_1px),linear-gradient(to_bottom,#1f2d47_1px,transparent_1px)] bg-[size:10px_10px] pointer-events-none" />
          
          <svg className="w-full h-full" viewBox="0 0 520 160">
            <defs>
              <filter id="centerGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="5" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Connection lines */}
            {nodes.map((node) => (
              <line
                key={`line-${node.id}`}
                x1={centerNode.x}
                y1={centerNode.y}
                x2={node.x}
                y2={node.y}
                className={node.color.split(" ")[1]}
                strokeWidth={hoveredNode === node.id ? 2 : 1}
                strokeOpacity={hoveredNode === node.id ? 0.8 : 0.4}
                strokeDasharray="3, 3"
              />
            ))}

            {/* Peripheral Nodes (circle + vector icon grouped together for perfect hover detection) */}
            {nodes.map((node) => {
              const isHovered = hoveredNode === node.id;
              return (
                <g
                  key={node.id}
                  className="cursor-pointer"
                  onMouseEnter={() => handleNodeHover(node)}
                  onMouseLeave={() => handleNodeHover(null)}
                >
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={isHovered ? 18 : 14}
                    fill="#0a0f19"
                    stroke={isHovered ? "currentColor" : "#1f2d47"}
                    strokeWidth={1.5}
                    className={`transition-all duration-300 ${isHovered ? node.color.split(" ")[0] : "text-slate-600"}`}
                  />
                  
                  {/* Icon rendered directly inside SVG workspace coordinates */}
                  <g transform={`translate(${node.x - 7}, ${node.y - 7})`} className="pointer-events-none">
                    {node.icon}
                  </g>

                  <text
                    x={node.x}
                    y={node.y + 21}
                    textAnchor="middle"
                    className="fill-slate-400 font-semibold text-[7px] tracking-wider uppercase pointer-events-none"
                  >
                    {node.label.split(" ")[0]}
                  </text>
                </g>
              );
            })}

            {/* Central Node */}
            <g>
              <circle
                cx={centerNode.x}
                cy={centerNode.y}
                r={16}
                fill="#080c14"
                stroke="#3b82f6"
                strokeWidth={2}
                filter="url(#centerGlow)"
              />
              <g transform={`translate(${centerNode.x - 7}, ${centerNode.y - 7})`} className="pointer-events-none">
                <Mail size={14} className="text-blue-400 animate-pulse" />
              </g>
            </g>
          </svg>
        </div>

        {/* Detailed Inspector Panel */}
        <div className="border border-cyber-border/40 bg-cyber-bg/30 rounded-lg p-3 h-full max-h-[170px] overflow-y-auto flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-1 text-[8px] text-blue-400 font-bold border-b border-cyber-border/20 pb-1 mb-1.5 uppercase shrink-0">
              <HelpCircle className="h-3.5 w-3.5" />
              <span>Indicator Inspector</span>
            </div>
            <p className="text-slate-400 leading-normal text-[8px] font-sans font-medium">
              {selectedNodeDetails}
            </p>
          </div>
          <div className="text-[7px] text-slate-600 pt-2 border-t border-cyber-border/10 uppercase font-mono shrink-0">
            Interactive correlation graph
          </div>
        </div>

      </div>
    </div>
  );
}
