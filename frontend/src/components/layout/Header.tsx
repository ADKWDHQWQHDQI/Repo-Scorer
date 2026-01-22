import { CheckCircle, Menu, ArrowRight } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'

interface HeaderProps {
  onMenuClick?: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const location = useLocation()
  const navigate = useNavigate()

  const getTitle = () => {
    switch (location.pathname) {
      case '/':
        return 'Welcome'
      case '/assessment':
        return 'Assessment in Progress'
      case '/results':
        return 'Assessment Results'
      default:
        return 'DevSecOps Assessment'
    }
  }

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="px-4 sm:px-6 py-3.5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5 min-w-0">
          {onMenuClick && (
            <button
              type="button"
              onClick={onMenuClick}
              className="lg:hidden p-2 -ml-1 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Open navigation"
            >
              <Menu className="w-5 h-5 text-gray-700" />
            </button>
          )}
          <div className="p-1.5 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg">
            <CheckCircle className="w-5 h-5 text-white" />
          </div>
          <div className="min-w-0">
            <h1 className="text-lg font-semibold text-gray-900 truncate">{getTitle()}</h1>
            <p className="text-xs text-gray-500 truncate">DevSecOps Assessment</p>
          </div>
        </div>
        {location.pathname === '/' && (
          <button
            onClick={() => navigate('/platform-selection')}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold text-sm rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
          >
            Get Started
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </header>
  )
}
