'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Activity, Video, AlertTriangle, ShieldCheck } from 'lucide-react';

interface CameraData {
  status: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState({ cameras: 0, active: 0, alerts: 0, departments: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [cameras, alerts, depts] = await Promise.all([
          api.getCameras(),
          api.getAlerts(),
          api.getDepartments(),
        ]);
        setStats({
          cameras: cameras.length,
          active: cameras.filter((c: CameraData) => c.status === 'ONLINE').length,
          alerts: alerts.length,
          departments: depts.length,
        });
      } catch (e) {
        console.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-wide">Command Center Overview</h1>
      
      {loading ? (
        <div className="flex justify-center items-center h-40 text-slate-500">Loading system status...</div>
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
