'use client';

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-defaulticon-compatibility';
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css';
import CameraDetailDrawer from './CameraDetailDrawer';
import { Filter } from 'lucide-react';

const createCustomIcon = (status: string, hasAlert: boolean) => {
  let bgColor = 'bg-slate-500';
  
  if (status === 'ONLINE') bgColor = 'bg-emerald-500';
  else if (status === 'DEGRADED') bgColor = 'bg-amber-500';
  else if (status === 'OFFLINE') bgColor = 'bg-red-500';

  const pulseHtml = hasAlert ? `<div class="absolute -inset-2 rounded-full ${bgColor} opacity-50 animate-ping"></div>` : '';

  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: `
      <div class="relative flex items-center justify-center w-6 h-6">
        ${pulseHtml}
        <div class="relative w-4 h-4 rounded-full ${bgColor} border-2 border-white shadow-lg"></div>
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });
};

interface Camera {
  id: string;
  name: string;
  department?: string;
  location: { lat: number; lng: number };
  status: string;
  stream_url?: string;
}

export default function GujaratCCTVMap() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/cameras')
      .then(res => res.json())
      .then(data => setCameras(data))
      .catch(err => console.error("Failed to load cameras", err));
  }, []);

  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
      <div className="absolute top-4 left-4 z-[400] flex gap-2">
        <div className="bg-slate-900/90 backdrop-blur border border-slate-700 p-2 rounded-lg flex items-center gap-2 shadow-lg text-sm text-slate-200">
          <Filter className="w-4 h-4 text-slate-400" />
          <select className="bg-transparent outline-none focus:ring-0">
            <option>All Departments</option>
            <option>Home Department</option>
            <option>RTO Gujarat</option>
            <option>Food & Civil Supplies</option>
          </select>
        </div>
      </div>
      
      <MapContainer 
        center={[22.2587, 71.1924]} 
        zoom={7} 
        style={{ height: '100%', width: '100%', background: '#0f172a' }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {cameras.map(cam => {
          if (!cam.location?.lat || !cam.location?.lng) return null;
          
          return (
            <Marker 
              key={cam.id} 
              position={[cam.location.lat, cam.location.lng]} 
              icon={createCustomIcon(cam.status, false)}
              eventHandlers={{
                click: () => setSelectedCamera(cam),
              }}
            />
          );
        })}
      </MapContainer>

      <CameraDetailDrawer camera={selectedCamera} onClose={() => setSelectedCamera(null)} />
    </div>
  );
}
