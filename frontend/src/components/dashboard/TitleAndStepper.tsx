import React from 'react'
import { FileText, Check } from 'lucide-react'

interface TitleAndStepperProps {
  currentStep: 1 | 2 | 3 | 4
  fileName: string
  filePages?: number
  fileSizeKb?: number
  profileName?: string
  onReplaceFile: () => void
  onTrySample: () => void
  isSampleLoaded: boolean
}

export const TitleAndStepper: React.FC<TitleAndStepperProps> = ({
  currentStep,
  fileName,
  filePages = 2,
  fileSizeKb = 184,
  profileName = 'Auto-detect',
  onReplaceFile,
  onTrySample,
  isSampleLoaded,
}) => {
  const steps = [
    { num: 1, label: 'Upload' },
    { num: 2, label: 'Extract table' },
    { num: 3, label: 'Categorize' },
    { num: 4, label: 'Export' },
  ]

  return (
    <div className="flex flex-col space-y-5">
      {/* Title & File Chip Row */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl sm:text-[28px] font-bold tracking-tight text-[#0B2545] font-['IBM_Plex_Sans']">
            Statement extraction
          </h1>
          <p className="mt-1 text-sm text-[#55657A]">
            Upload a bank statement, review the extracted table, then categorize and export.
          </p>
        </div>

        {/* Right: File chip & Replace button (or Sample button) */}
        <div className="flex items-center flex-wrap gap-2.5">
          {fileName ? (
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-3 rounded-[12px] border border-[#DDE3EA] bg-white px-3.5 py-2 shadow-xs">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#E3F4F5] text-[#0E7C86]">
                  <FileText className="h-5 w-5" />
                </div>
                <div className="flex flex-col text-left">
                  <span className="text-xs font-semibold text-[#0B2545] truncate max-w-[190px]">
                    {fileName}
                  </span>
                  <span className="text-[11px] text-[#55657A]">
                    {filePages} pages · {fileSizeKb} KB · Profile: {profileName}
                  </span>
                </div>
              </div>

              <button
                onClick={onReplaceFile}
                className="rounded-[10px] border border-[#DDE3EA] bg-white px-3.5 py-2 text-xs font-semibold text-[#0B2545] shadow-xs hover:bg-slate-50 transition min-h-[44px]"
              >
                Replace file
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <button
                onClick={onTrySample}
                className="rounded-[10px] border border-[#0E7C86] bg-[#E3F4F5] px-4 py-2 text-xs font-bold text-[#0E7C86] shadow-xs hover:bg-[#D4ECEE] transition min-h-[44px]"
              >
                Try sample statement
              </button>
              <button
                onClick={onReplaceFile}
                className="rounded-[10px] bg-[#0E7C86] px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-[#0B6B74] transition min-h-[44px]"
              >
                Upload PDF
              </button>
            </div>
          )}

          {!isSampleLoaded && fileName && (
            <button
              onClick={onTrySample}
              className="text-xs font-medium text-[#0E7C86] hover:underline px-2 py-1"
              title="Switch back to verified Bank Muscat sample statement"
            >
              Load sample
            </button>
          )}
        </div>
      </div>

      {/* Step Tracker (4 pills) */}
      <div className="flex items-center space-x-2 sm:space-x-3 overflow-x-auto py-1">
        {steps.map((step) => {
          const isDone = currentStep > step.num
          const isActive = currentStep === step.num

          if (isDone) {
            return (
              <div
                key={step.num}
                className="flex items-center space-x-2 rounded-full bg-white px-3.5 py-1.5 border border-[#DDE3EA] text-xs font-semibold text-[#0B2545] shadow-xs shrink-0"
              >
                <div className="flex h-5 w-5 items-center justify-center rounded-full bg-[#0E7C86] text-white">
                  <Check className="h-3 w-3 stroke-[3]" />
                </div>
                <span>{step.label}</span>
              </div>
            )
          }

          if (isActive) {
            return (
              <div
                key={step.num}
                className="flex items-center space-x-2 rounded-full bg-[#E3F4F5] px-3.5 py-1.5 border-2 border-[#0E7C86] text-xs font-bold text-[#0E7C86] shadow-xs shrink-0"
              >
                <div className="flex h-5 w-5 items-center justify-center rounded-full bg-[#0E7C86] text-white text-[11px]">
                  {step.num}
                </div>
                <span>{step.label}</span>
              </div>
            )
          }

          return (
            <div
              key={step.num}
              className="flex items-center space-x-2 rounded-full bg-transparent px-3 py-1.5 text-xs font-medium text-[#8A99AD] shrink-0"
            >
              <div className="flex h-5 w-5 items-center justify-center rounded-full border border-slate-300 text-slate-400 text-[11px]">
                {step.num}
              </div>
              <span>{step.label}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
