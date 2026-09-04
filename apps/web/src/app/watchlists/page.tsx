'use client';
import React, { useState } from 'react';
import WatchlistTable from '@/components/watchlists/WatchlistTable';
import AddWatchlistModal from '@/components/watchlists/AddWatchlistModal';
import { List, Plus, UploadCloud } from 'lucide-react';

export default function WatchlistsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="w-full h-full flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <List className="w-6 h-6 text-blue-500" />
            Watchlist Database
          </h1>
          <p className="text-slate-400">Manage unified records from eGujCop, VAHAN, and local BOLO directives</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 border border-slate-700">
            <UploadCloud className="w-4 h-4" /> Bulk CSV Import
          </button>
          <button 
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-lg"
          >
            <Plus className="w-4 h-4" /> Add Record
          </button>
        </div>
      </div>
      
      <div className="flex-1 min-h-0">
        <WatchlistTable />
      </div>

      <AddWatchlistModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
