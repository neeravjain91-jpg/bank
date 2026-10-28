import React, { useState, useRef } from 'react'
import { UploadCloud, X, AlertCircle, Sparkles, RefreshCw } from 'lucide-react'
import { useProfiles } from '../../hooks/useProfiles'
import { validateStatementFile } from '../../utils/validation'

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  onExtract: (file: File, profileId?: string) => void
  onLoadSample: () => void
  isExtracting: boolean
  error?: string | null
}

export const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  onExtract,
  onLoadSample,
  isExtracting,
  error,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const [selectedProfile, setSelectedProfile] = useState<string>('auto')
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { data: profilesData } = useProfiles()
  const profiles = profilesData?.profiles || []

  if (!isOpen) return null

  const handleFileChange = (file: File | null) => {
    if (!file) return
    const res = validateStatementFile(file)
    if (!res.isValid) {
      setValidationError(res.error || 'Invalid file')
      setSelectedFile(null)
      return
    }
    setValidationError(null)
    setSelectedFile(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0])
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = () => {
    setIsDragOver(false)
  }

  const handleSubmitExtract = () => {
    if (!selectedFile) return
    onExtract(selectedFile, selectedProfile === 'auto' ? undefined : selectedProfile)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0B2545]/60 p-4 backdrop-blur-xs">
      <div className="relative w-full max-w-lg rounded-[14px] border border-[#DDE3EA] bg-white p-6 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#DDE3EA]">
          <div>
            <h3 className="text-base font-bold text-[#0B2545] font-['IBM_Plex_Sans']">
              Upload Bank Statement
            </h3>
            <p className="text-xs text-[#55657A]">
              PDF, digital statements or scanned sheets up to 20MB
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-[#55657A] hover:bg-slate-100 transition"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Upload Drop Zone */}
        <div className="mt-4">
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={`flex flex-col items-center justify-center rounded-[12px] border-2 border-dashed p-6 text-center cursor-pointer transition ${
              isDragOver
                ? 'border-[#0E7C86] bg-[#E3F4F5]'
                : selectedFile
                ? 'border-emerald-400 bg-emerald-50/40'
                : 'border-[#DDE3EA] bg-[#F9FBFC] hover:bg-slate-50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.csv,.xlsx"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileChange(e.target.files[0])
                }
              }}
            />

            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#E3F4F5] text-[#0E7C86]">
              <UploadCloud className="h-6 w-6" />
            </div>

            <div className="mt-3 text-xs font-semibold text-[#0B2545]">
              {selectedFile ? selectedFile.name : 'Click to upload or drag & drop'}
            </div>
            <div className="mt-1 text-[11px] text-[#55657A]">
              {selectedFile
                ? `${(selectedFile.size / 1024).toFixed(1)} KB · Ready to extract`
                : 'PDF native statement recommended'}
            </div>
          </div>

          {/* Validation or API Error Banner */}
          {(validationError || error) && (
            <div className="mt-3 rounded-[10px] border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800 flex items-start space-x-2">
              <AlertCircle className="h-4 w-4 text-rose-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="font-semibold">Extraction notice</div>
                <div className="text-[11px] mt-0.5">{validationError || error}</div>
              </div>
            </div>
          )}

          {/* Profile Selector */}
          <div className="mt-4">
            <label className="block text-xs font-semibold text-[#0B2545] mb-1">
              Statement Layout Profile
            </label>
            <select
              value={selectedProfile}
              onChange={(e) => setSelectedProfile(e.target.value)}
              className="w-full rounded-lg border border-[#DDE3EA] bg-white px-3 py-2 text-xs text-[#0B2545] outline-none focus:border-[#0E7C86]"
            >
              <option value="auto">Auto-detect Profile (Recommended)</option>
              {profiles.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.currency} · {p.currency_decimals} decimals)
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 flex items-center justify-between pt-3 border-t border-[#DDE3EA]">
          <button
            onClick={() => {
              onLoadSample()
              onClose()
            }}
            className="flex items-center space-x-1.5 text-xs font-semibold text-[#0E7C86] hover:underline"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Load sample statement</span>
          </button>

          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="rounded-lg border border-[#DDE3EA] bg-white px-3 py-1.5 text-xs font-semibold text-[#55657A] hover:bg-slate-50 transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmitExtract}
              disabled={!selectedFile || isExtracting}
              className="rounded-lg bg-[#0E7C86] px-4 py-1.5 text-xs font-bold text-white shadow-xs hover:bg-[#0B6B74] transition disabled:opacity-50 flex items-center space-x-1.5"
            >
              {isExtracting ? (
                <>
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                  <span>Extracting...</span>
                </>
              ) : (
                <span>Extract table</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
