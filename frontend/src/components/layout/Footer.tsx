import React from 'react'
import { ShieldCheck, CheckCircle2 } from 'lucide-react'

export const Footer: React.FC = () => {
  return (
    <footer className="mt-16 border-t border-slate-200 bg-white py-6 text-xs text-slate-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6 lg:px-8">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="h-4 w-4 text-teal-600 dark:text-teal-400" />
          <span>
            HCL Fourth-Year Engineering Project • Bank Muscat BRD Series
          </span>
        </div>
        <div className="flex items-center space-x-4 text-[11px]">
          <span>FastAPI + PyMuPDF + scikit-learn</span>
          <span>•</span>
          <span>React + Vite + TypeScript + Tailwind</span>
          <span>•</span>
          <span className="flex items-center space-x-1 text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span>Zero Secrets Committed</span>
          </span>
        </div>
      </div>
    </footer>
  )
}
