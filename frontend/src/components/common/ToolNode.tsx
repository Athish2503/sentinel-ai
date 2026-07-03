import React from 'react';
import { 
  Search, 
  FileText, 
  Calculator, 
  Mail, 
  Database, 
  HelpCircle,
  AlertOctagon,
  CheckCircle2
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ToolNodeProps {
  name: string;
  order: number;
  latency?: number;
  status?: 'normal' | 'anomalous' | 'unauthorized';
  args?: Record<string, any>;
  className?: string;
}

export function ToolNode({
  name,
  order,
  latency,
  status = 'normal',
  args,
  className
}: ToolNodeProps) {
  const getToolIcon = (toolName: string) => {
    const lower = toolName.toLowerCase();
    if (lower.includes('search')) return <Search className="w-4 h-4" />;
    if (lower.includes('read') || lower.includes('document')) return <FileText className="w-4 h-4" />;
    if (lower.includes('calc')) return <Calculator className="w-4 h-4" />;
    if (lower.includes('email') || lower.includes('send')) return <Mail className="w-4 h-4" />;
    if (lower.includes('customer') || lower.includes('lookup')) return <Database className="w-4 h-4" />;
    return <HelpCircle className="w-4 h-4" />;
  };

  const getBorderColor = () => {
    if (status === 'anomalous') return 'border-red-500/40 hover:border-red-500/60 bg-red-950/10 text-red-200';
    if (status === 'unauthorized') return 'border-amber-500/40 hover:border-amber-500/60 bg-amber-950/10 text-amber-200';
    return 'border-zinc-800 bg-zinc-900/40 hover:border-zinc-700 text-zinc-100';
  };

  return (
    <div
      className={cn(
        "flex items-center gap-3.5 p-4 rounded-xl border backdrop-blur-md transition-all duration-200 min-w-[210px] select-none group",
        getBorderColor(),
        className
      )}
    >
      {/* Node Index Indicator */}
      <div className={cn(
        "flex h-6 w-6 shrink-0 items-center justify-center rounded-full font-mono text-[10px] font-bold border",
        status === 'anomalous' 
          ? "bg-red-500/20 border-red-500/30 text-red-400" 
          : status === 'unauthorized'
            ? "bg-amber-500/20 border-amber-500/30 text-amber-400"
            : "bg-zinc-900 border-zinc-800 text-zinc-500 group-hover:text-zinc-300"
      )}>
        {order}
      </div>

      {/* Tool details */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-1 mb-0.5">
          <span className="font-mono text-xs font-semibold truncate uppercase tracking-wider">
            {name.replace(/_/g, ' ')}
          </span>
          {status !== 'normal' && (
            <AlertOctagon className={cn(
              "w-3.5 h-3.5 shrink-0 animate-pulse",
              status === 'anomalous' ? "text-red-400" : "text-amber-400"
            )} />
          )}
        </div>
        <div className="flex items-center justify-between text-[10px] text-zinc-500 font-mono">
          <span>{name}</span>
          {latency !== undefined && <span>{latency.toFixed(3)}s</span>}
        </div>
      </div>
    </div>
  );
}
