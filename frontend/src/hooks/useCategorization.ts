import { useMutation } from '@tanstack/react-query'
import { categorizeTransactions } from '../api/categorization'
import { CategorizeResponse, Transaction } from '../types'

export function useCategorization() {
  const mutation = useMutation<
    CategorizeResponse,
    Error,
    { descriptions: string[]; useTransformers?: boolean }
  >({
    mutationFn: ({ descriptions, useTransformers }) =>
      categorizeTransactions(descriptions, useTransformers),
  })

  const applyCategorizationResults = (
    currentTransactions: Transaction[],
    response: CategorizeResponse
  ): Transaction[] => {
    // Map strictly by input array index per Phase 4.5
    return currentTransactions.map((tx, idx) => {
      const match = response.results[idx]
      if (match) {
        return {
          ...tx,
          category: match.category,
          channel: match.channel || tx.channel,
          reference_id: match.reference_id || tx.reference_id,
          _categoryConfidence: match.confidence,
          _isEdited: true,
        }
      }
      return tx
    })
  }

  return {
    ...mutation,
    applyCategorizationResults,
  }
}
