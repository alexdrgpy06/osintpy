"use client";

import { useState, useEffect, useRef } from "react";
import { 
  Search, Loader2, User, Phone, Globe, MapPin, X, Terminal, 
  ChevronRight, ChevronLeft, Activity, ShieldCheck, Database, 
  TrendingUp, Users, BarChart3, AlertCircle, Network, Briefcase, 
  Mail, Download, RefreshCw, Eye, Image as ImageIcon, Shield, 
  Zap, AlertTriangle, ExternalLink, PhoneCall, Trash2, Plus, 
  Edit3, Send, CheckCircle2, ArrowRight, Smartphone 
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Header from "@/components/Header";

// Link Analysis Graph Component (SVG based)
const LinkAnalysisGraph = ({ graph }: { graph: any }) => {
  if (!graph || !graph.nodes || graph.nodes.length === 0) return null;

  const targetNode = graph.nodes.find((n: any) => n.type === 'Target');
  const otherNodes = graph.nodes.filter((n: any) => n.type !== 'Target');
  
  const centerX = 400;
  const centerY = 300;
  const radius = 200;

  return (
    <div className="relative w-full overflow-x-auto custom-scrollbar bg-black/40 border border-white/5 rounded-3xl p-4 flex justify-center items-center h-[600px]">
      <div className="absolute top-4 left-6 z-10">
        <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 mb-2 flex items-center gap-2"><Network className="w-4 h-4 text-blue-500" /> Grafo Relacional</h4>
        <div className="flex gap-4 text-[9px] font-bold text-slate-400">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500"></span> Identidad</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-indigo-500"></span> Digital</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span> Contacto</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500"></span> Riesgo</span>
        </div>
      </div>
      <svg width="800" height="600" viewBox="0 0 800 600" className="opacity-90">
        <defs>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
        
        {/* Draw Edges */}
        {otherNodes.map((n: any, i: number) => {
          const angle = (i / otherNodes.length) * 2 * Math.PI;
          const x = centerX + radius * Math.cos(angle);
          const y = centerY + radius * Math.sin(angle);
          const isThreat = n.group === 'threat';
          return (
            <line key={`edge-${i}`} x1={centerX} y1={centerY} x2={x} y2={y} 
                  stroke={isThreat ? "rgba(239, 68, 68, 0.4)" : "rgba(59, 130, 246, 0.2)"} 
                  strokeWidth="1.5" strokeDasharray={isThreat ? "4,4" : "none"} />
          );
        })}

        {/* Draw Target Node Center */}
        {targetNode && (
          <g transform={`translate(${centerX}, ${centerY})`}>
            <circle r="45" fill="rgba(30, 58, 138, 0.3)" stroke="#3b82f6" strokeWidth="2" filter="url(#glow)" />
            <circle r="30" fill="#2563eb" />
            <User x="-12" y="-12" width="24" height="24" color="white" />
            <text y="65" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold" className="font-mono">{targetNode.label.slice(0, 15)}</text>
            <text y="80" textAnchor="middle" fill="#94a3b8" fontSize="9" fontWeight="bold" className="font-mono uppercase tracking-widest">Target</text>
          </g>
        )}

        {/* Draw Other Nodes */}
        {otherNodes.map((n: any, i: number) => {
          const angle = (i / otherNodes.length) * 2 * Math.PI;
          const x = centerX + radius * Math.cos(angle);
          const y = centerY + radius * Math.sin(angle);
          
          let color = "#64748b"; // default
          let icon = <Database x="-8" y="-8" width="16" height="16" color="white" />;
          if (n.group === 'social') { color = "#6366f1"; icon = <Globe x="-8" y="-8" width="16" height="16" color="white" />; }
          else if (n.group === 'contact') { color = "#10b981"; icon = <Mail x="-8" y="-8" width="16" height="16" color="white" />; }
          else if (n.group === 'location') { color = "#f59e0b"; icon = <MapPin x="-8" y="-8" width="16" height="16" color="white" />; }
          else if (n.group === 'threat') { color = "#ef4444"; icon = <AlertTriangle x="-8" y="-8" width="16" height="16" color="white" />; }
          else if (n.group === 'fiscal') { color = "#0ea5e9"; icon = <Briefcase x="-8" y="-8" width="16" height="16" color="white" />; }

          return (
            <g key={`node-${i}`} transform={`translate(${x}, ${y})`}>
              <circle r="22" fill={`${color}33`} stroke={color} strokeWidth="1.5" />
              <circle r="14" fill={color} />
              {icon}
              <text y="35" textAnchor="middle" fill="white" fontSize="9" fontWeight="bold" className="font-mono">{n.label.slice(0, 20)}</text>
              {n.sublabel && <text y="48" textAnchor="middle" fill={color} fontSize="8" fontWeight="bold" className="font-mono">{n.sublabel.slice(0,25)}</text>}
            </g>
          );
        })}
      </svg>
    </div>
  );
};

type ViewState = 'search' | 'tactical' | 'dossier' | 'radar';

const SystemStatusBoard = ({ health }: { health: any }) => {
  if (!health) return null;
  return (
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="fixed top-24 right-6 z-50 w-64 bg-black/80 backdrop-blur-2xl border border-white/10 rounded-2xl p-4 shadow-2xl hidden lg:block">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-4 h-4 text-blue-500 animate-pulse" />
        <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-white">System Status Board</h4>
      </div>
      <div className="space-y-3">
        <div>
          <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest block mb-2">APIs Cívicas / OSINT</span>
          <div className="space-y-1.5">
            {Object.entries(health.civic_apis || {}).map(([name, status]: [string, any]) => (
              <div key={name} className="flex justify-between items-center">
                <span className="text-[10px] font-medium text-slate-300">{name}</span>
                <span className={`w-2 h-2 rounded-full ${String(status).includes('ONLINE') ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'}`}></span>
              </div>
            ))}
          </div>
        </div>
        <div className="pt-2 border-t border-white/5">
          <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest block mb-2">Binarios Locales</span>
          <div className="space-y-1.5">
            {Object.entries(health.osint_binaries || {}).map(([name, status]: [string, any]) => (
              <div key={name} className="flex justify-between items-center">
                <span className="text-[10px] font-medium text-slate-300">{name}</span>
                <span className={`w-2 h-2 rounded-full ${String(status).includes('INSTALLED') ? 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]' : 'bg-slate-700'}`}></span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default function DashboardSPA() {
  // View management
  const [view, setView] = useState<ViewState>('search');
  const [targetData, setTargetData] = useState({ 
    ci_ruc: '', 
    nombre: '', 
    alias: '', 
    email: '', 
    telefono: '', 
    notas_adicionales: '' 
  });
  const [health, setHealth] = useState<any>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [discoveredNodes, setDiscoveredNodes] = useState<any[]>([]);
  const [profile, setProfile] = useState<any>(null);
  const [activeTools, setActiveTools] = useState<string[]>([]);
  const [taskStatus, setTaskStatus] = useState<string>("pending");
  const [globalStats, setGlobalStats] = useState({ total_profiles: 0, total_nodes: 0, total_emails: 0, total_phones: 0 });

  const [radarData, setRadarData] = useState<any>(null);
  const logEndRef = useRef<HTMLDivElement>(null);
  const dossierRef = useRef<HTMLDivElement>(null);
  const [isExportingPdf, setIsExportingPdf] = useState(false);

  // Interactive refinement state
  const [isEditing, setIsEditing] = useState(false);
  const [rejectedNodes, setRejectedNodes] = useState<{ value: string }[]>([]);
  const [newSeed, setNewSeed] = useState("");
  const [newSeeds, setNewSeeds] = useState<string[]>([]);
  const [verifiedNodes, setVerifiedNodes] = useState<any[]>([]); 
  const [pivotNode, setPivotNode] = useState<any>(null);

  // Initial health check & stats
  useEffect(() => {
    const init = async () => {
      try {
        const hResp = await fetch('http://localhost:8000/api/health');
        if (hResp.ok) setHealth(await hResp.json());
        
        const sResp = await fetch('http://localhost:8000/api/stats');
        if (sResp.ok) setGlobalStats(await sResp.json());
      } catch (e) { console.error("Initialization failed", e); }
    };
    init();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const hasData = Object.values(targetData).some(val => val.trim() !== '');
    if (!hasData) return;

    setIsSearching(true);
    setView('tactical');
    setTaskId(null);
    setProgress(5);
    setLogs(["[INIT] Despachando motor táctico v10.0..."]);
    
    try {
      const resp = await fetch("http://localhost:8000/api/search", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(targetData)
      });
      const data = await resp.json();
      setTaskId(data.task_id);
    } catch (err) {
      setTaskStatus("failed");
      setLogs(prev => [...prev, "[ERROR] Fallo en la conexión con el motor backend."]);
    } finally {
      setIsSearching(false);
    }
  };

  const executePivot = async () => {
    if (!pivotNode || !taskId) return;
    const value = pivotNode.value || pivotNode.data?.full_name;
    let target = value;
    if (pivotNode.type === 'social' && value.startsWith("http")) {
      target = value.split('/').pop() || value;
    }
    try {
      setLogs(prev => [...prev, `[PIVOT] Lanzando agentes tras nuevo objetivo: ${target}...`]);
      setPivotNode(null);
      const resp = await fetch(`http://localhost:8000/api/search/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId, new_seeds: [target] })
      });
      const data = await resp.json();
      if (data.task_id) {
        setTaskId(data.task_id);
        setProgress(5);
        setTaskStatus("pending");
        setActiveTools(["Omni-Pivot"]);
      }
    } catch (e) { console.error("Pivot error", e); }
  };

  const handleVerify = (node: any) => {
    setVerifiedNodes(prev => {
      const exists = prev.find(n => n.value === node.value);
      if (exists) return prev.filter(n => n.value !== node.value);
      return [...prev, node];
    });
  };

  const handleReject = (value: string) => {
    setRejectedNodes(prev => [...prev, { value }]);
  };

  const handleAddSeed = () => {
    if (newSeed.trim() && !newSeeds.includes(newSeed.trim())) {
      setNewSeeds(prev => [...prev, newSeed.trim()]);
      setNewSeed("");
    }
  };

  const submitCorrections = async () => {
    if (!taskId) return;
    try {
      const resp = await fetch(`http://localhost:8000/api/search/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          task_id: taskId, 
          rejected_nodes: rejectedNodes, 
          new_seeds: newSeeds,
          verified_nodes: verifiedNodes
        })
      });
      const data = await resp.json();
      if (data.task_id) window.location.href = `/?task=${data.task_id}`;
    } catch (err) { console.error(err); }
  };

  const saveProfileChanges = async () => {
    // CRITICAL FIX: Use profile.id (persistent) instead of taskId (volatile)
    const targetId = profile?.id || taskId;
    if (!targetId || !profile) return;
    try {
      const resp = await fetch(`http://localhost:8000/api/profiles/${targetId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile)
      });
      if (resp.ok) {
        setIsEditing(false);
        setLogs(prev => [...prev, "[OK] Cambios persistidos en la base de datos central."]);
      }
    } catch (err) { console.error(err); }
  };

  const loadRadar = async () => {
    setView('radar');
    setRadarData(null);
    try {
      const resp = await fetch(`http://localhost:8000/api/radar`);
      if (resp.ok) setRadarData(await resp.json());
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const taskParam = urlParams.get('task');
    if (taskParam) {
      setTaskId(taskParam);
      setView('tactical');
      setProgress(10);
      setLogs(["[INIT] Recuperando estado de actualización..."]);
    }
  }, []);

  useEffect(() => {
    if (view === 'search') {
      fetch('http://localhost:8000/api/stats')
        .then(res => res.json())
        .then(data => setGlobalStats(data))
        .catch(err => console.error(err));
    }
  }, [view]);


  useEffect(() => {
    if (!taskId || view !== 'tactical') return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/search/status/${taskId}`);
        const data = await res.json();
        setTaskStatus(data.status);
        if (data.status === "completed") {
          // If profile is returned directly, use it, otherwise fetch it
          if (data.profile) {
            setProfile(data.profile);
            setDiscoveredNodes(data.profile.digital_footprint || []);
          } else if (data.processed_profile_id) {
            const pRes = await fetch(`http://localhost:8000/api/profiles/${data.processed_profile_id}`);
            if (pRes.ok) {
              const pData = await pRes.json();
              setProfile(pData);
              setDiscoveredNodes(pData.digital_footprint || []);
            }
          }
          setProgress(100);
          setActiveTools([]);
          setLogs(prev => [...prev, "[SUCCESS] Inteligencia sintetizada y dossier generado."]);
          setTimeout(() => setView('dossier'), 800);
          clearInterval(interval);
        } else if (data.status === "failed") {
          setLogs(data.logs || []);
          setProgress(0);
          setActiveTools([]);
          clearInterval(interval);
        } else {
          if (data.logs) setLogs(data.logs);
          if (data.progress) setProgress(data.progress);
          if (data.found_nodes) setDiscoveredNodes(data.found_nodes);
          if (data.active_tools) setActiveTools(data.active_tools);
        }
      } catch (err) { console.error(err); }
    }, 1500);
    return () => clearInterval(interval);
  }, [taskId, view]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const exportJSON = () => {
    if (!profile) return;
    const blob = new Blob([JSON.stringify(profile, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dossier_target_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderSearch = () => (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto mt-10 md:mt-20 px-4">
      <SystemStatusBoard health={health} />
      
      <div className="text-center mb-12">
        <h1 className="text-6xl md:text-8xl font-black mb-4 tracking-tighter text-white drop-shadow-2xl">
          OSINTPY <span className="text-blue-500">v10</span>
        </h1>
        <p className="text-slate-400 text-lg font-medium">Reconocimiento Táctico Omni-Vectoreal — Paraguay</p>
      </div>
      
      <div className="bg-black/80 backdrop-blur-3xl border border-white/10 rounded-[2.5rem] p-8 md:p-12 shadow-2xl relative overflow-hidden ring-1 ring-white/5">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-600 via-cyan-400 to-blue-600"></div>
          
          <div className="flex justify-between items-center mb-10">
            <div className="space-y-1">
              <h3 className="text-3xl font-black text-white tracking-widest italic">MISSION INTAKE</h3>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.4em]">Configure target vectors for tactical deployment</p>
            </div>
            <div className="bg-blue-500/10 border border-blue-500/20 px-4 py-2 rounded-full hidden sm:block">
              <span className="text-[10px] font-black text-blue-400 tracking-widest">ENCRYPTED CHANNEL</span>
            </div>
          </div>
          
          <form onSubmit={handleSearch} className="space-y-8">
            {/* VECTORES CÍVICOS */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center border border-emerald-500/20">
                  <ShieldCheck className="w-4 h-4 text-emerald-500" />
                </div>
                <span className="text-xs font-black tracking-[0.4em] text-emerald-400 uppercase">Vectores Cívicos (Paraguay)</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase ml-1">Cédula / RUC</label>
                  <input type="text" value={targetData.ci_ruc} onChange={(e) => setTargetData({...targetData, ci_ruc: e.target.value})} placeholder="Ej. 1234567 o 4444444-1" className="w-full bg-white/5 border border-white/5 hover:border-white/10 focus:border-emerald-500/50 rounded-2xl px-6 py-4 text-white outline-none transition-all placeholder:text-slate-700" />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase ml-1">Nombre Completo</label>
                  <input type="text" value={targetData.nombre} onChange={(e) => setTargetData({...targetData, nombre: e.target.value})} placeholder="Ej. Juan Silvano Pérez" className="w-full bg-white/5 border border-white/5 hover:border-white/10 focus:border-emerald-500/50 rounded-2xl px-6 py-4 text-white outline-none transition-all placeholder:text-slate-700" />
                </div>
              </div>
            </div>

            {/* VECTORES DIGITALES */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center border border-blue-500/20">
                  <Network className="w-4 h-4 text-blue-500" />
                </div>
                <span className="text-xs font-black tracking-[0.4em] text-blue-400 uppercase">Vectores de Redes & Contactos</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase ml-1">Alias / Username</label>
                  <div className="relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
                    <input type="text" value={targetData.alias} onChange={(e) => setTargetData({...targetData, alias: e.target.value})} placeholder="@user_id" className="w-full bg-white/5 border border-white/5 hover:border-white/10 focus:border-blue-500/50 rounded-2xl pl-12 pr-6 py-4 text-white outline-none transition-all placeholder:text-slate-700" />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase ml-1">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
                    <input type="email" value={targetData.email} onChange={(e) => setTargetData({...targetData, email: e.target.value})} placeholder="target@host.com" className="w-full bg-white/5 border border-white/5 hover:border-white/10 focus:border-blue-500/50 rounded-2xl pl-12 pr-6 py-4 text-white outline-none transition-all placeholder:text-slate-700" />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase ml-1">Teléfono</label>
                  <div className="relative">
                    <Smartphone className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
                    <input type="text" value={targetData.telefono} onChange={(e) => setTargetData({...targetData, telefono: e.target.value})} placeholder="+595 9..." className="w-full bg-white/5 border border-white/5 hover:border-white/10 focus:border-blue-500/50 rounded-2xl pl-12 pr-6 py-4 text-white outline-none transition-all placeholder:text-slate-700" />
                  </div>
                </div>
              </div>
            </div>

            {/* NOTAS */}
            <div className="space-y-2">
              <label className="text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase ml-1">Briefing de Misión (Contexto)</label>
              <textarea value={targetData.notas_adicionales} onChange={(e) => setTargetData({...targetData, notas_adicionales: e.target.value})} placeholder="Ingresa datos sospechosos, asociaciones o información adicional que pueda ayudar a los agentes..." rows={3} className="w-full bg-white/5 border border-white/5 hover:border-white/10 focus:border-blue-500/50 rounded-3xl px-6 py-4 text-white outline-none transition-all placeholder:text-slate-700 resize-none custom-scrollbar" />
            </div>

            <div className="pt-6 flex flex-col sm:flex-row gap-6 justify-between items-center">
              <div className="flex items-center gap-6">
                <div className="flex -space-x-3">
                  {[1,2,3,4].map(i => (
                    <div key={i} className="w-8 h-8 rounded-full border-2 border-black bg-slate-800 flex items-center justify-center overflow-hidden">
                      <div className="w-full h-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center">
                        <User className="w-4 h-4 text-white/50" />
                      </div>
                    </div>
                  ))}
                </div>
                <div>
                  <p className="text-[10px] font-black text-white italic tracking-widest">AGENT POOL READY</p>
                  <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">{health?.osint_binaries ? Object.keys(health.osint_binaries).length : 0} Agentes Deterministas Activos</p>
                </div>
              </div>

              <button type="submit" disabled={isSearching} className="w-full sm:w-auto bg-blue-600 hover:bg-blue-500 text-white font-black px-12 py-5 rounded-2xl transition-all active:scale-95 shadow-[0_0_30px_rgba(37,99,235,0.3)] flex items-center justify-center gap-4 group">
                <span className="tracking-[0.2em] italic">LAUNCH RECONNAISSANCE</span>
                <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          </form>
      </div>


      <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 px-4">
        {[
          { icon: Users, label: "Profiles", value: globalStats.total_profiles },
          { icon: Database, label: "Nodes", value: globalStats.total_nodes },
          { icon: Mail, label: "Emails", value: globalStats.total_emails },
          { icon: Phone, label: "Numbers", value: globalStats.total_phones }
        ].map((stat, i) => (
          <div key={i} className="bg-black/40 border border-white/5 p-6 rounded-3xl">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-2xl bg-white/5 flex items-center justify-center">
                <stat.icon className="w-5 h-5 text-slate-400" />
              </div>
              <div>
                <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">{stat.label}</p>
                <p className="text-xl font-black text-white">{(stat.value || 0).toLocaleString()}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );

  // ══════════════════════════════════════════════  // ═══════════════════════════════════════════════════════════════
  // TACTICAL VIEW
  // ═══════════════════════════════════════════════════════════════
  const renderTactical = () => (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 md:gap-8 h-auto lg:h-[80vh] px-4">
      {/* Columna Izquierda: Consola y Estados */}
      <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="lg:col-span-7 bg-black/90 border border-white/10 rounded-[40px] p-6 md:p-10 font-mono text-[11px] md:text-[13px] flex flex-col shadow-2xl overflow-hidden min-h-[500px] ring-1 ring-white/5">
        <div className="flex items-center justify-between mb-8 pb-6 border-b border-white/5">
          <div className="flex items-center gap-4">
            <div className={`w-3.5 h-3.5 rounded-full ${taskStatus === 'failed' ? 'bg-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]' : 'bg-blue-500 animate-pulse shadow-[0_0_15px_rgba(59,130,246,0.5)]'}`}></div>
            <div>
              <span className="text-white font-black tracking-widest uppercase block">MISIÓN_ACTIVA</span>
              <span className="text-[9px] text-slate-500 font-bold uppercase tracking-[0.2em]">Target: {targetData.nombre || targetData.alias || "Omni-Resolve"}</span>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            {/* Tool Indicators */}
            <div className="hidden sm:flex gap-3">
              {activeTools.map(tool => (
                <div key={tool} className="flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/20 rounded-full text-[9px] font-black text-blue-400 uppercase tracking-widest animate-pulse">
                  <Activity className="w-3 h-3" /> {tool}
                </div>
              ))}
            </div>

            {/* Progress Ring */}
            <div className="relative w-14 h-14">
              <svg className="w-14 h-14 -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="16" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
                <motion.circle cx="18" cy="18" r="16" fill="none" stroke={taskStatus === 'failed' ? '#ef4444' : '#3b82f6'} strokeWidth="3" strokeLinecap="round" strokeDasharray="100 100" initial={{ strokeDashoffset: 100 }} animate={{ strokeDashoffset: 100 - progress }} transition={{ duration: 1 }} />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-[10px] font-black text-white">{progress}%</span>
              </div>
            </div>
          </div>
        </div>

        {taskStatus === 'failed' && (
          <div className="mb-6 p-6 bg-red-500/10 border border-red-500/30 rounded-3xl flex items-center gap-4 text-left">
            <div className="w-12 h-12 rounded-2xl bg-red-500/20 flex items-center justify-center shrink-0">
               <AlertTriangle className="w-6 h-6 text-red-500" />
            </div>
            <div className="flex-1">
              <p className="text-red-400 font-black text-sm uppercase tracking-widest">FALLO CRÍTICO DEL MOTOR</p>
              <p className="text-red-500/60 text-[10px] font-bold">La tarea de Celery ha expirado o el scraper fue bloqueado. Revisa los logs abajo.</p>
            </div>
            <button onClick={() => setView('search')} className="bg-red-600 text-white px-6 py-2 rounded-xl text-[10px] font-black hover:bg-red-500 transition-all">ABORTAR_MISIÓN</button>
          </div>
        )}

        <div className="flex-1 overflow-y-auto space-y-2 pr-4 custom-scrollbar-minimal">
          {logs.map((log, i) => (
            <div key={i} className="flex gap-4 group">
              <span className="text-slate-800 font-black min-w-[25px] select-none">{String(i).padStart(3, '0')}</span>
              <span className={
                log.includes('[+]') ? 'text-emerald-400 font-bold' :
                log.includes('[ERROR]') ? 'text-red-500 font-black' :
                log.includes('[INFO]') ? 'text-blue-400' :
                log.includes('[SET]') || log.includes('[GOV]') ? 'text-amber-400 font-bold' :
                log.includes('[AI]') ? 'text-cyan-400 italic' :
                log.includes('---') ? 'text-slate-200 font-black py-2 border-y border-white/5 my-2 w-full block' :
                'text-slate-500'
              }>{log}</span>
            </div>
          ))}
          <div ref={logEndRef} />
        </div>
      </motion.div>

      {/* Columna Derecha: Discovery Grid */}
      <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="lg:col-span-5 flex flex-col gap-6 h-full">
        <div className="flex gap-4">
          <div className="flex-1 bg-black/40 border border-white/5 rounded-3xl p-6 flex items-center gap-4 shadow-xl">
             <div className="w-12 h-12 bg-emerald-500/20 rounded-2xl flex items-center justify-center border border-emerald-500/20">
                <Network className="w-6 h-6 text-emerald-500" />
             </div>
             <div>
                <span className="text-2xl font-black text-white">{discoveredNodes.length}</span>
                <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest block">HALLAZGOS_TOTALES</span>
             </div>
          </div>
          <div className="flex-1 bg-black/40 border border-white/5 rounded-3xl p-6 flex items-center gap-4 shadow-xl">
             <div className="w-12 h-12 bg-amber-500/20 rounded-2xl flex items-center justify-center border border-amber-500/20">
                <Zap className="w-6 h-6 text-amber-500" />
             </div>
             <div>
                <span className="text-2xl font-black text-white">{discoveredNodes.filter(n => n.enriched_zap).length}</span>
                <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest block">ZAP_ENRICHED</span>
             </div>
          </div>
        </div>

        <div className="bg-slate-900/80 backdrop-blur-3xl border border-white/10 rounded-[40px] p-8 flex-1 overflow-y-auto custom-scrollbar shadow-3xl">
          <h3 className="text-xs font-black tracking-[0.4em] text-slate-500 uppercase mb-8 flex items-center gap-4">
            <Database className="w-4 h-4" /> DISCOVERY_GRID
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AnimatePresence>
              {discoveredNodes.map((node, i) => {
                const isEnriched = node.enriched_zap;
                const photo = node.meta?.photo || node.meta?.avatar || (node.type === 'photo' ? node.value : null);
                
                return (
                  <motion.div 
                    key={i} 
                    initial={{ opacity: 0, scale: 0.9 }} 
                    animate={{ opacity: 1, scale: 1 }}
                    onClick={() => setPivotNode(node)}
                    className={`relative p-5 rounded-3xl group cursor-pointer transition-all border-2 ${
                      isEnriched 
                        ? 'bg-amber-500/5 border-amber-500/40 shadow-[0_0_20px_rgba(245,158,11,0.1)]' 
                        : 'bg-white/5 border-transparent hover:border-blue-500/50 hover:bg-blue-500/5'
                    }`}
                  >
                    {isEnriched && <Zap className="absolute -top-2 -right-2 w-6 h-6 text-amber-500 fill-amber-500 filter drop-shadow-[0_0_10px_rgba(245,158,11,0.8)]" />}
                    
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-2xl overflow-hidden shrink-0 border border-white/10 flex items-center justify-center bg-slate-800">
                        {photo ? (
                          <img src={photo} className="w-full h-full object-cover" alt="" />
                        ) : (
                          <div className={
                            node.type === 'social' ? 'text-blue-400' :
                            node.type === 'identity' ? 'text-emerald-400' : 'text-slate-400'
                          }>
                            {node.type === 'social' ? <Users className="w-5 h-5" /> : <User className="w-5 h-5" />}
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-[9px] font-black text-blue-500 uppercase tracking-widest">{node.source}</div>
                        <div className="text-xs font-black text-white truncate max-w-[120px]">{node.value}</div>
                        {node.platform && <div className="text-[8px] font-bold text-slate-500 uppercase">{node.platform}</div>}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>

      {/* Modal de Pivot */}
      <AnimatePresence>
        {pivotNode && (
          <div className="fixed inset-0 z-[1000] flex items-center justify-center p-4">
             <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/90 backdrop-blur-xl" onClick={() => setPivotNode(null)} />
             <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.9, y: 20 }} className="bg-slate-900 border border-blue-500/30 rounded-[40px] p-10 max-w-md w-full relative z-10 shadow-[0_0_100px_rgba(59,130,246,0.2)]">
                <div className="flex items-center gap-4 mb-8">
                   <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20">
                      <Network className="w-8 h-8 text-white" />
                   </div>
                   <div>
                      <h3 className="text-2xl font-black text-white tracking-widest italic">PIVOT_INSIGHT</h3>
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Deep recursive exploration</p>
                   </div>
                </div>
                
                <div className="bg-black/50 border border-white/5 rounded-3xl p-6 mb-8 ring-1 ring-white/5">
                   <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest block mb-2">{pivotNode.type} :: {pivotNode.source}</span>
                   <span className="text-lg font-black text-white break-all">{pivotNode.value}</span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                   <button onClick={() => setPivotNode(null)} className="px-6 py-4 rounded-2xl border border-white/10 text-slate-400 font-black hover:bg-white/5 transition-all text-xs uppercase tracking-widest">Cerrar</button>
                   <button onClick={executePivot} className="px-6 py-4 bg-blue-600 text-white rounded-2xl font-black hover:bg-blue-500 transition-all text-xs uppercase tracking-widest shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2 group">
                      Pivotar <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                   </button>
                </div>
             </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );

  const renderDossier = () => {
    if (!profile) return (
      <div className="flex flex-col items-center justify-center h-[60vh] gap-6">
        <Loader2 className="w-16 h-16 text-blue-500 animate-spin" />
        <h2 className="text-xl font-black text-slate-500 uppercase tracking-widest animate-pulse">Sincronizando Archivos Inteligencia...</h2>
      </div>
    );

    const isRejected = (val: string) => (rejectedNodes || []).some((r: any) => r.value === val);
    const isVerified = (val: string) => (verifiedNodes || []).some((v: any) => v.value === val);

    const visibleFootprint = (profile.digital_footprint || []).filter((fp: any) => !isRejected(fp.url));
    const visibleEmails = (profile.contacts?.emails || []).filter((e: string) => !isRejected(e));
    const visiblePhones = (profile.contacts?.phones || []).filter((p: string) => !isRejected(p));
    const riskScore = profile.risk_score || 0;
    const certaintyScore = profile.certainty_score || 0;
    const certaintyColor = certaintyScore >= 90 ? '#10b981' : certaintyScore >= 70 ? '#3b82f6' : '#f59e0b';
    const riskColor = riskScore > 80 ? '#ef4444' : riskScore > 60 ? '#f97316' : riskScore > 30 ? '#eab308' : '#22c55e';
    const riskLabel = riskScore > 80 ? 'CRÍTICO' : riskScore > 60 ? 'ALTO' : riskScore > 30 ? 'MODERADO' : 'MÍNIMO';
    const circumference = 2 * Math.PI * 40;
    const strokeOffset = circumference - (riskScore / 100) * circumference;

    const handleMerge = (altName: string) => {
      setLogs(prev => [...prev, `[FUSION] Consolidando identidad: ${altName} -> ${profile.identity.full_name}`]);
      setProfile({
        ...profile,
        possible_alternatives: profile.possible_alternatives.filter((a: string) => a !== altName),
        notes: (profile.notes || "") + `\n[FUSION] Identidad '${altName}' integrada por el analista.`
      });
    };

    const exportPDF = async () => {
      if (!dossierRef.current || !profile) return;
      setIsExportingPdf(true);
      try {
        const html2pdf = (await import('html2pdf.js')).default;
        const opt = {
          margin:       0.2,
          filename:     `OSINTPY_Dossier_${profile.identity?.full_name?.replace(/\s+/g, '_')}.pdf`,
          image:        { type: 'jpeg' as const, quality: 0.98 },
          html2canvas:  { scale: 2, useCORS: true, backgroundColor: '#0a0a0a' },
          jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' as const }
        };
        await html2pdf().set(opt).from(dossierRef.current).save();
      } catch (err) { console.error(err); }
      finally { setIsExportingPdf(false); }
    };

    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="px-4 pb-20">
        {/* Header de Estación de Trabajo */}
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 mb-12">
          <div className="flex items-center gap-6">
            <button onClick={() => setView('search')} className="p-4 bg-white/5 rounded-2xl text-slate-500 hover:text-white transition-all border border-white/5 hover:border-blue-500/30"><ChevronLeft className="w-6 h-6" /></button>
            <div>
              <div className="flex items-center gap-3">
                <Shield className="w-5 h-5 text-blue-500" />
                <h2 className="text-[10px] font-black uppercase tracking-[0.5em] text-slate-500">Analytical Workstation v10</h2>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[9px] font-black uppercase tracking-widest text-emerald-400">Human-in-the-Loop Active</span>
              </div>
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <button onClick={() => setIsEditing(!isEditing)} className={`px-6 py-3 rounded-2xl text-[10px] font-black transition-all flex items-center gap-3 border shadow-2xl ${isEditing ? 'bg-amber-600 border-amber-400 text-white' : 'bg-white/5 border-white/10 text-slate-400 hover:text-white hover:bg-white/10'}`}>
              <Edit3 className="w-4 h-4" /> {isEditing ? 'FINALIZAR REFINAMIENTO' : 'MODO REFINAR MUESTRA'}
            </button>
            <button onClick={saveProfileChanges} className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl text-[10px] font-black shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2">
              <Database className="w-4 h-4" /> GUARDAR EN DB
            </button>
            <button onClick={exportPDF} disabled={isExportingPdf} className="px-6 py-3 bg-red-600/20 border border-red-500/30 text-red-400 hover:bg-red-600 hover:text-white rounded-2xl text-[10px] font-black transition-all flex items-center gap-2">
              {isExportingPdf ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />} EXPORTAR PDF
            </button>
          </div>
        </div>

        <div ref={dossierRef} className="bg-slate-900 border border-white/5 rounded-[40px] shadow-3xl overflow-hidden p-1 relative">
          {/* Top Banner: Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-0 border-b border-white/5 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/20">
            {/* Identity & Photo */}
            <div className="lg:col-span-8 p-12 flex flex-col md:flex-row gap-12 items-center md:items-start border-r border-white/5">
                <div className="relative group">
                  <div className="w-48 h-48 md:w-64 md:h-64 rounded-[64px] bg-slate-800 border-2 border-white/10 overflow-hidden shadow-2xl flex items-center justify-center">
                    {profile.photo_url ? <img src={profile.photo_url} className="w-full h-full object-cover" alt="primary" /> : <User className="w-24 h-24 text-slate-700" />}
                  </div>
                  {isEditing && (
                    <div className="absolute inset-0 bg-black/60 rounded-[64px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                      <ImageIcon className="w-8 h-8 text-white" />
                    </div>
                  )}
                </div>
                <div className="flex-1 space-y-6 text-center md:text-left">
                  {isEditing ? (
                    <div className="space-y-4">
                      <label className="text-[10px] font-black text-amber-500 tracking-widest">NOMBRE DEL SUJETO</label>
                      <input 
                        value={profile.identity?.full_name || ""} 
                        onChange={e => setProfile({...profile, identity: {...(profile.identity || {}), full_name: e.target.value}})}
                        className="w-full bg-black/50 border border-amber-500/30 rounded-3xl px-6 py-4 text-4xl font-black text-white focus:outline-none focus:border-amber-500"
                        placeholder="Nombre Completo"
                      />
                    </div>
                  ) : (
                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white leading-none">{profile.identity?.full_name || "TARGET_UNNAMED"}</h1>
                  )}
                  
                  <div className="flex flex-wrap gap-4 justify-center md:justify-start">
                    <div className="flex items-center gap-2 bg-white/5 px-4 py-2 rounded-full border border-white/5">
                       <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">ID</span>
                       <span className="text-xs font-bold text-white font-mono">{profile.identity?.ci || "---"}</span>
                    </div>
                    <div className="flex items-center gap-2 bg-emerald-500/5 px-4 py-2 rounded-full border border-emerald-500/10">
                       <span className="text-[9px] font-black text-emerald-500 uppercase tracking-widest">Fiscal</span>
                       <span className="text-xs font-bold text-emerald-200 font-mono">{profile.fiscal?.ruc || "---"}</span>
                    </div>
                  </div>

                  <div className="bg-blue-600/5 border border-blue-500/20 rounded-3xl p-6 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-blue-500" />
                    <Zap className="absolute top-4 right-4 w-4 h-4 text-blue-500/40" />
                    <h4 className="text-[9px] font-black text-blue-400 uppercase tracking-[0.3em] mb-3">Sintesis Forense (Gemini AI)</h4>
                    {isEditing ? (
                      <textarea 
                        value={profile.semantic_summary || ""}
                        onChange={e => setProfile({...profile, semantic_summary: e.target.value})}
                        className="w-full bg-transparent border-none text-slate-300 text-sm leading-relaxed focus:outline-none custom-scrollbar"
                        rows={3}
                      />
                    ) : (
                      <p className="text-slate-200 text-sm font-medium leading-relaxed italic">"{profile.semantic_summary || profile.summary || "Generando contexto..."}"</p>
                    )}
                  </div>
                </div>
            </div>

            {/* Scores & Alternatives */}
            <div className="lg:col-span-4 p-12 bg-black/20 flex flex-col justify-between gap-10">
              <div className="flex justify-around items-center">
                  <div className="text-center space-y-3">
                    <div className="relative w-24 h-24 mx-auto">
                        <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
                          <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                          <circle cx="50" cy="50" r="40" fill="none" stroke={riskColor} strokeWidth="8" strokeDasharray={251} strokeDashoffset={251 - (riskScore/100)*251} strokeLinecap="round" className="transition-all duration-1000" />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="text-2xl font-black" style={{ color: riskColor }}>{riskScore}</span>
                        </div>
                    </div>
                    <span className="text-[9px] font-black tracking-[0.3em] uppercase block" style={{ color: riskColor }}>Nivel_Riesgo</span>
                  </div>
                  <div className="text-center space-y-3">
                    <div className="relative w-24 h-24 mx-auto">
                        <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
                          <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                          <circle cx="50" cy="50" r="40" fill="none" stroke={certaintyColor} strokeWidth="8" strokeDasharray={251} strokeDashoffset={251 - (certaintyScore/100)*251} strokeLinecap="round" className="transition-all duration-1000" />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="text-2xl font-black text-white">{certaintyScore}%</span>
                        </div>
                    </div>
                    <span className="text-[9px] font-black tracking-[0.3em] uppercase block text-slate-500">Certeza_Audit</span>
                  </div>
              </div>

              {/* Identity Alternatives Fusion */}
              <div className="space-y-4">
                <h4 className="text-[9px] font-black text-slate-600 uppercase tracking-[0.3em] flex items-center gap-2">
                   <Users className="w-4 h-4" /> Posibles Alternativas ({profile.possible_alternatives?.length || 0})
                </h4>
                <div className="space-y-2 max-h-[150px] overflow-y-auto custom-scrollbar pr-2">
                  {profile.possible_alternatives?.map((alt: string, i: number) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5 hover:border-emerald-500/30 transition-all group">
                        <span className="text-[11px] font-bold text-slate-400 group-hover:text-white transition-colors">{alt}</span>
                        <button onClick={() => handleMerge(alt)} className="px-3 py-1 bg-emerald-600/20 text-emerald-400 border border-emerald-500/20 rounded-lg text-[8px] font-black hover:bg-emerald-600 hover:text-white transition-all uppercase tracking-widest">
                          Fusionar
                        </button>
                    </div>
                  ))}
                  {(!profile.possible_alternatives || profile.possible_alternatives.length === 0) && (
                    <div className="text-[10px] text-slate-700 italic">No se detectaron homónimos dudosos</div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Body: Knowledge Graph & Full Data */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-0">
             {/* Knowledge Graph Rendering */}
             <div className="lg:col-span-12 p-8 border-b border-white/5 h-[600px] relative bg-black/40">
                <div className="absolute top-8 left-10 z-10">
                   <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-3">
                      <Network className="w-5 h-5 text-blue-500" /> Relational Knowledge Graph
                   </h3>
                   <p className="text-[9px] font-bold text-slate-600 uppercase mt-1">v1.2 Visual Intelligence Prop</p>
                </div>
                {/* Integration of real force graph would go here, using profile.graph */}
                <div className="w-full h-full flex items-center justify-center border border-white/5 rounded-[40px] bg-black/20">
                    <LinkAnalysisGraph graph={profile.graph || { nodes: [], links: [] }} />
                </div>
             </div>

             {/* Functional Workspace */}
             <div className="lg:col-span-8 p-12 border-r border-white/5 space-y-12">
                {/* Visual Gallery of Evidence */}
                <div className="space-y-6">
                   <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                      <ImageIcon className="w-5 h-5 text-amber-500" /> Evidencia Fotográfica (Zap ⚡)
                   </h3>
                   <div className="flex flex-wrap gap-4">
                      {(discoveredNodes.filter(n => n.type === 'photo') || []).map((photo, i) => (
                        <div key={i} className="w-24 h-24 rounded-2xl overflow-hidden border border-white/10 group relative shadow-xl">
                           <img src={photo.value} className="w-full h-full object-cover group-hover:scale-110 transition-transform" alt="" />
                           <div className="absolute inset-0 bg-blue-600/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                              <ExternalLink className="w-4 h-4 text-white" />
                           </div>
                        </div>
                      ))}
                      {(discoveredNodes.filter(n => n.type === 'photo').length === 0) && (
                        <div className="p-10 border border-dashed border-white/5 rounded-3xl w-full text-center text-[10px] font-black text-slate-700 uppercase tracking-widest">
                           Sin hallazgos multimedia en esta sesión
                        </div>
                      )}
                   </div>
                </div>

                {/* Digital Footprint Workload */}
                <div className="space-y-6">
                   <div className="flex items-center justify-between">
                      <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2"><Globe className="w-5 h-5 text-indigo-500" /> Digital Discovery Grid</h3>
                      <div className="text-[10px] font-black bg-white/5 text-slate-500 px-3 py-1 rounded-lg">{visibleFootprint.length} Resultados Limpios</div>
                   </div>
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {visibleFootprint.map((fp: any, i: number) => (
                        <div key={i} className={`p-5 rounded-3xl border transition-all flex flex-col justify-between h-40 group relative overflow-hidden ${fp.enriched_zap ? 'bg-amber-600/5 border-amber-500/30' : 'bg-black/30 border-white/5 hover:border-blue-500/50'}`}>
                           {fp.enriched_zap && <Zap className="absolute top-4 right-4 w-4 h-4 text-amber-500 fill-amber-500 animate-pulse" />}
                           <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                 <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest">{fp.platform}</span>
                                 <span className="text-[8px] bg-white/5 px-1 rounded text-slate-600 uppercase">{fp.source}</span>
                              </div>
                              <div className="text-sm font-bold text-white truncate group-hover:whitespace-normal transition-all">{fp.url}</div>
                           </div>
                           <div className="flex items-center justify-between mt-4">
                              <a href={fp.url} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-[9px] font-black text-slate-500 hover:text-white transition-colors uppercase tracking-widest"><ExternalLink className="w-3 h-3" /> Ver Perfil</a>
                              {isEditing && (
                                <button onClick={() => handleReject(fp.url)} className="p-2 bg-red-600/20 text-red-500 rounded-lg hover:bg-red-600 hover:text-white transition-all"><Trash2 className="w-4 h-4" /></button>
                              )}
                           </div>
                        </div>
                      ))}
                   </div>
                </div>
             </div>

             {/* Intelligence Sidebar: Journal & Stats */}
             <div className="lg:col-span-4 p-12 bg-black/10 space-y-12">
                <div className="space-y-6">
                    <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2"><Briefcase className="w-5 h-5 text-emerald-500" /> Intelligence Journal</h3>
                    <div className="relative">
                       <textarea 
                          value={profile.notes || ""}
                          onChange={e => setProfile({...profile, notes: e.target.value})}
                          placeholder="Registra hallazgos críticos, contradicciones detectadas o deducciones del analista..."
                          className="w-full h-80 bg-black/40 border border-white/5 rounded-[32px] p-6 text-sm font-medium text-slate-300 focus:outline-none focus:border-emerald-500/50 transition-all custom-scrollbar placeholder:text-slate-700"
                       />
                       <div className="absolute bottom-6 right-6 p-2 bg-emerald-600 rounded-lg animate-pulse">
                          <Edit3 className="w-4 h-4 text-white" />
                       </div>
                    </div>
                </div>

                {/* Quick Stats / Addresses */}
                <div className="space-y-6">
                    <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2"><MapPin className="w-5 h-5 text-amber-500" /> Vectores de Localización</h3>
                    <div className="space-y-3">
                       {(profile.contacts?.addresses || []).map((addr: string, i: number) => (
                         <div key={i} className="p-4 bg-white/5 border border-white/5 rounded-2xl flex items-center gap-4 group">
                             <div className="p-2 bg-amber-500/10 rounded-lg"><MapPin className="w-4 h-4 text-amber-500" /></div>
                             <span className="text-xs font-bold text-slate-400 group-hover:text-white transition-colors truncate">{addr}</span>
                         </div>
                       ))}
                       {(profile.contacts?.addresses?.length === 0) && (
                         <div className="text-[10px] text-slate-700 font-bold uppercase tracking-widest italic text-center py-4">No se detectaron coordenadas físicas</div>
                       )}
                    </div>
                </div>
             </div>
          </div>
        </div>
      </motion.div>
    );
  };

  // ═══════════════════════════════════════════════════════════════
  // GLOBAL RADAR VIEW
  // ═══════════════════════════════════════════════════════════════
  const renderRadar = () => (
    <div className="flex flex-col gap-6 animate-in fade-in duration-700 w-full lg:w-4/5 mx-auto h-[75vh]">
      <div className="flex justify-between items-center mb-4">
        <div>
            <h2 className="text-2xl font-black text-white flex items-center gap-3"><Network className="w-8 h-8 text-indigo-400" /> Global Identity Radar</h2>
            <p className="text-xs text-slate-400 font-mono mt-1">Cross-Profile Link Analysis Engine</p>
        </div>
        <button onClick={() => setView('search')} className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-6 py-3 rounded-xl text-xs font-black transition-all flex items-center gap-2 tracking-widest">
          VOLVER AL INICIO
        </button>
      </div>
      <div className="bg-slate-900 border border-white/5 rounded-[40px] p-6 shadow-2xl flex-1 flex flex-col relative overflow-hidden">
        {!radarData ? (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-slate-400">
                <Activity className="w-10 h-10 animate-spin text-indigo-500" />
                <span className="text-xs tracking-[0.3em] font-black uppercase text-indigo-400">Calculando Vínculos Globales...</span>
            </div>
        ) : (
            <LinkAnalysisGraph graph={radarData} />
        )}
      </div>
    </div>
  );

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-50 selection:bg-indigo-500/30 overflow-x-hidden w-full max-w-full">
      <Header />
      <main className="flex-1 w-full max-w-7xl mx-auto py-6 md:py-12 px-4 md:px-8">
        <AnimatePresence mode="wait">
          {view === 'search' && renderSearch()}
          {view === 'tactical' && renderTactical()}
          {view === 'dossier' && renderDossier()}
          {view === 'radar' && renderRadar()}
        </AnimatePresence>
      </main>
      <footer className="p-8 text-center border-t border-white/5 text-slate-600 text-[10px] font-black uppercase tracking-[0.5em]">
        End-to-End Tactical Intelligence — v4.0.0
      </footer>
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 10px; }
      `}</style>
    </div>
  );
}
