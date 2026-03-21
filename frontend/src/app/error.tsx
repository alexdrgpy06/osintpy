'use client';

import { useEffect } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-white p-8">
      <div className="w-20 h-20 bg-red-500/10 border border-red-500/20 rounded-[30px] flex items-center justify-center mb-8">
        <AlertTriangle className="w-10 h-10 text-red-500" />
      </div>
      <h2 className="text-3xl font-black mb-4 uppercase tracking-tighter">Error de Aplicación</h2>
      <p className="text-slate-400 text-center max-w-md mb-8 font-medium">
        Se encontró un problema crítico en el renderizado del dashboard. 
        Revisa la consola para más detalles.
      </p>
      <button
        onClick={() => reset()}
        className="px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-full font-black text-xs tracking-widest flex items-center gap-3 transition-all shadow-xl shadow-blue-600/20"
      >
        <RefreshCw className="w-4 h-4" /> REINTENTAR CARGA
      </button>
    </div>
  );
}
