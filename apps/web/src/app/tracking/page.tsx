'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { Search, Navigation } from 'lucide-react';

const DynamicVisualizer = dynamic(() => import('@/components/map/RouteVisualizer'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-slate-900 rounded-xl border border-slate-800">
      <div className="flex flex-col items-center gap-4">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 font-medium">Initializing Trajectory Engine...</p>
      </div>
    </div>
  )
});

export default function TrackingPage() {
  const [searchInput, setSearchInput] = useState('');
  const [plateToTrack, setPlateToTrack] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setPlateToTrack(searchInput.trim().toUpperCase());
    }
  };

  return (
    <div className="w-full h-full flex flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Navigation className="w-6 h-6 text-blue-500" /> Route Reconstruction
          </h1>
          <p className="text-slate-400">Trace vehicle pathways across the statewide network</p>
        </div>
        
        <form onSubmit={handleSearch} className="flex-1 max-w-md relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-slate-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-24 py-3 bg-slate-900 border border-slate-700 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-inner font-mono text-lg uppercase"
            placeholder="e.g. GJ01ER8842"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <button 
            type="submit"
            className="absolute inset-y-1.5 right-1.5 bg-blue-600 hover:bg-blue-500 text-white px-4 py-1.5 rounded-lg text-sm font-semibold transition-colors shadow-lg"
          >
            Track
          </button>
        </form>
      </div>
      
      <div className="flex-1 min-h-0 relative">
        {plateToTrack ? (
          <DynamicVisualizer plateNumber={plateToTrack} />
        ) : (
          <div className="w-full h-full rounded-xl border border-dashed border-slate-700 bg-slate-900/50 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-700">
                <Search className="w-8 h-8 text-slate-500" />
              </div>
              <h3 className="text-lg font-medium text-slate-300">Awaiting Target</h3>
              <p className="text-slate-500 mt-1 max-w-sm">Enter a vehicle registration number above to reconstruct its spatial-temporal route.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
