import React, { useState } from 'react'
import { LayoutGrid, ExternalLink } from 'lucide-react'
import { useHealth } from '../../hooks/useHealth'

interface HeaderProps {
  activeTab: 'extract' | 'history' | 'profiles'
  onSelectTab: (tab: 'extract' | 'history' | 'profiles') => void
  onOpenBackendModal: () => void
  historyCount: number
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onSelectTab,
  onOpenBackendModal,
  historyCount,
}) => {
  const { isOnline, isDegraded, isLoading, latency, baseUrl } = useHealth()
  const [showTooltip, setShowTooltip] = useState(false)

  const docsUrl = `${baseUrl.replace(/\/+$/, '')}/docs`

  const isHealthy = isOnline && !isDegraded

  return (
    <header className="sticky top-0 z-40 bg-[#0B2545] text-white shadow-md">
      <div className="mx-auto flex max-w-[1344px] items-center justify-between px-6 py-3.5">
        {/* Brand & Left Navigation */}
        <div className="flex items-center space-x-8">
          {/* Logo Mark + Title */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onSelectTab('extract')}>
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#5FD0D8] text-[#0B2545] shadow-sm">
              <LayoutGrid className="h-5 w-5 stroke-[2.5]" />
            </div>
            <span className="text-lg font-bold tracking-tight text-white font-['IBM_Plex_Sans']">
              Statement Extractor
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
            <button
              onClick={() => onSelectTab('extract')}
              className={`relative py-1 transition ${
                activeTab === 'extract'
                  ? 'text-white font-semibold after:absolute after:bottom-[-8px] after:left-0 after:right-0 after:h-[2.5px] after:bg-[#5FD0D8]'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Extract
            </button>

            <button
              onClick={() => onSelectTab('history')}
              className={`relative py-1 transition flex items-center space-x-1.5 ${
                activeTab === 'history'
                  ? 'text-white font-semibold after:absolute after:bottom-[-8px] after:left-0 after:right-0 after:h-[2.5px] after:bg-[#5FD0D8]'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              <span>History</span>
              {historyCount > 0 && (
                <span className="rounded-full bg-slate-700/80 px-1.5 py-0.2 text-[10px] text-slate-300">
                  {historyCount}
                </span>
              )}
            </button>

            <button
              onClick={() => onSelectTab('profiles')}
              className={`relative py-1 transition ${
                activeTab === 'profiles'
                  ? 'text-white font-semibold after:absolute after:bottom-[-8px] after:left-0 after:right-0 after:h-[2.5px] after:bg-[#5FD0D8]'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Profiles
            </button>

            <a
              href={docsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-slate-300 transition hover:text-white"
            >
              <span>API docs</span>
              <ExternalLink className="h-3 w-3 opacity-70" />
            </a>
          </nav>
        </div>

        {/* Right: Status Pill */}
        <div className="relative">
          <button
            onClick={onOpenBackendModal}
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            className="flex items-center space-x-2 rounded-full bg-[#13325B] px-3.5 py-1.5 text-xs font-medium text-slate-200 border border-slate-700/50 hover:bg-[#1A4275] transition"
            title="Configure Backend Connection"
          >
            <span className="relative flex h-2 w-2">
              {isHealthy && (
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              )}
              <span
                className={`relative inline-flex h-2 w-2 rounded-full ${
                  isLoading
                    ? 'bg-amber-400'
                    : isHealthy
                    ? 'bg-emerald-400'
                    : 'bg-rose-500'
                }`}
              ></span>
            </span>
            <span>
              {isLoading
                ? 'Connecting...'
                : isHealthy
                ? 'Service online'
                : 'Service offline'}
            </span>
            {latency !== null && isHealthy && (
              <span className="text-[11px] text-slate-400 font-mono">
                {latency}ms
              </span>
            )}
          </button>

          {/* Tooltip */}
          {showTooltip && (
            <div className="absolute right-0 top-full mt-2 w-64 rounded-xl border border-slate-700 bg-[#0B2545] p-3 text-xs text-slate-200 shadow-xl z-50">
              <div className="font-semibold text-white mb-1">Backend Connection</div>
              <div className="truncate text-slate-400 text-[11px] mb-2">{baseUrl}</div>
              <div className="text-[11px] text-[#5FD0D8]">Click to switch endpoints or test ping.</div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
