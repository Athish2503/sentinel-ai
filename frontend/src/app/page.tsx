'use client';

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Users, 
  Shield, 
  AlertTriangle, 
  ShieldAlert, 
  Gauge, 
  Activity, 
  RefreshCw 
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  BarChart, 
  Bar, 
  Cell, 
  PieChart, 
  Pie 
} from 'recharts';

import { SectionHeader } from '@/components/common/SectionHeader';
import { MetricCard } from '@/components/cards/MetricCard';
import { ChartCard } from '@/components/cards/ChartCard';
import { TimelineCard } from '@/components/common/TimelineCard';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorState } from '@/components/common/ErrorState';
import { dashboardService } from '@/services/dashboard.service';

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const { 
    data: stats, 
    isLoading, 
    isError, 
    refetch, 
    isFetching 
  } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: dashboardService.getDashboardStats,
    refetchInterval: 10000, // Refresh dashboard metrics every 10 seconds
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <SectionHeader title="Security Overview" description="Loading real-time governance metrics..." />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <LoadingSkeleton key={i} />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LoadingSkeleton variant="card" className="h-80" />
          <LoadingSkeleton variant="card" className="h-80" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-6">
        <SectionHeader title="Security Overview" description="Error loading dashboard metrics" />
        <ErrorState onRetry={() => refetch()} />
      </div>
    );
  }

  const kpis = stats?.kpis || {
    totalSessions: 0,
    normalSessions: 0,
    suspiciousSessions: 0,
    injectedSessions: 0,
    avgAnomalyScore: 0,
    baselineStatus: 'Unknown',
    baselineThreshold: 0.65
  };

  const charts = stats?.charts || {
    anomalyTimeline: [],
    toolFrequencies: [],
    statusBreakdown: []
  };

  const latestDetections = stats?.latestDetections || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <SectionHeader 
        title="Security Overview" 
        description="Real-time behavioral monitoring and prompt injection detection for Sentinel AI agents."
        actions={
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-xs font-mono text-zinc-300 border border-zinc-800 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
            Sync Metrics
          </button>
        }
      />

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricCard
          title="Total Sessions"
          value={kpis.totalSessions}
          description="Monitored queries"
          icon={<Users className="w-4 h-4 text-blue-400" />}
          statusColor="zinc"
        />
        <MetricCard
          title="Normal Runs"
          value={kpis.normalSessions}
          description="Within baseline flow"
          icon={<Shield className="w-4 h-4 text-emerald-400" />}
          statusColor="emerald"
        />
        <MetricCard
          title="Suspicious Runs"
          value={kpis.suspiciousSessions}
          description="Elevated risk score"
          icon={<AlertTriangle className="w-4 h-4 text-amber-400" />}
          statusColor="amber"
        />
        <MetricCard
          title="Injected Attacks"
          value={kpis.injectedSessions}
          description="Critical prompt injection"
          icon={<ShieldAlert className="w-4 h-4 text-red-400" />}
          statusColor="red"
        />
        <MetricCard
          title="Avg Anomaly Score"
          value={kpis.avgAnomalyScore.toFixed(4)}
          description="Threat metric mean"
          icon={<Gauge className="w-4 h-4 text-purple-400" />}
          statusColor={kpis.avgAnomalyScore >= kpis.baselineThreshold ? 'red' : 'zinc'}
        />
        <MetricCard
          title="Baseline Status"
          value={kpis.baselineStatus.split(' ')[0]}
          description={`Threshold: ${kpis.baselineThreshold}`}
          icon={<Activity className="w-4 h-4 text-emerald-500" />}
          statusColor="emerald"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Line Chart: Anomaly Timeline */}
        <ChartCard 
          title="Behavioral Threat Vector Timeline" 
          description="Chronological record of session anomaly scores compared against threshold"
        >
          {mounted && (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={charts.anomalyTimeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis 
                  dataKey="time" 
                  stroke="#52525b" 
                  fontSize={9} 
                  fontFamily="monospace"
                  tickLine={false} 
                />
                <YAxis 
                  stroke="#52525b" 
                  fontSize={9} 
                  fontFamily="monospace"
                  domain={[0, 1]} 
                  tickLine={false} 
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#09090b', border: '1px solid #27272a', borderRadius: '8px' }}
                  labelStyle={{ fontFamily: 'monospace', fontSize: '10px', color: '#a1a1aa' }}
                  itemStyle={{ fontFamily: 'monospace', fontSize: '10px', color: '#10b981' }}
                />
                {/* Baseline threshold reference line */}
                <Line 
                  type="monotone" 
                  dataKey={() => kpis.baselineThreshold} 
                  stroke="#ef4444" 
                  strokeDasharray="4 4" 
                  name="Threshold"
                  strokeWidth={1.5}
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#10b981" 
                  strokeWidth={2} 
                  dot={{ r: 3, strokeWidth: 1 }}
                  activeDot={{ r: 5 }}
                  name="Anomaly Score"
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* Bar Chart: Tool Call Frequencies */}
        <ChartCard 
          title="Active Tool Call Distribution" 
          description="Cumulative frequency of specialized tool invocations by agent instances"
        >
          {mounted && (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={charts.toolFrequencies} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis 
                  dataKey="name" 
                  stroke="#52525b" 
                  fontSize={9} 
                  fontFamily="monospace"
                  tickLine={false} 
                />
                <YAxis 
                  stroke="#52525b" 
                  fontSize={9} 
                  fontFamily="monospace"
                  tickLine={false} 
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#09090b', border: '1px solid #27272a', borderRadius: '8px' }}
                  labelStyle={{ fontFamily: 'monospace', fontSize: '10px', color: '#a1a1aa' }}
                  itemStyle={{ fontFamily: 'monospace', fontSize: '10px', color: '#f59e0b' }}
                />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]}>
                  {charts.toolFrequencies.map((entry, idx) => (
                    <Cell 
                      key={`cell-${idx}`} 
                      fill={entry.name === 'send_email' ? '#ef4444' : '#10b981'} 
                      fillOpacity={0.8}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        {/* Pie Chart: Traffic Status Breakdown */}
        <ChartCard 
          title="Threat Classification Ratios" 
          description="Composition breakdown of audited agent runs"
        >
          {mounted && (
            <div className="flex flex-col sm:flex-row items-center justify-around h-full gap-4">
              <ResponsiveContainer width={180} height={180}>
                <PieChart>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#09090b', border: '1px solid #27272a', borderRadius: '8px' }}
                    itemStyle={{ fontFamily: 'monospace', fontSize: '10px' }}
                  />
                  <Pie
                    data={charts.statusBreakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {charts.statusBreakdown.map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={entry.color} fillOpacity={0.85} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              
              {/* Custom Legend */}
              <div className="space-y-3 font-mono text-xs">
                {charts.statusBreakdown.map((entry) => (
                  <div key={entry.name} className="flex items-center gap-3">
                    <span 
                      className="h-3 w-3 rounded-full border border-zinc-900" 
                      style={{ backgroundColor: entry.color }}
                    />
                    <span className="text-zinc-300 w-24">{entry.name}:</span>
                    <span className="text-zinc-100 font-bold">{entry.value}</span>
                    <span className="text-zinc-500 text-[10px]">
                      ({((entry.value / kpis.totalSessions) * 100).toFixed(1)}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </ChartCard>

        {/* Live Stream: Latest Detections */}
        <TimelineCard events={latestDetections} />
      </div>
    </div>
  );
}
