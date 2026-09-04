import React from 'react';
import StatewideMetrics from '@/components/health/StatewideMetrics';
import { Activity } from 'lucide-react';

export default function HealthPage() {
  return (
    <div className="w-full h-full flex flex-col gap-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Activity className="w-6 h-6 text-blue-500" />
            Statewide Infrastructure Health
          </h1>
          <p className="text-slate-400">Live telemetry and scaling metrics for the 80,000-node CCTV federation network</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg flex items-center gap-2">
             <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
             <span className="text-xs font-semibold text-emerald-400 uppercase tracking-widest">DR Site: Standby (GIFT City)</span>
          </div>
        </div>
      </div>
      
      <div className="flex-1 min-h-0">
        <StatewideMetrics />
      </div>
    </div>
  );
}
