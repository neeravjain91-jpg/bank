import React from 'react'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import { Row } from '../../types'
import {
  calculateSpendingByCategory,
  calculateBalanceHistory,
} from '../../utils/analytics'
import { formatAmountOnly } from '../../utils/currency'

interface InsightsRowProps {
  rows: Row[]
  openingBalance?: number
  currency?: string
}

export const InsightsRow: React.FC<InsightsRowProps> = ({
  rows,
  openingBalance = 1562.45,
  currency = 'OMR',
}) => {
  const { totalSpent, items: categoryItems } = calculateSpendingByCategory(rows)
  const balancePoints = calculateBalanceHistory(rows, openingBalance)

  // Format tick numbers for Y axis (e.g. 3,200, 3,350, 3,500)
  const yDomain = [
    Math.floor(Math.min(...balancePoints.map((p) => p.balance), 3200) / 100) * 100,
    Math.ceil(Math.max(...balancePoints.map((p) => p.balance), 3500) / 100) * 100,
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* 1. Spending by Category Card */}
      <div className="fintech-card bg-white p-5 shadow-xs flex flex-col">
        <div>
          <h2 className="text-base font-bold text-[#0B2545] font-['IBM_Plex_Sans']">
            Spending by category
          </h2>
          <p className="text-xs text-[#55657A]">
            Debits only · {currency}
          </p>
        </div>

        <div className="mt-4 flex flex-col sm:flex-row items-center justify-between gap-6 flex-1 min-h-[220px]">
          {/* Donut Chart with Centered Total */}
          <div className="relative w-52 h-52 shrink-0 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryItems}
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={92}
                  paddingAngle={2}
                  dataKey="amount"
                  isAnimationActive={false}
                >
                  {categoryItems.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="#ffffff" strokeWidth={2} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>

            {/* Centered Donut Label */}
            <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-lg font-bold text-[#0B2545] font-mono leading-tight">
                {formatAmountOnly(totalSpent, currency)}
              </span>
              <span className="text-[11px] text-[#55657A] font-medium">
                total spent
              </span>
            </div>
          </div>

          {/* Legend Listing */}
          <div className="flex-1 w-full flex flex-col justify-center space-y-2.5">
            {categoryItems.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span
                    className="h-2.5 w-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: item.color }}
                  ></span>
                  <span className="font-medium text-[#0B2545]">{item.name}</span>
                </div>
                <div className="flex items-center space-x-3 font-mono">
                  <span className="text-[#0B2545] font-medium">
                    {formatAmountOnly(item.amount, currency)}
                  </span>
                  <span className="w-11 text-right text-[#55657A]">
                    {item.percent.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 2. Running Balance Card */}
      <div className="fintech-card bg-white p-5 shadow-xs flex flex-col">
        <div>
          <h2 className="text-base font-bold text-[#0B2545] font-['IBM_Plex_Sans']">
            Running balance
          </h2>
          <p className="text-xs text-[#55657A]">
            After each transaction · {currency}
          </p>
        </div>

        <div className="mt-4 flex-1 w-full min-h-[220px]">
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={balancePoints} margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
              <defs>
                <linearGradient id="balanceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0E7C86" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#0E7C86" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#EAEFF4" />
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={{ stroke: '#DDE3EA' }}
                tick={{ fontSize: 11, fill: '#55657A' }}
                dy={6}
              />
              <YAxis
                domain={yDomain}
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 11, fill: '#55657A', fontFamily: 'IBM Plex Mono' }}
                tickFormatter={(val) => Math.round(val).toLocaleString()}
                dx={-6}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload as { date: string; balance: number }
                    return (
                      <div className="rounded-lg border border-[#DDE3EA] bg-white p-2.5 text-xs shadow-md">
                        <div className="font-medium text-[#55657A]">{data.date}</div>
                        <div className="mt-1 font-mono font-bold text-[#0E7C86]">
                          {formatAmountOnly(data.balance, currency)} {currency}
                        </div>
                      </div>
                    )
                  }
                  return null
                }}
              />
              <Area
                type="monotone"
                dataKey="balance"
                stroke="#0E7C86"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#balanceGradient)"
                dot={{ r: 3.5, fill: '#0E7C86', stroke: '#ffffff', strokeWidth: 1.5 }}
                activeDot={{ r: 5, fill: '#0E7C86', stroke: '#ffffff', strokeWidth: 2 }}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
