import React, { useState } from 'react'
import { X, Server, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react'
import { getApiBaseUrl } from '../../api/client'
import { setStoredApiUrl } from '../../utils/storage'

interface BackendModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: () => void
}

const PRESET_ENDPOINTS = [
  {
    name: 'Canonical Production API Alias (Vercel)',
    url: 'https://mayank-ten-indol.vercel.app',
    badge: 'Production Default',
    description: 'Public cloud endpoint supporting CORS and OpenAPI 3.1',
  },
  {
    name: 'Local FastAPI Server (High Performance)',
    url: 'http://127.0.0.1:8000',
    badge: 'Local Testing',
    description: 'Local Uvicorn server running on machine loopback',
  },
  {
    name: 'Vite Development Proxy Route',
    url: '/api-local',
    badge: 'Bypasses Browser CORS',
    description: 'Proxies requests through Vite dev server to localhost:8000',
  },
]

async function pingBackendHealth(targetUrl: string): Promise<{ success: boolean; latency: number; error?: string }> {
  const startTime = Date.now()
  try {
    const cleanUrl = targetUrl.replace(/\/+$/, '')
    const response = await fetch(`${cleanUrl}/health`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
    })
    const latency = Date.now() - startTime
    if (response.ok) {
      const data = await response.json().catch(() => null)
      if (data && data.status === 'healthy') {
        return { success: true, latency }
      }
    }
    return {
      success: false,
      latency,
      error: `HTTP ${response.status}: Server responded with non-healthy status.`,
    }
  } catch (err) {
    return {
      success: false,
      latency: 0,
      error: err instanceof Error ? err.message : 'Network / CORS connection failed.',
    }
  }
}

export const BackendModal: React.FC<BackendModalProps> = ({ isOpen, onClose, onSave }) => {
  const [selectedUrl, setSelectedUrl] = useState<string>(getApiBaseUrl())
  const [customUrl, setCustomUrl] = useState<string>('')
  const [testStatus, setTestStatus] = useState<{
    testing: boolean
    success?: boolean
    latency?: number
    error?: string
  }>({ testing: false })

  const handleTestConnection = async (targetUrl: string) => {
    setTestStatus({ testing: true })
    const result = await pingBackendHealth(targetUrl)
    setTestStatus({
      testing: false,
      success: result.success,
      latency: result.latency,
      error: result.error,
    })
  }

  const handleApply = () => {
    const finalUrl = customUrl.trim() || selectedUrl
    setStoredApiUrl(finalUrl)
    onSave()
    onClose()
  }

  const handleResetDefault = () => {
    setStoredApiUrl(null)
    onSave()
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4 dark:border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="rounded-xl bg-teal-50 p-2 text-teal-600 dark:bg-teal-950 dark:text-teal-400">
              <Server className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                Configure Backend API Endpoint
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Switch between live Vercel cloud and local FastAPI server
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200"
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mt-4 space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Select Preset Connection
          </div>
          {PRESET_ENDPOINTS.map((preset) => {
            const isSelected = selectedUrl === preset.url && !customUrl
            return (
              <div
                key={preset.url}
                onClick={() => {
                  setSelectedUrl(preset.url)
                  setCustomUrl('')
                  handleTestConnection(preset.url)
                }}
                className={`group flex cursor-pointer items-center justify-between rounded-xl border p-3 transition ${
                  isSelected
                    ? 'border-teal-500 bg-teal-50/50 ring-1 ring-teal-500 dark:border-teal-500 dark:bg-teal-950/30'
                    : 'border-slate-200 hover:border-slate-300 dark:border-slate-800 dark:hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold text-slate-900 dark:text-white">
                      {preset.name}
                    </span>
                    <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                      {preset.badge}
                    </span>
                  </div>
                  <div className="mt-0.5 font-mono text-[11px] text-slate-500 dark:text-slate-400">
                    {preset.url}
                  </div>
                  <div className="mt-0.5 text-[10px] text-slate-400 dark:text-slate-500">
                    {preset.description}
                  </div>
                </div>
                <div
                  className={`h-4 w-4 rounded-full border flex items-center justify-center shrink-0 ml-3 ${
                    isSelected
                      ? 'border-teal-600 bg-teal-600 dark:border-teal-400 dark:bg-teal-400'
                      : 'border-slate-300 dark:border-slate-600'
                  }`}
                >
                  {isSelected && <div className="h-1.5 w-1.5 rounded-full bg-white dark:bg-slate-900" />}
                </div>
              </div>
            )
          })}

          <div className="pt-2">
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
              Or Custom API Endpoint URL
            </label>
            <div className="mt-1 flex space-x-2">
              <input
                type="text"
                placeholder="https://your-custom-api.com"
                value={customUrl}
                onChange={(e) => setCustomUrl(e.target.value)}
                className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-900 outline-none focus:border-teal-500 focus:bg-white dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:border-teal-400"
              />
              <button
                onClick={() => handleTestConnection(customUrl)}
                disabled={!customUrl || testStatus.testing}
                className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
              >
                Test
              </button>
            </div>
          </div>

          {/* Test Status Feedback */}
          {testStatus.testing && (
            <div className="flex items-center space-x-2 rounded-xl bg-blue-50 p-2.5 text-xs text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Testing /health connection...</span>
            </div>
          )}
          {!testStatus.testing && testStatus.success && (
            <div className="flex items-center justify-between rounded-xl bg-emerald-50 p-2.5 text-xs text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                <span>Backend reachable and healthy!</span>
              </div>
              <span className="font-semibold">{testStatus.latency} ms</span>
            </div>
          )}
          {!testStatus.testing && testStatus.success === false && (
            <div className="flex items-start space-x-2 rounded-xl bg-rose-50 p-2.5 text-xs text-rose-700 dark:bg-rose-950/50 dark:text-rose-300">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
              <div>
                <span className="font-semibold">Connection failed: </span>
                <span>{testStatus.error}</span>
                <div className="mt-1 text-[11px] text-rose-600/90 dark:text-rose-400">
                  Tip: Ensure backend is running or select "Local FastAPI Server".
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4 dark:border-slate-800">
          <button
            onClick={handleResetDefault}
            className="text-xs font-medium text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
          >
            Reset to Environment Default
          </button>
          <div className="flex space-x-2">
            <button
              onClick={onClose}
              className="rounded-xl border border-slate-200 px-3.5 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              onClick={handleApply}
              className="rounded-xl bg-teal-600 px-4 py-2 text-xs font-semibold text-white shadow hover:bg-teal-700 dark:bg-teal-500 dark:hover:bg-teal-600"
            >
              Apply Endpoint
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
