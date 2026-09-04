'use client';
import React, { useState } from 'react';
import { ShieldCheck, Search, Filter } from 'lucide-react';

const mockData = [
  { id: 1, plate: 'GJ01ER8842', owner: 'Ramesh Patel', fir: '112/2026', offense: 'Stolen Vehicle (Fortuner)', date: '2026-09-01', priority: 'CRITICAL', source: 'eGujCop' },
  { id: 2, plate: 'GJ05XY1234', owner: 'Suresh Kumar', fir: 'N/A', offense: 'Tax Defaulter > 10 Yrs', date: '2026-08-20', priority: 'HIGH', source: 'VAHAN' },
  { id: 3, plate: 'GJ27CC9999', owner: 'Unknown', fir: '45/2026', offense: 'Hit and Run Suspect', date: '2026-09-02', priority: 'CRITICAL', source: 'Local BOLO' },
  { id: 4, plate: 'GJ01AB1111', owner: 'Anil Desai', fir: 'N/A', offense: 'Multiple Traffic Violations', date: '2026-07-15', priority: 'MEDIUM', source: 'RTO' },
  { id: 5, plate: 'GJ09PQ5555', owner: 'Vijay Shah', fir: '99/2026', offense: 'Wanted - Smuggling', date: '2026-08-25', priority: 'CRITICAL', source: 'eGujCop' }
];

export default function WatchlistTable() {
  const [activeTab, setActiveTab] = useState('ALL');
  
  const filtered = mockData.filter(d => activeTab === 'ALL' || d.source.includes(activeTab));

  return (
    <div className="w-full h-full flex flex-col gap-4">
      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-2">
        {['ALL', 'eGujCop', 'VAHAN', 'Local BOLO'].map(tab => (
          <button 
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-t-lg text-sm font-semibold transition-colors ${
              activeTab === tab ? 'bg-slate-800 text-blue-400 border-b-2 border-blue-500' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            {tab === 'ALL' ? 'All Records' : tab}
          </button>
        ))}
      </div>

      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col">
        <div className="p-4 border-b border-slate-800 flex justify-between">
           <div className="relative w-64">
             <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
             <input type="text" placeholder="Search plates..." className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-sm focus:border-blue-500 focus:outline-none text-white"/>
           </div>
           <button className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-lg text-sm text-slate-300 hover:text-white border border-slate-700">
             <Filter className="w-4 h-4" /> Filter
           </button>
        </div>
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs text-slate-400 uppercase bg-slate-950/50 border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Reg. Plate</th>
                <th className="px-6 py-4">Priority</th>
                <th className="px-6 py-4">Source DB</th>
                <th className="px-6 py-4">Owner Name</th>
                <th className="px-6 py-4">FIR Ref</th>
                <th className="px-6 py-4">Offense / Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filtered.map(row => (
                <tr key={row.id} className={`hover:bg-slate-800/50 transition-colors ${row.plate === 'GJ01ER8842' ? 'bg-blue-900/10' : ''}`}>
                  <td className="px-6 py-4">
                    <span className="font-mono font-bold text-white tracking-wide">{row.plate}</span>
                    {row.plate === 'GJ01ER8842' && <span className="ml-2 text-[10px] bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded border border-blue-500/30">TEST TARGET</span>}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold border
                      ${row.priority === 'CRITICAL' ? 'bg-red-500/10 text-red-500 border-red-500/20' : 
                        row.priority === 'HIGH' ? 'bg-orange-500/10 text-orange-500 border-orange-500/20' : 
                        'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'}`}
                    >
                      {row.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-slate-500" />
                      {row.source}
                    </div>
                  </td>
                  <td className="px-6 py-4">{row.owner}</td>
                  <td className="px-6 py-4 text-slate-400">{row.fir}</td>
                  <td className="px-6 py-4 text-slate-400 max-w-[200px] truncate">{row.offense}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
