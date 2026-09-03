'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Activity, Database, Server } from 'lucide-react';

interface HealthData {
  status: string;
  database?: { status: string; engine: string };
  redis?: { status: string };
}

export default function Health() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function fetchHealth() {
      try {
        const data = await api.getHealth();
        setHealth(data);
      } catch (e) {
        setError(true);
      } finally {
        setLoading(false);
      }
    }
    fetchHealth();
  }, []);

  return (
    <div className="space-y-6 max-w-4xl">
      <h1 className="text-2xl font-bold text-white tracking-wide">System Health</h1>
      
      {loading ? (
        <div className="flex justify-center items-center h-40 text-slate-500">Checking system status...</div>
      ) : error ? (
        <div className="bg-red-500/10 border border-red-500/50 p-6 rounded-lg text-red-500">
          <h2 className="text-lg font-bold flex items-center gap-2"><Server /> API Unreachable</h2>
          <p className="mt-2 text-sm">Failed to connect to the backend services. Please ensure the API is running.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg">
            <h3 className="text-slate-400 text-sm tracking-wider uppercase flex items-center gap-2 mb-4">
              <Server className="w-4 h-4" /> API Service
            </h3>
            <div className="flex justify-between items-center border-b border-slate-800 pb-2 mb-2">
              <span className="text-sm">Status</span>
              <span className="text-green-500 font-bold">{health?.status.toUpperCase()}</span>
            </div>
          </div>
          
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg">
            <h3 className="text-slate-400 text-sm tracking-wider uppercase flex items-center gap-2 mb-4">
              <Database className="w-4 h-4" /> Database ({health?.database?.engine ? health.database.engine.toUpperCase() : 'UNKNOWN'})
            </h3>
            <div className="flex justify-between items-center border-b border-slate-800 pb-2 mb-2">
              <span className="text-sm">Status</span>
              <span className={health?.database?.status === 'CONNECTED' ? "text-green-500 font-bold" : "text-yellow-500 font-bold"}>
                {health?.database?.status || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-500">Engine</span>
              <span className="text-sm text-slate-300">{health?.database?.engine || 'N/A'}</span>
            </div>
          </div>
          
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg">
            <h3 className="text-slate-400 text-sm tracking-wider uppercase flex items-center gap-2 mb-4">
              <Database className="w-4 h-4" /> Redis Cache
            </h3>
            <div className="flex justify-between items-center border-b border-slate-800 pb-2 mb-2">
              <span className="text-sm">Status</span>
              <span className={health?.redis?.status === 'CONNECTED' ? "text-green-500 font-bold" : health?.redis?.status === 'DISCONNECTED' ? "text-red-500 font-bold" : "text-slate-500 font-bold"}>
                {health?.redis?.status || 'UNKNOWN'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
