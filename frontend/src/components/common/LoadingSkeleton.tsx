import React from 'react';
import { cn } from '@/lib/utils';

interface LoadingSkeletonProps {
  className?: string;
  variant?: 'card' | 'table' | 'line' | 'graph';
}

export function LoadingSkeleton({ className, variant = 'card' }: LoadingSkeletonProps) {
  if (variant === 'table') {
    return (
      <div className={cn("w-full space-y-4 animate-pulse", className)}>
        <div className="h-10 bg-zinc-900/50 border border-zinc-800/80 rounded-lg" />
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-14 bg-zinc-900/30 border border-zinc-850/50 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (variant === 'line') {
    return (
      <div className={cn("w-full space-y-2 animate-pulse", className)}>
        <div className="h-4 bg-zinc-900/50 rounded w-1/4" />
        <div className="h-4 bg-zinc-900/30 rounded w-3/4" />
        <div className="h-4 bg-zinc-900/20 rounded w-1/2" />
      </div>
    );
  }

  if (variant === 'graph') {
    return (
      <div className={cn("w-full h-64 bg-zinc-900/30 border border-zinc-800/50 rounded-xl flex items-center justify-center animate-pulse", className)}>
        <div className="flex gap-8">
          <div className="w-16 h-16 rounded-full bg-zinc-800/50" />
          <div className="w-16 h-16 rounded-full bg-zinc-800/50" />
          <div className="w-16 h-16 rounded-full bg-zinc-800/50" />
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "p-6 bg-zinc-900/30 border border-zinc-800/50 rounded-xl backdrop-blur-md animate-pulse space-y-4",
        className
      )}
    >
      <div className="h-4 bg-zinc-800/60 rounded w-1/3" />
      <div className="h-8 bg-zinc-800/40 rounded w-1/2" />
      <div className="h-3 bg-zinc-800/20 rounded w-2/3" />
    </div>
  );
}
