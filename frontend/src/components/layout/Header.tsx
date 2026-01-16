import { CheckCircle, Activity, Info } from 'lucide-react'
import { useLocation } from 'react-router-dom'

export function Header() {
  const location = useLocation()

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
      <div className="px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg">
            <CheckCircle className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">{getTitle()}</h1>
            <p className="text-xs text-gray-500">DevSecOps Repository Assessment</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-green-50 rounded-lg border border-green-200">
            <Activity className="w-3.5 h-3.5 text-green-600" />
            <span className="text-xs font-medium text-green-700">System Ready</span>
          </div>
          <button 
            className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Information"
          >
            <Info className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      </div>
    </header>
  )
}
