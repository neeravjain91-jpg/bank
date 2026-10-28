import React, { useState, useEffect, useMemo } from 'react'
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  FileText,
  ExternalLink,
  Download,
  Eye,
} from 'lucide-react'

interface DocumentViewerProps {
  file: File | null
  documentUrl?: string | null
  fileName?: string
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  file,
  documentUrl,
  fileName = 'statement.pdf',
}) => {
  const [zoom, setZoom] = useState<number>(100)

  // Safely generate and revoke Object URL per Phase 10
  const activeUrl = useMemo(() => {
    if (file) {
      return URL.createObjectURL(file)
    }
    if (documentUrl) {
      return documentUrl
    }
    return null
  }, [file, documentUrl])

  useEffect(() => {
    return () => {
      if (file && activeUrl) {
        URL.revokeObjectURL(activeUrl)
      }
    }
  }, [file, activeUrl])

  return (
    <div className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      {/* Viewer Toolbar */}
      <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3 dark:border-slate-800">
        <div className="flex items-center space-x-2 truncate">
          <FileText className="h-4 w-4 shrink-0 text-teal-600 dark:text-teal-400" />
          <span className="truncate text-xs font-semibold text-slate-900 dark:text-white">
            {fileName}
          </span>
          <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
            Source PDF
          </span>
        </div>

        {/* Zoom & Action Controls */}
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setZoom((z) => Math.max(50, z - 25))}
            className="rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200"
            title="Zoom Out"
            aria-label="Zoom Out"
          >
            <ZoomOut className="h-3.5 w-3.5" />
          </button>
          <span className="w-10 text-center font-mono text-[11px] text-slate-600 dark:text-slate-400">
            {zoom}%
          </span>
          <button
            onClick={() => setZoom((z) => Math.min(250, z + 25))}
            className="rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200"
            title="Zoom In"
            aria-label="Zoom In"
          >
            <ZoomIn className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => setZoom(100)}
            className="rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200"
            title="Reset Zoom"
            aria-label="Reset Zoom"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
          {activeUrl && (
            <>
              <a
                href={activeUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200"
                title="Open PDF in new tab"
                aria-label="Open PDF in new tab"
              >
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
              <a
                href={activeUrl}
                download={fileName}
                className="rounded p-1 text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200"
                title="Download source PDF"
                aria-label="Download source PDF"
              >
                <Download className="h-3.5 w-3.5" />
              </a>
            </>
          )}
        </div>
      </div>

      {/* Embedded PDF View */}
      <div className="relative flex-1 overflow-auto bg-slate-100/70 p-4 dark:bg-slate-950/60">
        {activeUrl ? (
          <div
            className="h-full min-h-[550px] w-full transition-transform"
            style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}
          >
            <iframe
              src={`${activeUrl}#toolbar=0&navpanes=0`}
              title="Statement Document Viewer"
              className="h-full min-h-[600px] w-full rounded-xl border-0 bg-white shadow-sm dark:bg-slate-900"
            />
          </div>
        ) : (
          <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-8 text-center text-slate-400">
            <Eye className="h-10 w-10 stroke-[1.5] text-slate-300 dark:text-slate-600" />
            <p className="mt-2 text-xs font-medium">No source PDF loaded</p>
            <p className="text-[11px] text-slate-400 dark:text-slate-500">
              Upload a bank statement or load the Bank Muscat sample to inspect coordinates side-by-side
            </p>
          </div>
        )}
      </div>

      {/* Footer Instructions */}
      <div className="flex items-center justify-between border-t border-slate-100 px-4 py-2 text-[11px] text-slate-500 dark:border-slate-800 dark:text-slate-400">
        <span>Side-by-side Layout Verification</span>
        <span>Original vector text layer</span>
      </div>
    </div>
  )
}
