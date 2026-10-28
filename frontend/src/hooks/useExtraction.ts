import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { extractStatement, ExtractOptions } from '../api/extraction'
import { ExtractionResponse } from '../types'

export function useExtraction() {
  const [uploadProgress, setUploadProgress] = useState<number>(0)

  const mutation = useMutation<
    ExtractionResponse,
    Error,
    { file: File | Blob; options?: ExtractOptions }
  >({
    mutationFn: async ({ file, options }) => {
      setUploadProgress(0)
      return extractStatement(file, {
        ...options,
        onUploadProgress: (percent) => setUploadProgress(percent),
      })
    },
  })

  return {
    ...mutation,
    uploadProgress,
  }
}
