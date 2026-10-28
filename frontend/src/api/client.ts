import axios, { AxiosError, AxiosInstance } from 'axios'
import { ApiErrorDetail } from '../types'
import { getStoredApiUrl } from '../utils/storage'

/**
 * Canonical Base URL Resolution
 * Falls back to http://127.0.0.1:8000 if VITE_API_BASE_URL is not set.
 */
export function getApiBaseUrl(): string {
  const userOverride = getStoredApiUrl()
  if (userOverride) {
    return userOverride.replace(/\/+$/, '')
  }
  const envUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  return envUrl.replace(/\/+$/, '')
}

/**
 * Creates configured Axios instance without credentials.
 */
export function createApiClient(): AxiosInstance {
  const baseURL = getApiBaseUrl()

  return axios.create({
    baseURL,
    timeout: 60000, // 60 seconds for heavy document layout parsing
    withCredentials: false, // Strict requirement from Phase 3.2
    headers: {
      Accept: 'application/json',
    },
  })
}

/**
 * Structured error normalization handling all HTTP & network edge cases distinctly.
 */
export function normalizeApiError(error: unknown, endpoint?: string): ApiErrorDetail {
  if (axios.isAxiosError(error)) {
    const axiosErr = error as AxiosError<{ detail?: string | unknown }>
    const status = axiosErr.response?.status
    const isTimeout = axiosErr.code === 'ECONNABORTED' || axiosErr.message.toLowerCase().includes('timeout')
    
    // Explicit CORS check: Network error with no response object on a cross-origin call
    const isNetwork = !axiosErr.response && !isTimeout
    const isCors = isNetwork && window.location.origin !== new URL(getApiBaseUrl(), window.location.href).origin

    let message = 'An error occurred while communicating with the banking API.'

    if (isTimeout) {
      message = `Request timeout: The server took longer than 60 seconds to respond on ${endpoint || 'the API'}. The statement may be exceptionally large or the server is processing high load.`
    } else if (isCors) {
      message =
        'CORS Policy Rejection: The browser blocked the cross-origin request because the backend server has not permitted this frontend origin in its Access-Control-Allow-Origin headers.'
    } else if (isNetwork) {
      message =
        'Network Connection Failure: Unable to reach the backend server. Verify that the service is running and accessible.'
    } else if (status === 400) {
      message = 'Bad Request (400): The server could not process the request parameters.'
    } else if (status === 401) {
      message = 'Unauthorized (401): API authentication failed. Verify API Key or endpoint credentials.'
    } else if (status === 413) {
      message = 'Payload Too Large (413): The uploaded statement PDF exceeds the maximum file size permitted by the server.'
    } else if (status === 422) {
      const detail = axiosErr.response?.data?.detail
      if (typeof detail === 'string') {
        message = `Validation Error (422): ${detail}`
      } else if (Array.isArray(detail)) {
        const msgs = detail.map((d) => (typeof d === 'object' && d?.msg ? d.msg : JSON.stringify(d)))
        message = `Validation Error (422): ${msgs.join('; ')}`
      } else {
        message = 'Validation Error (422): The request body failed Pydantic schema validation.'
      }
    } else if (status === 429) {
      message = 'Rate Limit Exceeded (429): Too many requests submitted. Please wait a moment before retrying.'
    } else if (status === 500) {
      message =
        'Server Error (500): The backend failed while processing this request. (If running on Vercel Serverless, verify ephemeral disk quota /tmp is not exhausted).'
    } else if (status === 502 || status === 503) {
      message = `Service Unavailable (${status}): The backend gateway or host is temporarily offline.`
    } else if (axiosErr.response?.data?.detail && typeof axiosErr.response.data.detail === 'string') {
      message = axiosErr.response.data.detail
    } else if (axiosErr.message) {
      message = axiosErr.message
    }

    return {
      message,
      status,
      isCors,
      isTimeout,
      endpoint,
      details: axiosErr.response?.data,
      rawError: axiosErr,
    }
  }

  return {
    message: error instanceof Error ? error.message : 'Unknown application error occurred.',
    isCors: false,
    isTimeout: false,
    endpoint,
    rawError: error,
  }
}
