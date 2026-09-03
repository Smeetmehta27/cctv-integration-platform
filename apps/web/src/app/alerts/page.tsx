"use client";

import { useEffect, useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { useWebSocket } from "@/lib/websocket";

interface AlertData {
  id: string;
  camera_id: string;
  alert_type: string;
  priority: string;
  status: string;
  timestamp: string;
  description: string;
  evidence: {
    track_id?: string;
    plate?: {
      normalized_text?: string;
      confidence?: number;
      raw_text?: string;
    };
    notes?: string;
  };
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [loading, setLoading] = useState(true);
  const { isConnected, messages } = useWebSocket();

  // Fetch initial history
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const data = await api.getAlerts();
        setAlerts(data);
      } catch (e) {
        console.error("Failed to fetch alerts", e);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  // Connect WebSocket for live alerts
  useEffect(() => {
    if (messages.length === 0) return;
    const lastMessage = messages[messages.length - 1];
    
    if (lastMessage.event_type === "ALERT_TRIGGERED") {
      if (!lastMessage.payload || !lastMessage.camera_id) return;
      
      const payload = lastMessage.payload;
      const newAlert: AlertData = {
        id: typeof payload.alert_id === "string" ? payload.alert_id : "unknown-id",
        camera_id: lastMessage.camera_id,
        alert_type: "WATCHLIST_MATCH",
        priority: typeof payload.priority === "string" ? payload.priority : "HIGH",
        status: "NEW",
        timestamp: lastMessage.timestamp || new Date().toISOString(),
        description: typeof payload.description === "string" ? payload.description : "Alert Triggered",
        evidence: typeof payload.evidence === "object" && payload.evidence !== null ? (payload.evidence as AlertData["evidence"]) : {}
      };
      
      setAlerts((prev) => {
        if (prev.some(a => a.id === newAlert.id)) return prev;
        return [newAlert, ...prev];
      });
    }
  }, [messages]);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-red-500 mb-2">Active Alerts</h1>
          <p className="text-slate-400">Command Center real-time watchlist matches and security alerts.</p>
        </div>
        <Badge className="bg-red-500/20 text-red-400 border border-red-500/50 px-4 py-1 text-sm font-bold">
          LIVE
        </Badge>
      </div>

      <div className="rounded-md border border-slate-800 bg-slate-900/50 backdrop-blur-md">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-slate-800/50">
              <TableHead className="text-slate-400">Time</TableHead>
              <TableHead className="text-slate-400">Severity</TableHead>
              <TableHead className="text-slate-400">Camera</TableHead>
              <TableHead className="text-slate-400">Description</TableHead>
              <TableHead className="text-slate-400">Evidence</TableHead>
              <TableHead className="text-slate-400 text-right">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {alerts.length === 0 && !loading && (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-slate-500 py-12">
                  No active alerts.
                </TableCell>
              </TableRow>
            )}
            {alerts.map((a) => (
              <TableRow key={a.id} className="border-slate-800 hover:bg-slate-800/50 group">
                <TableCell className="font-mono text-slate-400 whitespace-nowrap">
                  {new Date(a.timestamp).toLocaleTimeString()}
                </TableCell>
                <TableCell>
                  <Badge variant="outline" className={
                    a.priority === 'HIGH' ? "border-red-500/50 text-red-400 bg-red-500/10 font-bold" :
                    "border-amber-500/50 text-amber-400 bg-amber-500/10 font-bold"
                  }>
                    {a.priority}
                  </Badge>
                </TableCell>
                <TableCell className="font-mono text-slate-300">{a.camera_id}</TableCell>
                <TableCell className="text-slate-200">{a.description}</TableCell>
                <TableCell>
                  {a.evidence?.plate?.normalized_text && (
                    <Badge variant="outline" className="border-yellow-500/50 text-yellow-400 bg-yellow-500/10 font-mono font-bold text-sm">
                      {a.evidence.plate.normalized_text}
                    </Badge>
                  )}
                  {a.evidence?.notes && (
                    <p className="text-xs text-slate-500 mt-1 max-w-[200px] truncate" title={a.evidence.notes}>
                      {a.evidence.notes}
                    </p>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <Badge className="bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 cursor-pointer">
                    {a.status}
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
