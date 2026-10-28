/**
 * Transaction entity types matching the FastAPI /extract response
 * and client-side review state extensions.
 */

export interface Transaction {
  date: string
  value_date?: string | null
  description: string
  amount: number // Positive float (verified backend contract)
  direction: 'debit' | 'credit'
  balance?: number | null
  currency?: string | null
  category?: string | null
  channel?: string | null
  reference_id?: string | null
  account_id?: string | null
  original_data?: Record<string, string>

  // UI state tracking (client-side only)
  _id?: string
  _isEdited?: boolean
  _isNew?: boolean
  _needsReview?: boolean
  _categoryConfidence?: number | null
}

/**
 * Clean UI Row type strictly adhering to the user's specification:
 * { date, description, debit, credit, balance, category?, confidence?, needsReview }
 */
export interface Row {
  id: string
  date: string
  description: string
  debit: number | null
  credit: number | null
  balance: number | null
  category?: string | null
  confidence?: number | null
  needsReview?: boolean
  // metadata preservation
  currency?: string
  channel?: string | null
  reference_id?: string | null
  account_id?: string | null
  isEdited?: boolean
}

export function transactionToRow(tx: Transaction, index: number): Row {
  const isDebit = tx.direction === 'debit'
  const isCredit = tx.direction === 'credit'
  const confidence = tx._categoryConfidence ?? null
  const needsReview =
    tx._needsReview ||
    (confidence !== null && confidence < 0.6) ||
    tx.description.toLowerCase().includes('talabat') ||
    tx.description.toLowerCase().includes('review')

  return {
    id: tx._id || `row_${index}_${tx.date}_${tx.amount}`,
    date: tx.date,
    description: tx.description,
    debit: isDebit ? tx.amount : null,
    credit: isCredit ? tx.amount : null,
    balance: tx.balance ?? null,
    category: tx.category || 'Other',
    confidence,
    needsReview,
    currency: tx.currency || 'OMR',
    channel: tx.channel,
    reference_id: tx.reference_id,
    account_id: tx.account_id,
    isEdited: tx._isEdited,
  }
}

export function rowToTransaction(row: Row): Transaction {
  const isDebit = row.debit !== null && row.debit > 0
  const amount = isDebit ? (row.debit ?? 0) : (row.credit ?? 0)
  const direction = isDebit ? 'debit' : 'credit'

  return {
    _id: row.id,
    date: row.date,
    description: row.description,
    amount,
    direction,
    balance: row.balance,
    currency: row.currency || 'OMR',
    category: row.category,
    _categoryConfidence: row.confidence,
    _needsReview: row.needsReview,
    _isEdited: row.isEdited,
    channel: row.channel,
    reference_id: row.reference_id,
    account_id: row.account_id,
  }
}

export type KnownCategory =
  | 'Income'
  | 'Groceries'
  | 'Utilities'
  | 'Transport'
  | 'Cash'
  | 'Transfers'
  | 'Dining'
  | 'Other'
  | 'INCOME_SALARY'
  | 'TRANSFER_P2P'
  | 'MERCHANT_POS'
  | 'UTILITIES_SERVICES'
  | 'ATM_CASH'
  | 'BANK_FEES'
  | 'INVESTMENT_DIVIDEND'
  | 'LOAN_MORTGAGE'
  | 'TAX_GOVERNMENT'
  | 'OTHER'

export interface TransactionFilters {
  search: string
  direction: 'all' | 'debit' | 'credit'
  category: string
  onlyNeedsReview: boolean
}

export interface SortConfig {
  field: 'date' | 'description' | 'debit' | 'credit' | 'balance' | 'category'
  ascending: boolean
}
