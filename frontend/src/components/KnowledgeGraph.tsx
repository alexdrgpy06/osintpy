"use client";

import { motion } from "framer-motion";
import { Share2, Users, Building, MapPin, Target } from "lucide-react";

export default function KnowledgeGraph() {
  // Semi-dynamic nodes for visualization
  const nodes = [
    { id: 1, label: "SANTIAGO BALBUENA", type: "person", x: "50%", y: "50%" },
    { id: 2, label: "Empresa ABC S.A.", type: "company", x: "30%", y: "30%" },
    { id: 3, label: "Asunción, PY", type: "location", x: "70%", y: "40%" },
    { id: 4, label: "Familiar (Hermano)", type: "person", x: "40%", y: "70%" },
    { id: 5, label: "RUC 4567890-1", type: "id", x: "60%", y: "80%" },
  ];

  return (
    <div className="relative w-full h-[500px] bg-slate-900/40 rounded-3xl border border-white/5 overflow-hidden flex items-center justify-center">
      <div className="absolute top-6 left-6 z-10">
        <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-1">Knowledge Graph</h3>
        <p className="text-[10px] text-blue-400 font-bold uppercase">Relaciones Identificadas (5)</p>
      </div>

      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        {/* Simple lines between nodes */}
        <line x1="50%" y1="50%" x2="30%" y2="30%" stroke="rgba(59, 130, 246, 0.2)" strokeWidth="2" />
        <line x1="50%" y1="50%" x2="70%" y2="40%" stroke="rgba(59, 130, 246, 0.2)" strokeWidth="2" />
        <line x1="50%" y1="50%" x2="40%" y2="70%" stroke="rgba(59, 130, 246, 0.2)" strokeWidth="2" />
        <line x1="50%" y1="50%" x2="60%" y2="80%" stroke="rgba(59, 130, 246, 0.2)" strokeWidth="2" />
      </svg>

      {nodes.map((node) => (
        <motion.div
          key={node.id}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: node.id * 0.1 }}
          className="absolute group cursor-pointer"
          style={{ left: node.x, top: node.y, transform: "translate(-50%, -50%)" }}
        >
          <div className="relative">
            <div className="p-3 rounded-2xl bg-slate-800 border border-white/10 shadow-2xl group-hover:border-blue-500/50 transition-all flex items-center justify-center">
              {node.type === "person" && <Users className="w-5 h-5 text-blue-400" />}
              {node.type === "company" && <Building className="w-5 h-5 text-emerald-400" />}
              {node.type === "location" && <MapPin className="w-5 h-5 text-orange-400" />}
              {node.type === "id" && <Target className="w-5 h-5 text-purple-400" />}
            </div>
            <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              <span className="bg-slate-950 text-[10px] font-bold px-2 py-1 rounded border border-white/10 uppercase tracking-widest leading-none">
                {node.label}
              </span>
            </div>
          </div>
        </motion.div>
      ))}

      <div className="absolute bottom-6 right-6 flex gap-2">
        <button className="p-2 rounded-xl bg-slate-800 border border-white/10 text-slate-400 hover:text-white transition-all"><Share2 className="w-4 h-4" /></button>
        <button className="px-4 py-2 rounded-xl bg-blue-600 font-bold text-xs">Expandir Grafo</button>
      </div>
    </div>
  );
}
