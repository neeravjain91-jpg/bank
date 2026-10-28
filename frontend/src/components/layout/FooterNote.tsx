import React from 'react'
import { Lock } from 'lucide-react'

export const FooterNote: React.FC = () => {
  return (
    <div className="flex items-center space-x-2 text-xs text-[#55657A] pt-4 pb-12">
      <Lock className="h-3.5 w-3.5 text-[#55657A] shrink-0" />
      <span>
        Statements are sent only to your configured extraction service and are not stored in this browser.
      </span>
    </div>
  )
}
