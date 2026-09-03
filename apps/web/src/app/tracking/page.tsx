"use client";

import { useEffect, useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { fetchAPI } from "@/lib/api";

interface Track {
  camera_id: string;
  track_id: number;
  class_name: string;
  confidence: number;
  bbox: { x1: number, y1: number, x2: number, y2: number };
  image_plane_velocity: number;
  plate?: { normalized_text: string, confidence: number };
}

export default function TrackingPage() {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTracks = async () => {
      try {
        const data = await fetchAPI("/tracks");
        setTracks(data.tracks || []);
      } catch (e) {
        console.error("Failed to fetch tracks", e);
      } finally {
        setLoading(false);
      }
    };

    fetchTracks();
    const interval = setInterval(fetchTracks, 1000); // Poll every second for live updates
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Live Vehicle Tracking</h1>
        <p className="text-slate-400">Real-time object multi-tracking across all active camera streams.</p>
      </div>

      <div className="rounded-md border border-slate-800 bg-slate-900/50 backdrop-blur-md">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-slate-800/50">
              <TableHead className="text-slate-400">Camera</TableHead>
              <TableHead className="text-slate-400">Track ID</TableHead>
              <TableHead className="text-slate-400">Vehicle Type</TableHead>
              <TableHead className="text-slate-400">License Plate</TableHead>
              <TableHead className="text-slate-400">Img Velocity (px/s)</TableHead>
              <TableHead className="text-slate-400">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tracks.length === 0 && !loading && (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-slate-500 py-8">
                  NO HISTORICAL DATA / NO ACTIVE TRACKS
                </TableCell>
              </TableRow>
            )}
            {tracks.map((t, idx) => (
              <TableRow key={`${t.camera_id}-${t.track_id}-${idx}`} className="border-slate-800 hover:bg-slate-800/50">
                <TableCell className="font-mono text-slate-300">{t.camera_id}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="border-blue-500/30 text-blue-400 bg-blue-500/10">
                    #{t.track_id}
                  </Badge>
                </TableCell>
                <TableCell className="uppercase text-slate-300">
                  {t.class_name} <span className="text-slate-500 text-xs ml-1">{(t.confidence * 100).toFixed(0)}%</span>
                </TableCell>
                <TableCell className="font-mono font-bold text-yellow-400">
                  {t.plate?.normalized_text ? (
                    <span>
                      {t.plate.normalized_text} <span className="text-slate-500 text-xs ml-1 font-sans font-normal">{((t.plate.confidence || 0) * 100).toFixed(0)}%</span>
                    </span>
                  ) : (
                    <span className="text-slate-600 font-sans font-normal">Detecting...</span>
                  )}
                </TableCell>
                <TableCell className="font-mono text-slate-400">{t.image_plane_velocity > 0 ? t.image_plane_velocity.toFixed(1) : '-'}</TableCell>
                <TableCell>
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-none hover:bg-emerald-500/30">
                    ACTIVE
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
