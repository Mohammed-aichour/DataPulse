import React from "react";
import { Menu, BookOpen, Sparkles, ExternalLink } from "lucide-react";
import { API_BASE_URL } from "../services/api";

interface NavbarProps {
  onToggleSidebar: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  return (
    <header className="sticky top-0 z-30 h-16 bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          aria-label="Open menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-slate-800 tracking-tight hidden sm:inline">
            Smart Campus Intelligence
          </span>
          <span className="text-slate-300 hidden sm:inline">•</span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200/60">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Live DB Connected
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <a
          href={`${API_BASE_URL}/docs`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 hover:text-indigo-600 hover:bg-slate-100 rounded-lg transition-colors border border-slate-200"
        >
          <BookOpen className="h-3.5 w-3.5" />
          <span>Swagger API</span>
          <ExternalLink className="h-3 w-3 text-slate-400" />
        </a>

        <div className="hidden md:flex items-center gap-2 pl-3 border-l border-slate-200">
          <div className="h-8 w-8 rounded-full bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700 font-bold text-xs">
            UIA
          </div>
          <div className="text-left leading-none">
            <p className="text-xs font-semibold text-slate-800">Mohamed</p>
            <p className="text-[10px] text-slate-500 font-medium">Computer Engineering</p>
          </div>
        </div>
      </div>
    </header>
  );
};
