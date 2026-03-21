"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ChevronLeft, Download, RefreshCw, User, Globe, Mail, Shield, ExternalLink, Briefcase, PhoneCall, Edit3, Plus, Trash2, Send, X } from "lucide-react";
import Header from "@/components/Header";
import { motion, AnimatePresence } from "framer-motion";

export default function ProfileDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [rejectedNodes, setRejectedNodes] = useState<any[]>([]);
  const [newSeed, setNewSeed] = useState("");
  const [newSeeds, setNewSeeds] = useState<string[]>([]);

  useEffect(() => {
    fetch(`http://localhost:8000/api/profiles/${id}`)
      .then(res => res.json())
      .then(data => {
        setProfile(data.data || data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  const isRejected = (val: string) => rejectedNodes.some(r => r.value === val);

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
    try {
      const res = await fetch(`http://localhost:8000/api/profiles/${id}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rejected_nodes: rejectedNodes, new_seeds: newSeeds })
      });
      const data = await res.json();
      window.location.href = `/?task=${data.task_id}`;
    } catch { alert("Error al actualizar."); }
  };

  const exportJSON = () => {
    if (!profile) return;
    const blob = new Blob([JSON.stringify(profile, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dossier_${id.slice(0,8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-6">
      <div className="w-16 h-16 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
      <p className="text-slate-500 font-black uppercase tracking-[0.5em] text-xs">Cargando Dossier...</p>
    </div>
  );

  if (!profile) return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center gap-6">
      <p className="text-red-500 font-black uppercase tracking-[0.5em] text-xs">Perfil no encontrado</p>
      <button onClick={() => window.location.href = '/profiles'} className="px-6 py-2 bg-white/5 rounded-full text-xs font-bold text-slate-300">Volver</button>
    </div>
  );

  const identity = profile.identity || {};
  const fiscal = profile.fiscal || {};
  const contacts = profile.contacts || {};
  const footprint = (profile.digital_footprint || []).filter((fp: any) => !isRejected(fp.url));
  const emails = (contacts.emails || []).filter((e: string) => !isRejected(e));
  const phones = (contacts.phones || []).filter((p: string) => !isRejected(p));
  const riskColor = (profile.risk_score || 0) > 70 ? 'text-red-500' : (profile.risk_score || 0) > 40 ? 'text-amber-500' : 'text-emerald-500';

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-50">
      <Header />
      <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur-xl sticky top-20 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <button onClick={() => window.location.href = '/profiles'} className="flex items-center gap-2 text-slate-500 hover:text-white transition-colors">
              <ChevronLeft className="w-4 h-4" />
              <span className="text-[10px] font-black uppercase tracking-widest">Volver</span>
            </button>
            <div className="h-4 w-[1px] bg-white/10" />
            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-400">EXPEDIENTE #{id.slice(0,8)}</span>
          </div>
          <div className="flex gap-3">
            <button onClick={() => setIsEditing(!isEditing)} className={`px-4 py-2 rounded-xl text-[10px] font-black transition-all flex items-center gap-2 ${isEditing ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' : 'bg-white/5 text-slate-400 hover:text-white'}`}>
              <Edit3 className="w-3 h-3" /> {isEditing ? 'EDITANDO' : 'REFINAR'}
            </button>
            <button onClick={exportJSON} className="bg-white text-black px-6 py-2 rounded-xl font-black text-[10px] uppercase tracking-widest hover:bg-slate-200 transition-all flex items-center gap-2">
              <Download className="w-4 h-4" /> JSON
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        {/* Edit Mode Bar */}
        <AnimatePresence>
          {isEditing && (
            <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden mb-6">
              <div className="p-6 bg-amber-500/5 border border-amber-500/20 rounded-3xl space-y-4">
                <p className="text-[11px] text-slate-400">Marca datos incorrectos y agrega nuevos términos para re-buscar.</p>
                <div className="flex gap-3">
                  <input value={newSeed} onChange={e => setNewSeed(e.target.value)} onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), handleAddSeed())} placeholder="Nuevo alias, email..." className="flex-1 bg-black border border-white/10 rounded-xl px-4 py-3 text-sm outline-none text-white focus:border-amber-500" />
                  <button onClick={handleAddSeed} className="bg-amber-600 text-white px-5 py-3 rounded-xl font-black text-xs flex items-center gap-2"><Plus className="w-4 h-4" /></button>
                </div>
                {(newSeeds.length > 0 || rejectedNodes.length > 0) && (
                  <div className="flex flex-wrap gap-2">
                    {newSeeds.map((s, i) => <span key={`s${i}`} className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-bold rounded-lg flex items-center gap-2"><Plus className="w-3 h-3" />{s}<button onClick={() => setNewSeeds(p => p.filter((_, j) => j !== i))}><X className="w-3 h-3" /></button></span>)}
                    {rejectedNodes.map((r, i) => <span key={`r${i}`} className="px-3 py-1 bg-red-500/20 text-red-400 text-xs font-bold rounded-lg line-through flex items-center gap-2">{r.value.slice(0, 30)}<button onClick={() => setRejectedNodes(p => p.filter((_, j) => j !== i))}><X className="w-3 h-3" /></button></span>)}
                  </div>
                )}
                {(rejectedNodes.length > 0 || newSeeds.length > 0) && (
                  <button onClick={submitCorrections} className="w-full bg-amber-600 text-white py-3 rounded-xl font-black text-xs uppercase tracking-widest hover:bg-amber-500 flex items-center justify-center gap-2">
                    <Send className="w-4 h-4" /> Re-buscar con correcciones
                  </button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="bg-slate-900 border border-white/5 rounded-[40px] overflow-hidden">
          {/* Header */}
          <div className="p-8 md:p-12 border-b border-white/5 flex flex-col md:flex-row gap-8 items-center md:items-start">
            <div className="w-32 h-32 md:w-40 md:h-40 rounded-[40px] bg-slate-800 border-2 border-white/5 overflow-hidden flex items-center justify-center shrink-0">
              {profile.photo_url ? <img src={profile.photo_url} className="w-full h-full object-cover" alt="" /> : <User className="w-16 h-16 text-blue-500" />}
            </div>
            <div className="flex-1 text-center md:text-left space-y-4">
              <h1 className="text-4xl md:text-5xl font-black tracking-tighter">{identity.full_name || 'DESCONOCIDO'}</h1>
              <p className="text-slate-400 text-sm font-medium leading-relaxed whitespace-pre-wrap">{profile.summary}</p>
              <div className="flex flex-wrap justify-center md:justify-start gap-3 pt-2">
                <span className="px-3 py-1.5 bg-blue-600 text-white rounded-full text-[10px] font-black uppercase">CI: {identity.ci || 'N/A'}</span>
                <span className="px-3 py-1.5 bg-emerald-600 text-white rounded-full text-[10px] font-black uppercase">RUC: {fiscal.ruc || 'N/A'}</span>
                <span className={`px-3 py-1.5 rounded-full text-[10px] font-black uppercase border border-white/10 ${riskColor}`}>Riesgo: {profile.risk_score || 0}/100</span>
              </div>
            </div>
          </div>

          {/* Body */}
          <div className="grid grid-cols-1 md:grid-cols-2 p-8 md:p-12 gap-12">
            <div className="space-y-6">
              <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest flex items-center gap-2"><Globe className="w-4 h-4 text-blue-500" /> Huella Digital ({footprint.length})</h3>
              <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                {footprint.map((fp: any, i: number) => (
                  <div key={i} className="flex items-center gap-2">
                    <a href={fp.url} target="_blank" rel="noreferrer" className="flex-1 p-3 bg-black/40 border border-white/5 rounded-xl flex items-center justify-between hover:border-blue-500/50 transition-all min-w-0">
                      <span className="text-sm font-bold text-slate-300 truncate">{fp.platform}</span>
                      <ExternalLink className="w-3 h-3 text-slate-700 shrink-0" />
                    </a>
                    {isEditing && <button onClick={() => handleReject(fp.url)} className="p-2 bg-red-500/10 text-red-500 rounded-lg hover:bg-red-500 hover:text-white"><Trash2 className="w-3 h-3" /></button>}
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-8">
              <div className="space-y-4">
                <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest flex items-center gap-2"><Mail className="w-4 h-4 text-purple-500" /> Contactos</h3>
                {emails.map((e: string, i: number) => (
                  <div key={i} className="flex items-center gap-2"><div className="flex-1 p-3 bg-black/40 border border-white/5 rounded-xl text-sm text-slate-300 font-mono truncate">{e}</div>{isEditing && <button onClick={() => handleReject(e)} className="p-2 bg-red-500/10 text-red-500 rounded-lg hover:bg-red-500 hover:text-white"><Trash2 className="w-3 h-3" /></button>}</div>
                ))}
                {phones.map((p: string, i: number) => (
                  <div key={i} className="flex items-center gap-2"><div className="flex-1 p-3 bg-black/40 border border-white/5 rounded-xl text-sm text-slate-300 font-mono flex items-center gap-2"><PhoneCall className="w-3 h-3 text-amber-500" />{p}</div>{isEditing && <button onClick={() => handleReject(p)} className="p-2 bg-red-500/10 text-red-500 rounded-lg hover:bg-red-500 hover:text-white"><Trash2 className="w-3 h-3" /></button>}</div>
                ))}
                {emails.length === 0 && phones.length === 0 && <p className="text-slate-600 text-xs">Sin contactos.</p>}
              </div>
              {fiscal.ruc && (
                <div className="space-y-4">
                  <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest flex items-center gap-2"><Briefcase className="w-4 h-4 text-emerald-500" /> Datos Fiscales</h3>
                  <div className="p-4 bg-black/40 border border-white/5 rounded-xl space-y-2">
                    <div className="flex justify-between text-xs"><span className="text-slate-500">RUC</span><span className="text-emerald-400 font-mono font-bold">{fiscal.ruc}</span></div>
                    <div className="flex justify-between text-xs"><span className="text-slate-500">Estado</span><span className="text-slate-300 font-bold">{fiscal.status}</span></div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
