import AlertFeed from '@/components/alerts/AlertFeed';
import { BellRing } from 'lucide-react';

export default function AlertsPage() {
  return (
    <div className="w-full h-full flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <BellRing className="w-6 h-6 text-blue-500" />
            Operations Center
          </h1>
          <p className="text-slate-400">Real-time alert telemetry and incident response hub</p>
        </div>
      </div>
      
      <div className="flex-1 min-h-0">
        <AlertFeed />
      </div>
    </div>
  );
}
