"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { Activity, Menu, X } from "lucide-react";

export default function Header() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-[100]">
      <div className="max-w-7xl mx-auto px-4 md:px-6 h-20 flex items-center justify-between">
        <div 
          className="flex items-center gap-3 group cursor-pointer" 
          onClick={() => window.location.href = '/'}
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 via-blue-500 to-emerald-500 flex items-center justify-center font-black shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform duration-500">K</div>
          <div className="flex flex-col text-left">
            <span className="font-black text-xl tracking-tighter leading-none group-hover:text-blue-400 transition-colors uppercase">Kuarahy</span>
            <div className="flex items-center gap-2">
                <span className="text-[9px] font-black text-slate-500 tracking-[0.2em] uppercase">Intelligence Platform</span>
                <div className="w-1 h-1 rounded-full bg-emerald-500 animate-pulse" />
            </div>
          </div>
        </div>
        
        {/* Desktop Nav */}
        <nav className="hidden md:flex gap-10 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 relative">
          <a href="/" className="hover:text-white transition-all relative py-2 group">
            Buscador
            <div className="absolute bottom-0 left-0 w-0 h-[2px] bg-blue-500 group-hover:w-full transition-all duration-500" />
          </a>
          <a href="/profiles" className="hover:text-white transition-all relative py-2 group">
            Perfiles
            <div className="absolute bottom-0 left-0 w-0 h-[2px] bg-blue-500 group-hover:w-full transition-all duration-500" />
          </a>
          <a href="/dashboard" className="hover:text-white transition-all relative py-2 group">
            Métricas
            <div className="absolute bottom-0 left-0 w-0 h-[2px] bg-blue-500 group-hover:w-full transition-all duration-500" />
          </a>
        </nav>

        <div className="hidden md:flex items-center gap-4">
             <div className="flex flex-col items-end">
                <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest text-right">Engine Status</span>
                <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-tighter">v4.0 Online</span>
             </div>
             <div className="w-10 h-10 rounded-full border border-white/5 bg-white/5 flex items-center justify-center">
                <Activity className="w-4 h-4 text-blue-500 animate-pulse" />
             </div>
        </div>

        {/* Mobile Menu Button */}
        <button onClick={() => setIsOpen(!isOpen)} className="md:hidden p-2 text-slate-400 hover:text-white transition-colors">
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Nav */}
      <AnimatePresence>
        {isOpen && (
            <motion.div 
                initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
                className="md:hidden bg-slate-900 border-b border-white/10 overflow-hidden"
            >
                <div className="flex flex-col p-6 gap-6 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
                    <a href="/" className="hover:text-white">Buscador</a>
                    <a href="/profiles" className="hover:text-white">Perfiles</a>
                    <a href="/dashboard" className="hover:text-white">Métricas</a>
                </div>
            </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
