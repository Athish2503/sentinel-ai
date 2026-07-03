import React from 'react';
import Link from 'next/link';
import { ShieldAlert, ArrowRight, Clock } from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import { cn } from '@/lib/utils';

interface TimelineEvent {
  id: string;
  session_id: string;
  score: number;
  reason: string;
  created_at: string;
  prompt: string;
  status: string;
}

interface TimelineCardProps {
  events: TimelineEvent[];
  className?: string;
}

export function TimelineCard({ events, className }: TimelineCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl bg-zinc-950/40 border border-zinc-800/80 p-6 backdrop-blur-md flex flex-col justify-between hover:border-zinc-700/80 transition-all duration-300",
        className
      )}
    >
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-sm font-semibold font-mono text-zinc-100 uppercase tracking-wider">
          LIVE DETECTION STREAM
        </h3>
        <span className="text-[10px] font-mono text-red-400 bg-red-950/20 border border-red-900/30 px-2 py-0.5 rounded animate-pulse">
          REAL-TIME
        </span>
      </div>

      <div className="relative border-l border-zinc-800/80 pl-6 ml-3 space-y-6">
        {events.length === 0 ? (
          <div className="text-xs text-zinc-500 py-4 pl-2">No injections detected in stream.</div>
        ) : (
          events.map((event) => (
            <div key={event.id} className="relative group">
              {/* Timeline Indicator Dot */}
              <div className="absolute -left-[31px] top-1 flex h-4 w-4 items-center justify-center rounded-full bg-zinc-950 border border-red-500/50 group-hover:border-red-400 transition-colors">
                <div className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
              </div>

              {/* Event Content Card */}
              <div className="bg-zinc-900/10 border border-zinc-900 hover:border-zinc-800/80 rounded-lg p-4 transition-all duration-200">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <StatusBadge status={event.status} />
                    <span className="text-[10px] font-mono text-zinc-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(event.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                  </div>
                  <span className="text-xs font-mono text-red-400 font-semibold bg-red-500/5 px-2 py-0.5 rounded border border-red-500/10">
                    Score: {event.score.toFixed(4)}
                  </span>
                </div>

                <p className="text-xs font-mono font-medium text-zinc-300 mb-1.5">
                  {event.reason}
                </p>

                <div className="text-[10px] font-sans text-zinc-500 truncate max-w-xl mb-3">
                  Prompt: "{event.prompt}"
                </div>

                <div className="flex items-center justify-between text-[10px] font-mono border-t border-zinc-900 pt-2.5">
                  <span className="text-zinc-500">SESSION: {event.session_id}</span>
                  <Link 
                    href={`/sessions?id=${event.session_id}`}
                    className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1 group/link"
                  >
                    Investigate Session
                    <ArrowRight className="w-3 h-3 group-hover/link:translate-x-0.5 transition-transform" />
                  </Link>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
