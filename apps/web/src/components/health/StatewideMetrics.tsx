'use client';
import React, { useState, useEffect } from 'react';
import { Activity, Server, Network, Database, Cpu, HardDrive, Wifi, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function StatewideMetrics() {
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => setPulse(p => !p), 2000);
    return () => clearInterval(interval);
  }, []);

  const regions = [
    { name: 'Ahmedabad Zone', gpus: 168, load: 84, status: 'Healthy' },
    { name: 'Surat Zone', gpus: 160, load: 92, status: 'Warning' },
    { name: 'Vadodara Zone', gpus: 140, load: 76, status: 'Healthy' },
    { name: 'Rajkot Zone', gpus: 120, load: 65, status: 'Healthy' },
    { name: 'Bhavnagar Zone', gpus: 90, load: 58, status: 'Healthy' },
    { name: 'Gandhinagar (Central)', gpus: 322, load: 88, status: 'Healthy' },
  ];

  return (
    <div className="w-full h-full flex flex-col gap-6 overflow-y-auto pr-2 pb-6">
      
      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-lg relative overflow-hidden">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-500/10 rounded-full blur-xl"></div>
          <div className="flex items-center gap-3 text-slate-400 mb-2">
            <Activity className="w-5 h-5 text-blue-500" /> State Camera Nodes
          </div>
          <div className="text-3xl font-bold text-white tracking-tight">80,000</div>
          <div className="mt-2 text-sm flex items-center gap-2">
            <span className="text-emerald-400 flex items-center"><CheckCircle2 className="w-3 h-3 mr-1"/> 79,402 Online</span>
            <span className="text-red-400 flex items-center"><ShieldAlert className="w-3 h-3 mr-1"/> 598 Offline</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-lg relative overflow-hidden">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl"></div>
          <div className="flex items-center gap-3 text-slate-400 mb-2">
            <Network className="w-5 h-5 text-emerald-500" /> GSWAN Bandwidth Usage
          </div>
          <div className="text-3xl font-bold text-white tracking-tight">1.54 <span className="text-lg text-slate-500">Gbps</span></div>
          <div className="mt-2 text-xs text-slate-400 border border-emerald-500/30 bg-emerald-500/10 px-2 py-1 rounded inline-block">
            METADATA-FIRST OPTIMIZED
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-lg relative overflow-hidden">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-purple-500/10 rounded-full blur-xl"></div>
          <div className="flex items-center gap-3 text-slate-400 mb-2">
            <Cpu className="w-5 h-5 text-purple-500" /> Active GPU Compute
          </div>
          <div className="text-3xl font-bold text-white tracking-tight">1,000 <span className="text-lg text-slate-500">NVIDIA L4</span></div>
          <div className="mt-2 text-sm text-purple-400">Distributing 14.2M Daily Inferences</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-lg relative overflow-hidden">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-orange-500/10 rounded-full blur-xl"></div>
          <div className="flex items-center gap-3 text-slate-400 mb-2">
            <Database className="w-5 h-5 text-orange-500" /> State Alert Broker (Kafka)
          </div>
          <div className="text-3xl font-bold text-white tracking-tight">4,250 <span className="text-lg text-slate-500">msg/sec</span></div>
          <div className="mt-2 text-sm text-slate-400 flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full bg-orange-500 ${pulse ? 'opacity-100' : 'opacity-40'} transition-opacity duration-300`}></div>
            Stream Healthy (RPO {'<'} 1s)
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Regional GPU Load Visualization */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl shadow-lg p-6">
           <div className="flex items-center justify-between mb-6 border-b border-slate-800 pb-4">
             <h2 className="text-lg font-bold text-white flex items-center gap-2">
               <Server className="w-5 h-5 text-blue-500" /> Regional GPU Cluster Utilization
             </h2>
             <span className="text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded">LIVE TELEMETRY</span>
           </div>
           
           <div className="space-y-5">
             {regions.map((region) => (
               <div key={region.name}>
                 <div className="flex justify-between items-end mb-1">
                   <div className="flex items-center gap-2">
                     <span className="text-sm font-semibold text-slate-200">{region.name}</span>
                     {region.status === 'Warning' ? (
                       <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">HIGH LOAD</span>
                     ) : (
                       <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">OK</span>
                     )}
                   </div>
                   <div className="text-xs font-mono text-slate-400">
                     {region.gpus}x L4 &nbsp;|&nbsp; <span className={region.load > 90 ? 'text-orange-400 font-bold' : 'text-slate-300'}>{region.load}% UTIL</span>
                   </div>
                 </div>
                 <div className="w-full bg-slate-950 rounded-full h-2.5 border border-slate-800 overflow-hidden">
                   <div className={`h-2.5 rounded-full ${region.load > 90 ? 'bg-orange-500' : 'bg-blue-500'}`} style={{ width: `${region.load}%` }}></div>
                 </div>
               </div>
             ))}
           </div>
        </div>

        {/* Storage Topology */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-lg p-6 flex flex-col">
           <div className="flex items-center justify-between mb-6 border-b border-slate-800 pb-4">
             <h2 className="text-lg font-bold text-white flex items-center gap-2">
               <HardDrive className="w-5 h-5 text-emerald-500" /> Tiered Storage Map
             </h2>
           </div>
           
           <div className="flex-1 flex flex-col gap-4">
              <div className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-4 relative group hover:border-slate-600 transition-colors">
                <div className="text-xs text-red-400 font-bold tracking-wider mb-1">HOT TIER (3 DAYS)</div>
                <div className="text-sm text-slate-300 font-medium">NVMe SSD Array</div>
                <div className="mt-2 text-2xl font-bold text-white">4.2 <span className="text-sm text-slate-500">TB / 10TB</span></div>
                <div className="w-full bg-slate-900 rounded-full h-1.5 mt-2"><div className="bg-red-500 h-1.5 rounded-full w-[42%]"></div></div>
              </div>
              
              <div className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-4 relative group hover:border-slate-600 transition-colors">
                <div className="text-xs text-orange-400 font-bold tracking-wider mb-1">WARM TIER (30 DAYS)</div>
                <div className="text-sm text-slate-300 font-medium">Ceph Object Storage</div>
                <div className="mt-2 text-2xl font-bold text-white">42.0 <span className="text-sm text-slate-500">TB / 50TB</span></div>
                <div className="w-full bg-slate-900 rounded-full h-1.5 mt-2"><div className="bg-orange-500 h-1.5 rounded-full w-[84%]"></div></div>
              </div>

              <div className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-4 relative group hover:border-slate-600 transition-colors">
                <div className="text-xs text-blue-400 font-bold tracking-wider mb-1">COLD TIER (1-3 YEARS)</div>
                <div className="text-sm text-slate-300 font-medium">AWS S3 Glacier / Tape</div>
                <div className="mt-2 text-2xl font-bold text-white">259 <span className="text-sm text-slate-500">TB / 1PB</span></div>
                <div className="w-full bg-slate-900 rounded-full h-1.5 mt-2"><div className="bg-blue-500 h-1.5 rounded-full w-[25%]"></div></div>
              </div>
           </div>
        </div>

      </div>
    </div>
  );
}
