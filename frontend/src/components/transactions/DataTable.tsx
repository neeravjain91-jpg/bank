import React, { useState, useMemo } from 'react'
import {
  Search,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Plus,
  Sparkles,
  AlertTriangle,
  FileSpreadsheet,
  Download,
  Copy,
  CheckCheck,
  Filter,
  Eye,
  RefreshCw,
  RotateCcw,
  X,
  FileCode,
} from 'lucide-react'
import { Transaction, ExtractionResponse, KnownCategory, FinancialSummary } from '../../types'
import { TransactionRow } from './TransactionRow'
import { exportToCsv, exportToExcel, exportToJson, copyToClipboard } from '../../utils/exports'
import { CATEGORY_COLORS } from '../../utils/currency'

interface DataTableProps {
  transactions: Transaction[]
  onUpdateTransactions: (updated: Transaction[]) => void
  onResetEdits: () => void
  hasEdits: boolean
  onRunCategorization: (useTransformers: boolean) => void
  isCategorizing: boolean
  currency: string
  fullData?: ExtractionResponse
  summary?: FinancialSummary
  viewMode: 'full' | 'split'
  onToggleViewMode: () => void
  onToast: (title: string, desc?: string, type?: 'success' | 'error' | 'info') => void
}

type SortField = 'date' | 'description' | 'debit' | 'credit' | 'balance' | 'category'

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

