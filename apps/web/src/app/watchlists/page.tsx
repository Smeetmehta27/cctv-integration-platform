'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface Watchlist {
  id: string;
  name: string;
  category: string;
  description: string;
}

export default function WatchlistsPage() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function loadWatchlists() {
      try {
        const data = await api.getWatchlists();
        setWatchlists(data);
      } catch (e) {
        console.error("Failed to load watchlists", e);
        setError(true);
      } finally {
        setLoading(false);
      }
    }
    loadWatchlists();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Watchlists</h1>
        <p className="text-slate-400">Manage surveillance watchlists and tracked entities.</p>
      </div>

      <div className="rounded-md border border-slate-800 bg-slate-900/50 backdrop-blur-md">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-slate-800/50">
              <TableHead className="text-slate-400">Name</TableHead>
              <TableHead className="text-slate-400">Category</TableHead>
              <TableHead className="text-slate-400">Description</TableHead>
              <TableHead className="text-slate-400 font-mono text-right">ID</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading && (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-slate-500 py-12">
                  Loading watchlists...
                </TableCell>
              </TableRow>
            )}
            {!loading && error && (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-red-500 py-12">
                  Failed to load watchlists. Please check backend connection.
                </TableCell>
              </TableRow>
            )}
            {!loading && !error && watchlists.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-slate-500 py-12">
                  No watchlists configured.
                </TableCell>
              </TableRow>
            )}
            {!loading && !error && watchlists.map((w) => (
              <TableRow key={w.id} className="border-slate-800 hover:bg-slate-800/50">
                <TableCell className="font-medium text-white">{w.name}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="border-blue-500/50 text-blue-400 bg-blue-500/10">
                    {w.category}
                  </Badge>
                </TableCell>
                <TableCell className="text-slate-300">{w.description}</TableCell>
                <TableCell className="font-mono text-slate-500 text-xs text-right">{w.id}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
