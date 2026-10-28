import React from 'react'
import { RowSummaryMetrics } from '../../utils/analytics'
import { formatAmountOnly } from '../../utils/currency'

interface SummaryCardsProps {
  metrics: RowSummaryMetrics
  currency?: string
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ metrics, currency = 'OMR' }) => {
  const netFlowSign = metrics.netFlow > 0 ? '+' : ''

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* 1. Total Credits */}
      <div className="fintech-card p-5 bg-white shadow-xs">
        <div className="text-xs font-medium text-[#55657A]">
          Total credits
        </div>
        <div className="mt-2 text-2xl sm:text-[28px] font-bold tracking-tight text-[#0B7A4B] font-mono">
          {formatAmountOnly(metrics.totalCredits, currency)}
        </div>
        <div className="mt-1 text-xs text-[#55657A]">
          {currency} · {metrics.creditCount} transactions
        </div>
      </div>

      {/* 2. Total Debits */}
      <div className="fintech-card p-5 bg-white shadow-xs">
        <div className="text-xs font-medium text-[#55657A]">
          Total debits
        </div>
        <div className="mt-2 text-2xl sm:text-[28px] font-bold tracking-tight text-[#B42318] font-mono">
          {formatAmountOnly(metrics.totalDebits, currency)}
        </div>
        <div className="mt-1 text-xs text-[#55657A]">
          {currency} · {metrics.debitCount} transactions
        </div>
      </div>

      {/* 3. Net Flow */}
      <div className="fintech-card p-5 bg-white shadow-xs">
        <div className="text-xs font-medium text-[#55657A]">
          Net flow
        </div>
        <div className="mt-2 text-2xl sm:text-[28px] font-bold tracking-tight text-[#0B2545] font-mono">
          {netFlowSign}{formatAmountOnly(metrics.netFlow, currency)}
        </div>
        <div className="mt-1 text-xs text-[#55657A] truncate">
          Opening {formatAmountOnly(metrics.openingBalance, currency)} → closing {formatAmountOnly(metrics.closingBalance, currency)}
        </div>
      </div>

      {/* 4. Needs Review (Amber Card) */}
      <div className="rounded-[14px] border border-[#F0D58C] bg-[#FFF8E6] p-5 shadow-xs">
        <div className="text-xs font-medium text-[#6B4200]">
          Needs review
        </div>
        <div className="mt-2 text-2xl sm:text-[28px] font-bold tracking-tight text-[#6B4200] font-mono">
          {metrics.needsReviewCount} {metrics.needsReviewCount === 1 ? 'row' : 'rows'}
        </div>
        <div className="mt-1 text-xs text-[#6B4200]">
          {metrics.needsReviewCount > 0
            ? 'Low-confidence amount detected'
            : 'All rows verified and reconciled'}
        </div>
      </div>
    </div>
  )
}
