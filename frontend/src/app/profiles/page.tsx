"use client";

import { useState, useEffect } from "react";
import { Search, Loader2, User, Phone, Globe, MapPin, X, Terminal, ChevronRight, Activity, ShieldCheck, Database, TrendingUp, Users, BarChart3, AlertCircle, Bookmark, RefreshCw, Trash2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Header from "@/components/Header";

export default function ProfilesPage() {
  const [profiles, setProfiles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchProfiles = () => {
    setLoading(true);
    fetch("http://localhost:8000/api/profiles")
      .then(res => res.json())
      .then(data => {
        setProfiles(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchProfiles();
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-50 selection:bg-blue-500/30">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 md:px-6 py-8 md:py-12">
        <div className="flex flex-col md:flex-row items-center justify-between mb-12 md:mb-16 gap-6">
            <div className="space-y-2 text-center md:text-left">
                <h1 className="text-5xl md:text-6xl font-black tracking-tighter uppercase">Archivos</h1>
                <p className="text-slate-500 font-medium">Bases de datos de inteligencia persistente.</p>
            </div>
            <div className="px-6 py-3 md:px-8 md:py-4 bg-slate-900/40 border border-white/5 rounded-3xl flex items-center gap-4">
                <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[9px] md:text-[10px] font-black uppercase tracking-widest text-slate-400">Archivo Local Seguro</span>
            </div>
        </div>

        {loading ? (
            <div className="flex flex-col items-center justify-center py-40 gap-6">
                <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
                <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-700">Sincronizando Archivos...</p>
            </div>
        ) : profiles.length === 0 ? (
            <div className="py-40 text-center space-y-6 px-4">
                <div className="w-20 h-20 bg-slate-900 border border-white/5 rounded-full flex items-center justify-center mx-auto opacity-20">
                    <Database className="w-10 h-10" />
                </div>
                <h3 className="text-2xl font-black text-slate-700 uppercase">No hay perfiles indexados</h3>
                <p className="text-slate-500 font-medium max-w-sm mx-auto">Realiza una búsqueda profunda para generar un expediente persistente.</p>
            </div>
        ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
                {profiles.map((p) => (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                        key={p.id}
                        onClick={() => window.location.href = `/profiles/${p.id}`}
                        className="p-6 md:p-8 bg-slate-900/40 border border-white/5 rounded-[30px] md:rounded-[40px] hover:bg-slate-900 hover:border-blue-500/30 transition-all cursor-pointer group relative overflow-hidden flex flex-col h-full"
                    >
                        <div className="absolute top-0 left-0 w-1 h-full bg-blue-500/50 group-hover:w-2 transition-all" />
                        
                        <div className="flex items-center justify-between mb-6 md:mb-8">
                            <div className="w-12 h-12 md:w-16 md:h-16 rounded-2xl bg-slate-800 flex items-center justify-center overflow-hidden border border-white/5 shrink-0">
                                {p.data?.photo_url ? (
                                    <img src={p.data.photo_url} alt={p.full_name} className="w-full h-full object-cover" />
                                ) : (
                                    <User className="w-6 h-6 md:w-8 md:h-8 text-blue-400" />
                                )}
                            </div>
                            <span className={`text-[8px] md:text-[9px] font-black uppercase tracking-widest px-3 py-1.5 md:px-4 md:py-2 rounded-full border ${p.data?.risk_score > 50 ? 'border-red-500/30 text-red-500 bg-red-500/5' : 'border-emerald-500/30 text-emerald-500 bg-emerald-500/5'}`}>
                                {p.data?.risk_score > 50 ? 'Alto Riesgo' : 'Validado'}
                            </span>
                        </div>

                        <div className="space-y-2 mb-6 md:mb-8 flex-1">
                            <h3 className="text-2xl md:text-3xl font-black tracking-tight leading-none group-hover:text-blue-500 transition-colors line-clamp-2 uppercase">{p.full_name}</h3>
                            <p className="text-slate-500 font-medium text-xs md:text-sm flex items-center gap-2 truncate">
                                <Bookmark className="w-3 h-3 shrink-0" />
                                {p.query}
                            </p>
                        </div>

                        <div className="flex flex-wrap gap-2 mb-6">
                            {p.data?.digital_footprint?.slice(0, 3).map((sm: any, i: number) => (
                                <span key={i} className="px-3 py-1 bg-slate-800 border border-white/5 rounded-full text-[8px] md:text-[9px] font-bold text-slate-400 uppercase">{sm.platform}</span>
                            ))}
                            {p.data?.digital_footprint?.length > 3 && <span className="text-[8px] md:text-[9px] text-slate-600 font-black">+{p.data.digital_footprint.length - 3}</span>}
                        </div>

                        <div className="mt-auto pt-6 md:pt-8 border-t border-white/5 flex items-center justify-between">
                            <span className="text-[8px] md:text-[9px] font-black uppercase tracking-widest text-slate-700">Actualizado: {new Date(p.updated_at).toLocaleDateString()}</span>
                            <ChevronRight className="w-4 h-4 text-slate-700 group-hover:text-blue-500 group-hover:translate-x-1 transition-all" />
                        </div>
                    </motion.div>
                ))}
            </div>
        )}
      </main>
    </div>
  );
}
