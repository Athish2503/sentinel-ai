import React from 'react';
import { ArrowRight, HelpCircle, CornerDownRight } from 'lucide-react';
import { ToolNode } from './ToolNode';
import { cn } from '@/lib/utils';

interface GraphNode {
  name: string;
  latency?: number;
  status?: 'normal' | 'anomalous' | 'unauthorized';
  args?: Record<string, any>;
}

interface SequenceGraphProps {
  nodes: GraphNode[];
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

export function SequenceGraph({
  nodes,
  orientation = 'horizontal',
  className
}: SequenceGraphProps) {
  if (nodes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 border border-dashed border-zinc-800 rounded-xl text-zinc-500 text-xs font-mono">
        <HelpCircle className="w-5 h-5 mb-2 text-zinc-600" />
        No execution sequence graph data.
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex flex-wrap items-center gap-4 p-4 rounded-xl bg-zinc-950/20 border border-zinc-900/60",
        orientation === 'vertical' ? 'flex-col items-start pl-8' : 'flex-row',
        className
      )}
    >
      {nodes.map((node, index) => {
        const isLast = index === nodes.length - 1;

        return (
          <React.Fragment key={index}>
            <div className="relative">
              <ToolNode
                name={node.name}
                order={index + 1}
                latency={node.latency}
                status={node.status}
                args={node.args}
              />
            </div>
            
            {!isLast && (
              <div className={cn(
                "flex items-center justify-center text-zinc-700 shrink-0",
                orientation === 'vertical' ? 'h-6 ml-24' : 'w-6'
              )}>
                {orientation === 'vertical' ? (
                  <CornerDownRight className="w-4 h-4 text-zinc-650" />
                ) : (
                  <ArrowRight className="w-4 h-4 text-zinc-650 animate-pulse" />
                )}
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
