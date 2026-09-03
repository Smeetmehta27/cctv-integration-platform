'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Video, Map as MapIcon, Bell, Car, List, Shield, Activity } from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();
  const links = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Live Cameras', href: '/cameras', icon: Video },
    { name: 'GIS Map', href: '/map', icon: MapIcon },
    { name: 'Alerts', href: '/alerts', icon: Bell },
    { name: 'Vehicle Tracking', href: '/tracking', icon: Car },
    { name: 'Watchlists', href: '/watchlists', icon: List },
    { name: 'Camera Registry', href: '/registry', icon: Shield },
    { name: 'System Health', href: '/health', icon: Activity },
  ];

  return (
    <div className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex flex-col h-full">
      <div className="p-6 border-b border-slate-800">
        <h1 className="text-xl font-bold text-white tracking-widest flex items-center gap-2">
          <Shield className="w-6 h-6 text-blue-500" />
          VIGILIS
        </h1>
        <p className="text-xs text-slate-500 mt-1 uppercase tracking-wider">Command Center</p>
      </div>
      <nav className="flex-1 py-4">
        <ul className="space-y-1 px-3">
          {links.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <li key={link.name}>
                <Link 
                  href={link.href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${isActive ? 'bg-blue-500/10 text-blue-500 font-semibold' : 'hover:bg-slate-800 hover:text-white'}`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-blue-500' : 'text-slate-400'}`} />
                  <span className={isActive ? 'text-blue-500' : 'text-sm font-medium'}>{link.name}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
        VIGILIS OS v1.0
      </div>
    </div>
  );
}
