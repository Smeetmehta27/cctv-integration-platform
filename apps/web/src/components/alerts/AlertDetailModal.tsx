import React from 'react';
import { X, Navigation, Map, AlertTriangle, ShieldCheck } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface Alert {
  id: string;
  plate: string;
  severity: string;
  time: string;
  camera: string;
  desc: string;
  evidence: any;
}

interface Props {
  alert: Alert | null;
  onClose: () => void;
}

export default function AlertDetailModal({ alert, onClose }: Props) {
  const router = useRouter();
  if (!alert) return null;

  const handleRouteReconstruction = () => {
    // Navigate to tracking page with query param
    router.push(`/tracking?plate=${alert.plate}`);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 shadow-2xl rounded-xl w-full max-w-5xl flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">
        
        {/* Header */}
        <div className={`p-4 flex justify-between items-center ${
          alert.severity === 'CRITICAL' ? 'bg-red-950/50 border-b border-red-900/50' : 
          alert.severity === 'HIGH' ? 'bg-orange-950/50 border-b border-orange-900/50' : 
          'bg-yellow-950/50 border-b border-yellow-900/50'
        }`}>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <AlertTriangle className={`w-6 h-6 ${
              alert.severity === 'CRITICAL' ? 'text-red-500' : 
              alert.severity === 'HIGH' ? 'text-orange-500' : 'text-yellow-500'
            }`} />
            Alert Details: {alert.plate}
          </h2>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-800 rounded-full text-slate-400 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex flex-col md:flex-row flex-1 p-6 gap-6 overflow-y-auto">
          
          {/* Left Panel: Evidence Snapshot */}
          <div className="flex-1 space-y-4">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Detection Evidence</h3>
            <div className="relative w-full aspect-video bg-black rounded-lg border border-slate-700 overflow-hidden shadow-inner group">
              <img 
                src="https://vigilis-storage.local/snapshots/mock.jpg" 
                alt="Detection Snapshot"
                className="w-full h-full object-cover opacity-80"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiMxZTI5M2IiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1zaXplPSIxOHB4IiBmb250LWZhbWlseT0ic2Fucy1zZXJpZiIgZmlsbD0iIzQ3NTU2OSIgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgdGV4dC1hbmNob3I9Im1pZGRsZSI+T0NSIFNOQVBTSE9UIFVOQVZBSUxBQkxFPC90ZXh0Pjwvc3ZnPg==';
                }}
              />
              {/* Simulated Bounding Box */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-16 border-2 border-emerald-500 bg-emerald-500/10 flex items-end justify-center pb-1">
                 <span className="bg-emerald-500 text-black text-[10px] font-bold px-1 rounded shadow">{alert.plate} 98%</span>
              </div>
              <div className="absolute top-3 left-3 bg-black/70 px-2 py-1 rounded text-xs text-white font-mono border border-slate-700">
                CAM: {alert.camera}
              </div>
              <div className="absolute bottom-3 left-3 bg-black/70 px-2 py-1 rounded text-xs text-white font-mono border border-slate-700">
                {alert.time}
              </div>
            </div>
            <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
               <div className="text-sm text-slate-300"><span className="font-semibold text-slate-400">Trigger: </span> {alert.desc}</div>
               <div className="text-sm text-slate-300 mt-2"><span className="font-semibold text-slate-400">Track ID: </span> {alert.evidence?.track_id || 'N/A'}</div>
            </div>
          </div>

          {/* Right Panel: Watchlist Record */}
          <div className="flex-1 space-y-4">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Official Database Record</h3>
            <div className="bg-slate-800 rounded-lg border border-slate-700 p-5 space-y-4">
              <div className="flex items-center gap-3 pb-4 border-b border-slate-700">
                <div className="w-12 h-12 bg-blue-900/50 rounded-lg flex items-center justify-center border border-blue-500/30">
                  <ShieldCheck className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <h4 className="text-lg font-bold text-white">{alert.severity === 'CRITICAL' ? 'eGujCop Stolen Vehicle' : 'VAHAN Blacklist'}</h4>
                  <p className="text-sm text-slate-400">Record Matched on {alert.plate}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-y-4 gap-x-2 text-sm">
                <div>
                  <div className="text-slate-500 mb-1">FIR Number</div>
                  <div className="font-semibold text-slate-200">112/2026</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Police Station</div>
                  <div className="font-semibold text-slate-200">Vastrapur, Ahmedabad</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Owner Name</div>
                  <div className="font-semibold text-slate-200">Ramesh Patel</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Vehicle Model</div>
                  <div className="font-semibold text-slate-200">Toyota Fortuner (White)</div>
                </div>
                <div className="col-span-2">
                  <div className="text-slate-500 mb-1">Offense Category</div>
                  <div className="font-semibold text-red-400">Theft / Unauthorized Use</div>
                </div>
                <div className="col-span-2">
                  <div className="text-slate-500 mb-1">Officer Notes</div>
                  <div className="text-slate-300 italic bg-slate-900/50 p-3 rounded border border-slate-700/50">
                    {alert.evidence?.notes || 'Vehicle reported stolen from SG Highway. Suspects armed. Do not approach without backup.'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-800 bg-slate-950 flex flex-wrap gap-3 justify-end">
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 border border-slate-700">
            <Map className="w-4 h-4" /> View on GIS Map
          </button>
          <button 
            onClick={handleRouteReconstruction}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-lg"
          >
            <Navigation className="w-4 h-4" /> Reconstruct Route
          </button>
          <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg">
            Acknowledge Alert
          </button>
          <button className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-red-900/20">
            Dispatch Intercept Unit
          </button>
        </div>
        
      </div>
    </div>
  );
}
