import React, { useState } from 'react'
import { Search, Sparkles, Download, FileSpreadsheet, FileCode, Check, AlertTriangle } from 'lucide-react'
import { Row } from '../../types'
import { formatAmountOnly, getCategoryStyle } from '../../utils/currency'
import { exportRowsToCsv, exportRowsToExcel, exportToJson } from '../../utils/exports'

interface ExtractedTransactionsCardProps {
  rows: Row[]
  onUpdateRows: (updated: Row[]) => void
  onCategorize: () => void
  isCategorizing: boolean
  currency?: string
  isSampleData?: boolean
  onShowToast: (title: string, message: string) => void
}

export const ExtractedTransactionsCard: React.FC<ExtractedTransactionsCardProps> = ({
  rows,
  onUpdateRows,
  onCategorize,
  isCategorizing,
  currency = 'OMR',
  isSampleData = true,
  onShowToast,
}) => {
  const [activeFilter, setActiveFilter] = useState<'all' | 'needsReview'>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [editingRowId, setEditingRowId] = useState<string | null>(null)
  const [editFormData, setEditFormData] = useState<Partial<Row>>({})

  const needsReviewCount = rows.filter((r) => r.needsReview).length

  // Filter rows
  const filteredRows = rows.filter((r) => {
    if (activeFilter === 'needsReview' && !r.needsReview) return false
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase()
      const descMatch = r.description.toLowerCase().includes(q)
      const dateMatch = r.date.toLowerCase().includes(q)
      const catMatch = (r.category || '').toLowerCase().includes(q)
      return descMatch || dateMatch || catMatch
    }
    return true
  })

  // Start inline editing
  const handleStartEdit = (row: Row) => {
    setEditingRowId(row.id)
    setEditFormData({ ...row })
  }

  // Save inline editing
  const handleSaveEdit = (rowId: string) => {
    const updated = rows.map((r) => {
      if (r.id === rowId) {
        return {
          ...r,
          ...editFormData,
          isEdited: true,
          // If user manually updated and approved, clear needsReview or keep depending on user edit
        }
      }
      return r
    })
    onUpdateRows(updated)
    setEditingRowId(null)
    onShowToast('Row Updated', 'Transaction updated and financial metrics recalculated.')
  }

  // Export handlers
  const handleExportCsv = () => {
    exportRowsToCsv(rows, 'bank_statement_transactions.csv')
    onShowToast('Exported CSV', 'Transaction records exported as RFC 4180 CSV.')
  }

  const handleExportExcel = () => {
    exportRowsToExcel(rows, 'bank_statement_transactions.xlsx')
    onShowToast('Exported Excel', 'Worksheet exported as .xlsx format.')
  }

  const handleExportJson = () => {
    exportToJson(rows, 'bank_statement_transactions.json')
    onShowToast('Exported JSON', 'Full JSON payload exported to downloads.')
  }

  const allCategories = [
    'Income',
    'Groceries',
    'Utilities',
    'Transport',
    'Cash',
    'Transfers',
    'Dining',
    'Other',
  ]

  return (
    <div className="fintech-card bg-white p-5 shadow-xs flex flex-col h-full">
      {/* Header with Title and Controls */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between pb-3">
        <div>
          <h2 className="text-base font-bold text-[#0B2545] font-['IBM_Plex_Sans']">
            Extracted transactions
          </h2>
          <p className="text-xs text-[#55657A]">
            Click any cell to correct it before exporting
          </p>
        </div>

        {/* Right: Segmented control & Search */}
        <div className="flex items-center flex-wrap gap-2">
          {/* Segmented Toggle: All vs Needs review */}
          <div className="flex items-center rounded-lg border border-[#DDE3EA] bg-[#F3F6F9] p-0.5 text-xs font-semibold">
            <button
              onClick={() => setActiveFilter('all')}
              className={`rounded-md px-3 py-1 transition ${
                activeFilter === 'all'
                  ? 'bg-white text-[#0B2545] shadow-xs'
                  : 'text-[#55657A] hover:text-[#0B2545]'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setActiveFilter('needsReview')}
              className={`rounded-md px-2.5 py-1 transition flex items-center space-x-1.5 ${
                activeFilter === 'needsReview'
                  ? 'bg-white text-[#6B4200] shadow-xs'
                  : 'text-[#55657A] hover:text-[#0B2545]'
              }`}
            >
              <span>Needs review</span>
              <span className="rounded-full bg-[#FFF1D6] px-1.5 py-0.2 text-[10px] text-[#7A4A00] font-bold">
                {needsReviewCount}
              </span>
            </button>
          </div>

          {/* Search Input */}
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-2.5 h-3.5 w-3.5 text-[#55657A]" />
            <input
              type="text"
              placeholder="Search description"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-36 sm:w-44 rounded-lg border border-[#DDE3EA] bg-white py-1.5 pl-8 pr-2.5 text-xs text-[#0B2545] placeholder-[#55657A] outline-none focus:border-[#0E7C86] transition"
            />
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div className="relative mt-2 flex-1 overflow-x-auto rounded-[10px] border border-[#DDE3EA]">
        <table className="w-full border-collapse text-left text-xs">
          <thead>
            <tr className="border-b border-[#DDE3EA] bg-[#F9FBFC] text-[11px] font-semibold text-[#55657A] uppercase tracking-wider">
              <th className="px-3.5 py-2.5">Date</th>
              <th className="px-3.5 py-2.5">Description</th>
              <th className="px-3.5 py-2.5 text-right font-mono">Debit</th>
              <th className="px-3.5 py-2.5 text-right font-mono">Credit</th>
              <th className="px-3.5 py-2.5 text-right font-mono">Balance</th>
              <th className="px-3.5 py-2.5">Category</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#DDE3EA] bg-white">
            {filteredRows.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-xs text-[#55657A]">
                  No transactions match the selected filter.
                </td>
              </tr>
            ) : (
              filteredRows.map((row) => {
                const isEditing = editingRowId === row.id
                const isAmberRow = row.needsReview && !isEditing
                const catStyle = getCategoryStyle(row.category)

                return (
                  <tr
                    key={row.id}
                    onClick={() => !isEditing && handleStartEdit(row)}
                    className={`transition cursor-pointer ${
                      isAmberRow
                        ? 'bg-[#FFF8E6] hover:bg-[#FFF3D1]'
                        : 'hover:bg-slate-50'
                    }`}
                  >
                    {/* Date */}
                    <td className="whitespace-nowrap px-3.5 py-2.5 text-[#55657A] font-medium">
                      {isEditing ? (
                        <input
                          type="text"
                          value={editFormData.date || ''}
                          onChange={(e) =>
                            setEditFormData({ ...editFormData, date: e.target.value })
                          }
                          className="w-24 rounded border border-[#0E7C86] px-1.5 py-0.5 text-xs"
                          onClick={(e) => e.stopPropagation()}
                        />
                      ) : (
                        row.date
                      )}
                    </td>

                    {/* Description */}
                    <td className="px-3.5 py-2.5 font-medium text-[#0B2545]">
                      {isEditing ? (
                        <div className="flex items-center space-x-1" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="text"
                            value={editFormData.description || ''}
                            onChange={(e) =>
                              setEditFormData({ ...editFormData, description: e.target.value })
                            }
                            className="w-full rounded border border-[#0E7C86] px-2 py-0.5 text-xs"
                          />
                          <button
                            onClick={() => handleSaveEdit(row.id)}
                            className="rounded bg-[#0E7C86] p-1 text-white hover:bg-[#0B6B74]"
                            title="Save inline edit"
                          >
                            <Check className="h-3 w-3" />
                          </button>
                        </div>
                      ) : (
                        <div className="flex flex-col">
                          <span>{row.description}</span>
                          {row.needsReview && (
                            <span className="mt-1 inline-flex items-center space-x-1 w-max rounded-md border border-[#F0D58C] bg-[#FFF8E6] px-2 py-0.5 text-[10px] font-semibold text-[#6B4200]">
                              <AlertTriangle className="h-2.5 w-2.5 text-[#6B4200]" />
                              <span>Review · low-confidence amount</span>
                            </span>
                          )}
                        </div>
                      )}
                    </td>

                    {/* Debit */}
                    <td className="whitespace-nowrap px-3.5 py-2.5 text-right font-mono font-medium text-[#B42318]">
                      {isEditing ? (
                        <input
                          type="number"
                          step="0.001"
                          value={editFormData.debit ?? ''}
                          onChange={(e) =>
                            setEditFormData({
                              ...editFormData,
                              debit: e.target.value ? parseFloat(e.target.value) : null,
                            })
                          }
                          className="w-20 text-right rounded border border-[#0E7C86] px-1.5 py-0.5 text-xs font-mono"
                          onClick={(e) => e.stopPropagation()}
                        />
                      ) : row.debit !== null && row.debit > 0 ? (
                        formatAmountOnly(row.debit, currency)
                      ) : (
                        '—'
                      )}
                    </td>

                    {/* Credit */}
                    <td className="whitespace-nowrap px-3.5 py-2.5 text-right font-mono font-medium text-[#0B7A4B]">
                      {isEditing ? (
                        <input
                          type="number"
                          step="0.001"
                          value={editFormData.credit ?? ''}
                          onChange={(e) =>
                            setEditFormData({
                              ...editFormData,
                              credit: e.target.value ? parseFloat(e.target.value) : null,
                            })
                          }
                          className="w-20 text-right rounded border border-[#0E7C86] px-1.5 py-0.5 text-xs font-mono"
                          onClick={(e) => e.stopPropagation()}
                        />
                      ) : row.credit !== null && row.credit > 0 ? (
                        formatAmountOnly(row.credit, currency)
                      ) : (
                        '—'
                      )}
                    </td>

                    {/* Balance */}
                    <td className="whitespace-nowrap px-3.5 py-2.5 text-right font-mono font-medium text-[#0B2545]">
                      {isEditing ? (
                        <input
                          type="number"
                          step="0.001"
                          value={editFormData.balance ?? ''}
                          onChange={(e) =>
                            setEditFormData({
                              ...editFormData,
                              balance: e.target.value ? parseFloat(e.target.value) : null,
                            })
                          }
                          className="w-20 text-right rounded border border-[#0E7C86] px-1.5 py-0.5 text-xs font-mono"
                          onClick={(e) => e.stopPropagation()}
                        />
                      ) : (
                        formatAmountOnly(row.balance, currency)
                      )}
                    </td>

                    {/* Category Chip */}
                    <td className="whitespace-nowrap px-3.5 py-2.5">
                      {isEditing ? (
                        <select
                          value={editFormData.category || 'Other'}
                          onChange={(e) =>
                            setEditFormData({ ...editFormData, category: e.target.value })
                          }
                          className="rounded border border-[#0E7C86] px-2 py-0.5 text-xs outline-none"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {allCategories.map((cat) => (
                            <option key={cat} value={cat}>
                              {cat}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span
                          className="inline-block rounded-md px-2.5 py-0.5 text-[11px] font-semibold"
                          style={{ backgroundColor: catStyle.bg, color: catStyle.text }}
                        >
                          {catStyle.label || row.category || 'Other'}
                        </span>
                      )}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Footer with Row Counts & Action Buttons */}
      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between pt-2 border-t border-[#DDE3EA]">
        <div className="text-xs text-[#55657A]">
          Showing 1–{filteredRows.length} of {rows.length} · amounts in {currency}
          {isSampleData && ' · sample data'}
        </div>

        {/* Buttons Group */}
        <div className="flex items-center flex-wrap gap-2">
          {/* Export Buttons */}
          <div className="flex items-center space-x-1.5">
            <button
              onClick={handleExportCsv}
              className="rounded-lg border border-[#DDE3EA] bg-white px-3 py-1.5 text-xs font-semibold text-[#0B2545] shadow-xs hover:bg-slate-50 transition min-h-[38px] flex items-center space-x-1"
            >
              <Download className="h-3 w-3 text-[#55657A]" />
              <span>CSV</span>
            </button>
            <button
              onClick={handleExportExcel}
              className="rounded-lg border border-[#DDE3EA] bg-white px-3 py-1.5 text-xs font-semibold text-[#0B2545] shadow-xs hover:bg-slate-50 transition min-h-[38px] flex items-center space-x-1"
            >
              <FileSpreadsheet className="h-3 w-3 text-emerald-600" />
              <span>Excel</span>
            </button>
            <button
              onClick={handleExportJson}
              className="rounded-lg border border-[#DDE3EA] bg-white px-3 py-1.5 text-xs font-semibold text-[#0B2545] shadow-xs hover:bg-slate-50 transition min-h-[38px] flex items-center space-x-1"
            >
              <FileCode className="h-3 w-3 text-amber-600" />
              <span>JSON</span>
            </button>
          </div>

          {/* Primary Action Button: Categorize Transactions */}
          <button
            onClick={onCategorize}
            disabled={isCategorizing || rows.length === 0}
            className="rounded-lg bg-[#0E7C86] px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-[#0B6B74] transition disabled:opacity-50 min-h-[38px] flex items-center space-x-1.5"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>{isCategorizing ? 'Categorizing...' : 'Categorize transactions'}</span>
          </button>
        </div>
      </div>
    </div>
  )
}
