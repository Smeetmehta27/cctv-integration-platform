'use client';
import { Bell, UserCircle } from 'lucide-react';
import { useWebSocket } from '@/lib/websocket';

export default function Header() {
  const { isConnected, messages } = useWebSocket();
  const alerts = messages.filter(m => m.event_type === 'ALERT_TRIGGERED');

  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-xs text-slate-400 uppercase tracking-wider">
            {isConnected ? 'System Online' : 'Connecting...'}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-6 text-slate-300">
        <div className="relative cursor-pointer hover:text-white transition-colors">
          <Bell className="w-5 h-5" />
          {alerts.length > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center">
              {alerts.length}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 cursor-pointer hover:text-white transition-colors">
          <UserCircle className="w-6 h-6" />
          <span className="text-sm font-medium">SUPER_ADMIN</span>
        </div>
      </div>
    </header>
  );
}
