import React, { useState } from 'react'
import { ZoomIn, ZoomOut, FileText } from 'lucide-react'
import { Document, Page, pdfjs } from 'react-pdf'

// Configure pdfjs worker if available
if (typeof window !== 'undefined') {
  pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`
}

interface SourceDocumentCardProps {
  file: File | null
  pageCount?: number
  confidence?: number
  rowCount?: number
  colCount?: number
}

export const SourceDocumentCard: React.FC<SourceDocumentCardProps> = ({
  file,
  pageCount = 2,
  confidence = 98.2,
  rowCount = 8,
  colCount = 5,
}) => {
  const [zoom, setZoom] = useState<number>(1.0)
  const [currentPage] = useState<number>(1)
  const [pdfNumPages, setPdfNumPages] = useState<number>(pageCount)
  const [pdfLoadError, setPdfLoadError] = useState<boolean>(false)

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.15, 2.0))
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.15, 0.7))

  return (
    <div className="fintech-card bg-white p-5 shadow-xs flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-3">
        <div>
          <h2 className="text-base font-bold text-[#0B2545] font-['IBM_Plex_Sans']">
            Source document
          </h2>
          <p className="text-xs text-[#55657A]">
            Page {currentPage} of {pdfNumPages} · detected region highlighted
          </p>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center space-x-1">
          <button
            onClick={handleZoomOut}
            aria-label="Zoom out"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#DDE3EA] bg-white text-[#55657A] hover:bg-slate-50 transition"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <button
            onClick={handleZoomIn}
            aria-label="Zoom in"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#DDE3EA] bg-white text-[#55657A] hover:bg-slate-50 transition"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Body Canvas (#E9EEF3) */}
      <div className="relative mt-2 flex-1 min-h-[380px] rounded-[10px] bg-[#E9EEF3] p-4 flex items-center justify-center overflow-auto">
        {file && !pdfLoadError ? (
          <div className="relative shadow-md bg-white rounded-xs" style={{ transform: `scale(${zoom})`, transformOrigin: 'top center' }}>
            <Document
              file={file}
              onLoadSuccess={({ numPages }) => {
                setPdfNumPages(numPages)
                setPdfLoadError(false)
              }}
              onLoadError={() => setPdfLoadError(true)}
              loading={
                <div className="flex h-[360px] w-[260px] items-center justify-center bg-white text-xs text-[#55657A]">
                  Loading document page...
                </div>
              }
            >
              <Page
                pageNumber={currentPage}
                width={320}
                renderTextLayer={false}
                renderAnnotationLayer={false}
              />
            </Document>

            {/* Dashed Teal Table Detection Overlay */}
            <div className="pointer-events-none absolute inset-x-4 top-24 bottom-16 rounded-xs border-2 border-dashed border-[#0E7C86] bg-[#0E7C86]/5">
              <div className="absolute -top-3 left-2 rounded-xs bg-[#0E7C86] px-2 py-0.5 text-[10px] font-bold text-white shadow-xs">
                Table 1 · {confidence}% confidence
              </div>
            </div>
          </div>
        ) : (
          /* Exact Illustration from Screenshot 2 */
          <div
            className="relative flex flex-col w-[300px] h-[360px] rounded-xs bg-white p-5 shadow-sm border border-slate-200 transition"
            style={{ transform: `scale(${zoom})`, transformOrigin: 'center center' }}
          >
            {/* Bank Header Skeleton */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <div className="h-5 w-5 rounded-xs bg-[#0E7C86]/20 flex items-center justify-center text-[#0E7C86]">
                  <FileText className="h-3 w-3" />
                </div>
                <div className="h-2.5 w-24 rounded-full bg-slate-300"></div>
              </div>
              <div className="h-2 w-12 rounded-full bg-slate-200"></div>
            </div>

            {/* Account Details Box Skeleton */}
            <div className="mt-3 flex items-center justify-between px-2 py-1.5 rounded bg-slate-50 border border-slate-100">
              <div className="space-y-1">
                <div className="h-2 w-28 rounded-full bg-slate-300"></div>
                <div className="h-1.5 w-16 rounded-full bg-slate-200"></div>
              </div>
              <div className="h-3 w-10 rounded-full bg-emerald-100"></div>
            </div>

            {/* Dashed Teal Overlay Around Table */}
            <div className="relative mt-4 flex-1 rounded-sm border-2 border-dashed border-[#0E7C86] bg-[#0E7C86]/3 p-2.5 flex flex-col justify-between">
              {/* Badge */}
              <div className="absolute -top-3 left-2 rounded-xs bg-[#0E7C86] px-2 py-0.5 text-[9px] font-bold text-white shadow-xs">
                Table 1 · {confidence}% confidence
              </div>

              {/* Simulated Table Lines */}
              <div className="space-y-2 mt-1">
                <div className="grid grid-cols-4 gap-2 border-b border-[#0E7C86]/20 pb-1">
                  <div className="h-2 rounded bg-[#0E7C86]/30"></div>
                  <div className="h-2 rounded bg-[#0E7C86]/30"></div>
                  <div className="h-2 rounded bg-[#0E7C86]/30"></div>
                  <div className="h-2 rounded bg-[#0E7C86]/30"></div>
                </div>
                {Array.from({ length: 6 }).map((_, idx) => (
                  <div key={idx} className="grid grid-cols-4 gap-2">
                    <div className="h-1.5 rounded bg-slate-300/80"></div>
                    <div className="h-1.5 rounded bg-slate-300/80"></div>
                    <div className="h-1.5 rounded bg-slate-300/80"></div>
                    <div className="h-1.5 rounded bg-slate-300/80"></div>
                  </div>
                ))}
              </div>

              <div className="pt-1 border-t border-slate-100 flex justify-between text-[8px] text-slate-400">
                <span>Transactions Section</span>
                <span>Verified Extracted Area</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-3 text-xs text-[#55657A]">
        1 table detected · {rowCount} rows · {colCount} columns. Illustrative preview; the real viewer shows the uploaded page.
      </div>
    </div>
  )
}