export const DataTable: React.FC<DataTableProps> = ({
  transactions,
  onUpdateTransactions,
  onResetEdits,
  hasEdits,
  onRunCategorization,
  isCategorizing,
  currency,
  fullData,
  summary,
  viewMode,
  onToggleViewMode,
  onToast,
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortField, setSortField] = useState<SortField>('date')
  const [sortAsc, setSortAsc] = useState<boolean>(true)
  const [directionFilter, setDirectionFilter] = useState<'all' | 'debit' | 'credit'>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [onlyNeedsReview, setOnlyNeedsReview] = useState(false)
  const [pageSize, setPageSize] = useState<number>(10)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [editingRowId, setEditingRowId] = useState<string | null>(null)
  const [editFormData, setEditFormData] = useState<Partial<Transaction>>({})
  const [copied, setCopied] = useState(false)
  const [useTransformers, setUseTransformers] = useState(false)

  // Needs review count
  const needsReviewCount = useMemo(() => {
    return transactions.filter(
      (t) =>
        (t._categoryConfidence !== null &&
          t._categoryConfidence !== undefined &&
          t._categoryConfidence < 0.65) ||
        t._needsReview ||
        t._isNew
    ).length
  }, [transactions])

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc)
    } else {
      setSortField(field)
      setSortAsc(true)
    }
  }

  // Filter & Sort Logic
  const filteredTransactions = useMemo(() => {
    return transactions
      .filter((t) => {
        const matchesSearch =
          t.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          t.date.includes(searchTerm) ||
          t.amount.toString().includes(searchTerm) ||
          (t.reference_id && t.reference_id.toLowerCase().includes(searchTerm.toLowerCase()))

        const matchesDirection = directionFilter === 'all' || t.direction === directionFilter
        const matchesCategory = categoryFilter === 'all' || t.category === categoryFilter
        const matchesReview =
          !onlyNeedsReview ||
          (t._categoryConfidence !== null &&
            t._categoryConfidence !== undefined &&
            t._categoryConfidence < 0.65) ||
          t._needsReview ||
          t._isNew

        return matchesSearch && matchesDirection && matchesCategory && matchesReview
      })
      .sort((a, b) => {
        let valA: unknown = ''
        let valB: unknown = ''

        switch (sortField) {
          case 'date':
            valA = new Date(a.date).getTime()
            valB = new Date(b.date).getTime()
            break
          case 'description':
            valA = a.description.toLowerCase()
            valB = b.description.toLowerCase()
            break
          case 'debit':
            valA = a.direction === 'debit' ? a.amount : 0
            valB = b.direction === 'debit' ? b.amount : 0
            break
          case 'credit':
            valA = a.direction === 'credit' ? a.amount : 0
            valB = b.direction === 'credit' ? b.amount : 0
            break
          case 'balance':
            valA = a.balance ?? 0
            valB = b.balance ?? 0
            break
          case 'category':
            valA = a.category || ''
            valB = b.category || ''
            break
        }

        if (valA! < valB!) return sortAsc ? -1 : 1
        if (valA! > valB!) return sortAsc ? 1 : -1
        return 0
      })
  }, [transactions, searchTerm, sortField, sortAsc, directionFilter, categoryFilter, onlyNeedsReview])

  // Pagination
  const totalPages = Math.ceil(filteredTransactions.length / pageSize) || 1
  const paginatedTransactions = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    return filteredTransactions.slice(start, start + pageSize)
  }, [filteredTransactions, currentPage, pageSize])

  // Start Editing
  const startEdit = (t: Transaction) => {
    setEditingRowId(t._id || `${t.description}_${t.date}`)
    setEditFormData({ ...t })
  }

  const cancelEdit = () => {
    setEditingRowId(null)
    setEditFormData({})
  }

  // Save Inline Edit (Validates non-negative amounts per Phase 8.2)
  const saveEdit = (rowId: string) => {
    const rawAmt = Number(editFormData.amount)
    if (isNaN(rawAmt) || rawAmt <= 0) {
      onToast('Invalid Amount', 'Transaction amount must be a positive number.', 'error')
      return
    }

    const updated = transactions.map((t) => {
      const matchId = t._id || `${t.description}_${t.date}`
      if (matchId === rowId) {
        return {
          ...t,
          ...editFormData,
          amount: Math.abs(rawAmt),
          balance: editFormData.balance !== undefined ? Number(editFormData.balance) : t.balance,
          _isEdited: true,
        } as Transaction
      }
      return t
    })
    onUpdateTransactions(updated)
    setEditingRowId(null)
    setEditFormData({})
    onToast('Row Updated', 'Transaction values updated and totals recalculated.')
  }

  // Delete Row
  const handleDeleteRow = (rowId: string) => {
    const updated = transactions.filter((t) => {
      const matchId = t._id || `${t.description}_${t.date}`
      return matchId !== rowId
    })
    onUpdateTransactions(updated)
    onToast('Row Deleted', 'Recalculated running balance and totals.')
  }

  // Add Transaction Row
  const handleAddNewRow = () => {
    const newTx: Transaction = {
      _id: `custom_${Date.now()}`,
      date: new Date().toISOString().split('T')[0],
      description: 'NEW TRANSACTION ENTRY',
      amount: 10.0,
      direction: 'debit',
      currency,
      balance: null,
      category: 'OTHER',
      _isNew: true,
      _isEdited: true,
    }
    onUpdateTransactions([newTx, ...transactions])
    startEdit(newTx)
  }

  // Change Category
  const handleCategoryChange = (rowId: string, newCat: string) => {
    const updated = transactions.map((t) => {
      const matchId = t._id || `${t.description}_${t.date}`
      if (matchId === rowId) {
        return {
          ...t,
          category: newCat,
          _isEdited: true,
        }
      }
      return t
    })
    onUpdateTransactions(updated)
  }

  // Copy JSON handler
  const handleCopyJson = async () => {
    const ok = await copyToClipboard(JSON.stringify(transactions, null, 2))
    if (ok) {
      setCopied(true)
      onToast('JSON Copied', 'Extracted transaction JSON copied to clipboard.')
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="flex flex-col space-y-4">
      {/* Table Toolbar */}
      <div className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900 sm:flex-row sm:items-center sm:justify-between">
        {/* Left: Search & Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search Input */}
          <div className="relative min-w-[200px] flex-1 sm:w-64">
            <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search narrative, amount, date..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setCurrentPage(1)
              }}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-xs outline-none transition focus:border-teal-500 focus:bg-white dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:border-teal-400"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>

          {/* Direction Filter */}
          <select
            value={directionFilter}
            onChange={(e) => {
              setDirectionFilter(e.target.value as 'all' | 'debit' | 'credit')
              setCurrentPage(1)
            }}
            className="rounded-xl border border-slate-200 bg-slate-50 px-2.5 py-2 text-xs font-medium text-slate-700 outline-none focus:border-teal-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
          >
            <option value="all">All Directions</option>
            <option value="debit">Withdrawals (Debits)</option>
            <option value="credit">Deposits (Credits)</option>
          </select>

          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => {
              setCategoryFilter(e.target.value)
              setCurrentPage(1)
            }}
            className="rounded-xl border border-slate-200 bg-slate-50 px-2.5 py-2 text-xs font-medium text-slate-700 outline-none focus:border-teal-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
          >
            <option value="all">All Categories</option>
            {ALL_CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {CATEGORY_COLORS[cat]?.label || cat}
              </option>
            ))}
          </select>

          {/* Needs Review Filter Toggle */}
          <button
            onClick={() => {
              setOnlyNeedsReview(!onlyNeedsReview)
              setCurrentPage(1)
            }}
            className={`inline-flex items-center space-x-1.5 rounded-xl border px-3 py-2 text-xs font-semibold transition ${
              onlyNeedsReview
                ? 'border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950/60 dark:text-amber-300'
                : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300'
            }`}
          >
            <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
            <span>Needs Review</span>
            {needsReviewCount > 0 && (
              <span className="ml-1 rounded-full bg-amber-200/80 px-1.5 py-0.2 text-[10px] font-bold text-amber-900 dark:bg-amber-900 dark:text-amber-200">
                {needsReviewCount}
              </span>
            )}
          </button>
        </div>

        {/* Right: Actions Bar */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Side-by-Side Split View Toggle */}
          <button
            onClick={onToggleViewMode}
            className={`inline-flex items-center space-x-1.5 rounded-xl border px-3 py-2 text-xs font-semibold transition ${
              viewMode === 'split'
                ? 'border-teal-500 bg-teal-50 text-teal-800 dark:border-teal-500 dark:bg-teal-950/50 dark:text-teal-300'
                : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200'
            }`}
            title="Toggle Side-by-Side source document verification view"
          >
            <Eye className="h-3.5 w-3.5 text-teal-600 dark:text-teal-400" />
            <span>{viewMode === 'split' ? 'Full Table' : 'Split View'}</span>
          </button>

          {/* Reset Unsaved Edits */}
          {hasEdits && (
            <button
              onClick={onResetEdits}
              className="inline-flex items-center space-x-1 rounded-xl border border-rose-200 bg-rose-50 px-2.5 py-2 text-xs font-semibold text-rose-700 hover:bg-rose-100 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-300"
              title="Reset all local row edits back to original extraction state"
            >
              <RotateCcw className="h-3 w-3" />
              <span>Reset Edits</span>
            </button>
          )}

          {/* Add Row Button */}
          <button
            onClick={handleAddNewRow}
            className="inline-flex items-center space-x-1 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
            title="Add a new transaction manually"
          >
            <Plus className="h-3.5 w-3.5 text-slate-500" />
            <span>Add Row</span>
          </button>

          {/* Categorize Button (Phase 9) */}
          <div className="flex items-center rounded-xl border border-teal-200 bg-teal-50 p-0.5 dark:border-teal-800 dark:bg-teal-950/50">
            <button
              onClick={() => onRunCategorization(useTransformers)}
              disabled={isCategorizing}
              className="inline-flex items-center space-x-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-bold text-white shadow-sm transition hover:bg-teal-700 disabled:opacity-50 dark:bg-teal-500 dark:hover:bg-teal-600"
            >
              {isCategorizing ? (
                <RefreshCw className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Sparkles className="h-3.5 w-3.5" />
              )}
              <span>{isCategorizing ? 'Categorizing...' : 'NLP Categorize'}</span>
            </button>
            <button
              onClick={() => setUseTransformers(!useTransformers)}
              className="ml-1 rounded-md px-2 py-1 text-[10px] font-semibold text-teal-800 hover:bg-teal-100 dark:text-teal-300 dark:hover:bg-teal-900/60"
              title="Toggle fast scikit-learn ML (default) vs Hugging Face zero-shot Transformer"
            >
              {useTransformers ? 'HF Transf.' : 'Fast ML'}
            </button>
          </div>

          {/* Export Actions (Phase 12) */}
          <div className="flex items-center space-x-1">
            <button
              onClick={() => {
                exportToCsv(
                  transactions,
                  `${fullData?.metadata.bank || 'statement'}_transactions.csv`
                )
                onToast('Export Complete', 'Exported transactions to CSV.')
              }}
              className="inline-flex items-center space-x-1 rounded-xl border border-slate-200 bg-white px-2.5 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
              title="Export as CSV"
            >
              <Download className="h-3.5 w-3.5 text-slate-500" />
              <span className="hidden md:inline">CSV</span>
            </button>
            <button
              onClick={() => {
                exportToExcel(
                  transactions,
                  summary,
                  fullData,
                  `${fullData?.metadata.bank || 'statement'}_report.xlsx`
                )
                onToast('Export Complete', 'Exported transactions & summary to Excel (.xlsx).')
              }}
              className="inline-flex items-center space-x-1 rounded-xl border border-slate-200 bg-white px-2.5 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
              title="Export as Excel (.xlsx)"
            >
              <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-600" />
              <span className="hidden md:inline">Excel</span>
            </button>
            <button
              onClick={() => {
                if (fullData) {
                  exportToJson(fullData, `${fullData.metadata.bank || 'statement'}_data.json`)
                } else {
                  exportToJson({ transactions, summary }, 'transactions.json')
                }
                onToast('Export Complete', 'Exported JSON file to downloads.')
              }}
              className="inline-flex items-center space-x-1 rounded-xl border border-slate-200 bg-white px-2.5 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
              title="Download JSON file"
            >
              <FileCode className="h-3.5 w-3.5 text-amber-600" />
              <span className="hidden md:inline">JSON</span>
            </button>
            <button
              onClick={handleCopyJson}
              className="inline-flex items-center space-x-1 rounded-xl border border-slate-200 bg-white px-2.5 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
              title="Copy JSON to clipboard"
            >
              {copied ? (
                <CheckCheck className="h-3.5 w-3.5 text-emerald-600" />
              ) : (
                <Copy className="h-3.5 w-3.5 text-slate-500" />
              )}
              <span className="hidden md:inline">{copied ? 'Copied' : 'JSON'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Table Container */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            {/* Sticky Table Header */}
            <thead className="sticky top-0 z-10 border-b border-slate-200 bg-slate-50/95 font-semibold text-slate-600 backdrop-blur-sm dark:border-slate-800 dark:bg-slate-800/90 dark:text-slate-300">
              <tr>
                <th
                  onClick={() => handleSort('date')}
                  className="cursor-pointer px-4 py-3 hover:text-slate-900 dark:hover:text-white"
                >
                  <div className="flex items-center space-x-1">
                    <span>Date</span>
                    {sortField === 'date' ? (
                      sortAsc ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    )}
                  </div>
                </th>
                <th className="px-3 py-3">Value Date</th>
                <th
                  onClick={() => handleSort('description')}
                  className="cursor-pointer px-4 py-3 hover:text-slate-900 dark:hover:text-white"
                >
                  <div className="flex items-center space-x-1">
                    <span>Description / Narrative</span>
                    {sortField === 'description' ? (
                      sortAsc ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('debit')}
                  className="cursor-pointer px-4 py-3 text-right hover:text-slate-900 dark:hover:text-white"
                >
                  <div className="flex items-center justify-end space-x-1">
                    <span>Debit (-)</span>
                    {sortField === 'debit' ? (
                      sortAsc ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('credit')}
                  className="cursor-pointer px-4 py-3 text-right hover:text-slate-900 dark:hover:text-white"
                >
                  <div className="flex items-center justify-end space-x-1">
                    <span>Credit (+)</span>
                    {sortField === 'credit' ? (
                      sortAsc ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('balance')}
                  className="cursor-pointer px-4 py-3 text-right hover:text-slate-900 dark:hover:text-white"
                >
                  <div className="flex items-center justify-end space-x-1">
                    <span>Running Balance</span>
                    {sortField === 'balance' ? (
                      sortAsc ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    )}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('category')}
                  className="cursor-pointer px-4 py-3 hover:text-slate-900 dark:hover:text-white"
                >
                  <div className="flex items-center space-x-1">
                    <span>Category</span>
                    {sortField === 'category' ? (
                      sortAsc ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                    ) : (
                      <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    )}
                  </div>
                </th>
                <th className="px-3 py-3">Channel</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>

            {/* Table Body */}
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {paginatedTransactions.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    <Filter className="mx-auto h-8 w-8 stroke-[1.5] text-slate-300 dark:text-slate-600" />
                    <p className="mt-2 text-xs font-semibold">No transactions match current filters</p>
                    <button
                      onClick={() => {
                        setSearchTerm('')
                        setDirectionFilter('all')
                        setCategoryFilter('all')
                        setOnlyNeedsReview(false)
                      }}
                      className="mt-2 text-xs font-medium text-teal-600 underline dark:text-teal-400"
                    >
                      Clear all filters
                    </button>
                  </td>
                </tr>
              ) : (
                paginatedTransactions.map((tx, idx) => (
                  <TransactionRow
                    key={tx._id || `${tx.description}_${tx.date}_${idx}`}
                    tx={tx}
                    index={idx}
                    currency={currency}
                    isEditing={editingRowId === (tx._id || `${tx.description}_${tx.date}`)}
                    editFormData={editFormData}
                    onEditChange={(field, val) =>
                      setEditFormData((prev) => ({ ...prev, [field]: val }))
                    }
                    onStartEdit={startEdit}
                    onSaveEdit={saveEdit}
                    onCancelEdit={cancelEdit}
                    onDeleteRow={handleDeleteRow}
                    onCategoryChange={handleCategoryChange}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination & Row Controls */}
        <div className="flex flex-col items-center justify-between gap-3 border-t border-slate-100 px-4 py-3 sm:flex-row dark:border-slate-800">
          <div className="flex items-center space-x-2 text-xs text-slate-500 dark:text-slate-400">
            <span>
              Showing {(currentPage - 1) * pageSize + 1} to{' '}
              {Math.min(currentPage * pageSize, filteredTransactions.length)} of{' '}
              {filteredTransactions.length} transactions
            </span>
            {transactions.length !== filteredTransactions.length && (
              <span className="text-teal-600 dark:text-teal-400">
                (filtered from {transactions.length} total)
              </span>
            )}
          </div>

          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1.5 text-xs text-slate-500 dark:text-slate-400">
              <span>Rows per page:</span>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value))
                  setCurrentPage(1)
                }}
                className="rounded-lg border border-slate-200 bg-slate-50 px-2 py-1 text-xs outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>

            <div className="flex items-center space-x-1">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-40 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                Previous
              </button>
              <span className="px-2 font-mono text-xs text-slate-600 dark:text-slate-300">
                {currentPage} / {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-40 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
