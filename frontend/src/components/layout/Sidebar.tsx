import { CheckCircle, Brain, Shield, TrendingUp, Info, Lightbulb, Target, Clock, Award, FileText, Menu, X } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import { useAssessmentStore } from '../../store/assessmentStore'
import { formatToolName } from '../../lib/utils'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const location = useLocation()
  const { tool } = useAssessmentStore()

  // Determine page-specific content
  const getPageContent = () => {
    switch (location.pathname) {
      case '/':
        return {
          title: 'Why Choose Us?',
          items: [
            { icon: <Brain className="w-5 h-5" />, title: 'AI-Powered Analysis', description: 'Azure OpenAI provides intelligent insights and recommendations' },
            { icon: <Target className="w-5 h-5" />, title: '15 Assessment Criteria', description: 'Comprehensive evaluation across all DevSecOps dimensions' },
            { icon: <Award className="w-5 h-5" />, title: 'Actionable Results', description: 'Prioritized recommendations with clear implementation paths' },
            { icon: <Clock className="w-5 h-5" />, title: 'Quick & Efficient', description: 'Complete assessment in under 10 minutes' }
          ]
        }
      case '/platform-selection':
        return {
          title: 'Platform Selection Tips',
          items: [
            { icon: <Info className="w-5 h-5" />, title: 'Choose Your Stack', description: 'Select the tools that match your current infrastructure' },
            { icon: <Lightbulb className="w-5 h-5" />, title: 'Multi-Platform Support', description: 'We support GitHub, GitLab, Azure DevOps, and more' },
            { icon: <Target className="w-5 h-5" />, title: 'Accurate Assessment', description: 'Platform-specific questions ensure relevant insights' }
          ]
        }
      case '/email-capture':
        return {
          title: 'Your Privacy Matters',
          items: [
            { icon: <Shield className="w-5 h-5" />, title: 'Secure & Confidential', description: 'Your email is only used for sending assessment results' },
            { icon: <FileText className="w-5 h-5" />, title: 'Detailed Report', description: 'Receive a comprehensive PDF report with all findings' },
            { icon: <Clock className="w-5 h-5" />, title: '48-Hour Access', description: 'Your shareable link remains active for 48 hours' }
          ]
        }
      case '/assessment':
        return {
          title: 'Assessment Guide',
          items: [
            { icon: <Info className="w-5 h-5" />, title: 'Answer Honestly', description: 'Accurate responses lead to better recommendations' },
            { icon: <Target className="w-5 h-5" />, title: 'Importance Levels', description: 'Questions are weighted by security and operational impact' },
            { icon: <Lightbulb className="w-5 h-5" />, title: 'Take Your Time', description: 'Progress is tracked - you can review before submitting' }
          ]
        }
      case '/results':
        return {
          title: 'Understanding Results',
          items: [
            { icon: <TrendingUp className="w-5 h-5" />, title: 'Score Breakdown', description: 'View performance across all assessment pillars' },
            { icon: <FileText className="w-5 h-5" />, title: 'Executive Summary', description: 'AI-generated analysis of your DevSecOps maturity' },
            { icon: <Award className="w-5 h-5" />, title: 'Action Items', description: 'Prioritized recommendations for immediate improvement' }
          ]
        }
      default:
        if (location.pathname.startsWith('/shared/')) {
          return {
            title: 'Shared Assessment',
            items: [
              { icon: <FileText className="w-5 h-5" />, title: 'Public View', description: 'This is a read-only shared assessment report' },
              { icon: <Clock className="w-5 h-5" />, title: 'Time-Limited', description: 'Shared links expire after 48 hours' },
              { icon: <Target className="w-5 h-5" />, title: 'Create Your Own', description: 'Start a free assessment for your repository' }
            ]
          }
        }
        return {
          title: 'Platform Features',
          items: [
            { icon: <Brain className="w-5 h-5" />, title: 'AI Analysis', description: 'Intelligent recommendations' },
            { icon: <Shield className="w-5 h-5" />, title: 'Security Focus', description: 'Critical practices prioritized' },
            { icon: <TrendingUp className="w-5 h-5" />, title: 'Actionable Results', description: 'Clear improvement paths' }
          ]
        }
    }
  }

  const pageContent = getPageContent()

  return (
    <aside
      className={`${isOpen ? 'w-80 max-w-[85vw]' : 'w-16'} bg-slate-900 border-r border-slate-700 min-h-screen h-full transition-all duration-300 relative flex flex-col`}
    >
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute right-2 top-4 bg-slate-800 hover:bg-slate-700 text-slate-100 rounded-full p-2 shadow-lg border border-slate-600 z-10 transition-all duration-200 hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
        aria-label={isOpen ? 'Close sidebar' : 'Open sidebar'}
      >
        {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>
      
      <div className={`flex-1 space-y-8 ${isOpen ? 'p-6 opacity-100' : 'p-2 opacity-0'} transition-opacity duration-300 overflow-y-auto`}>
        {/* Logo */}
        <div className="text-center py-4">
          <CheckCircle className="w-16 h-16 text-blue-400 mx-auto mb-3" />
          <h2 className="text-2xl font-bold text-white">DevSecOps Assessment</h2>
          <p className="text-sm text-slate-400">AI-Powered Assessment</p>
        </div>

        <div className="h-px bg-slate-700" />

        {/* Current Assessment */}
        {tool && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-slate-400 uppercase">Current Assessment</h3>
            <div className="bg-blue-900/30 rounded-lg p-4 border border-blue-700/50">
              <p className="text-white font-medium">{formatToolName(tool)}</p>
            </div>
          </div>
        )}

        {/* Page-Specific Information */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-400 uppercase">{pageContent.title}</h3>
          <div className="space-y-3">
            {pageContent.items.map((item, index) => (
              <InfoItem
                key={index}
                icon={item.icon}
                title={item.title}
                description={item.description}
              />
            ))}
          </div>
        </div>

      
      {/* Collapsed state icon */}
      {!isOpen && (
        <div className="flex justify-center pt-6">
          <CheckCircle className="w-8 h-8 text-blue-400" />
        </div>
      )}
        <div className="h-px bg-slate-700" />

        {/* About */}
        <div className="text-center text-xs text-slate-500">
          <p>DevSecOps</p>
          <p>Assessment Platform</p>
          <p className="mt-4 text-slate-600">v1.0.2</p>
        </div>
      </div>
    </aside>
  )
}

function InfoItem({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="flex gap-3">
      <div className="text-blue-400 flex-shrink-0">{icon}</div>
      <div>
        <p className="text-sm font-medium text-white">{title}</p>
        <p className="text-xs text-slate-400">{description}</p>
      </div>
    </div>
  )
}
