import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { 
  ArrowRight, 
  CheckCircle2, 
  Shield,
  Target,
  Zap,
  BarChart3,
  FileText,
  TrendingUp,

  GitCommit,
  Award,
  Sparkles
} from 'lucide-react'

export function WelcomePage() {
  const navigate = useNavigate()

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [])

  const handleGetStarted = () => {
    navigate('/platform-selection')
  }

  return (
    <div className="max-w-6xl mx-auto py-6 sm:py-8 px-4 sm:px-6">

      {/* Platform Overview */}
      <section className="mb-8 bg-white rounded-xl p-6 sm:p-8 border border-gray-200 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Target className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900">Platform Overview</h2>
        </div>
        
        <p className="text-gray-700 text-base leading-relaxed mb-6 max-w-4xl">
          An AI-powered assessment that evaluates your development practices across key DevSecOps maturity dimensions. 
          Gain clear visibility into delivery performance, security posture, and operational maturity—along with actionable 
          recommendations to improve.
        </p>

        {/* Highlights */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-5 border border-blue-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            Highlights
          </h3>
          <ul className="space-y-3 text-gray-700 text-sm max-w-4xl">
            <li className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
              <span><strong>Maturity-Based Evaluation:</strong> Weighted criteria across delivery, security, and reliability</span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
              <span><strong>AI-Driven Insights:</strong> Context-aware recommendations mapped to best practices</span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
              <span><strong>Multi-Platform:</strong> GitHub, GitLab, Azure DevOps, Jenkins and others covered</span>
            </li>
          </ul>
        </div>
      </section>

      {/* Assessment Deliverables Section */}
      <section className="mb-8 bg-white rounded-xl p-5 sm:p-6 border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2.5 mb-5">
          <div className="p-2.5 bg-indigo-600 rounded-lg">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900">Assessment Deliverables</h2>
        </div>
        <p className="text-gray-700 mb-5 text-sm">
          Upon completion, you receive a comprehensive assessment package designed for technical leadership and development teams:
        </p>
        <div className="grid md:grid-cols-3 gap-5">
          <DeliverableCard
            icon={<Award className="w-8 h-8" />}
            title="Overall Score"
            description="Weighted score out of 100 based on industry best practices and security standards"
            color="blue"
          />
          <DeliverableCard
            icon={<BarChart3 className="w-8 h-8" />}
            title="Visual Analytics"
            description="Interactive charts showing category breakdowns, strengths, and improvement areas"
            color="green"
          />
          <DeliverableCard
            icon={<TrendingUp className="w-8 h-8" />}
            title="AI Recommendations"
            description="AI-generated actionable insights and prioritized improvement roadmap"
            color="purple"
          />
          <DeliverableCard
            icon={<Shield className="w-8 h-8" />}
            title="Security Analysis"
            description="Vulnerability detection, dependency scanning, and compliance gap identification"
            color="red"
          />
          <DeliverableCard
            icon={<GitCommit className="w-8 h-8" />}
            title="Process Metrics"
            description="Detailed evaluation of branching strategy, code review practices, and workflow efficiency"
            color="orange"
          />
          <DeliverableCard
            icon={<FileText className="w-8 h-8" />}
            title="Executive Summary"
            description="Downloadable report with findings, benchmarks, and implementation guidance"
            color="indigo"
          />
        </div>
      </section>

      {/* Assessment Workflow Section */}
      <section className="mb-8 bg-white rounded-xl p-5 sm:p-6 border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2.5 mb-5">
          <div className="p-2.5 bg-emerald-600 rounded-lg">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900">Assessment Workflow</h2>
        </div>
        <p className="text-gray-700 mb-6 text-sm">
          Our streamlined process ensures a thorough evaluation in under 10 minutes:
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <WorkflowStep
            number="1"
            title="Select Platforms"
            description="Choose your repository, CI/CD and other platforms: GitHub, GitLab, Azure DevOps, Jenkins"
            icon={<Target className="w-6 h-6" />}
          />
          <WorkflowStep
            number="2"
            title="Answer Questions"
            description="Answer the questions about your repository, CI/CD, and development practices"
            icon={<CheckCircle2 className="w-6 h-6" />}
          />
          <WorkflowStep
            number="3"
            title="Review Results"
            description="Access your detailed score, visualizations, and actionable recommendations"
            icon={<BarChart3 className="w-6 h-6" />}
          />
        </div>
      </section>

      {/* Call to Action */}
      <div className="text-center py-4">
        <button
          onClick={handleGetStarted}
          className="inline-flex items-center gap-3 px-10 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold text-lg rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
        >
          Get Started
          <ArrowRight className="w-5 h-5" />
        </button>
        <p className="text-gray-600 mt-4 text-sm">
          Begin your comprehensive DevSecOps maturity assessment
        </p>
      </div>
      
      {/* Trust Indicators */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid md:grid-cols-4 gap-6 text-center">
          <TrustIndicator
            icon={<Sparkles className="w-6 h-6" />}
            title="AI-Powered"
            description="AI-generated actionable insights"
          />
          <TrustIndicator
            icon={<Zap className="w-6 h-6" />}
            title="Fast Assessment"
            description="Complete in under 10 minutes"
          />
          <TrustIndicator
            icon={<Award className="w-6 h-6" />}
            title="Industry Standards"
            description="Based on DevSecOps best practices"
          />
          <TrustIndicator
            icon={<TrendingUp className="w-6 h-6" />}
            title="Actionable Insights"
            description="Prioritized improvement roadmap"
          />
        </div>
      </div>
    </div>
  )
}


// Component: Deliverable Card
function DeliverableCard({
  icon,
  title,
  description,
  color,
}: {
  icon: React.ReactNode
  title: string
  description: string
  color: 'blue' | 'green' | 'purple' | 'red' | 'orange' | 'indigo'
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    green: 'bg-green-50 text-green-600 border-green-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
    red: 'bg-red-50 text-red-600 border-red-100',
    orange: 'bg-orange-50 text-orange-600 border-orange-100',
    indigo: 'bg-indigo-50 text-indigo-600 border-indigo-100',
  }

  return (
    <div className="bg-gradient-to-br from-white to-gray-50 rounded-lg p-4 shadow-sm border border-gray-200 hover:shadow-md transition-all hover:border-gray-300">
      <div className={`inline-flex items-center justify-center w-11 h-11 rounded-lg mb-3 ${colorClasses[color]}`}>
        {icon}
      </div>
      <h3 className="font-semibold text-gray-900 mb-1.5 text-base">{title}</h3>
      <p className="text-xs text-gray-600 leading-relaxed">{description}</p>
    </div>
  )
}

// Component: Workflow Step
function WorkflowStep({
  number,
  title,
  description,
  icon,
}: {
  number: string
  title: string
  description: string
  icon: React.ReactNode
}) {
  return (
    <div className="relative">
      <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-lg p-4 border border-emerald-200 hover:border-emerald-300 transition-all h-full">
        <div className="flex items-center gap-2.5 mb-3">
          <div className="flex items-center justify-center w-9 h-9 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 text-white font-semibold text-base shadow-sm">
            {number}
          </div>
          <div className="p-1.5 bg-white rounded-lg text-emerald-600">
            {icon}
          </div>
        </div>
        <h3 className="font-semibold text-gray-900 mb-1.5 text-base">{title}</h3>
        <p className="text-xs text-gray-600 leading-relaxed">{description}</p>
      </div>
    </div>
  )
}

// Component: Trust Indicator
function TrustIndicator({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="flex flex-col items-center">
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 text-blue-600 mb-3">
        {icon}
      </div>
      <h4 className="font-semibold text-gray-900 mb-1">{title}</h4>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  )
}

