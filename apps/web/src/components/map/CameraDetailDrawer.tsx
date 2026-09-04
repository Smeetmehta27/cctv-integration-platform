import React from 'react';
import { X, MapPin, HardDrive, Video, ShieldAlert } from 'lucide-react';

interface Camera {
  id: string;
  name: string;
  department: string;
  location: { coordinates: [number, number] } | null;
  status: string;
}

interface Props {
  camera: Camera | null;
  onClose: () => void;
}

export default function CameraDetailDrawer({ camera, onClose }: Props) {
  if (!camera) return null;
  
  return (
    <div className="absolute top-0 right-0 h-full w-96 bg-slate-900 border-l border-slate-700 shadow-2xl flex flex-col z-[1000] transition-transform duration-300">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950">
        <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <Video className="w-5 h-5 text-blue-400" />
          Camera Details
        </h2>
        <button onClick={onClose} className="p-1 hover:bg-slate-800 rounded-full text-slate-400">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-6">
          
          {/* Metadata */}
          <div>
            <h3 className="text-xl font-bold text-white mb-1">{camera.name}</h3>
            <span className="inline-block px-2 py-1 bg-slate-800 text-xs font-medium text-slate-300 rounded border border-slate-700">
              {camera.department}
            </span>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
              <div className="text-xs text-slate-400 flex items-center gap-1 mb-1">
                <MapPin className="w-3 h-3" /> Location
              </div>
              <div className="text-sm text-slate-200">
                {camera.location ? `${camera.location.coordinates[1].toFixed(4)}, ${camera.location.coordinates[0].toFixed(4)}` : 'Unknown'}
              </div>
            </div>
            <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
              <div className="text-xs text-slate-400 flex items-center gap-1 mb-1">
                <HardDrive className="w-3 h-3" /> Retention
              </div>
              <div className="text-sm text-slate-200">30 Days</div>
            </div>
          </div>

          {/* Live Feed */}
          <div>
            <div className="text-xs text-slate-400 flex items-center gap-1 mb-2 font-medium">
              <Video className="w-4 h-4 text-emerald-400" /> LIVE FEED
            </div>
            <div className="relative w-full aspect-video bg-black rounded-lg border border-slate-700 overflow-hidden shadow-inner group">
              <img 
                src={`http://localhost:8000/api/v1/stream/simulate-feed/${camera.id}`} 
                alt="Live Stream"
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/fallback-stream.png';
                }}
              />
              <div className="absolute top-2 right-2 flex items-center gap-1.5 bg-black/60 px-2 py-1 rounded backdrop-blur-sm">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[10px] font-bold text-white">LIVE</span>
              </div>
            </div>
          </div>

          {/* Recent ANPR Logs Placeholder */}
          <div>
            <div className="text-xs text-slate-400 flex items-center gap-1 mb-2 font-medium">
              <ShieldAlert className="w-4 h-4 text-amber-400" /> RECENT DETECTIONS
            </div>
            <div className="bg-slate-800 rounded-lg border border-slate-700 divide-y divide-slate-700/50">
              <div className="p-3 text-sm flex justify-between items-center text-slate-300">
                <span className="font-mono text-emerald-400">GJ01ER8842</span>
                <span className="text-xs text-slate-500">Just now</span>
              </div>
              <div className="p-3 text-sm flex justify-between items-center text-slate-300">
                <span className="font-mono">GJ05AB1234</span>
                <span className="text-xs text-slate-500">2 min ago</span>
              </div>
              <div className="p-3 text-sm flex justify-between items-center text-slate-300">
                <span className="font-mono">GJ27CC9999</span>
                <span className="text-xs text-slate-500">5 min ago</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
