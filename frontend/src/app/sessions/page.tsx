'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { 
  Search, 
  ChevronDown, 
  ChevronUp, 
  SlidersHorizontal, 
  Clock, 
  ChevronLeft, 
  ChevronRight,
  ShieldAlert,
  ArrowRight,
  X,
  Play
} from 'lucide-react';
import { cn } from '@/lib/utils';

import { SectionHeader } from '@/components/common/SectionHeader';
import { StatusBadge } from '@/components/common/StatusBadge';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { sessionService } from '@/services/session.service';
import { Session, ToolCall } from '@/types';

// Main component containing searchParams logic
function SessionsTableContent() {
  const searchParams = useSearchParams();
  const targetId = searchParams.get('id');

  // Query sessions
  const { data: sessions = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => sessionService.getSessions(0, 150),
  });

  // Table state
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortField, setSortField] = useState<'timestamp' | 'score'>('timestamp');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const itemsPerPage = 10;

  // Initialize search from query parameter if it exists
  useEffect(() => {
    if (targetId) {
      setSearchTerm(targetId);
      // Auto expand target session
      setExpandedRows(new Set([targetId]));
    }
  }, [targetId]);

  const toggleRow = (id: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRows(newExpanded);
  };

  // Filter and sort logic
  const filteredSessions = sessions.filter(session => {
    const matchesSearch = 
      session.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      session.prompt.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || session.status.toLowerCase() === statusFilter.toLowerCase();
    
    return matchesSearch && matchesStatus;
  });

  const sortedSessions = [...filteredSessions].sort((a, b) => {
    let comparison = 0;
    if (sortField === 'timestamp') {
      comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    } else if (sortField === 'score') {
      comparison = a.anomaly_score - b.anomaly_score;
    }
    return sortOrder === 'desc' ? -comparison : comparison;
  });

  // Pagination logic
  const totalPages = Math.ceil(sortedSessions.length / itemsPerPage);
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = sortedSessions.slice(indexOfFirstItem, indexOfLastItem);

  // Reset page when filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, statusFilter, sortField, sortOrder]);

  if (isLoading) {
    return <LoadingSkeleton variant="table" />;
  }

  if (isError) {
    return <ErrorState onRetry={() => refetch()} />;
  }

  return (
    <div className="space-y-6">
      {/* Filters Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl bg-zinc-950/40 border border-zinc-900/80 backdrop-blur-md">
        <div className="flex-1 max-w-md relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
          <input
            type="text"
            placeholder="Search prompt payload or session ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-8 py-2 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-700 transition-colors"
          />
          {searchTerm && (
            <button 
              onClick={() => setSearchTerm('')} 
              className="absolute right-3 top-3 text-zinc-500 hover:text-zinc-300"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Status Filter */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono text-zinc-500">STATUS:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono text-zinc-350 focus:outline-none focus:border-zinc-700"
            >
              <option value="all">All Traffic</option>
              <option value="normal">Normal</option>
              <option value="suspicious">Suspicious</option>
              <option value="injected">Injected</option>
            </select>
          </div>

          {/* Sort Field */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono text-zinc-500">SORT BY:</span>
            <select
              value={sortField}
              onChange={(e) => setSortField(e.target.value as any)}
              className="px-3 py-1.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono text-zinc-350 focus:outline-none focus:border-zinc-700"
            >
              <option value="timestamp">Timestamp</option>
              <option value="score">Anomaly Score</option>
            </select>
          </div>

          {/* Sort Order */}
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="px-3 py-1.5 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono text-zinc-350 hover:bg-zinc-900 hover:text-zinc-200 transition-colors"
          >
            {sortOrder === 'desc' ? 'DESC' : 'ASC'}
          </button>
        </div>
      </div>

      {/* Sessions Table */}
      {currentItems.length === 0 ? (
        <EmptyState title="No sessions found" description="Adjust your filters or search keywords and try again." iconType="search" />
      ) : (
        <div className="border border-zinc-900 rounded-xl overflow-hidden bg-zinc-950/20 backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-zinc-900 text-[10px] font-mono text-zinc-500 uppercase bg-zinc-950/60">
                  <th className="px-6 py-4 font-semibold">Session ID</th>
                  <th className="px-6 py-4 font-semibold">Timestamp</th>
                  <th className="px-6 py-4 font-semibold">Prompt Preview</th>
                  <th className="px-6 py-4 font-semibold">Tools Run</th>
                  <th className="px-6 py-4 font-semibold">Anomaly Score</th>
                  <th className="px-6 py-4 font-semibold">Status</th>
                  <th className="px-6 py-4 font-semibold text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-900 text-xs">
                {currentItems.map((session) => {
                  const isExpanded = expandedRows.has(session.id);
                  const toolList = session.tool_calls || [];
                  const uniqueTools = Array.from(new Set(toolList.map(t => t.tool_name)));

                  return (
                    <React.Fragment key={session.id}>
                      <tr 
                        className={cn(
                          "hover:bg-zinc-900/25 transition-colors cursor-pointer border-b border-zinc-900/60",
                          isExpanded && "bg-zinc-900/20"
                        )}
                        onClick={() => toggleRow(session.id)}
                      >
                        <td className="px-6 py-4 font-mono font-semibold text-zinc-300">
                          {session.id.slice(0, 8)}...
                        </td>
                        <td className="px-6 py-4 text-zinc-400 font-mono whitespace-nowrap">
                          {new Date(session.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </td>
                        <td className="px-6 py-4 text-zinc-300 max-w-xs truncate font-sans">
                          {session.prompt}
                        </td>
                        <td className="px-6 py-4 text-zinc-400 font-mono whitespace-nowrap">
                          <span className="px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[10px]">
                            {toolList.length} calls ({uniqueTools.length} unique)
                          </span>
                        </td>
                        <td className={cn(
                          "px-6 py-4 font-mono font-semibold whitespace-nowrap",
                          session.anomaly_score >= 0.75 ? "text-red-400" : session.anomaly_score >= 0.40 ? "text-amber-400" : "text-zinc-400"
                        )}>
                          {session.anomaly_score.toFixed(4)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <StatusBadge status={session.status} />
                        </td>
                        <td className="px-6 py-4 text-right whitespace-nowrap">
                          <button className="text-zinc-500 hover:text-zinc-200">
                            {isExpanded ? <ChevronUp className="w-4 h-4 inline" /> : <ChevronDown className="w-4 h-4 inline" />}
                          </button>
                        </td>
                      </tr>

                      {/* Expanded Section */}
                      {isExpanded && (
                        <tr>
                          <td colSpan={7} className="px-6 py-5 bg-zinc-950/80 border-b border-zinc-900">
                            <div className="space-y-5">
                              {/* Full Prompt */}
                              <div>
                                <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block mb-1">
                                  Full Query Payload
                                </span>
                                <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg text-zinc-200 font-sans break-all leading-relaxed">
                                  {session.prompt}
                                </div>
                              </div>

                              {/* Tool Executions Sequence */}
                              <div>
                                <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block mb-2">
                                  Tool Invocations History ({toolList.length} Calls)
                                </span>
                                {toolList.length === 0 ? (
                                  <div className="text-xs text-zinc-600 font-mono italic p-2 border border-dashed border-zinc-900 rounded-lg">
                                    No tools were invoked during this session execution flow.
                                  </div>
                                ) : (
                                  <div className="space-y-3">
                                    {/* visual flow */}
                                    <div className="flex items-center gap-2 overflow-x-auto pb-2 font-mono text-[9px] text-zinc-400">
                                      {toolList.map((tc, index) => (
                                        <React.Fragment key={tc.id}>
                                          {index > 0 && <ArrowRight className="w-3 h-3 text-zinc-650 shrink-0" />}
                                          <div className={cn(
                                            "flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-900 border shrink-0",
                                            tc.tool_name === 'send_email' ? "border-red-950 text-red-400 bg-red-950/10" : "border-zinc-800"
                                          )}>
                                            <span className="text-zinc-650">{tc.execution_order}.</span>
                                            <span>{tc.tool_name}</span>
                                            <span className="text-zinc-550">({tc.execution_time.toFixed(3)}s)</span>
                                          </div>
                                        </React.Fragment>
                                      ))}
                                    </div>

                                    {/* Detailed breakdown list */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                      {toolList.map((tc) => (
                                        <div key={tc.id} className="p-3.5 bg-zinc-900/50 border border-zinc-900 rounded-lg space-y-2">
                                          <div className="flex justify-between items-center text-[10px] font-mono border-b border-zinc-850 pb-1.5">
                                            <span className="text-zinc-300 font-bold">{tc.tool_name}</span>
                                            <span className="text-zinc-500">Order: {tc.execution_order} | Latency: {tc.execution_time.toFixed(4)}s</span>
                                          </div>
                                          <div className="space-y-1">
                                            <span className="text-[9px] font-mono text-zinc-500 block">ARGUMENTS:</span>
                                            <pre className="p-2 bg-zinc-950 rounded text-[9px] font-mono text-zinc-400 overflow-x-auto max-h-24">
                                              {JSON.stringify(tc.tool_arguments, null, 2)}
                                            </pre>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>

                              {/* Alert Details if Any */}
                              {session.alerts && session.alerts.length > 0 && (
                                <div className="p-4 bg-red-950/5 border border-red-900/30 rounded-lg">
                                  <div className="flex items-center gap-2 text-xs font-mono font-semibold text-red-400 mb-2">
                                    <ShieldAlert className="w-4 h-4 text-red-500" />
                                    <span>BEHAVIORAL ANOMALY ALERT TRIGGERED</span>
                                  </div>
                                  <ul className="space-y-1 text-xs text-zinc-400 font-sans list-disc list-inside">
                                    {session.alerts.map((alert) => (
                                      <li key={alert.id} className="leading-relaxed">
                                        <span className="font-mono text-red-400 font-medium">[{alert.reason}]</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-6 py-4 border-t border-zinc-900 bg-zinc-950/60 font-mono text-xs">
              <span className="text-zinc-500">
                Showing {indexOfFirstItem + 1} to {Math.min(indexOfLastItem, sortedSessions.length)} of {sortedSessions.length} sessions
              </span>
              
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="p-1.5 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors disabled:opacity-50"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-zinc-300">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="p-1.5 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors disabled:opacity-50"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function SessionsPage() {
  return (
    <div className="space-y-6">
      <SectionHeader 
        title="Audit Sessions" 
        description="Auditing history logs of AI agent execution flows, tool sequences, and anomaly assessments." 
      />
      <Suspense fallback={<LoadingSkeleton variant="table" />}>
        <SessionsTableContent />
      </Suspense>
    </div>
  );
}
