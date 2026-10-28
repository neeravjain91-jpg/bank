import React, { useState, useRef } from 'react'
import {
  Upload,
  Sparkles,
  AlertCircle,
  FileText,
  Lock,
  ChevronDown,
} from 'lucide-react'
import { useProfiles } from '../../hooks/useProfiles'
import { FilePreview } from './FilePreview'
import { validateStatementFile } from '../../utils/validation'

interface UploadZoneProps {
  onFileSelect: (file: File) => void
  onTrySample: () => void
  onLoadDemoMode: () => void
  selectedFile: File | null
  onClearFile: () => void
  selectedProfile: string
  onProfileChange: (profile: string) => void
  onExtract: () => void
  isExtracting: boolean
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onFileSelect,
  onTrySample,
  onLoadDemoMode,
  selectedFile,
  onClearFile,
  selectedProfile,
  onProfileChange,
  onExtract,
  isExtracting,
}) => {
  const [isDragOver, setIsDragOver] = useState(false)
  const [validationError, setValidationError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { data: profilesData, isLoading: profilesLoading } = useProfiles()

  const handleValidateAndSelect = (file: File) => {
    setValidationError(null)
    const result = validateStatementFile(file)
    if (!result.isValid) {
      setValidationError(result.error || 'Invalid file.')
      return
    }
    onFileSelect(file)
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleValidateAndSelect(e.dataTransfer.files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition dark:border-slate-800 dark:bg-slate-900">
      {/* Header with Sample Triggers */}
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-base font-semibold text-slate-900 dark:text-white">
            Upload Bank Statement PDF
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Extract tabular transaction rows and reconcile running balances automatically
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Try Sample Statement Button (Phase 6.4) */}
          <button
            onClick={onTrySample}
            disabled={isExtracting}
            className="inline-flex items-center space-x-1.5 rounded-xl border border-teal-200 bg-teal-50 px-3 py-2 text-xs font-semibold text-teal-800 shadow-sm transition hover:bg-teal-100 disabled:opacity-50 dark:border-teal-800/80 dark:bg-teal-950/60 dark:text-teal-300 dark:hover:bg-teal-900/60"
            title="Load the bundled synthetic Bank Muscat statement PDF for real extraction"
          >
            <Sparkles className="h-3.5 w-3.5 text-teal-600 dark:text-teal-400" />
            <span>Load Bank Muscat Sample</span>
          </button>

          {/* Quick Demo Mode Trigger (Phase 14) */}
          <button
            onClick={onLoadDemoMode}
            disabled={isExtracting}
            className="inline-flex items-center space-x-1 rounded-xl border border-amber-200 bg-amber-50 px-2.5 py-2 text-xs font-semibold text-amber-800 transition hover:bg-amber-100 dark:border-amber-900 dark:bg-amber-950/50 dark:text-amber-300 dark:hover:bg-amber-900/50"
            title="View verified synthetic fixtures without making API requests"
          >
            <span>Demo Data</span>
          </button>
        </div>
      </div>

      {/* Dropzone Container */}
      <div className="mt-5">
        {!selectedFile ? (
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                fileInputRef.current?.click()
              }
            }}
            className={`group relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition-all ${
              isDragOver
                ? 'border-teal-500 bg-teal-50/50 dark:border-teal-400 dark:bg-teal-950/20'
                : 'border-slate-300 hover:border-teal-500 hover:bg-slate-50/80 dark:border-slate-700 dark:hover:border-teal-500 dark:hover:bg-slate-800/50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleValidateAndSelect(e.target.files[0])
                }
              }}
            />

            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-50 text-teal-600 ring-8 ring-teal-50/50 transition group-hover:scale-105 dark:bg-teal-950 dark:text-teal-400 dark:ring-teal-950/30">
              <Upload className="h-7 w-7" />
            </div>

            <p className="mt-4 text-sm font-semibold text-slate-800 dark:text-slate-200">
              Drag and drop your bank statement PDF here
            </p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Supports <span className="font-semibold text-slate-700 dark:text-slate-300">Digital Native PDF</span> up to 20MB
            </p>

            <button
              type="button"
              className="mt-4 inline-flex items-center rounded-lg bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-700 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50 dark:bg-slate-800 dark:text-slate-200 dark:ring-slate-700 dark:hover:bg-slate-700"
            >
              Browse Files
            </button>
          </div>
        ) : (
          <FilePreview file={selectedFile} onRemove={onClearFile} disabled={isExtracting} />
        )}

        {/* Validation Error Message */}
        {validationError && (
          <div className="mt-3 flex items-start space-x-2 rounded-lg bg-rose-50 p-2.5 text-xs text-rose-700 dark:bg-rose-950/50 dark:text-rose-300">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
            <span>{validationError}</span>
          </div>
        )}
      </div>

      {/* Profile & Action Controls */}
      <div className="mt-5 grid grid-cols-1 gap-4 border-t border-slate-100 pt-5 sm:grid-cols-2 lg:grid-cols-3 dark:border-slate-800">
        {/* Profile Selector */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
            Extraction Layout Profile
          </label>
          <div className="relative mt-1">
            <select
              value={selectedProfile}
              onChange={(e) => onProfileChange(e.target.value)}
              disabled={isExtracting || profilesLoading}
              className="w-full appearance-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-800 outline-none transition focus:border-teal-500 focus:bg-white disabled:opacity-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:focus:border-teal-400"
            >
              <option value="auto">⚡ Auto-detect Profile (Default)</option>
              {profilesData?.profiles?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.currency} - {p.country})
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2.5 top-2.5 h-4 w-4 text-slate-400" />
          </div>
        </div>

        {/* Privacy Note (Phase 6.1) */}
        <div className="flex items-center space-x-2 text-xs text-slate-500 dark:text-slate-400">
          <Lock className="h-4 w-4 shrink-0 text-teal-600 dark:text-teal-400" />
          <span>
            Digital in-memory extraction. Statement text layers are processed without persistent disk storage.
          </span>
        </div>

        {/* Extract Table Action Button */}
        <div className="flex items-end sm:col-span-2 lg:col-span-1">
          <button
            onClick={onExtract}
            disabled={!selectedFile || isExtracting}
            className="flex w-full items-center justify-center space-x-2 rounded-xl bg-gradient-to-r from-teal-600 to-teal-700 py-2.5 text-xs font-bold text-white shadow-md shadow-teal-600/20 transition hover:from-teal-700 hover:to-teal-800 disabled:cursor-not-allowed disabled:opacity-50 dark:from-teal-500 dark:to-teal-600"
          >
            <FileText className="h-4 w-4" />
            <span>{isExtracting ? 'Extracting Statement...' : 'Extract Table & Reconcile'}</span>
          </button>
        </div>
      </div>
    </div>
  )
}
