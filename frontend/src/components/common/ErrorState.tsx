import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = 'System query failure',
  description = 'Failed to establish connection with the Kavalar anomaly detection backend.',
  onRetry,
  className
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center border border-red-900/30 rounded-xl bg-red-950/10 backdrop-blur-sm",
        className
      )}
    >
      <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/20 mb-4 text-red-400 animate-pulse">
        <AlertCircle className="w-5 h-5" />
      </div>
      <h3 className="text-sm font-semibold font-mono text-zinc-200">{title}</h3>
      <p className="mt-1 text-xs text-zinc-500 font-sans max-w-sm">{description}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-xs font-mono text-zinc-200 border border-zinc-800 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Retry Connection
        </button>
      )}
    </div>
  );
}
