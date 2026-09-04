'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Activity, Video, AlertTriangle, ShieldCheck, WifiOff } from 'lucide-react';

interface CameraData {
  status: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState({ cameras: 0, active: 0, alerts: 0, departments: 0 });
  const [loading, setLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        const [cameras, alerts, depts] = await Promise.all([
          api.getCameras(),
          api.getAlerts(),
          api.getDepartments(),
        ]);
        
        if (!isMounted) return;
        
        setStats({
          cameras: cameras?.length || 0,
          active: cameras?.filter((c: CameraData) => c.status === 'ONLINE').length || 0,
          alerts: alerts?.length || 0,
          departments: depts?.length || 0,
        });
        
        // Detect fallback conditions indicating backend offline
        if ((cameras?.length === 0 || !cameras) && depts?.length === 4) {
          setHasError(true);
        } else {
          setHasError(false);
        }
      } catch (e) {
        if (!isMounted) return;
        setHasError(true);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => { isMounted = false; };
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-wide">Command Center Overview</h1>
      
      {loading ? (
        <div className="flex justify-center items-center h-40 text-slate-500 animate-pulse">
           Connecting to Central CCTV Gateway (http://localhost:8000)...
        </div>
      ) : hasError ? (
        <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-6 flex flex-col items-center justify-center text-orange-400 space-y-3 shadow-lg">
           <WifiOff className="w-8 h-8 opacity-70" />
           <p className="font-medium text-lg">Connecting to Central CCTV Gateway</p>
           <p className="text-sm opacity-80 text-center max-w-md">The backend services at http://localhost:8000 are currently initializing or unavailable. Retrying in the background...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm tracking-wider uppercase">Total Cameras</p>
              <p className="text-3xl font-bold text-white mt-2">{stats.cameras}</p>
            </div>
            <Video className="w-10 h-10 text-blue-500/50" />
          </div>
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm tracking-wider uppercase">Online Cameras</p>
              <p className="text-3xl font-bold text-green-500 mt-2">{stats.active}</p>
            </div>
            <Activity className="w-10 h-10 text-green-500/50" />
          </div>
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm tracking-wider uppercase">Active Alerts</p>
              <p className="text-3xl font-bold text-red-500 mt-2">{stats.alerts}</p>
            </div>
            <AlertTriangle className="w-10 h-10 text-red-500/50" />
          </div>
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm tracking-wider uppercase">Departments</p>
              <p className="text-3xl font-bold text-purple-500 mt-2">{stats.departments}</p>
            </div>
            <ShieldCheck className="w-10 h-10 text-purple-500/50" />
          </div>
        </div>
      )}
      
      <div className="bg-slate-900 border border-slate-800 rounded-lg h-96 flex items-center justify-center text-slate-600">
        <p>Interactive Map & Live Grid Area (Phase 3)</p>
      </div>
    </div>
  );
}
