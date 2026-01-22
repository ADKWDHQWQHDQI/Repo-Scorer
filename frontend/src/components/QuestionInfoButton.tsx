import { useState, useRef, useEffect } from 'react'
import { Info, ExternalLink, X } from 'lucide-react'

interface QuestionInfoButtonProps {
  description?: string
  docUrl?: string
}

export function QuestionInfoButton({ description, docUrl }: QuestionInfoButtonProps) {
  const [isOpen, setIsOpen] = useState(false)
  const infoBoxRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        isOpen &&
        infoBoxRef.current &&
        buttonRef.current &&
        !infoBoxRef.current.contains(event.target as Node) &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  // Don't render if no description or doc URL
  if (!description && !docUrl) {
    return null
  }

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={() => setIsOpen(!isOpen)}
        className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-500 hover:text-gray-700"
        aria-label="Show feature information"
        type="button"
      >
        <Info className="w-4 h-4" />
      </button>

      {isOpen && (
        <div
          ref={infoBoxRef}
          className="absolute right-0 top-full mt-2 w-80 sm:w-96 bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-10 animate-in fade-in slide-in-from-top-2 duration-200"
        >
          <div className="flex items-start justify-between mb-3">
            <h4 className="text-sm font-semibold text-gray-900">Feature Information</h4>
            <button
              onClick={() => setIsOpen(false)}
              className="p-0.5 rounded hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
              aria-label="Close"
              type="button"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {description && (
            <p className="text-sm text-gray-700 leading-relaxed mb-3">
              {description}
            </p>
          )}

          {docUrl && (
            <a
              href={docUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline transition-colors"
            >
              View Official Documentation
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      )}
    </div>
  )
}
