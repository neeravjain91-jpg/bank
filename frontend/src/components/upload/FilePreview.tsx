import React from 'react'
import { FileCheck2, X } from 'lucide-react'

interface FilePreviewProps {
  file: File
  onRemove: () => void
  disabled?: boolean
}

export const FilePreview: React.FC<FilePreviewProps> = ({ file, onRemove, disabled }) => {
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <div className="flex items-center justify-between rounded-xl border border-teal-200 bg-teal-50/40 p-4 dark:border-teal-900/60 dark:bg-teal-950/20">
      <div className="flex items-center space-x-3.5 truncate">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-teal-600 text-white shadow-sm dark:bg-teal-500">
          <FileCheck2 className="h-6 w-6" />
        </div>
        <div className="truncate">
          <div className="flex items-center space-x-2">
            <span className="truncate text-sm font-semibold text-slate-900 dark:text-white">
              {file.name}
            </span>
            <span className="shrink-0 rounded bg-teal-100 px-2 py-0.5 text-[10px] font-bold text-teal-800 dark:bg-teal-900 dark:text-teal-200">
              PDF Ready
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {formatSize(file.size)} • Digital Native Bank Statement
          </p>
        </div>
      </div>

      <button
        onClick={onRemove}
        disabled={disabled}
        className="ml-4 shrink-0 rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 disabled:opacity-50 dark:hover:bg-slate-800 dark:hover:text-slate-200"
        title="Remove selected file"
        aria-label="Remove selected file"
      >
        <X className="h-5 w-5" />
      </button>
    </div>
  )
}
