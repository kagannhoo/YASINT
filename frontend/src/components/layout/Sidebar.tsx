"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  PlusCircle,
  History,
  Settings,
  Shield,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/analysis/new", label: "Yeni Analiz", icon: PlusCircle },
  { href: "/history", label: "Geçmiş", icon: History },
  { href: "#", label: "Ayarlar", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-bg-secondary border-r border-border flex flex-col z-50">
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-2">
          <Shield className="w-7 h-7 text-accent" />
          <div>
            <h1 className="font-display font-bold text-lg text-text-primary">
              YASINT
            </h1>
            <p className="text-xs text-text-secondary">Yet Another OSINT</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors",
                active
                  ? "bg-accent-dim text-accent"
                  : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary"
              )}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border space-y-1">
        <p className="text-xs text-text-secondary">v1.0.0</p>
        <a
          href="https://github.com/kagannhoo/YASINT/blob/master/KAYNAKCA.md"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-accent hover:underline block"
        >
          Kaynakça
        </a>
        <a
          href="https://github.com/kagannhoo"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-text-secondary hover:text-text-primary block"
        >
          @kagannhoo
        </a>
      </div>
    </aside>
  );
}
