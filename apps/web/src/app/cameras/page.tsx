'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { HlsPlayer } from '@/components/HlsPlayer';

interface Camera {
  id: string;
  name: string;
  status: string;
  stream_url?: string;
}

export default function Cameras() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCameras().then(setCameras).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white tracking-wide">Live Cameras</h1>
      {loading ? (
        <div className="text-slate-500">Loading cameras...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.map((cam) => (
            <div key={cam.id} className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
              <div className="aspect-video bg-black flex items-center justify-center border-b border-slate-800 relative overflow-hidden">
                {cam.stream_url ? (
                  cam.stream_url.includes('.m3u8') ? (
                    <HlsPlayer 
                      src={cam.stream_url} 
                      className="absolute top-0 left-0 w-full h-full"
                    />
                  ) : (
                    <>
                      <img 
                        src={cam.stream_url} 
                        alt={cam.name} 
                        className="w-full h-full object-cover z-10" 
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                          if (e.currentTarget.nextElementSibling) {
                            e.currentTarget.nextElementSibling.classList.remove('hidden');
                          }
                        }}
                      />
                      <span className="text-slate-600 text-sm tracking-widest hidden absolute">NO SIGNAL</span>
                    </>
                  )
                ) : (
                  <span className="text-slate-600 text-sm tracking-widest">NO SIGNAL</span>
                )}
              </div>
              <div className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-white font-medium">{cam.name}</h3>
                    <p className="text-xs text-slate-500 mt-1">{cam.id}</p>
                  </div>
                  <div className={`px-2 py-1 text-[10px] font-bold rounded ${cam.status === 'ONLINE' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                    {cam.status}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
