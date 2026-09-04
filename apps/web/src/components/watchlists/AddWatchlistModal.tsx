import React, { useState } from 'react';
import { X, Save } from 'lucide-react';

export default function AddWatchlistModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 shadow-2xl rounded-xl w-full max-w-lg flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">
        
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950">
          <h2 className="text-xl font-bold text-white">Add Suspect Vehicle</h2>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-800 rounded-full text-slate-400">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Registration Plate</label>
            <input type="text" className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-blue-500 font-mono uppercase" placeholder="e.g. GJ01ER8842" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Category</label>
              <select className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-blue-500">
                <option>Stolen Vehicle</option>
                <option>Wanted Person (BOLO)</option>
                <option>Tax Defaulter</option>
                <option>Suspicious Activity</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Priority</label>
              <select className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-blue-500">
                <option value="CRITICAL">Critical (Red)</option>
                <option value="HIGH">High (Orange)</option>
                <option value="MEDIUM">Medium (Yellow)</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Reason / Notes</label>
            <textarea className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-blue-500 h-24" placeholder="Enter FIR details or specific instructions..."></textarea>
          </div>
        </div>

        <div className="p-4 border-t border-slate-800 bg-slate-950 flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 bg-transparent text-slate-400 hover:text-white transition-colors">Cancel</button>
          <button onClick={onClose} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors flex items-center gap-2 shadow-lg">
            <Save className="w-4 h-4" /> Save Record
          </button>
        </div>
      </div>
    </div>
  );
}
