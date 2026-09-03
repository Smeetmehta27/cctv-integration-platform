export default function MapPage() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">GIS Map</h1>
        <p className="text-slate-400">Interactive geographic visualization of assets and events.</p>
      </div>
      <div className="flex flex-col items-center justify-center h-96 border border-slate-800 bg-slate-900/50 rounded-lg text-slate-500 p-8 text-center">
        <h2 className="text-xl font-medium text-slate-300 mb-2">Module coming in Phase 3</h2>
        <p className="max-w-md">
          GIS mapping requires camera and track geolocation data which is currently not exposed by the production API. This visualization will be enabled in Phase 3.
        </p>
      </div>
    </div>
  );
}
