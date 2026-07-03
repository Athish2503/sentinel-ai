'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  ShieldCheck, 
  Settings2, 
  Clock, 
  HelpCircle, 
  Sliders, 
  Play, 
  BarChart2, 
  Timer, 
  FileJson,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip,
  Cell
} from 'recharts';
import { cn } from '@/lib/utils';

import { SectionHeader } from '@/components/common/SectionHeader';
import { MetricCard } from '@/components/cards/MetricCard';
import { ChartCard } from '@/components/cards/ChartCard';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorState } from '@/components/common/ErrorState';
import { baselineService } from '@/services/baseline.service';
import { mockBaselineStats } from '@/mock/data';
import { BaselineStatistics } from '@/types';

export default function BaselinePage() {
  const queryClient = useQueryClient();
  const [mounted, setMounted] = useState(false);

  // Training parameters
  const [numRuns, setNumRuns] = useState(25);
  const [useRealAgent, setUseRealAgent] = useState(false);
  const [trainingSuccessInfo, setTrainingSuccessInfo] = useState<any | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Fetch active baseline
  const { 
    data: activeBaseline, 
    isLoading: isBaselineLoading, 
    isError: isBaselineError,
    refetch: refetchBaseline
  } = useQuery({
    queryKey: ['activeBaseline'],
    queryFn: () => baselineService.getActiveBaseline(),
  });

  // Train Baseline Mutation
  const trainMutation = useMutation({
    mutationFn: (params: { numRuns: number; useRealAgent: boolean }) => 
      baselineService.trainBaseline(params.numRuns, params.useRealAgent),
    onSuccess: (data) => {
      // Invalidate queries so components reload baseline
      queryClient.invalidateQueries({ queryKey: ['activeBaseline'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
      setTrainingSuccessInfo(data);
    }
  });

  const handleTrain = () => {
    setTrainingSuccessInfo(null);
    trainMutation.mutate({ numRuns, useRealAgent });
  };

  if (isBaselineLoading) {
    return <LoadingSkeleton variant="card" className="h-96" />;
  }

  if (isBaselineError) {
    return <ErrorState onRetry={() => refetchBaseline()} />;
  }

  // Use statistics from training success or active baseline, falling back to mock baseline statistics
  const stats: BaselineStatistics = trainingSuccessInfo?.statistics || activeBaseline?.statistics || mockBaselineStats;
  const currentBaseline = activeBaseline;

  // Chart data formatting: Tool frequencies
  const toolFreqData = Object.entries(stats.tool_frequencies)
    .map(([name, count]) => ({ name, count: count as number }))
    .sort((a, b) => b.count - a.count);

  // Common sequences list
  const sequences = Object.entries(stats.sequences_frequency || {})
    .map(([seq, count]) => ({ seq: seq.replace(/,/g, ' → '), count: count as number }))
    .sort((a, b) => b.count - a.count);

  return (
    <div className="space-y-6">
      {/* Header */}
      <SectionHeader 
        title="Behavioral Baselines" 
        description="Establish agent behavior models, compile normal tool execution transitions, and adjust detector thresholds." 
      />

      {/* Overview Metric Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Baseline Model Version"
          value={currentBaseline?.model_version || 'v1.0.0'}
          description="Active model identifier"
          icon={<ShieldCheck className="w-4 h-4 text-emerald-400" />}
          statusColor="emerald"
        />
        <MetricCard
          title="Training Set Count"
          value={`${currentBaseline?.training_runs || 25} Runs`}
          description="Predefined normal prompts"
          icon={<Settings2 className="w-4 h-4 text-blue-400" />}
        />
        <MetricCard
          title="Anomaly Threshold"
          value={currentBaseline?.threshold.toFixed(2) || '0.65'}
          description="IForest decision limit"
          icon={<Sliders className="w-4 h-4 text-amber-400" />}
        />
        <MetricCard
          title="Last Sync Date"
          value={currentBaseline ? new Date(currentBaseline.created_at).toLocaleDateString() : new Date().toLocaleDateString()}
          description="Timestamp of model save"
          icon={<Clock className="w-4 h-4 text-zinc-500" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Side: Training Console (5 cols) */}
        <div className="lg:col-span-5 p-6 border border-zinc-900 rounded-xl bg-zinc-950/40 backdrop-blur-md space-y-6">
          <div>
            <h3 className="font-mono text-sm font-semibold text-zinc-200 uppercase tracking-wider mb-1">
              BASELINE MODEL CONSOLE
            </h3>
            <p className="text-xs text-zinc-500 font-sans leading-relaxed">
              Launch profile training runs to execute mock prompts and rebuild the Isolation Forest model parameters.
            </p>
          </div>

          <div className="space-y-4">
            {/* Num Runs Selector */}
            <div className="space-y-2">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider block">
                Number of Profiling Runs ({numRuns})
              </label>
              <input
                type="range"
                min="20"
                max="30"
                value={numRuns}
                onChange={(e) => setNumRuns(parseInt(e.target.value))}
                className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
              <div className="flex justify-between text-[9px] font-mono text-zinc-550">
                <span>20 Min</span>
                <span>25 Default</span>
                <span>30 Max</span>
              </div>
            </div>

            {/* Real Agent Checkbox */}
            <div className="flex items-center gap-3 p-3 bg-zinc-900/40 border border-zinc-900 rounded-lg">
              <input
                type="checkbox"
                id="realAgent"
                checked={useRealAgent}
                onChange={(e) => setUseRealAgent(e.target.checked)}
                className="w-4 h-4 rounded bg-zinc-950 border-zinc-800 text-emerald-500 accent-emerald-500"
              />
              <div className="flex flex-col text-left">
                <label htmlFor="realAgent" className="text-xs font-mono font-medium text-zinc-300 cursor-pointer">
                  Utilize Production Agent Graph
                </label>
                <span className="text-[9px] font-sans text-zinc-500">
                  Sends calls directly to Groq (requires GROQ_API_KEY environment variable).
                </span>
              </div>
            </div>

            {/* Execute Button */}
            <button
              onClick={handleTrain}
              disabled={trainMutation.isPending}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 font-mono text-xs font-semibold text-zinc-950 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {trainMutation.isPending ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  PROFILING SEQUENCE RUNNING...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  GENERATE & REBUILD BASELINE
                </>
              )}
            </button>
          </div>

          {/* Training logs output */}
          {trainMutation.isPending && (
            <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-900 space-y-2 animate-pulse text-left">
              <span className="text-[10px] font-mono text-zinc-500 uppercase block">
                Live Output Stream
              </span>
              <div className="text-[10px] font-mono text-emerald-500 space-y-1">
                <div>[04:30:11] INITIALIZING BASELINE PROFILER ENGINE</div>
                <div>[04:30:13] SELECTING PROMPTS FOR {numRuns} SEQUENCES</div>
                <div>[04:30:15] EXECUTING ITERATION 1-10 (MOCK MODE)</div>
                <div className="animate-bounce">... PROCESSING ...</div>
              </div>
            </div>
          )}

          {/* Success Dialog */}
          {trainingSuccessInfo && (
            <div className="p-4 rounded-lg bg-emerald-500/5 border border-emerald-500/10 space-y-2 text-left">
              <div className="flex items-center gap-2 text-xs font-mono font-semibold text-emerald-400">
                <CheckCircle2 className="w-4 h-4" />
                <span>TRAINING ITERATION COMPLETE</span>
              </div>
              <p className="text-[10px] font-sans text-zinc-400">
                Baseline profile saved successfully: Version <span className="font-mono text-zinc-200">{trainingSuccessInfo.model_version}</span>. Isolation Forest thresholds adjusted.
              </p>
              <div className="border-t border-emerald-950/20 pt-2 flex items-center justify-between text-[9px] font-mono text-zinc-500">
                <span>ID: {trainingSuccessInfo.baseline_id.slice(0, 8)}...</span>
                <span>Threshold: {trainingSuccessInfo.threshold}</span>
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Feature Statistics & Tool Frequencies (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Summary Feature stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 border border-zinc-900 rounded-xl p-5 bg-zinc-950/40 backdrop-blur-md text-left">
            <div className="space-y-1">
              <span className="text-[9px] font-mono text-zinc-500 uppercase flex items-center gap-1">
                <BarChart2 className="w-3 h-3" />
                Avg Tool Sequence Length
              </span>
              <div className="text-lg font-mono font-bold text-zinc-200">
                {stats.avg_execution_count_per_run.toFixed(2)} steps
              </div>
              <span className="text-[9px] text-zinc-650 font-sans block">
                Max length: {stats.max_execution_count_per_run}
              </span>
            </div>

            <div className="space-y-1">
              <span className="text-[9px] font-mono text-zinc-500 uppercase flex items-center gap-1">
                <Timer className="w-3 h-3" />
                Average Tool Latency
              </span>
              <div className="text-lg font-mono font-bold text-zinc-200">
                {stats.avg_execution_time.toFixed(4)}s
              </div>
              <span className="text-[9px] text-zinc-650 font-sans block">
                Includes remote API wait times
              </span>
            </div>

            <div className="space-y-1">
              <span className="text-[9px] font-mono text-zinc-500 uppercase flex items-center gap-1">
                <FileJson className="w-3 h-3" />
                Avg Parameter Size
              </span>
              <div className="text-lg font-mono font-bold text-zinc-200">
                {stats.avg_parameter_length.toFixed(1)} chars
              </div>
              <span className="text-[9px] text-zinc-650 font-sans block">
                Stringified JSON payload length
              </span>
            </div>
          </div>

          {/* Bar Chart: Baseline tool frequencies */}
          <ChartCard 
            title="Baseline Tool Call Distributions" 
            description="Comparison of tool frequencies in normal baseline executions"
          >
            {mounted && (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={toolFreqData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
                    itemStyle={{ fontFamily: 'monospace', fontSize: '10px', color: '#10b981' }}
                  />
                  <Bar dataKey="count" fill="#10b981" fillOpacity={0.8} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </ChartCard>

          {/* Common Sequences Table */}
          <div className="p-5 border border-zinc-900 rounded-xl bg-zinc-950/40 backdrop-blur-md space-y-3">
            <h4 className="text-xs font-semibold font-mono text-zinc-200 uppercase tracking-wider">
              ESTABLISHED TRANSITION SEQUENCES
            </h4>
            <div className="divide-y divide-zinc-900 text-xs font-mono">
              {sequences.map((seq, idx) => (
                <div key={idx} className="flex justify-between items-center py-2.5">
                  <span className="text-zinc-400 font-mono text-[10px] break-all max-w-sm text-left">
                    {seq.seq}
                  </span>
                  <span className="text-emerald-400 bg-emerald-500/5 px-2 py-0.5 rounded border border-emerald-500/10 shrink-0">
                    Freq: {seq.count} runs
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
