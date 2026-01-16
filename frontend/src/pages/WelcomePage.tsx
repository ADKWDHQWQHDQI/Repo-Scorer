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
  Lock,
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
    <div className="max-w-6xl mx-auto py-6 px-4">
      {/* Hero Section */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 mb-5 shadow-md">
          <Shield className="w-9 h-9 text-white" />
        </div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-900 via-blue-800 to-indigo-900 bg-clip-text text-transparent mb-3">
          DevSecOps Pipeline Assessment
        </h1>
        <p className="text-lg text-gray-700 max-w-3xl mx-auto font-medium mb-2">
          AI-Powered Evaluation Platform for Modern Software Development
        </p>
        <p className="text-sm text-gray-600 max-w-2xl mx-auto">
          Comprehensive analysis of your repository governance, CI/CD maturity, code quality, and security posture
        </p>
      </div>

      {/* Platform Overview Section */}
      <section className="mb-8 bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2.5 mb-5">
          <div className="p-2.5 bg-blue-600 rounded-lg">
            <Target className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900">Platform Overview</h2>
        </div>
        <div className="grid md:grid-cols-2 gap-5">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-5 border border-blue-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-2.5 flex items-center gap-2">
              <Sparkles className="w-4.5 h-4.5 text-blue-600" />
              What We Do
            </h3>
            <p className="text-gray-700 text-sm leading-relaxed mb-3.5">
              Our platform delivers enterprise-grade repository assessments using Azure OpenAI technology. 
              We evaluate 15 critical dimensions of your software development lifecycle, from repository structure 
              to security compliance, providing data-driven insights to optimize your DevSecOps practices.
            </p>
            <ul className="space-y-1.5 text-gray-700 text-sm">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span><strong>Comprehensive Analysis:</strong> 15 weighted assessment criteria</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span><strong>AI-Enhanced:</strong> AI-powered recommendations</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <span><strong>Multi-Platform:</strong> GitHub, GitLab, Azure DevOps support</span>
              </li>
            </ul>
          </div>
          <div className="bg-gradient-to-br from-slate-50 to-gray-50 rounded-lg p-5 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-2.5 flex items-center gap-2">
              <Shield className="w-4.5 h-4.5 text-blue-600" />
              Assessment Focus Areas
            </h3>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <GitCommit className="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Repository Governance</h4>
                  <p className="text-sm text-gray-600">Branch protection, access controls, compliance</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="p-2 bg-green-50 rounded-lg">
                  <Zap className="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">CI/CD Maturity</h4>
                  <p className="text-sm text-gray-600">Pipeline automation, testing, deployment strategies</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="p-2 bg-purple-50 rounded-lg">
                  <BarChart3 className="w-4 h-4 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Code Quality & Security</h4>
                  <p className="text-sm text-gray-600">Static analysis, vulnerability scanning, best practices</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Assessment Deliverables Section */}
      <section className="mb-8 bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
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
      <section className="mb-8 bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2.5 mb-5">
          <div className="p-2.5 bg-emerald-600 rounded-lg">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900">Assessment Workflow</h2>
        </div>
        <p className="text-gray-700 mb-6 text-sm">
          Our streamlined process ensures a thorough evaluation in under 10 minutes:
        </p>
        <div className="grid md:grid-cols-4 gap-6">
          <WorkflowStep
            number="1"
            title="Select Platform"
            description="Choose your repository platform: GitHub, GitLab, or Azure DevOps"
            icon={<Target className="w-6 h-6" />}
          />
          <WorkflowStep
            number="2"
            title="Answer Questions"
            description="Complete 15 targeted questions about your repository setup and practices"
            icon={<CheckCircle2 className="w-6 h-6" />}
          />
          <WorkflowStep
            number="3"
            title="AI Analysis"
            description="AI processes your responses and generates comprehensive insights"
            icon={<Sparkles className="w-6 h-6" />}
          />
          <WorkflowStep
            number="4"
            title="Review Results"
            description="Access your detailed score, visualizations, and actionable recommendations"
            icon={<BarChart3 className="w-6 h-6" />}
          />
        </div>
      </section>

      {/* Call to Action */}
      <div className="text-center py-8">
        <button
          onClick={handleGetStarted}
          className="inline-flex items-center gap-2.5 px-8 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold text-base rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
        >
          Get Started
          <ArrowRight className="w-5 h-5" />
        </button>
        <p className="text-gray-600 mt-4 text-sm">
          Begin your comprehensive DevSecOps assessment
        </p>
      </div>

      {/* Trust Indicators */}
      <div className="mt-12 pt-8 border-t border-gray-200">
        <div className="grid md:grid-cols-4 gap-6 text-center">
          <TrustIndicator
            icon={<Lock className="w-6 h-6" />}
            title="Enterprise Security"
            description="Azure OpenAI with data privacy"
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

