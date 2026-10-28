import { HistoryItem } from '../types'

const STORAGE_KEYS = {
  HISTORY: 'fintech_statement_history_v1',
  THEME: 'fintech_theme_mode_v1',
  API_URL: 'fintech_api_url_override_v1',
  HISTORY_OPT_IN: 'fintech_history_storage_enabled_v1',
}

export function isHistoryStorageEnabled(): boolean {
  try {
    const val = localStorage.getItem(STORAGE_KEYS.HISTORY_OPT_IN)
    // Default to true for demo experience, user can toggle off anytime
    return val !== 'false'
  } catch {
    return true
  }
}

export function setHistoryStorageEnabled(enabled: boolean): void {
  try {
    localStorage.setItem(STORAGE_KEYS.HISTORY_OPT_IN, enabled ? 'true' : 'false')
    if (!enabled) {
      clearHistory()
    }
  } catch (err) {
    console.error('Failed to update history storage preference:', err)
  }
}

export function getHistory(): HistoryItem[] {
  if (!isHistoryStorageEnabled()) return []
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.HISTORY)
    if (!raw) return []
    return JSON.parse(raw) as HistoryItem[]
  } catch (err) {
    console.error('Failed to read history from localStorage:', err)
    return []
  }
}

export function saveToHistory(item: HistoryItem): void {
  if (!isHistoryStorageEnabled()) return
  try {
    const current = getHistory()
    const filtered = current.filter((h) => h.id !== item.id)
    // Strictly cap at last 10 sessions per Phase 13
    const updated = [item, ...filtered].slice(0, 10)
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(updated))
  } catch (err) {
    console.error('Failed to save session to history (quota or storage disabled):', err)
  }
}

export function deleteHistoryItem(id: string): void {
  try {
    const current = getHistory()
    const filtered = current.filter((h) => h.id !== id)
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(filtered))
  } catch (err) {
    console.error('Failed to delete history item:', err)
  }
}

export function clearHistory(): void {
  try {
    localStorage.removeItem(STORAGE_KEYS.HISTORY)
  } catch (err) {
    console.error('Failed to clear history:', err)
  }
}

export function getStoredTheme(): 'light' | 'dark' {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.THEME)
    if (stored === 'light' || stored === 'dark') return stored
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark'
    }
  } catch {
    // fallback
  }
  return 'light'
}

export function setStoredTheme(theme: 'light' | 'dark'): void {
  try {
    localStorage.setItem(STORAGE_KEYS.THEME, theme)
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  } catch (err) {
    console.error('Failed to persist theme:', err)
  }
}

export function getStoredApiUrl(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEYS.API_URL)
  } catch {
    return null
  }
}

export function setStoredApiUrl(url: string | null): void {
  try {
    if (url) {
      localStorage.setItem(STORAGE_KEYS.API_URL, url)
    } else {
      localStorage.removeItem(STORAGE_KEYS.API_URL)
    }
  } catch (err) {
    console.error('Failed to persist API URL override:', err)
  }
}
