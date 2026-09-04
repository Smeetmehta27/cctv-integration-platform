'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '@/lib/websocket';
import { format } from 'date-fns';
import { Volume2, VolumeX, AlertTriangle, ShieldAlert, Car, Search, Filter } from 'lucide-react';
import AlertDetailModal from './AlertDetailModal';

// Base64 encoded short beep sound
const BEEP_SOUND = "data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU"+
"A+t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3"; 
// Note: We use a placeholder string, in reality we would load a tiny mp3 or use Web Audio API oscillator.
// We will use a reliable Web Audio API approach instead.

function playBeep() {
  try {
    const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, ctx.currentTime); // A5
    osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.1);
    
    gainNode.gain.setValueAtTime(0.5, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
    
    osc.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    osc.start();
    osc.stop(ctx.currentTime + 0.1);
  } catch(e) {
    console.error("Audio play failed", e);
  }
}

export default function AlertFeed() {
  const { messages, isConnected } = useWebSocket();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [isMuted, setIsMuted] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<any | null>(null);
  
  // Track messages length to detect new ones
  const prevMsgCount = useRef(0);

  useEffect(() => {
    if (messages.length > prevMsgCount.current) {
      // Find new alerts
      const newAlertMsgs = messages.slice(prevMsgCount.current).filter(m => m.event_type === 'ALERT_TRIGGERED');
      
      if (newAlertMsgs.length > 0) {
        if (!isMuted) {
          playBeep();
        }
        
        // Map to our local alert format
        const formattedAlerts = newAlertMsgs.map(msg => ({
          id: msg.payload?.alert_id || Math.random().toString(),
          plate: msg.payload?.plate_number || 'UNKNOWN',
          severity: msg.payload?.priority || 'HIGH',
          time: msg.timestamp ? format(new Date(msg.timestamp), 'PPpp') : format(new Date(), 'PPpp'),
          camera: msg.camera_id || 'Unknown Camera',
          desc: msg.payload?.description || 'Watchlist match detected',
          evidence: msg.payload?.evidence || {}
        }));
        
        setAlerts(prev => [...formattedAlerts, ...prev].slice(0, 100)); // Keep last 100
      }
      prevMsgCount.current = messages.length;
    }
  }, [messages, isMuted]);

  // Generate some initial mock alerts for visual population if empty
  useEffect(() => {
    if (alerts.length === 0) {
      setAlerts([
        {
          id: '1', plate: 'GJ01ER8842', severity: 'CRITICAL', time: format(new Date(Date.now() - 1000*60*5), 'PPpp'),
          camera: 'Ahmedabad SG Highway Toll', desc: 'Watchlist match for GJ01ER8842', evidence: { track_id: 't_123', notes: 'Stolen vehicle' }
        },
        {
          id: '2', plate: 'GJ05XY1234', severity: 'HIGH', time: format(new Date(Date.now() - 1000*60*45), 'PPpp'),
          camera: 'Surat Kadodara Checkpost', desc: 'Watchlist match for GJ05XY1234', evidence: { track_id: 't_456', notes: 'Tax Defaulter' }
        },
        {
          id: '3', plate: 'GJ27CC9999', severity: 'MEDIUM', time: format(new Date(Date.now() - 1000*60*120), 'PPpp'),
          camera: 'Gandhinagar CH-0', desc: 'Watchlist match for GJ27CC9999', evidence: { track_id: 't_789', notes: 'Unauthorized Entry' }
        }
      ]);
    }
  }, []);

  return (
    <div className="w-full h-full flex flex-col gap-4">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-900 p-4 rounded-xl border border-slate-800 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-sm font-medium text-slate-300">
              {isConnected ? 'Live WebSocket Connected' : 'Disconnected'}
            </span>
          </div>
          <button 
            onClick={() => setIsMuted(!isMuted)}
            className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 text-sm transition-colors border border-slate-700"
          >
            {isMuted ? <VolumeX className="w-4 h-4 text-red-400" /> : <Volume2 className="w-4 h-4 text-emerald-400" />}
            {isMuted ? 'Muted' : 'Audio On'}
          </button>
        </div>
        
        <div className="flex gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input 
              type="text" 
              placeholder="Filter Plate..." 
              className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button className="p-1.5 bg-slate-800 rounded-lg border border-slate-700 text-slate-400 hover:text-slate-200">
            <Filter className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Feed Table */}
      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs text-slate-400 uppercase bg-slate-950/50 border-b border-slate-800 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-4 font-semibold">Severity</th>
                <th className="px-6 py-4 font-semibold">Timestamp</th>
                <th className="px-6 py-4 font-semibold">Plate Number</th>
                <th className="px-6 py-4 font-semibold">Camera Node</th>
                <th className="px-6 py-4 font-semibold">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    <ShieldAlert className="w-12 h-12 mx-auto mb-3 opacity-20" />
                    No alerts in the current session.
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr 
                    key={alert.id} 
                    onClick={() => setSelectedAlert(alert)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors group"
                  >
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded text-xs font-bold border flex w-min items-center gap-1.5
                        ${alert.severity === 'CRITICAL' ? 'bg-red-500/10 text-red-500 border-red-500/20' : 
                          alert.severity === 'HIGH' ? 'bg-orange-500/10 text-orange-500 border-orange-500/20' : 
                          'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'}`}
                      >
                        <div className={`w-1.5 h-1.5 rounded-full ${alert.severity === 'CRITICAL' ? 'bg-red-500 animate-pulse' : alert.severity === 'HIGH' ? 'bg-orange-500' : 'bg-yellow-500'}`}></div>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-400 whitespace-nowrap">{alert.time}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Car className="w-4 h-4 text-slate-500" />
                        <span className="font-mono font-bold text-slate-200">{alert.plate}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">{alert.camera}</td>
                    <td className="px-6 py-4 text-slate-400 max-w-xs truncate">{alert.desc}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <AlertDetailModal alert={selectedAlert} onClose={() => setSelectedAlert(null)} />
    </div>
  );
}
