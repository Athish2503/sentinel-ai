import React from 'react';
import { Database, Search } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  title?: string;
  description?: string;
  iconType?: 'search' | 'database';
  className?: string;
}

export function EmptyState({
  title = 'No records found',
  description = 'There is currently no data matching this configuration.',
  iconType = 'database',
  className
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-12 text-center border border-dashed border-zinc-800 rounded-xl bg-zinc-900/10 backdrop-blur-sm",
        className
      )}
    >
      <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-zinc-900/50 border border-zinc-800/80 mb-4 text-zinc-500">
        {iconType === 'search' ? <Search className="w-6 h-6" /> : <Database className="w-6 h-6" />}
      </div>
      <h3 className="text-sm font-semibold font-mono text-zinc-200">{title}</h3>
      <p className="mt-1 text-xs text-zinc-500 font-sans max-w-xs">{description}</p>
    </div>
  );
}
