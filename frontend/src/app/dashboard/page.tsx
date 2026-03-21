"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { TrendingUp, Users, Search, Activity, BarChart3, PieChart, Info, Database } from "lucide-react";
import Header from "@/components/Header";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState({
    total_profiles: 0,
    total_social_accounts: 0,
    total_emails_leaked: 0,
    total_news_mentions: 0,
    high_risk_profiles: 0
  });

  useEffect(() => {
    fetch("http://localhost:8000/api/metrics")
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(console.error);
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-50">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-12">
        <div className="flex items-center justify-between mb-12">
            <div>
                <h1 className="text-4xl font-extrabold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
                    Métricas de Inteligencia
                </h1>
                <p className="text-slate-400">Actividad del sistema y KPIs de investigación.</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-bold uppercase tracking-widest text-slate-500">
                <span className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> Backend Online</span>
                <span className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" /> LLM Ready</span>
            </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <div className="p-6 bg-slate-900/40 border border-white/5 rounded-3xl backdrop-blur-md">
                <Database className="w-8 h-8 text-blue-400 mb-4" />
                <h3 className="text-3xl font-black">{metrics.total_profiles}</h3>
                <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Perfiles Base</p>
            </div>
            <div className="p-6 bg-slate-900/40 border border-white/5 rounded-3xl backdrop-blur-md">
                <Users className="w-8 h-8 text-emerald-400 mb-4" />
                <h3 className="text-3xl font-black">{metrics.total_social_accounts}</h3>
                <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Cuentas Sociales</p>
            </div>
            <div className="p-6 bg-slate-900/40 border border-white/5 rounded-3xl backdrop-blur-md">
                <TrendingUp className="w-8 h-8 text-purple-400 mb-4" />
                <h3 className="text-3xl font-black">{metrics.total_emails_leaked}</h3>
                <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Emails Leakeados</p>
            </div>
            <div className="p-6 bg-slate-900/40 border border-white/5 rounded-3xl backdrop-blur-md">
                <BarChart3 className="w-8 h-8 text-red-400 mb-4" />
                <h3 className="text-3xl font-black">{metrics.high_risk_profiles}</h3>
                <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Perfiles Alto Riesgo</p>
            </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="p-8 bg-slate-900/60 border border-white/5 rounded-[48px] shadow-2xl overflow-hidden relative group">
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-700">
                    <PieChart className="w-40 h-40" />
                </div>
                <h2 className="text-xl font-bold mb-8 tracking-tight uppercase tracking-widest text-slate-400 text-sm">Distribución de Fuentes</h2>
                <div className="space-y-6 relative z-10">
                    {[
                        { label: "Bases de Datos Públicas (PY)", val: 45, color: "bg-emerald-500" },
                        { label: "Redes Sociales (OSINT)", val: 35, color: "bg-blue-500" },
                        { label: "Brechas de Datos / Dark Web", val: 15, color: "bg-red-500" },
                        { label: "Otros", val: 5, color: "bg-slate-700" }
                    ].map((item) => (
                        <div key={item.label} className="space-y-2">
                            <div className="flex justify-between text-xs font-bold uppercase tracking-wider">
                                <span className="text-slate-300">{item.label}</span>
                                <span className="text-slate-500">{item.val}%</span>
                            </div>
                            <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                                <motion.div 
                                    initial={{ width: 0 }}
                                    animate={{ width: `${item.val}%` }}
                                    transition={{ duration: 1.5, ease: "easeOut" }}
                                    className={`h-full ${item.color}`}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="p-8 bg-slate-900/60 border border-white/5 rounded-[48px] shadow-2xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-700">
                    <Activity className="w-40 h-40" />
                </div>
                <h2 className="text-xl font-bold mb-8 tracking-tight uppercase tracking-widest text-slate-400 text-sm">Carga del Procesador (LLM)</h2>
                <div className="flex flex-col justify-center items-center h-48 gap-4 relative z-10">
                    <div className="w-full max-w-sm p-6 bg-slate-800/40 rounded-3xl border border-white/5 text-center">
                        <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Status Gemini 1.5 Flash</p>
                        <p className="text-2xl font-black text-emerald-400">OPTIMIZADO</p>
                    </div>
                    <div className="flex gap-2">
                        {[1, 2, 3, 4, 5, 2, 3, 4, 6, 2].map((h, i) => (
                            <motion.div 
                                key={i}
                                initial={{ height: 0 }}
                                animate={{ height: h * 8 }}
                                transition={{ repeat: Infinity, duration: 1, repeatType: "reverse", delay: i * 0.1 }}
                                className="w-2 bg-blue-500/50 rounded-full"
                            />
                        ))}
                    </div>
                </div>
                <div className="mt-8 p-4 bg-blue-500/5 rounded-2xl border border-blue-500/10 flex items-start gap-3">
                    <Info className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                    <p className="text-[10px] text-slate-400 leading-relaxed">
                        El sistema está operando dentro de los límites del Free Tier. Se extrajeron {metrics.total_news_mentions} menciones en noticias para su consolidación inteligente.
                    </p>
                </div>
            </div>
        </div>
      </main>
    </div>
  );
}
