'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Terminal, 
  Network, 
  ShieldCheck, 
  PlayCircle, 
  ShieldAlert, 
  Settings,
  Shield,
  Menu,
  X
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Sessions', href: '/sessions', icon: Terminal },
    { name: 'Behavior Explorer', href: '/explorer', icon: Network },
    { name: 'Baseline', href: '/baseline', icon: ShieldCheck },
    { name: 'Simulator', href: '/simulator', icon: PlayCircle },
    { name: 'Alerts', href: '/alerts', icon: ShieldAlert },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-zinc-950/80 backdrop-blur-sm lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={cn(
          "fixed top-0 bottom-0 left-0 z-50 flex flex-col w-64 bg-zinc-950 border-r border-zinc-900 transition-transform duration-300 lg:translate-x-0 lg:static lg:h-full",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Header/Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-zinc-900">
          <Link href="/" className="flex items-center gap-2.5" onClick={() => setIsOpen(false)}>
            <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-500">
              <Shield className="w-5 h-5" />
            </div>
            <span className="font-mono font-bold text-sm tracking-wider uppercase text-zinc-100">
              Kavalar
            </span>
          </Link>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 rounded-lg text-zinc-500 hover:bg-zinc-900 lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setIsOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-4 py-2.5 rounded-lg font-mono text-xs font-medium transition-all duration-200 group border",
                  isActive
                    ? "bg-zinc-900 border-zinc-800 text-emerald-400 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200 bg-transparent border-transparent hover:bg-zinc-900/40"
                )}
              >
                <Icon className={cn(
                  "w-4 h-4 transition-colors",
                  isActive ? "text-emerald-400" : "text-zinc-500 group-hover:text-zinc-300"
                )} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Footer/Version */}
        <div className="p-4 border-t border-zinc-900">
          <div className="flex items-center gap-3 px-4 py-2 bg-zinc-900/30 border border-zinc-900/80 rounded-lg">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <div className="flex flex-col">
              <span className="text-[10px] font-mono text-zinc-400">MONITOR ACTIVE</span>
              <span className="text-[9px] font-mono text-zinc-600">v1.0.0 (Enterprise)</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
