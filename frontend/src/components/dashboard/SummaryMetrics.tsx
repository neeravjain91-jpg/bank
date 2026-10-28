import React from 'react'
import {
  TrendingUp,
  TrendingDown,
  Scale,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react'
import { FinancialSummary } from '../../types'
import { formatCurrency, formatAmountOnly } from '../../utils/currency'

interface SummaryMetricsProps {
  summary: FinancialSummary
  currency: string
}

export const SummaryMetrics: React.FC<SummaryMetricsProps> = ({ summary, currency }) => {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {/* Total Credits */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
            Total Deposits (Credits)
          </span>
          <div className="rounded-xl bg-emerald-50 p-2 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
            <TrendingUp className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 font-mono text-xl font-bold text-slate-900 dark:text-white">
          {formatCurrency(summary.totalCredits, currency)}
        </div>
        <div className="mt-1 flex items-center space-x-1.5 text-xs text-slate-500 dark:text-slate-400">
          <span className="font-semibold text-emerald-600 dark:text-emerald-400">
            {summary.creditCount} transactions
          </span>
          <span>inflow</span>
        </div>
      </div>

      {/* Total Debits */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
            Total Withdrawals (Debits)
          </span>
          <div className="rounded-xl bg-rose-50 p-2 text-rose-600 dark:bg-rose-950 dark:text-rose-400">
            <TrendingDown className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 font-mono text-xl font-bold text-slate-900 dark:text-white">
          {formatCurrency(summary.totalDebits, currency)}
        </div>
        <div className="mt-1 flex items-center space-x-1.5 text-xs text-slate-500 dark:text-slate-400">
          <span className="font-semibold text-rose-600 dark:text-rose-400">
            {summary.debitCount} transactions
          </span>
          <span>outflow</span>
        </div>
      </div>

      {/* Net Flow */}
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
            Net Cash Flow
          </span>
          <div
            className={`rounded-xl p-2 ${
              summary.netFlow >= 0
                ? 'bg-teal-50 text-teal-600 dark:bg-teal-950 dark:text-teal-400'
                : 'bg-rose-50 text-rose-600 dark:bg-rose-950 dark:text-rose-400'
            }`}
          >
            <Scale className="h-4 w-4" />
          </div>
        </div>
        <div
          className={`mt-3 font-mono text-xl font-bold ${
            summary.netFlow >= 0
              ? 'text-teal-700 dark:text-teal-300'
              : 'text-rose-600 dark:text-rose-400'
          }`}
        >
          {summary.netFlow >= 0 ? '+' : ''}
          {formatCurrency(summary.netFlow, currency)}
        </div>
        <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          Total Credits minus Debits
        </div>
      </div>

      {/* Reconciliation Status Card (Phase 8.3 & 11.1) */}
      <div
        className={`rounded-2xl border p-5 shadow-sm transition ${
          summary.isReconciled
            ? 'border-emerald-200 bg-emerald-50/40 dark:border-emerald-900/60 dark:bg-emerald-950/20'
            : 'border-amber-300 bg-amber-50/50 dark:border-amber-900/60 dark:bg-amber-950/20'
        }`}
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">
            Reconciliation Proof
          </span>
          {summary.isReconciled ? (
            <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
          ) : (
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          )}
        </div>
        <div className="mt-2 flex items-center space-x-2">
          <span
            className={`rounded-md px-2 py-0.5 text-xs font-bold ${
              summary.isReconciled
                ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200'
                : 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200'
            }`}
          >
            {summary.isReconciled ? 'RECONCILED' : 'DISCREPANCY'}
          </span>
          {summary.isModifiedAfterExtraction && (
            <span className="rounded bg-teal-100 px-1.5 py-0.5 text-[10px] font-semibold text-teal-800 dark:bg-teal-900 dark:text-teal-200">
              User Modified
            </span>
          )}
        </div>
        <div className="mt-2 text-[11px] text-slate-600 dark:text-slate-400 font-mono">
          {summary.openingBalance !== null && summary.closingBalance !== null
            ? `${formatAmountOnly(summary.openingBalance, currency)} + ${formatAmountOnly(
                summary.totalCredits,
                currency
              )} - ${formatAmountOnly(summary.totalDebits, currency)} = ${formatAmountOnly(
                summary.calculatedClosingBalance,
                currency
              )}`
            : 'Zero running balance errors detected'}
        </div>
      </div>
    </div>
  )
}
