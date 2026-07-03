import React from 'react';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const normalized = status.toLowerCase();

  let styles = 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20';
  let label = status;

  if (normalized === 'normal' || normalized === 'success' || normalized === 'completed') {
    styles = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    label = normalized === 'completed' ? 'Completed' : 'Normal';
  } else if (normalized === 'suspicious' || normalized === 'warning') {
    styles = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    label = 'Suspicious';
  } else if (normalized === 'injected' || normalized === 'danger' || normalized === 'failed') {
    styles = 'bg-red-500/10 text-red-400 border-red-500/20';
    label = normalized === 'failed' ? 'Failed' : 'Injected';
  } else if (normalized === 'pending') {
    styles = 'bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse';
    label = 'Pending';
  }

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium border backdrop-blur-sm',
        styles,
        className
      )}
    >
      <span className={cn('h-1.5 w-1.5 rounded-full bg-current')} />
      {label}
    </span>
  );
}
