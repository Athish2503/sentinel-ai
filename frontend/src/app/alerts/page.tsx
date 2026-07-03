'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ShieldAlert, RefreshCw, Filter, ShieldCheck, X } from 'lucide-react';
import { cn } from '@/lib/utils';

import { SectionHeader } from '@/components/common/SectionHeader';
import { AlertCard } from '@/components/alerts/AlertCard';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { alertService } from '@/services/alert.service';
import { sessionService } from '@/services/session.service';

export default function AlertsPage() {
  const [severityFilter, setSeverityFilter] = useState<'all' | 'critical' | 'high' | 'medium'>('all');

  // Fetch alerts
  const { data: alerts = [], isLoading: isAlertsLoading, isError: isAlertsError, refetch: refetchAlerts, isFetching } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertService.getAlerts(0, 100),
  });

  // Fetch sessions to map prompts
  const { data: sessions = [], isLoading: isSessionsLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => sessionService.getSessions(0, 150),
  });

  // Filter alerts by score/severity
  const filteredAlerts = alerts.filter(alert => {
    if (severityFilter === 'critical') return alert.score >= 0.75;
    if (severityFilter === 'high') return alert.score >= 0.40 && alert.score < 0.75;
    if (severityFilter === 'medium') return alert.score < 0.40;
    return true;
  });

  if (isAlertsLoading || isSessionsLoading) {
    return (
      <div className="space-y-6">
        <SectionHeader title="Security Alerts" description="Retrieving security alerts..." />
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <LoadingSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (isAlertsError) {
    return <ErrorState onRetry={() => refetchAlerts()} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <SectionHeader 
        title="Security Alerts" 
        description="Audits of all flagged behavioral anomalies, prompt injection attack matches, and policy violations." 
        actions={
          <button
            onClick={() => refetchAlerts()}
            disabled={isFetching}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-xs font-mono text-zinc-300 border border-zinc-800 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
            Refresh Stream
          </button>
        }
      />

      {/* Filter bar */}
      <div className="flex items-center justify-between gap-4 p-4 rounded-xl bg-zinc-950/40 border border-zinc-900/80 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-zinc-500" />
          <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">
            FILTER SEVERITY:
          </span>
        </div>

        <div className="flex items-center gap-2">
          {['all', 'critical', 'high', 'medium'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev as any)}
              className={cn(
                "px-2.5 py-1 rounded-md text-[10px] font-mono font-medium border uppercase transition-all duration-150",
                severityFilter === sev
                  ? sev === 'critical'
                    ? "bg-red-950/20 border-red-500/30 text-red-400 font-semibold"
                    : sev === 'high'
                      ? "bg-amber-950/20 border-amber-500/30 text-amber-400 font-semibold"
                      : "bg-zinc-900 border-zinc-700 text-zinc-200 font-semibold"
                  : "bg-transparent border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50"
              )}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Stream output */}
      {filteredAlerts.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 border border-dashed border-zinc-800 rounded-xl bg-zinc-900/5 text-center">
          <div className="w-10 h-10 rounded-full bg-emerald-500/5 border border-emerald-500/10 flex items-center justify-center text-emerald-400 mb-4 animate-pulse">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <span className="text-xs font-mono font-semibold text-zinc-200">NO ACTIVE THREAT ALERTS DETECTED</span>
          <span className="text-[10px] text-zinc-505 font-sans mt-0.5 max-w-xs">All audited sessions currently comply with active behavioral thresholds.</span>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAlerts.map((alert) => {
            const matchedSession = sessions.find(s => s.id === alert.session_id);
            const prompt = matchedSession ? matchedSession.prompt : undefined;
            const toolSequence = matchedSession?.tool_calls?.map(tc => tc.tool_name);
            
            return (
              <AlertCard 
                key={alert.id} 
                alert={alert}
                prompt={prompt}
                toolSequence={toolSequence}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
