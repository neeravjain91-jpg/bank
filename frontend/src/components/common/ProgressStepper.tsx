import React from 'react'
import { UploadCloud, FileSearch, Cpu, CheckCircle2, Loader2 } from 'lucide-react'

export type ExtractionStage = 'uploading' | 'extracting' | 'parsing' | 'done'

interface ProgressStepperProps {
  currentStage: ExtractionStage
  uploadProgress?: number
}

const STAGES = [
  { id: 'uploading', label: 'Uploading PDF', icon: UploadCloud, desc: 'Multipart transfer to backend' },
  { id: 'extracting', label: 'Extracting Table', icon: FileSearch, desc: 'PyMuPDF coordinate geometry' },
  { id: 'parsing', label: 'Parsing & Reconciling', icon: Cpu, desc: 'Line roles & running balance' },
  { id: 'done', label: 'Extraction Ready', icon: CheckCircle2, desc: '100% structured data' },
]

export const ProgressStepper: React.FC<ProgressStepperProps> = ({ currentStage, uploadProgress = 0 }) => {
  const getStageStatus = (stageId: string) => {
    const order = ['uploading', 'extracting', 'parsing', 'done']
    const currentIndex = order.indexOf(currentStage)
    const stageIndex = order.indexOf(stageId)

    if (currentStage === 'done') return 'completed'
    if (currentIndex === stageIndex) return 'current'
    if (currentIndex > stageIndex) return 'completed'
    return 'upcoming'
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between pb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            FastAPI Pipeline Execution
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Running hybrid visual geometry analysis and scikit-learn tabular parsing
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs font-semibold text-teal-600 dark:text-teal-400">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Processing</span>
        </div>
      </div>

      {/* Stepper Steps */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
        {STAGES.map((stage, idx) => {
          const status = getStageStatus(stage.id)
          const Icon = stage.icon

          return (
            <div
              key={stage.id}
              className={`relative flex flex-col justify-between rounded-xl border p-4 transition-all ${
                status === 'current'
                  ? 'border-teal-500 bg-teal-50/50 shadow-sm ring-1 ring-teal-500 dark:border-teal-500 dark:bg-teal-950/40'
                  : status === 'completed'
                  ? 'border-slate-200 bg-slate-50/80 dark:border-slate-800 dark:bg-slate-800/40'
                  : 'border-slate-100 bg-white opacity-60 dark:border-slate-800/60 dark:bg-slate-900'
              }`}
            >
              <div className="flex items-center justify-between">
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                    status === 'current'
                      ? 'bg-teal-600 text-white'
                      : status === 'completed'
                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/60 dark:text-emerald-300'
                      : 'bg-slate-100 text-slate-400 dark:bg-slate-800'
                  }`}
                >
                  {status === 'current' ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : status === 'completed' ? (
                    <CheckCircle2 className="h-4 w-4" />
                  ) : (
                    <Icon className="h-4 w-4" />
                  )}
                </div>
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500">
                  Step 0{idx + 1}
                </span>
              </div>

              <div className="mt-3">
                <div className="text-xs font-bold text-slate-900 dark:text-white">
                  {stage.label}
                </div>
                <div className="mt-0.5 text-[11px] text-slate-500 dark:text-slate-400">
                  {stage.id === 'uploading' && currentStage === 'uploading' && uploadProgress > 0
                    ? `${uploadProgress}% uploaded`
                    : stage.desc}
                </div>
              </div>

              {/* Progress bar line for current step */}
              {status === 'current' && (
                <div className="mt-3 h-1 w-full overflow-hidden rounded-full bg-teal-100 dark:bg-teal-950">
                  <div className="h-full animate-pulse rounded-full bg-teal-600 dark:bg-teal-400" />
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Skeleton Preview Placeholder (Phase 7) */}
      <div className="mt-6 space-y-3 rounded-xl border border-slate-100 bg-slate-50/60 p-4 dark:border-slate-800 dark:bg-slate-800/30">
        <div className="flex justify-between">
          <div className="h-4 w-48 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
          <div className="h-4 w-24 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
        </div>
        <div className="space-y-2 pt-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex space-x-3">
              <div className="h-6 w-24 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-6 flex-1 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-6 w-20 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-6 w-20 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-6 w-24 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
