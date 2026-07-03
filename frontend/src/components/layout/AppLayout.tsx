'use client';

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';

// Initialize React Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5000,
    },
  },
});

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen w-screen overflow-hidden bg-zinc-950 text-zinc-100 font-mono">
        {/* Sidebar Nav */}
        <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

        {/* Content Wrapper */}
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          {/* Header Nav */}
          <Navbar onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
          
          {/* Page Main Content */}
          <main className="flex-1 overflow-y-auto bg-zinc-950/20 px-4 py-6 sm:px-6 md:py-8">
            <div className="max-w-7xl mx-auto space-y-6">
              {children}
            </div>
          </main>
        </div>
      </div>
    </QueryClientProvider>
  );
}
