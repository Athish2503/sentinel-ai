import React from 'react';
import { cn } from '@/lib/utils';

interface ChartCardProps {
  title: string;
  description?: string;
  headerAction?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function ChartCard({
  title,
  description,
  headerAction,
  children,
  className
}: ChartCardProps) {
  return (
    <div
      className={cn(
        "p-6 rounded-xl bg-zinc-950/40 border border-zinc-800/80 backdrop-blur-md flex flex-col justify-between hover:border-zinc-700/80 transition-all duration-300",
        className
      )}
    >
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-sm font-semibold font-mono text-zinc-100 uppercase tracking-wider">
            {title}
          </h3>
          {description && (
            <p className="text-xs text-zinc-500 font-sans mt-0.5">
              {description}
            </p>
          )}
        </div>
        {headerAction && (
          <div className="flex items-center gap-2">
            {headerAction}
          </div>
        )}
      </div>

      <div className="flex-1 w-full min-h-[240px]">
        {children}
      </div>
    </div>
  );
}
