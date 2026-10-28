import React from 'react'
import { Sparkles, RefreshCw } from 'lucide-react'

interface DemoModeBadgeProps {
  onRetryRealApi?: () => void
  isRetrying?: boolean
}

export const DemoModeBadge: React.FC<DemoModeBadgeProps> = ({ onRetryRealApi, isRetrying }) => {
  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 rounded-xl border border-amber-300 bg-amber-50 px-4 py-2.5 text-xs text-amber-900 shadow-sm dark:border-amber-800 dark:bg-amber-950/60 dark:text-amber-200">
      <div className="flex items-center space-x-2">
        <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-amber-200/80 text-amber-800 dark:bg-amber-900 dark:text-amber-300">
          <Sparkles className="h-3.5 w-3.5" />
        </span>
        <div>
          <span className="font-bold tracking-wide uppercase">
            DEMO DATA — NOT A LIVE API RESPONSE
          </span>
          <span className="hidden md:inline ml-2 text-[11px] text-amber-700 dark:text-amber-300">
            • Displaying verified synthetic Bank Muscat fixtures. No live API extraction was claimed.
          </span>
        </div>
      </div>

      {onRetryRealApi && (
        <button
          onClick={onRetryRealApi}
          disabled={isRetrying}
          className="inline-flex items-center space-x-1.5 rounded-lg border border-amber-400/80 bg-white px-2.5 py-1 text-[11px] font-semibold text-amber-900 hover:bg-amber-100/60 disabled:opacity-50 dark:border-amber-700 dark:bg-amber-900 dark:text-amber-100"
        >
          <RefreshCw className={`h-3 w-3 ${isRetrying ? 'animate-spin' : ''}`} />
          <span>{isRetrying ? 'Connecting...' : 'Attempt Live Extraction'}</span>
        </button>
      )}
    </div>
  )
}
