import React from 'react'
import {
  X,
  History,
  CheckCircle2,
  AlertTriangle,
  Trash2,
  Calendar,
  Layers,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react'
import { HistoryItem } from '../../types'
import { formatCurrency } from '../../utils/currency'
import { formatDate } from '../../utils/dates'

interface HistoryDrawerProps {
  isOpen: boolean
  onClose: () => void
  historyItems: HistoryItem[]
  onRestoreItem: (item: HistoryItem) => void
  onDeleteItem: (id: string) => void
  onClearHistory: () => void
  isHistoryEnabled: boolean
  onToggleHistoryEnabled: (enabled: boolean) => void
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  isOpen,
  onClose,
  historyItems,
  onRestoreItem,
  onDeleteItem,
  onClearHistory,
  isHistoryEnabled,
  onToggleHistoryEnabled,
}) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-sm">
      <div className="relative flex h-full w-full max-w-md flex-col border-l border-slate-200 bg-white shadow-2xl transition-all dark:border-slate-800 dark:bg-slate-900">
        {/* Drawer Header */}
        <div className="flex items-center justify-between border-b border-slate-100 p-5 dark:border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="rounded-xl bg-teal-50 p-2 text-teal-600 dark:bg-teal-950 dark:text-teal-400">
              <History className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                Extraction History
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Last {historyItems.length} extraction sessions
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200"
            aria-label="Close history drawer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Opt-in Privacy Toggle (Phase 13) */}
        <div className="border-b border-slate-100 bg-slate-50/80 p-4 dark:border-slate-800 dark:bg-slate-800/40">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">
                Save history on this device
              </span>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Opt-in caching. Never stores original PDF file bytes.
              </p>
            </div>
            <label className="relative inline-flex cursor-pointer items-center">
              <input
                type="checkbox"
                checked={isHistoryEnabled}
                onChange={(e) => onToggleHistoryEnabled(e.target.checked)}
                className="peer sr-only"
              />
              <div className="peer h-5 w-9 rounded-full bg-slate-300 after:absolute after:left-[2px] after:top-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-all after:content-[''] peer-checked:bg-teal-600 peer-checked:after:translate-x-full peer-focus:outline-none dark:bg-slate-700"></div>
            </label>
          </div>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto p-5 space-y-3">
          {!isHistoryEnabled ? (
            <div className="flex h-64 flex-col items-center justify-center text-center text-slate-400 p-4">
              <ShieldAlert className="h-10 w-10 text-slate-300 dark:text-slate-600" />
              <p className="mt-2 text-xs font-semibold">Local History Disabled</p>
              <p className="mt-1 text-[11px] text-slate-400 dark:text-slate-500">
                Enable "Save history on this device" above to store session tables locally.
              </p>
            </div>
          ) : historyItems.length === 0 ? (
            <div className="flex h-64 flex-col items-center justify-center text-center text-slate-400 p-4">
              <History className="h-10 w-10 text-slate-300 dark:text-slate-600" />
              <p className="mt-2 text-xs font-semibold">No recent extraction sessions</p>
              <p className="mt-1 text-[11px] text-slate-400 dark:text-slate-500">
                Processed statements will be cached here automatically.
              </p>
            </div>
          ) : (
            historyItems.map((item) => (
              <div
                key={item.id}
                className="group relative flex flex-col justify-between rounded-xl border border-slate-200 bg-slate-50/60 p-4 transition hover:border-teal-500 hover:bg-white hover:shadow-md dark:border-slate-800 dark:bg-slate-800/40 dark:hover:border-teal-400 dark:hover:bg-slate-800"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-1.5">
                      <span className="font-semibold text-slate-900 dark:text-white">
                        {item.bankName || 'Bank Statement'}
                      </span>
                      {item.isDemo && (
                        <span className="rounded bg-amber-100 px-1.5 py-0.2 text-[9px] font-bold text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                          Demo
                        </span>
                      )}
                    </div>
                    <p className="truncate text-xs text-slate-500 dark:text-slate-400">
                      {item.fileName}
                    </p>
                  </div>
                  <div className="flex items-center space-x-1">
                    {item.reconciled ? (
                      <span className="inline-flex items-center space-x-1 rounded bg-emerald-100 px-1.5 py-0.5 text-[10px] font-bold text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                        <CheckCircle2 className="h-3 w-3" />
                        <span>Reconciled</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-bold text-amber-800 dark:bg-amber-950 dark:text-amber-300">
                        <AlertTriangle className="h-3 w-3" />
                        <span>Review</span>
                      </span>
                    )}
                    <button
                      onClick={() => onDeleteItem(item.id)}
                      className="rounded p-1 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400"
                      title="Delete session"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>

                <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-slate-600 dark:text-slate-400">
                  <div className="flex items-center space-x-1.5">
                    <Layers className="h-3.5 w-3.5 text-slate-400" />
                    <span>{item.transactionCount} transactions</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <Calendar className="h-3.5 w-3.5 text-slate-400" />
                    <span>{formatDate(item.timestamp)}</span>
                  </div>
                </div>

                <div className="mt-2 flex items-center justify-between border-t border-slate-200/60 pt-2 text-xs dark:border-slate-700/60">
                  <span className="font-mono text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                    Net: {formatCurrency(item.netChange, item.currency)}
                  </span>
                  <button
                    onClick={() => {
                      onRestoreItem(item)
                      onClose()
                    }}
                    className="inline-flex items-center space-x-1 text-xs font-bold text-teal-600 hover:text-teal-700 dark:text-teal-400 dark:hover:text-teal-300"
                  >
                    <span>Restore Session</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Drawer Footer */}
        {isHistoryEnabled && historyItems.length > 0 && (
          <div className="border-t border-slate-100 p-4 dark:border-slate-800">
            <button
              onClick={onClearHistory}
              className="flex w-full items-center justify-center space-x-1.5 rounded-xl border border-slate-200 bg-white py-2 text-xs font-semibold text-rose-600 transition hover:bg-rose-50 dark:border-slate-800 dark:bg-slate-900 dark:hover:bg-rose-950/30"
            >
              <Trash2 className="h-3.5 w-3.5" />
              <span>Clear All History</span>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
