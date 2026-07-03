'use client';

import React from 'react';
import { 
  Bell, 
  Menu, 
  Moon, 
  ShieldAlert, 
  Info,
  Sliders,
  Cpu
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { alertService } from '@/services/alert.service';
import { baselineService } from '@/services/baseline.service';

interface NavbarProps {
  onMenuToggle: () => void;
}

export function Navbar({ onMenuToggle }: NavbarProps) {
  // Fetch alerts to show the live notification count
  const { data: alerts = [] } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertService.getAlerts(0, 100),
    refetchInterval: 15000, // Refresh alerts every 15s to feel dynamic
  });

  const { data: activeBaseline } = useQuery({
    queryKey: ['activeBaseline'],
    queryFn: () => baselineService.getActiveBaseline(),
  });

  const unreadAlertsCount = alerts.length;

  return (
    <header className="h-16 border-b border-zinc-900 bg-zinc-950/60 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-6">
      {/* Left items: Mobile Menu button & Title */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuToggle}
          className="p-1.5 rounded-lg text-zinc-400 hover:bg-zinc-900 lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
        
        {/* Environment Status Pills - visible on desktop */}
        <div className="hidden sm:flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900/80 border border-zinc-800 text-zinc-300 font-mono text-[10px] font-medium">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span>MODEL: ISOLATION_FOREST</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900/80 border border-zinc-800 text-zinc-300 font-mono text-[10px] font-medium">
            <Sliders className="w-3.5 h-3.5 text-amber-400" />
            <span>THRESHOLD: {activeBaseline?.threshold || 0.65}</span>
          </div>
        </div>
      </div>

      {/* Right items: System Notifications, User Profile */}
      <div className="flex items-center gap-4">
        {/* Status indicator */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/5 border border-emerald-500/10 text-emerald-400 font-mono text-[10px]">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-ping" />
          <span>ALL SYSTEMS OPERATIONAL</span>
        </div>

        {/* Notifications Icon */}
        <div className="relative">
          <button className="p-2 rounded-lg text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200 transition-colors border border-zinc-900">
            <Bell className="w-4 h-4" />
            {unreadAlertsCount > 0 && (
              <span className="absolute top-1.5 right-1.5 flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
              </span>
            )}
          </button>
        </div>

        {/* Static Theme Toggle Indicator */}
        <button className="p-2 rounded-lg text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200 transition-colors border border-zinc-900">
          <Moon className="w-4 h-4 text-emerald-400" />
        </button>

        {/* Divider */}
        <div className="h-6 w-px bg-zinc-850" />

        {/* User avatar */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center text-xs font-mono font-bold text-zinc-300">
            SA
          </div>
          <div className="hidden md:flex flex-col text-left">
            <span className="text-[11px] font-mono font-medium text-zinc-300 leading-tight">Admin User</span>
            <span className="text-[9px] font-sans text-zinc-500">Kavalar Security</span>
          </div>
        </div>
      </div>
    </header>
  );
}
