import React from 'react'
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts'
import { CategoryMetric } from '../../types'
import { formatCurrency, CATEGORY_COLORS } from '../../utils/currency'

interface CategoryDonutChartProps {
  data: CategoryMetric[]
  currency: string
}

export const CategoryDonutChart: React.FC<CategoryDonutChartProps> = ({ data, currency }) => {
  if (data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-xs text-slate-400">
        No categorized transactions available
      </div>
    )
  }

  const chartData = data.map((d) => ({
    name: d.label,
    value: d.total,
    count: d.count,
    color: CATEGORY_COLORS[d.category]?.chartColor || '#94a3b8',
  }))

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={3}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: any) => [formatCurrency(Number(value), currency), 'Spending']}
            contentStyle={{
              backgroundColor: '#0f172a',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '12px',
              border: 'none',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
