'use client';

import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Server, 
  Cpu, 
  Sliders, 
  Palette, 
  Info,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Save
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { cn } from '@/lib/utils';
import { SectionHeader } from '@/components/common/SectionHeader';

export default function SettingsPage() {
  const [backendUrl, setBackendUrl] = useState('http://localhost:8000/api/v1');
  const [llmProvider, setLlmProvider] = useState('mock-sandbox');
  const [threshold, setThreshold] = useState(0.65);
  const [themeName, setThemeName] = useState('zinc-dark');
  const [isSaved, setIsSaved] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedUrl = localStorage.getItem('kavalar_backend_url');
      if (savedUrl) setBackendUrl(savedUrl);
      
      const savedProvider = localStorage.getItem('kavalar_llm_provider');
      if (savedProvider) setLlmProvider(savedProvider);

      const savedThreshold = localStorage.getItem('kavalar_threshold');
      if (savedThreshold) setThreshold(parseFloat(savedThreshold));

      const savedTheme = localStorage.getItem('kavalar_theme');
      if (savedTheme) setThemeName(savedTheme);
    }
  }, []);

  // Backend Health Check Query
  const { data: healthStatus, isFetching: isCheckingHealth, refetch: checkHealth } = useQuery({
    queryKey: ['backendHealth', backendUrl],
    queryFn: async () => {
      try {
        const response = await axios.get(`${backendUrl}/health`, { timeout: 3000 });
        return response.data;
      } catch (error) {
        return { status: 'offline', error: 'Connection refused.' };
      }
    },
    retry: false,
    refetchInterval: 20000, // check health every 20s
  });

  const handleSave = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('kavalar_backend_url', backendUrl);
      localStorage.setItem('kavalar_llm_provider', llmProvider);
      localStorage.setItem('kavalar_threshold', threshold.toString());
      localStorage.setItem('kavalar_theme', themeName);
      
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 2000);
      
      // Force reload or invalidate queries
      checkHealth();
    }
  };

  const isConnected = healthStatus?.status === 'ok' || healthStatus?.status === 'healthy';

  return (
    <div className="space-y-6">
      {/* Header */}
      <SectionHeader 
        title="Settings" 
        description="Configure API integration routers, threat threshold parameters, LLM backends, and UI themes." 
        actions={
          <button
            onClick={handleSave}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 font-mono text-xs font-semibold text-zinc-950 transition-colors"
          >
            <Save className="w-3.5 h-3.5" />
            Save Configurations
          </button>
        }
      />

      {isSaved && (
        <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-3 text-xs font-mono text-emerald-400">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>Configuration details updated successfully. Reloading network clients.</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left pane: Options cards (8 cols) */}
        <div className="lg:col-span-8 space-y-6 text-left">
          {/* Section 1: Backend API Configuration */}
          <div className="p-6 border border-zinc-900 rounded-xl bg-zinc-950/40 backdrop-blur-md space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-zinc-200 uppercase tracking-wider">
              <Server className="w-4 h-4 text-blue-400" />
              <span>Backend API Server</span>
            </div>
            
            <div className="space-y-3.5">
              <div className="space-y-1.5">
                <label className="text-[10px] font-mono text-zinc-400 uppercase">
                  Service URL Host Endpoint
                </label>
                <input
                  type="text"
                  value={backendUrl}
                  onChange={(e) => setBackendUrl(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono text-zinc-250 placeholder-zinc-550 focus:outline-none focus:border-zinc-700"
                />
                <span className="text-[9px] text-zinc-500 font-sans block">
                  Kavalar UI will dispatch Axios requests to this route prefix. Default: http://localhost:8000/api/v1
                </span>
              </div>

              {/* Health check status display */}
              <div className="flex items-center justify-between p-3.5 bg-zinc-900/30 border border-zinc-900 rounded-lg">
                <div className="flex items-center gap-2.5">
                  {isConnected ? (
                    <div className="p-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                  ) : (
                    <div className="p-1 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 animate-pulse">
                      <XCircle className="w-4 h-4" />
                    </div>
                  )}
                  <div className="flex flex-col text-left">
                    <span className="text-[10px] font-mono text-zinc-400 leading-tight">CONNECTION STATUS</span>
                    <span className={cn(
                      "text-xs font-mono font-bold",
                      isConnected ? "text-emerald-400" : "text-red-400"
                    )}>
                      {isConnected ? 'FASTAPI BACKEND ONLINE' : 'CONNECTION REFUSED (OFFLINE fallback active)'}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => checkHealth()}
                  disabled={isCheckingHealth}
                  className="p-2 rounded bg-zinc-900 border border-zinc-850 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
                >
                  <RefreshCw className={cn("w-3.5 h-3.5", isCheckingHealth && "animate-spin")} />
                </button>
              </div>
            </div>
          </div>

          {/* Section 2: LLM Configuration */}
          <div className="p-6 border border-zinc-900 rounded-xl bg-zinc-950/40 backdrop-blur-md space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-zinc-200 uppercase tracking-wider">
              <Cpu className="w-4 h-4 text-purple-400" />
              <span>LLM Orchestrator</span>
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-mono text-zinc-400 uppercase">
                Active Sandbox LLM Provider
              </label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono text-zinc-350 focus:outline-none focus:border-zinc-700"
              >
                <option value="mock-sandbox">Mock Sandbox (Pre-recorded agent trace runs)</option>
                <option value="groq-llama3">Groq Llama-3-70b (Production agent router)</option>
                <option value="openai-gpt4">OpenAI GPT-4o-mini (Governance firewall)</option>
                <option value="gemini-flash">Gemini 3.5 Flash (Behavior visualizer)</option>
              </select>
              <span className="text-[9px] text-zinc-500 font-sans block">
                Determines which model graph executes prompt validations inside the simulator node network.
              </span>
            </div>
          </div>

          {/* Section 3: Detection Parameters */}
          <div className="p-6 border border-zinc-900 rounded-xl bg-zinc-950/40 backdrop-blur-md space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-zinc-200 uppercase tracking-wider">
              <Sliders className="w-4 h-4 text-amber-400" />
              <span>Threat Detection Parameters</span>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-[10px] font-mono text-zinc-400 uppercase">
                    Anomaly Score Threshold
                  </label>
                  <span className="text-xs font-mono font-bold text-amber-400">{threshold.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.95"
                  step="0.05"
                  value={threshold}
                  onChange={(e) => setThreshold(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
                />
                <div className="flex justify-between text-[9px] font-mono text-zinc-550">
                  <span>0.10 Sensitive</span>
                  <span>0.65 Recommended</span>
                  <span>0.95 Lenient</span>
                </div>
              </div>
            </div>
          </div>

          {/* Section 4: Themes */}
          <div className="p-6 border border-zinc-900 rounded-xl bg-zinc-950/40 backdrop-blur-md space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold text-zinc-200 uppercase tracking-wider">
              <Palette className="w-4 h-4 text-emerald-400" />
              <span>User Interface Customization</span>
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-mono text-zinc-400 uppercase">
                Active Theme Profile
              </label>
              <select
                value={themeName}
                onChange={(e) => setThemeName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono text-zinc-350 focus:outline-none focus:border-zinc-700"
              >
                <option value="zinc-dark">SaaS Dark (Zinc/Slate & Emerald)</option>
                <option value="monochrome">Terminal Mono (Black & Amber)</option>
                <option value="security-focus">Triage View (Zinc & High-Contrast Red)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Right pane: About card (4 cols) */}
        <div className="lg:col-span-4 p-6 border border-zinc-900 rounded-xl bg-zinc-950/40 backdrop-blur-md text-left space-y-4">
          <div className="flex items-center gap-2 text-xs font-mono font-semibold text-zinc-200 uppercase tracking-wider">
            <Info className="w-4 h-4 text-zinc-450" />
            <span>About Kavalar</span>
          </div>

          <div className="space-y-3.5 text-xs font-sans text-zinc-450 leading-relaxed">
            <p>
              <span className="font-semibold text-zinc-300">Kavalar</span> is a state-of-the-art enterprise AI Governance and Security Firewall. 
            </p>
            <p>
              By intercepting agent tool executions and analyzing transition pathways through an <span className="font-mono text-xs text-zinc-350 bg-zinc-900 px-1 py-0.5 rounded border border-zinc-850">Isolation Forest</span> behavioral model, Kavalar flags anomalies, sequence deviation payloads, and prompt injection attacks in real time.
            </p>
            
            <div className="border-t border-zinc-900 pt-3 space-y-2 text-[10px] font-mono text-zinc-500">
              <div>ENGINE VERSION: 1.0.0-PROD</div>
              <div>MODEL LAYERS: ISOLATION FOREST v1.0</div>
              <div>DEVELOPMENT GROUP: DEEPMIND ADVANCED CODING</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
