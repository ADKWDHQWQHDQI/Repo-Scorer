import { CheckCircle, Brain, Shield, TrendingUp, Info, Lightbulb, Target, Clock, Award, FileText, Menu, X, CheckCircle2 } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import { useAssessmentProgressStore } from '../../store/assessmentProgressStore'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const location = useLocation()
  const assessmentProgress = useAssessmentProgressStore()

  const isAssessmentPage = location.pathname === '/assessment'

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
      className={`${isOpen ? 'w-80 max-w-[85vw]' : 'w-16'} bg-slate-900 border-r border-slate-700 sticky top-0 h-screen overflow-hidden transition-all duration-300 relative flex flex-col`}
    >
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute right-2 top-4 bg-slate-800 hover:bg-slate-700 text-slate-100 rounded-full p-2 shadow-lg border border-slate-600 z-10 transition-all duration-200 hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400"
        aria-label={isOpen ? 'Close sidebar' : 'Open sidebar'}
      >
        {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>
      
      <div className={`flex-1 space-y-8 ${isOpen ? 'p-6 opacity-100' : 'p-2 opacity-0'} transition-opacity duration-300 overflow-hidden`}>
        {/* Logo */}
        <div className="text-center py-4">
          <CheckCircle className="w-10 h-10 text-blue-400 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-white">DevSecOps Assessment</h2>
          <p className="text-xs text-slate-400">AI-Powered Assessment</p>
        </div>

        <div className="h-px bg-slate-700" />

        {/* Assessment Page Specific Content */}
        {isAssessmentPage && assessmentProgress.totalQuestions > 0 ? (
          <>
            {/* Instructions */}
            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
              <p className="text-sm text-slate-300 leading-relaxed">
                Please answer all questions below. Select Yes or No for each question based on your current practices.
              </p>
            </div>

            {/* Progress Bar */}
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-slate-400 uppercase">Your Progress</h3>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-400" />
                    <span className="text-xs font-semibold text-white">
                      {assessmentProgress.answeredCount} of {assessmentProgress.totalQuestions}
                    </span>
                  </div>
                  <span className="text-xs font-semibold text-blue-400">
                    {Math.round(assessmentProgress.percentage)}%
                  </span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${assessmentProgress.percentage}%` }}
                  />
                </div>
              </div>
            </div>
          </>
        ) : (
          /* Page-Specific Information */
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
        )}

        {/* Spacer to push footer to bottom */}
        <div className="flex-1"></div>

        <div className="h-px bg-slate-700" />

        {/* Footer */}
        <div className="text-center text-xs text-slate-400 pb-4">
          <p>Developed by</p>
          <a 
            href="https://ecanarys.com/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
          >
            Canarys Automations
          </a>
        </div>
      </div>

      {/* Collapsed state icon */}
      {!isOpen && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2">
          <CheckCircle className="w-8 h-8 text-blue-400" />
        </div>
      )}
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
