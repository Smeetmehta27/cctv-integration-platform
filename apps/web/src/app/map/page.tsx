'use client';
import dynamic from 'next/dynamic';

const DynamicMap = dynamic(() => import('@/components/map/GujaratCCTVMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-slate-900 rounded-xl border border-slate-800">
      <div className="flex flex-col items-center gap-4">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400 font-medium">Loading Statewide Mapping Engine...</p>
      </div>
    </div>
  )
});

export default function MapPage() {
  return (
    <div className="w-full h-full flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Statewide GIS Intelligence</h1>
          <p className="text-slate-400">Live geographic distribution of state CCTV assets</p>
        </div>
      </div>
      
      <div className="flex-1 min-h-0">
        <DynamicMap />
      </div>
    </div>
  );
}
