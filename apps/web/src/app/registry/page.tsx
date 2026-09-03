'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface Camera {
  id: string;
  name: string;
  status: string;
}

export default function RegistryPage() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function loadCameras() {
      try {
        const data = await api.getCameras();
        setCameras(data);
      } catch (e) {
        console.error("Failed to load cameras", e);
        setError(true);
      } finally {
        setLoading(false);
      }
    }
    loadCameras();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Camera Registry</h1>
        <p className="text-slate-400">Manage all registered surveillance cameras and endpoints.</p>
      </div>

      <div className="rounded-md border border-slate-800 bg-slate-900/50 backdrop-blur-md">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-slate-800/50">
              <TableHead className="text-slate-400">Name</TableHead>
              <TableHead className="text-slate-400">Status</TableHead>
              <TableHead className="text-slate-400 font-mono text-right">ID</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading && (
              <TableRow>
                <TableCell colSpan={3} className="text-center text-slate-500 py-12">
                  Loading cameras...
                </TableCell>
              </TableRow>
            )}
            {!loading && error && (
              <TableRow>
                <TableCell colSpan={3} className="text-center text-red-500 py-12">
                  Failed to load camera registry. Please check backend connection.
                </TableCell>
              </TableRow>
            )}
            {!loading && !error && cameras.length === 0 && (
              <TableRow>
                <TableCell colSpan={3} className="text-center text-slate-500 py-12">
                  No cameras registered.
                </TableCell>
              </TableRow>
            )}
            {!loading && !error && cameras.map((c) => (
              <TableRow key={c.id} className="border-slate-800 hover:bg-slate-800/50">
                <TableCell className="font-medium text-white">{c.name}</TableCell>
                <TableCell>
                  <Badge variant="outline" className={
                    c.status === 'ONLINE' ? "border-green-500/50 text-green-400 bg-green-500/10" : "border-red-500/50 text-red-400 bg-red-500/10"
                  }>
                    {c.status}
                  </Badge>
                </TableCell>
                <TableCell className="font-mono text-slate-500 text-xs text-right">{c.id}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
