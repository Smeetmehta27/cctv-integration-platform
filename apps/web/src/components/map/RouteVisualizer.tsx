'use client';

import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Play, Pause, Download, MapPin, Navigation, Clock, Activity } from 'lucide-react';
import { format } from 'date-fns';

function ChangeView({ bounds }: { bounds: L.LatLngBoundsExpression }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) map.fitBounds(bounds, { padding: [50, 50] });
  }, [bounds, map]);
  return null;
}

const customIcon = L.divIcon({
  className: 'custom-leaflet-icon',
  html: `<div class="w-4 h-4 rounded-full bg-blue-500 border-2 border-white shadow-lg"></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8]
});

const vehicleIcon = L.divIcon({
  className: 'custom-leaflet-icon',
  html: `
    <div class="relative w-6 h-6">
      <div class="absolute -inset-2 rounded-full bg-emerald-500 opacity-50 animate-ping"></div>
      <div class="relative w-6 h-6 rounded-full bg-emerald-500 border-2 border-white shadow-xl flex items-center justify-center">
        <div class="w-2 h-2 bg-white rounded-full"></div>
      </div>
    </div>
  `,
  iconSize: [24, 24],
  iconAnchor: [12, 12]
});

interface Waypoint {
  camera_id: string;
  camera_name: string;
  district: string;
  latitude: number;
  longitude: number;
  entry_time: string;
  speed_from_prev: number;
}

interface TrajectoryData {
  summary: {
    total_distance_km: number;
    total_transit_time_minutes: number;
    cameras_passed_count: number;
    average_speed_kmh: number;
  };
  waypoints: Waypoint[];
}

export default function RouteVisualizer({ plateNumber }: { plateNumber: string }) {
  const [data, setData] = useState<TrajectoryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [playbackIdx, setPlaybackIdx] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!plateNumber) return;
    setLoading(true);
    fetch('http://localhost:8000/api/v1/tracking/route', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plate_number: plateNumber })
    })
      .then(r => r.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  }, [plateNumber]);

  useEffect(() => {
    let interval: any;
    if (isPlaying && data?.waypoints && playbackIdx < data.waypoints.length - 1) {
      interval = setInterval(() => {
        setPlaybackIdx(prev => prev + 1);
      }, 2000);
    } else if (playbackIdx >= (data?.waypoints?.length || 1) - 1) {
      setIsPlaying(false);
    }
    return () => clearInterval(interval);
  }, [isPlaying, playbackIdx, data]);

  const handleDownload = () => {
    window.open(`http://localhost:8000/api/v1/reports/export?format=pdf&plate_number=${plateNumber}`, '_blank');
  };

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-900 rounded-xl border border-slate-800">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!data || !data.waypoints || data.waypoints.length === 0) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-slate-900/50 rounded-xl border border-slate-800 text-slate-400 p-8 text-center">
        <Navigation className="w-12 h-12 mb-4 opacity-20" />
        <p className="text-lg font-medium">No tracking data found for "{plateNumber}"</p>
        <p className="text-sm mt-2 opacity-60">The vehicle may not have passed through our network or OCR was inconclusive.</p>
      </div>
    );
  }

  const positions: [number, number][] = data.waypoints.map(w => [w.latitude, w.longitude]);
  const bounds = L.latLngBounds(positions);
  const currentWp = data.waypoints[playbackIdx];

  return (
    <div className="flex h-full gap-4">
      <div className="flex-1 relative rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-900">
        <MapContainer 
          zoom={7} 
          style={{ height: '100%', width: '100%', background: '#0f172a' }}
          zoomControl={false}
        >
          <ChangeView bounds={bounds} />
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; CARTO'
          />
          
          <Polyline 
            positions={positions} 
            color="#3b82f6" 
            weight={4} 
            opacity={0.6}
            dashArray="10, 10" 
            className="animate-pulse"
          />
          
          {data.waypoints.map((wp, i) => (
            <Marker key={i} position={[wp.latitude, wp.longitude]} icon={customIcon}>
              <Popup className="custom-popup">
                <div className="text-slate-800 font-semibold">{wp.camera_name}</div>
                <div className="text-xs text-slate-500">{format(new Date(wp.entry_time), 'PPp')}</div>
              </Popup>
            </Marker>
          ))}

          <Marker position={[currentWp.latitude, currentWp.longitude]} icon={vehicleIcon} />
        </MapContainer>

        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-[400] bg-slate-900/90 backdrop-blur border border-slate-700 p-3 rounded-full flex items-center gap-4 shadow-2xl">
          <button 
            onClick={() => {
              if (playbackIdx >= data.waypoints.length - 1) setPlaybackIdx(0);
              setIsPlaying(!isPlaying);
            }}
            className="w-10 h-10 bg-blue-600 hover:bg-blue-500 rounded-full flex items-center justify-center text-white transition-colors shadow-lg"
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-1" />}
          </button>
          <div className="flex-1 min-w-[200px]">
            <input 
              type="range" 
              min={0} 
              max={data.waypoints.length - 1} 
              value={playbackIdx}
              onChange={(e) => {
                setPlaybackIdx(parseInt(e.target.value));
                setIsPlaying(false);
              }}
              className="w-full accent-blue-500"
            />
          </div>
          <div className="text-xs font-medium text-slate-300 w-16 text-center">
            {playbackIdx + 1} / {data.waypoints.length}
          </div>
        </div>
      </div>

      <div className="w-96 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl flex flex-col overflow-hidden">
        <div className="p-5 border-b border-slate-800 bg-slate-950/50">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Navigation className="w-5 h-5 text-blue-500" />
            Route Journey
          </h2>
          <p className="text-sm text-slate-400 mt-1">Vehicle: <span className="font-mono text-emerald-400 font-bold">{plateNumber}</span></p>
        </div>
        
        <div className="p-4 grid grid-cols-2 gap-3 border-b border-slate-800">
          <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs text-slate-500 flex items-center gap-1"><MapPin className="w-3 h-3"/> Distance</div>
            <div className="text-lg font-bold text-slate-200 mt-1">{data.summary.total_distance_km} <span className="text-xs font-normal text-slate-400">km</span></div>
          </div>
          <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs text-slate-500 flex items-center gap-1"><Activity className="w-3 h-3"/> Avg Speed</div>
            <div className="text-lg font-bold text-slate-200 mt-1">{data.summary.average_speed_kmh} <span className="text-xs font-normal text-slate-400">km/h</span></div>
          </div>
          <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs text-slate-500 flex items-center gap-1"><Clock className="w-3 h-3"/> Time</div>
            <div className="text-lg font-bold text-slate-200 mt-1">{data.summary.total_transit_time_minutes} <span className="text-xs font-normal text-slate-400">min</span></div>
          </div>
          <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs text-slate-500 flex items-center gap-1"><Activity className="w-3 h-3"/> Nodes</div>
            <div className="text-lg font-bold text-slate-200 mt-1">{data.summary.cameras_passed_count}</div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="relative border-l-2 border-slate-700 ml-3 space-y-6 pb-4">
            {data.waypoints.map((wp, i) => (
              <div key={i} className="relative pl-6">
                <div className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 border-slate-900 ${i === playbackIdx ? 'bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)]' : 'bg-slate-500'}`} />
                
                <div className="mb-1 text-xs font-medium text-blue-400">
                  {format(new Date(wp.entry_time), 'MMM d, HH:mm:ss')}
                </div>
                <div className="font-semibold text-slate-200">{wp.camera_name}</div>
                <div className="text-xs text-slate-500 mt-0.5">{wp.district}</div>
                
                {i > 0 && wp.speed_from_prev > 0 && (
                  <div className="mt-2 text-xs font-medium bg-slate-800 inline-block px-2 py-1 rounded text-slate-300 border border-slate-700">
                    <Activity className="w-3 h-3 inline mr-1 opacity-70" />
                    {wp.speed_from_prev} km/h from previous
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
        
        <div className="p-4 border-t border-slate-800 bg-slate-950/50">
          <button 
            onClick={handleDownload}
            className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors border border-slate-700 shadow-sm"
          >
            <Download className="w-4 h-4" /> Download Audit Report
          </button>
        </div>
      </div>
    </div>
  );
}
