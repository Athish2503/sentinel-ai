'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { 
  ChevronDown, 
  ChevronUp, 
  AlertTriangle, 
  ShieldAlert, 
  ExternalLink,
  Clock,
  Terminal
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface AlertCardProps {
  alert: {
    id: string;
    session_id: string;
    score: number;
    reason: string;
    created_at: string;
  };
  prompt?: string;
  toolSequence?: string[];
}

export function AlertCard({ alert, prompt = "Unavailable session context", toolSequence }: AlertCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getSeverity = (score: number) => {
    if (score >= 0.75) return { label: 'CRITICAL', color: 'text-red-400 bg-red-950/20 border-red-500/30' };
    if (score >= 0.40) return { label: 'HIGH', color: 'text-amber-400 bg-amber-950/20 border-amber-500/30' };
    return { label: 'MEDIUM', color: 'text-zinc-400 bg-zinc-900/30 border-zinc-800' };
  };

  const severity = getSeverity(alert.score);

  return (
    <div
      className={cn(
        "rounded-xl bg-zinc-950/40 border transition-all duration-300 backdrop-blur-md",
        alert.score >= 0.75 ? "border-red-900/30 hover:border-red-800/50" : "border-zinc-800/80 hover:border-zinc-700/80"
      )}
    >
      {/* Card Header (Collapsed view) */}
      <div 
        onClick={() => setExpanded(!expanded)}
        className="p-5 flex items-center justify-between gap-4 cursor-pointer select-none"
      >
        <div className="flex items-center gap-4 flex-1 min-w-0">
          <div className={cn(
            "p-2 rounded-lg border",
            alert.score >= 0.75 ? "bg-red-500/10 border-red-500/20 text-red-400" : "bg-amber-500/10 border-amber-500/20 text-amber-400"
          )}>
            {alert.score >= 0.75 ? <ShieldAlert className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className={cn("px-2 py-0.5 rounded font-mono text-[9px] font-bold border", severity.color)}>
                {severity.label}
              </span>
              <span className="text-xs font-mono font-semibold text-red-400">
                Score: {alert.score.toFixed(4)}
              </span>
              <span className="text-[10px] font-mono text-zinc-500 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {new Date(alert.created_at).toLocaleString()}
              </span>
            </div>
            
            <h4 className="text-xs sm:text-sm font-mono font-medium text-zinc-200 truncate pr-4">
              {alert.reason}
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="hidden sm:inline font-mono text-[10px] text-zinc-500">
            SESS: {alert.session_id.slice(0, 8)}
          </span>
          <button className="p-1 rounded bg-zinc-900 text-zinc-400 hover:text-zinc-200">
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Card Content (Expanded view) */}
      {expanded && (
        <div className="px-5 pb-5 pt-3 border-t border-zinc-900 bg-zinc-950/20 rounded-b-xl space-y-4">
          {/* Prompt section */}
          <div>
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block mb-1">
              Triggering Prompt Payload
            </span>
            <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg text-xs text-zinc-300 font-sans leading-relaxed break-all">
              {prompt}
            </div>
          </div>

          {/* Tool call path if available */}
          {toolSequence && toolSequence.length > 0 && (
            <div>
              <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block mb-1">
                Observed Tool Execution Sequence
              </span>
              <div className="flex items-center gap-1.5 flex-wrap p-2.5 bg-zinc-950/60 border border-zinc-900 rounded-lg font-mono text-[10px] text-zinc-400">
                {toolSequence.map((tool, idx) => (
                  <React.Fragment key={idx}>
                    {idx > 0 && <span className="text-zinc-650">→</span>}
                    <span className={cn(
                      "px-1.5 py-0.5 rounded border border-zinc-850 bg-zinc-900/60",
                      tool === 'send_email' && "text-red-400 border-red-950 bg-red-950/10"
                    )}>
                      {tool}
                    </span>
                  </React.Fragment>
                ))}
              </div>
            </div>
          )}

          {/* Action Footer */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-zinc-900/60 text-[10px] font-mono">
            <div className="text-zinc-500">
              ALERT ID: <span className="text-zinc-400 select-all">{alert.id}</span>
            </div>
            
            <div className="flex items-center gap-4">
              <span className="text-zinc-500">
                SESSION ID: <span className="text-zinc-400 select-all">{alert.session_id}</span>
              </span>
              <Link 
                href={`/sessions?id=${alert.session_id}`}
                className="inline-flex items-center gap-1 text-emerald-400 hover:text-emerald-300 transition-colors font-semibold"
              >
                Full Session Details
                <ExternalLink className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
