import React from 'react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  description?: string;
  trend?: {
    value: number | string;
    direction: 'up' | 'down' | 'neutral';
  };
  icon?: React.ReactNode;
  statusColor?: 'emerald' | 'amber' | 'red' | 'zinc';
  className?: string;
}

export function MetricCard({
  title,
  value,
  description,
  trend,
  icon,
  statusColor = 'zinc',
  className
}: MetricCardProps) {
  const getBorderColor = () => {
    switch (statusColor) {
      case 'emerald': return 'border-emerald-500/20 hover:border-emerald-500/40';
      case 'amber': return 'border-amber-500/20 hover:border-amber-500/40';
      case 'red': return 'border-red-500/20 hover:border-red-500/40';
      default: return 'border-zinc-800/80 hover:border-zinc-700';
    }
  };

  const getTrendColor = () => {
    if (!trend) return '';
    if (trend.direction === 'up') return 'text-red-400'; // up on anomaly/attack metrics is bad
    if (trend.direction === 'down') return 'text-emerald-400'; // down on attack metrics is good
    return 'text-zinc-400';
  };

  return (
    <div
      className={cn(
        "p-6 rounded-xl bg-zinc-950/40 border backdrop-blur-md transition-all duration-300 group flex flex-col justify-between",
        getBorderColor(),
        className
      )}
    >
      <div className="flex justify-between items-start">
        <span className="text-xs font-mono font-medium text-zinc-400 tracking-wider uppercase group-hover:text-zinc-300 transition-colors">
          {title}
        </span>
        {icon && (
          <div className="p-2 rounded-lg bg-zinc-900/80 border border-zinc-800/50 text-zinc-400 group-hover:text-zinc-200 transition-colors">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-4">
        <h3 className="text-3xl font-semibold font-mono tracking-tight text-zinc-50">
          {value}
        </h3>
        
        {(trend || description) && (
          <div className="mt-2 flex items-center gap-1.5 text-xs">
            {trend && (
              <span className={cn("font-mono font-medium", getTrendColor())}>
                {trend.direction === 'up' ? '▲' : trend.direction === 'down' ? '▼' : '■'} {trend.value}
              </span>
            )}
            {description && (
              <span className="text-zinc-500 font-sans">{description}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
