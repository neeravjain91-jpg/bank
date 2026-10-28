import React from 'react'
import { X, Building2 } from 'lucide-react'
import { useProfiles } from '../../hooks/useProfiles'

interface ProfilesModalProps {
  isOpen: boolean
  onClose: () => void
}

export const ProfilesModal: React.FC<ProfilesModalProps> = ({ isOpen, onClose }) => {
  const { data, isLoading } = useProfiles()
  const profiles = data?.profiles || []

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0B2545]/60 p-4 backdrop-blur-xs">
      <div className="relative w-full max-w-2xl rounded-[14px] border border-[#DDE3EA] bg-white p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-[#DDE3EA]">
          <div className="flex items-center space-x-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#E3F4F5] text-[#0E7C86]">
              <Building2 className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#0B2545] font-['IBM_Plex_Sans']">
                Extraction Profiles ({profiles.length})
              </h3>
              <p className="text-xs text-[#55657A]">
                Supported financial institution statement layouts & decimal standards
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-[#55657A] hover:bg-slate-100 transition"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-4 max-h-[380px] overflow-y-auto divide-y divide-[#DDE3EA]">
          {isLoading ? (
            <div className="py-8 text-center text-xs text-[#55657A]">
              Loading profiles from backend...
            </div>
          ) : (
            profiles.map((p) => (
              <div key={p.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-xs text-[#0B2545]">{p.name}</span>
                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-mono text-[#55657A]">
                      {p.id}
                    </span>
                    {p.id === 'bank_muscat' && (
                      <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                        Default BRD
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-[#55657A] mt-0.5">
                    Country: {p.country} · Date Format: {p.date_format} · Column Derivation: {p.direction_derivation}
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs font-mono font-bold text-[#0E7C86]">
                    {p.currency} ({p.currency_decimals} dec)
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="mt-4 pt-3 border-t border-[#DDE3EA] flex justify-end">
          <button
            onClick={onClose}
            className="rounded-lg bg-[#0E7C86] px-4 py-2 text-xs font-bold text-white hover:bg-[#0B6B74] transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
