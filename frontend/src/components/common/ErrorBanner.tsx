import React, { useState } from 'react'
import { AlertCircle, ChevronDown, ChevronUp, RefreshCw, Server, HelpCircle } from 'lucide-react'
import { ApiErrorDetail } from '../../types'

interface ErrorBannerProps {
  error: ApiErrorDetail | Error | null
  onRetry?: () => void
  onOpenBackendModal?: () => void
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({
  error,
  onRetry,
  onOpenBackendModal,
}) => {
  const [showDetails, setShowDetails] = useState(false)

  if (!error) return null

  const isDetail = 'isCors' in error
  const isCors = isDetail ? (error as ApiErrorDetail).isCors : false
  const isTimeout = isDetail ? (error as ApiErrorDetail).isTimeout : false
  const status = isDetail ? (error as ApiErrorDetail).status : undefined
  const endpoint = isDetail ? (error as ApiErrorDetail).endpoint : undefined
  const details = isDetail ? (error as ApiErrorDetail).details : undefined
  const message = error.message || 'An error occurred while executing the extraction pipeline.'

  return (
    <div className="rounded-2xl border border-rose-200 bg-rose-50/70 p-5 shadow-sm dark:border-rose-900/60 dark:bg-rose-950/20">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <div className="rounded-xl bg-rose-100 p-2 text-rose-600 dark:bg-rose-900/60 dark:text-rose-300">
            <AlertCircle className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-rose-900 dark:text-rose-200">
                Backend Pipeline Exception
              </h3>
              {status && (
                <span className="rounded bg-rose-200/60 px-1.5 py-0.5 font-mono text-[10px] font-bold text-rose-900 dark:bg-rose-900 dark:text-rose-200">
                  HTTP {status}
                </span>
              )}
              {endpoint && (
                <span className="font-mono text-[10px] text-rose-700/80 dark:text-rose-300/80">
                  [{endpoint}]
                </span>
              )}
            </div>
            <p className="mt-1 text-xs text-rose-700 dark:text-rose-300">{message}</p>
          </div>
        </div>

        {/* Retry Action */}
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center space-x-1.5 rounded-xl bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-rose-700 dark:bg-rose-500 dark:hover:bg-rose-600"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Retry</span>
          </button>
        )}
      </div>

      {/* Actionable CORS Advice (Phase 3.3 & 16.4) */}
      {isCors && (
        <div className="mt-4 rounded-xl border border-rose-300/80 bg-white/80 p-3 text-xs text-slate-700 dark:border-rose-900 dark:bg-slate-900/80 dark:text-slate-300">
          <div className="flex items-center space-x-1.5 font-semibold text-rose-800 dark:text-rose-300">
            <HelpCircle className="h-4 w-4" />
            <span>CORS Resolution Advice</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-600 dark:text-slate-400">
            The browser blocked the cross-origin request. Configure the backend FastAPI application to
            include <code className="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded font-mono">{window.location.origin}</code> in its <code className="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded font-mono">allow_origins</code> CORS middleware list, or switch the dashboard to the local server.
          </p>
          {onOpenBackendModal && (
            <div className="mt-2.5">
              <button
                onClick={onOpenBackendModal}
                className="inline-flex items-center space-x-1.5 rounded-lg bg-slate-800 px-2.5 py-1 text-[11px] font-semibold text-white hover:bg-slate-700 dark:bg-slate-700 dark:hover:bg-slate-600"
              >
                <Server className="h-3 w-3" />
                <span>Configure Backend Connection</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Collapsible Technical Details */}
      <div className="mt-4 border-t border-rose-200/60 pt-3 dark:border-rose-900/40">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="flex items-center space-x-1 text-[11px] font-semibold text-rose-800 hover:text-rose-900 dark:text-rose-300"
        >
          <span>{showDetails ? 'Hide Technical Diagnostics' : 'Show Technical Diagnostics'}</span>
          {showDetails ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </button>

        {showDetails && (
          <div className="mt-2 max-h-48 overflow-auto rounded-xl bg-slate-950 p-3 font-mono text-[10px] text-slate-200">
            <pre className="whitespace-pre-wrap break-all">
              {JSON.stringify(
                {
                  message: error.message,
                  status,
                  isCors,
                  isTimeout,
                  endpoint,
                  details,
                },
                null,
                2
              )}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
