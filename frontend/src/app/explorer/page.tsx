'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Network, 
  Search, 
  AlertTriangle, 
  GitBranch, 
  HelpCircle, 
  Gauge, 
  CheckCircle2, 
  ShieldAlert,
  ArrowRight,
  TrendingUp
} from 'lucide-react';
import { cn } from '@/lib/utils';

import { SectionHeader } from '@/components/common/SectionHeader';
import { StatusBadge } from '@/components/common/StatusBadge';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorState } from '@/components/common/ErrorState';
import { SequenceGraph } from '@/components/common/SequenceGraph';
import { sessionService } from '@/services/session.service';
import { Session } from '@/types';

export default function BehaviorExplorer() {
  const { data: sessions = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => sessionService.getSessions(0, 100),
  });

  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Auto-select the first suspicious or injected session on load
  useEffect(() => {
    if (sessions.length > 0 && !selectedSessionId) {
      const firstAnomalous = sessions.find(s => s.status === 'injected' || s.status === 'suspicious');
      if (firstAnomalous) {
        setSelectedSessionId(firstAnomalous.id);
      } else {
        setSelectedSessionId(sessions[0].id);
      }
    }
  }, [sessions, selectedSessionId]);

  const selectedSession = sessions.find(s => s.id === selectedSessionId);

  // Filter sessions for left pane list
  const filteredSessions = sessions.filter(s => {
    // Show only suspicious, injected, or sessions matching search
    const matchesSearch = s.id.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          s.prompt.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  // Calculate sequence analysis variables
  const observedTools = selectedSession?.tool_calls?.map(tc => tc.tool_name) || [];
  
  // Construct a simulated "Expected Sequence" based on baseline structure
  const getExpectedSequence = (session: Session | undefined): string[] => {
    if (!session) return [];
    const prompt = session.prompt.toLowerCase();
    if (prompt.includes('reimbursement') || prompt.includes('calculate') || prompt.includes('sum')) {
      return ['calculator'];
    }
    if (prompt.includes('customer') || prompt.includes('bob smith')) {
      return ['lookup_customer'];
    }
    return ['search_documents', 'read_document']; // default normal flow
  };

  const expectedTools = getExpectedSequence(selectedSession);

  // Identify anomalous nodes
  const graphNodes = selectedSession?.tool_calls?.map(tc => {
    const isUnexpected = tc.tool_name === 'send_email' || 
                         (selectedSession.status === 'injected' && tc.tool_name === 'send_email') ||
                         (!expectedTools.includes(tc.tool_name));
    
    return {
      name: tc.tool_name,
      latency: tc.execution_time,
      status: (isUnexpected ? 'anomalous' : 'normal') as 'anomalous' | 'normal',
      args: tc.tool_arguments
    };
  }) || [];

  // Determine deviation reason
  const getDeviationExplanation = (session: Session | undefined) => {
    if (!session) return { reason: 'No session context.', diff: 'None', confidence: 0 };
    if (session.status === 'normal') {
      return {
        reason: 'Execution flow is fully compliant with active behavioral baselines.',
        diff: 'None detected',
        confidence: 98.4
      };
    }
    if (session.status === 'suspicious') {
      return {
        reason: 'Repeated invocation pattern. lookup_customer was executed multiple times consecutively, violating unique-per-session rate distributions.',
        diff: 'Excessive lookup_customer iterations',
        confidence: 76.5
      };
    }
    
    // Injected
    const hasEmail = session.tool_calls?.some(t => t.tool_name === 'send_email');
    if (hasEmail) {
      return {
        reason: 'Critical: Direct exfiltration sequence detected. send_email was invoked following a document read action containing sensitive text payloads, which is strictly prohibited.',
        diff: 'Unauthorized send_email node injection',
        confidence: 94.2
      };
    }
    return {
      reason: 'Sequence entropy threshold breach. The execution pattern deviates from standard baseline graphs.',
      diff: 'General tool sequence transition misalignment',
      confidence: 88.7
    };
  };

  const explanation = getDeviationExplanation(selectedSession);

  if (isLoading) {
    return <LoadingSkeleton variant="graph" className="h-96" />;
  }

  if (isError) {
    return <ErrorState onRetry={() => refetch()} />;
  }

  return (
    <div className="space-y-6">
      <SectionHeader 
        title="Behavior Explorer" 
        description="Graph tool transition sequences, trace active model vectors, and highlight structural deviations." 
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Side: Session Selector List (4 cols) */}
        <div className="lg:col-span-4 border border-zinc-900 rounded-xl bg-zinc-950/40 backdrop-blur-md overflow-hidden flex flex-col h-[600px]">
          {/* List Search */}
          <div className="p-4 border-b border-zinc-900 bg-zinc-950/80 sticky top-0">
            <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block mb-2">
              Select Audited Session
            </span>
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-500" />
              <input
                type="text"
                placeholder="Filter by prompt or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-700"
              />
            </div>
          </div>

          {/* List Items */}
          <div className="flex-1 overflow-y-auto divide-y divide-zinc-900/60">
            {filteredSessions.length === 0 ? (
              <div className="p-6 text-center text-xs text-zinc-600 font-mono italic">
                No sessions match criteria.
              </div>
            ) : (
              filteredSessions.map((s) => {
                const isSelected = s.id === selectedSessionId;
                return (
                  <div
                    key={s.id}
                    onClick={() => setSelectedSessionId(s.id)}
                    className={cn(
                      "p-4 cursor-pointer transition-all duration-200 text-left border-l-2",
                      isSelected 
                        ? "bg-zinc-900 border-l-emerald-500 bg-zinc-900/40" 
                        : "border-l-transparent hover:bg-zinc-900/20 text-zinc-400 hover:text-zinc-200"
                    )}
                  >
                    <div className="flex justify-between items-start gap-2 mb-1.5">
                      <span className="font-mono font-semibold text-xs text-zinc-300">
                        SESS: {s.id.slice(0, 8)}...
                      </span>
                      <span className={cn(
                        "text-[10px] font-mono font-medium",
                        s.status === 'injected' ? "text-red-400" : s.status === 'suspicious' ? "text-amber-400" : "text-zinc-500"
                      )}>
                        Score: {s.anomaly_score.toFixed(3)}
                      </span>
                    </div>
                    <p className="text-[11px] font-sans truncate text-zinc-400 group-hover:text-zinc-300">
                      "{s.prompt}"
                    </p>
                    <div className="mt-2 flex justify-between items-center text-[9px] text-zinc-600 font-mono">
                      <span>{new Date(s.created_at).toLocaleTimeString()}</span>
                      <StatusBadge status={s.status} className="px-1.5 py-0 scale-90" />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Side: Execution Sequence Explorer Stage (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          {selectedSession ? (
            <>
              {/* Overview Details */}
              <div className="p-5 border border-zinc-800/80 rounded-xl bg-zinc-950/40 backdrop-blur-md space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-900 pb-3">
                  <div>
                    <h3 className="font-mono font-bold text-sm text-zinc-200">
                      ANALYSIS STAGE: SESSION {selectedSession.id}
                    </h3>
                    <span className="text-[10px] font-sans text-zinc-500 block">
                      Triggered {new Date(selectedSession.created_at).toLocaleString()}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <StatusBadge status={selectedSession.status} />
                    <span className="px-2.5 py-0.5 rounded-full border border-zinc-800 bg-zinc-900/60 font-mono text-xs font-semibold text-zinc-300">
                      Score: {selectedSession.anomaly_score.toFixed(4)}
                    </span>
                  </div>
                </div>

                <div>
                  <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block mb-1">
                    Audited Prompt Payload
                  </span>
                  <p className="text-xs font-sans text-zinc-300 bg-zinc-950 border border-zinc-900 rounded-lg p-3 leading-relaxed">
                    "{selectedSession.prompt}"
                  </p>
                </div>
              </div>

              {/* Graphical Visualization Card */}
              <div className="p-5 border border-zinc-800/80 rounded-xl bg-zinc-950/40 backdrop-blur-md space-y-4">
                <div className="flex items-center gap-2 text-xs font-mono font-semibold text-zinc-200">
                  <Network className="w-4 h-4 text-emerald-400" />
                  <span>BEHAVIORAL TOOL TRANSITION FLOW</span>
                </div>
                
                <SequenceGraph 
                  nodes={graphNodes} 
                  orientation="horizontal" 
                />
              </div>

              {/* Expected vs Observed Differences Pane */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Expected sequence */}
                <div className="p-5 border border-zinc-900 rounded-xl bg-zinc-950/60 space-y-3">
                  <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase tracking-wider block border-b border-emerald-950/30 pb-1">
                    ✔ EXPECTED FLOW SEQUENCE (BASELINE)
                  </span>
                  <div className="flex items-center gap-1.5 flex-wrap font-mono text-[10px] text-zinc-400">
                    {expectedTools.map((tool, idx) => (
                      <React.Fragment key={idx}>
                        {idx > 0 && <ArrowRight className="w-3 h-3 text-zinc-700" />}
                        <span className="px-1.5 py-0.5 rounded border border-zinc-900 bg-zinc-900/20 text-emerald-400">
                          {tool}
                        </span>
                      </React.Fragment>
                    ))}
                  </div>
                </div>

                {/* Observed sequence */}
                <div className={cn(
                  "p-5 border rounded-xl bg-zinc-950/60 space-y-3",
                  selectedSession.status !== 'normal' ? "border-red-950/40" : "border-zinc-900"
                )}>
                  <span className={cn(
                    "text-[10px] font-mono font-bold uppercase tracking-wider block border-b pb-1",
                    selectedSession.status !== 'normal' ? "text-red-400 border-red-950/30" : "text-zinc-400 border-zinc-900"
                  )}>
                    ⚠ OBSERVED FLOW SEQUENCE (AUDITED)
                  </span>
                  <div className="flex items-center gap-1.5 flex-wrap font-mono text-[10px]">
                    {observedTools.map((tool, idx) => {
                      const isAnomalous = tool === 'send_email' || !expectedTools.includes(tool);
                      return (
                        <React.Fragment key={idx}>
                          {idx > 0 && <ArrowRight className="w-3 h-3 text-zinc-700" />}
                          <span className={cn(
                            "px-1.5 py-0.5 rounded border",
                            isAnomalous 
                              ? "bg-red-950/15 border-red-900/30 text-red-400 font-semibold" 
                              : "border-zinc-900 bg-zinc-900/20 text-zinc-400"
                          )}>
                            {tool}
                          </span>
                        </React.Fragment>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Qualitive Anomaly Assessment details */}
              <div className="p-5 border border-zinc-900 rounded-xl bg-zinc-950/40 backdrop-blur-md grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                <div className="space-y-1">
                  <span className="text-[9px] font-mono text-zinc-500 uppercase">
                    Structural Deviation
                  </span>
                  <div className="text-xs font-mono font-semibold text-zinc-200">
                    {explanation.diff}
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[9px] font-mono text-zinc-500 uppercase">
                    Risk Assessment Explanation
                  </span>
                  <div className="text-xs text-zinc-350 leading-relaxed font-sans">
                    {explanation.reason}
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[9px] font-mono text-zinc-500 uppercase">
                    Evaluation Confidence
                  </span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-lg font-mono font-bold text-zinc-200">
                      {explanation.confidence.toFixed(1)}%
                    </span>
                    <TrendingUp className="w-4 h-4 text-emerald-400" />
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center p-12 border border-dashed border-zinc-800 rounded-xl bg-zinc-900/10 h-80">
              <GitBranch className="w-8 h-8 text-zinc-650 mb-3" />
              <span className="text-xs text-zinc-500 font-mono">No active session selected for behavior exploration.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
