import React from 'react'
import { Edit2, Trash2, AlertTriangle } from 'lucide-react'
import { Transaction, KnownCategory } from '../../types'
import { formatDate } from '../../utils/dates'
import { formatAmountOnly, CATEGORY_COLORS } from '../../utils/currency'

interface TransactionRowProps {
  tx: Transaction
  index: number
  currency: string
  isEditing: boolean
  editFormData: Partial<Transaction>
  onEditChange: (field: keyof Transaction, val: unknown) => void
  onStartEdit: (tx: Transaction) => void
  onSaveEdit: (rowId: string) => void
  onCancelEdit: () => void
  onDeleteRow: (rowId: string) => void
  onCategoryChange: (rowId: string, category: string) => void
}

const ALL_CATEGORIES: KnownCategory[] = [
  'INCOME_SALARY',
  'TRANSFER_P2P',
  'MERCHANT_POS',
  'UTILITIES_SERVICES',
  'ATM_CASH',
  'BANK_FEES',
  'INVESTMENT_DIVIDEND',
  'LOAN_MORTGAGE',
  'TAX_GOVERNMENT',
  'OTHER',
]

export const TransactionRow: React.FC<TransactionRowProps> = ({
  tx,
  index,
  currency,
  isEditing,
  editFormData,
  onEditChange,
  onStartEdit,
  onSaveEdit,
  onCancelEdit,
  onDeleteRow,
  onCategoryChange,
}) => {
  const rowId = tx._id || `${tx.description}_${tx.date}_${index}`
  const catStyle = CATEGORY_COLORS[tx.category || 'OTHER'] || CATEGORY_COLORS.OTHER

  const isLowConfidence =
    tx._categoryConfidence !== null &&
    tx._categoryConfidence !== undefined &&
    tx._categoryConfidence < 0.65

  return (
    <tr
      className={`group transition hover:bg-slate-50/80 dark:hover:bg-slate-800/40 ${
        isLowConfidence
          ? 'bg-amber-50/20 dark:bg-amber-950/10'
          : tx._isEdited
          ? 'bg-teal-50/20 dark:bg-teal-950/10'
          : ''
      }`}
    >
      {/* Date */}
      <td className="whitespace-nowrap px-4 py-3 font-mono text-[11px] text-slate-700 dark:text-slate-300">
        {isEditing ? (
          <input
            type="text"
            value={editFormData.date || ''}
            onChange={(e) => onEditChange('date', e.target.value)}
            className="w-24 rounded border border-slate-300 bg-white px-1.5 py-0.5 text-xs text-slate-900 outline-none focus:border-teal-500 dark:border-slate-600 dark:bg-slate-800 dark:text-white"
          />
        ) : (
          <span>{formatDate(tx.date)}</span>
        )}
      </td>

      {/* Value Date */}
      <td className="whitespace-nowrap px-3 py-3 font-mono text-[11px] text-slate-500 dark:text-slate-400">
        {isEditing ? (
          <input
            type="text"
            value={editFormData.value_date || ''}
            placeholder="YYYY-MM-DD"
            onChange={(e) => onEditChange('value_date', e.target.value || null)}
            className="w-24 rounded border border-slate-300 bg-white px-1.5 py-0.5 text-xs text-slate-900 outline-none focus:border-teal-500 dark:border-slate-600 dark:bg-slate-800 dark:text-white"
          />
        ) : (
          <span>{tx.value_date ? formatDate(tx.value_date) : '—'}</span>
        )}
      </td>

      {/* Narrative / Description */}
      <td className="px-4 py-3">
        {isEditing ? (
          <input
            type="text"
            value={editFormData.description || ''}
            onChange={(e) => onEditChange('description', e.target.value)}
            className="w-full rounded border border-slate-300 bg-white px-2 py-0.5 text-xs text-slate-900 outline-none focus:border-teal-500 dark:border-slate-600 dark:bg-slate-800 dark:text-white"
          />
        ) : (
          <div>
            <div className="font-medium text-slate-900 dark:text-white">{tx.description}</div>
            <div className="flex items-center space-x-2 text-[10px] text-slate-400">
              {tx.channel && <span>Channel: {tx.channel}</span>}
              {tx.reference_id && <span>• Ref: {tx.reference_id}</span>}
              {tx._isEdited && (
                <span className="font-semibold text-teal-600 dark:text-teal-400">• Edited</span>
              )}
            </div>
          </div>
        )}
      </td>

      {/* Debit Column (Derived from amount & direction === 'debit') */}
      <td className="whitespace-nowrap px-4 py-3 text-right font-mono font-medium text-rose-600 dark:text-rose-400">
        {isEditing ? (
          <input
            type="number"
            step="0.001"
            value={editFormData.direction === 'debit' ? editFormData.amount || '' : ''}
            placeholder="0.000"
            onChange={(e) => {
              const val = Math.abs(parseFloat(e.target.value) || 0)
              onEditChange('amount', val)
              onEditChange('direction', 'debit')
            }}
            className="w-20 rounded border border-slate-300 bg-white px-1.5 py-0.5 text-right text-xs outline-none focus:border-teal-500 dark:border-slate-600 dark:bg-slate-800"
          />
        ) : tx.direction === 'debit' ? (
          <span>{formatAmountOnly(tx.amount, currency)}</span>
        ) : (
          <span className="text-slate-300 dark:text-slate-700">—</span>
        )}
      </td>

      {/* Credit Column (Derived from amount & direction === 'credit') */}
      <td className="whitespace-nowrap px-4 py-3 text-right font-mono font-medium text-emerald-600 dark:text-emerald-400">
        {isEditing ? (
          <input
            type="number"
            step="0.001"
            value={editFormData.direction === 'credit' ? editFormData.amount || '' : ''}
            placeholder="0.000"
            onChange={(e) => {
              const val = Math.abs(parseFloat(e.target.value) || 0)
              onEditChange('amount', val)
              onEditChange('direction', 'credit')
            }}
            className="w-20 rounded border border-slate-300 bg-white px-1.5 py-0.5 text-right text-xs outline-none focus:border-teal-500 dark:border-slate-600 dark:bg-slate-800"
          />
        ) : tx.direction === 'credit' ? (
          <span>{formatAmountOnly(tx.amount, currency)}</span>
        ) : (
          <span className="text-slate-300 dark:text-slate-700">—</span>
        )}
      </td>

      {/* Running Balance */}
      <td className="whitespace-nowrap px-4 py-3 text-right font-mono text-slate-800 dark:text-slate-200">
        {isEditing ? (
          <input
            type="number"
            step="0.001"
            value={editFormData.balance ?? ''}
            onChange={(e) =>
              onEditChange('balance', e.target.value ? parseFloat(e.target.value) : null)
            }
            className="w-20 rounded border border-slate-300 bg-white px-1.5 py-0.5 text-right text-xs outline-none focus:border-teal-500 dark:border-slate-600 dark:bg-slate-800"
          />
        ) : tx.balance !== null && tx.balance !== undefined ? (
          <span>{formatAmountOnly(tx.balance, currency)}</span>
        ) : (
          <span className="text-slate-300 dark:text-slate-700">—</span>
        )}
      </td>

      {/* Category Chip & Manual Re-categorization Dropdown */}
      <td className="whitespace-nowrap px-4 py-3">
        <div className="flex items-center space-x-1.5">
          <select
            value={tx.category || 'OTHER'}
            onChange={(e) => onCategoryChange(rowId, e.target.value)}
            className={`rounded-lg border px-2 py-0.5 text-[11px] font-semibold outline-none transition ${catStyle.bg} ${catStyle.text} ${catStyle.border || 'border-slate-200'}`}
          >
            {ALL_CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {CATEGORY_COLORS[cat]?.label || cat}
              </option>
            ))}
          </select>

          {/* Category Confidence Badge (Phase 8.2) */}
          {tx._categoryConfidence !== null && tx._categoryConfidence !== undefined && (
            <span
              className={`rounded px-1.5 py-0.2 text-[10px] font-mono font-bold ${
                tx._categoryConfidence >= 0.8
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                  : tx._categoryConfidence >= 0.6
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                  : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
              }`}
              title={`NLP Category Confidence: ${Math.round(tx._categoryConfidence * 100)}%`}
            >
              {Math.round(tx._categoryConfidence * 100)}%
            </span>
          )}

          {isLowConfidence && (
            <span className="text-amber-500" title="Low category confidence: please review">
              <AlertTriangle className="h-3 w-3" />
            </span>
          )}
        </div>
      </td>

      {/* Channel */}
      <td className="whitespace-nowrap px-3 py-3 font-mono text-[11px] text-slate-500 dark:text-slate-400">
        {tx.channel || '—'}
      </td>

      {/* Actions */}
      <td className="whitespace-nowrap px-4 py-3 text-right">
        {isEditing ? (
          <div className="flex items-center justify-end space-x-1.5">
            <button
              onClick={() => onSaveEdit(rowId)}
              className="rounded bg-teal-600 px-2 py-0.5 text-[10px] font-bold text-white hover:bg-teal-700"
            >
              Save
            </button>
            <button
              onClick={onCancelEdit}
              className="rounded border border-slate-300 px-2 py-0.5 text-[10px] font-semibold text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300"
            >
              Cancel
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-end space-x-1 opacity-60 transition group-hover:opacity-100">
            <button
              onClick={() => onStartEdit(tx)}
              className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-200"
              title="Edit row inline"
            >
              <Edit2 className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => onDeleteRow(rowId)}
              className="rounded p-1 text-slate-400 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/50 dark:hover:text-rose-400"
              title="Delete row"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        )}
      </td>
    </tr>
  )
}
