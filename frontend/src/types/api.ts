/**
 * Verified API Contract Types matching OpenAPI 3.1.0 specifications
 * Canonical Backend: https://mayank-ten-indol.vercel.app
 */

export interface HealthResponse {
  status: string
  service: string
  version: string
  brd_series: string
  ml_line_classifier_loaded: boolean
  nlp_categorizer_loaded: boolean
  supported_profiles: string[]
  timestamp: number
}

export interface BankProfile {
  id: string
  name: string
  country: string
  currency: string
  currency_decimals: number
  date_format: string
  direction_derivation: string
  multi_account: boolean
}

export interface ProfilesResponse {
  profiles: BankProfile[]
  count: number
}

export interface ExtractionMetadata {
  content_hash: string
  file_name: string
  page_count: number
  bank?: string | null
  profile_used: string
  currency?: string | null
  transaction_count: number
  extraction_method: string
  processing_time_seconds: number
}

export interface Account {
  id: string
  account_number?: string | null
  name?: string | null
  iban?: string | null
  currency?: string | null
  opening_balance?: number | null
  closing_balance?: number | null
}

export interface BalanceValidationResult {
  reconciled: boolean
  opening_balance?: number | null
  closing_balance?: number | null
  calculated_closing_balance?: number | null
  total_debits: number
  total_credits: number
  net_change: number
  discrepancy_count: number
  discrepancies: Array<Record<string, unknown>>
  warnings: string[]
}

export interface ExtractionResponse {
  metadata: ExtractionMetadata
  accounts: Account[]
  transactions: import('./transaction').Transaction[]
  validation: BalanceValidationResult
}

export interface CategorizeRequest {
  descriptions: string[]
  use_transformers?: boolean
}

export interface CategorizeResult {
  description: string
  category: string
  confidence: number
  channel?: string | null
  reference_id?: string | null
  counterparty?: string | null
}

export interface CategorizeResponse {
  results: CategorizeResult[]
  model_used: string
}

export interface ApiErrorDetail {
  message: string
  status?: number
  isCors: boolean
  isTimeout: boolean
  endpoint?: string
  details?: unknown
  rawError?: unknown
}
