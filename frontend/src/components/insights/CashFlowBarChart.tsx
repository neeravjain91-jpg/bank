import React from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import { DailyCashFlow } from '../../types'
import { formatCurrency, formatAmountOnly } from '../../utils/currency'
import { formatDate } from '../../utils/dates'

interface CashFlowBarChartProps {
  data: DailyCashFlow[]
  currency: string
}

export const CashFlowBarChart: React.FC<CashFlowBarChartProps> = ({ data, currency }) => {
  if (data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-xs text-slate-400">
        No chronological cash flow data available
      </div>
    )
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
          <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={(d) => formatDate(d)} />
          <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => formatAmountOnly(v, currency)} />
          <Tooltip
            formatter={(value: any, name: any) => [
              formatCurrency(Number(value), currency),
              name === 'credits' ? 'Deposits (+)' : 'Withdrawals (-)',
            ]}
            labelFormatter={(label) => `Date: ${formatDate(String(label))}`}
            contentStyle={{
              backgroundColor: '#0f172a',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '12px',
              border: 'none',
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: '11px' }}
            formatter={(val) => (val === 'credits' ? 'Deposits (+)' : 'Withdrawals (-)')}
          />
          <Bar dataKey="credits" fill="#10b981" name="credits" radius={[4, 4, 0, 0]} />
          <Bar dataKey="debits" fill="#f43f5e" name="debits" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
