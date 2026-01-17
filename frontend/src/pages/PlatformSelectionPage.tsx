import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  Github, 
  GitBranch, 
  Cloud, 
  ArrowRight, 
  CheckCircle2,
  Zap,
  Rocket,
  Server,
  Box,
  Circle
} from 'lucide-react'
import { useAssessmentStore } from '../store/assessmentStore'
import { RepositoryTool } from '../types'

// Platform types
type RepositoryPlatform = 'github' | 'gitlab' | 'azure_repos' | 'bitbucket'
type CICDPlatform = 'github_actions' | 'azure_pipelines' | 'gitlab_ci' | 'jenkins' | 'circleci'
type DeploymentPlatform = 'azure' | 'aws' | 'gcp' | 'on_premise' | 'kubernetes'

export function PlatformSelectionPage() {
  const navigate = useNavigate()
  const { setTool } = useAssessmentStore()
  const [repositoryPlatform, setRepositoryPlatform] = useState<RepositoryPlatform | null>(null)
  const [cicdPlatform, setCicdPlatform] = useState<CICDPlatform | null>(null)
  const [deploymentPlatform, setDeploymentPlatform] = useState<DeploymentPlatform | null>(null)

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [])

  // Map selections to backend RepositoryTool
  const getRepositoryTool = (): RepositoryTool | null => {
    if (repositoryPlatform === 'github') return RepositoryTool.GITHUB
    if (repositoryPlatform === 'gitlab') return RepositoryTool.GITLAB
    if (repositoryPlatform === 'azure_repos') return RepositoryTool.AZURE_DEVOPS
    // For Bitbucket, default to GitHub for now (you can extend the backend later)
    if (repositoryPlatform === 'bitbucket') return RepositoryTool.GITHUB
    return null
  }

  const handleContinue = () => {
    const tool = getRepositoryTool()
    if (tool && repositoryPlatform && cicdPlatform && deploymentPlatform) {
      // Set tool in store
      setTool(tool)
      
      // Store selections in session storage for later use
      sessionStorage.setItem('repository_platform', repositoryPlatform || '')
      sessionStorage.setItem('cicd_platform', cicdPlatform || '')
      sessionStorage.setItem('deployment_platform', deploymentPlatform || '')
      
      // Navigate to email page
      navigate('/email')
    }
  }

  const isFormComplete = repositoryPlatform && cicdPlatform && deploymentPlatform

  return (
    <div className="max-w-6xl mx-auto py-6 sm:py-8 px-4 sm:px-6">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 mb-4 shadow-md">
          <Zap className="w-7 h-7 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2.5">
          Configure Your Technology Stack
        </h1>
        <p className="text-sm text-gray-600 max-w-2xl mx-auto">
          Select the platforms you use across your development, CI/CD, and deployment lifecycle
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <StepIndicator active={!!repositoryPlatform} label="Repository" />
          <div className="hidden sm:block w-10 md:w-16 h-0.5 bg-gray-300" />
          <StepIndicator active={!!cicdPlatform} label="CI/CD" />
          <div className="hidden sm:block w-10 md:w-16 h-0.5 bg-gray-300" />
          <StepIndicator active={!!deploymentPlatform} label="Deployment" />
        </div>
      </div>

      {/* Repository Platform Section */}
      <section className="mb-6 bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="p-2 bg-blue-600 rounded-lg">
            <GitBranch className="w-4.5 h-4.5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Repository Platform</h2>
            <p className="text-xs text-gray-600">Where do you host your source code?</p>
          </div>
        </div>
        <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <PlatformCard
            icon={<Github className="w-8 h-8" />}
            name="GitHub"
            description="GitHub Repositories"
            selected={repositoryPlatform === 'github'}
            onClick={() => setRepositoryPlatform('github')}
            color="gray"
          />
          <PlatformCard
            icon={<GitBranch className="w-8 h-8" />}
            name="GitLab"
            description="GitLab Projects"
            selected={repositoryPlatform === 'gitlab'}
            onClick={() => setRepositoryPlatform('gitlab')}
            color="orange"
          />
          <PlatformCard
            icon={<Cloud className="w-8 h-8" />}
            name="Azure Repos"
            description="Azure DevOps Repos"
            selected={repositoryPlatform === 'azure_repos'}
            onClick={() => setRepositoryPlatform('azure_repos')}
            color="blue"
          />
          <PlatformCard
            icon={<Box className="w-8 h-8" />}
            name="Bitbucket"
            description="Atlassian Bitbucket"
            selected={repositoryPlatform === 'bitbucket'}
            onClick={() => setRepositoryPlatform('bitbucket')}
            color="blue"
          />
        </div>
      </section>

      {/* CI/CD Platform Section */}
      <section className="mb-6 bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="p-2 bg-emerald-600 rounded-lg">
            <Zap className="w-4.5 h-4.5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">CI/CD Pipeline Platform</h2>
            <p className="text-xs text-gray-600">Which tool manages your continuous integration and delivery?</p>
          </div>
        </div>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <PlatformCard
            icon={<Github className="w-8 h-8" />}
            name="GitHub Actions"
            description="Workflows"
            selected={cicdPlatform === 'github_actions'}
            onClick={() => setCicdPlatform('github_actions')}
            color="gray"
          />
          <PlatformCard
            icon={<Cloud className="w-8 h-8" />}
            name="Azure Pipelines"
            description="Azure DevOps"
            selected={cicdPlatform === 'azure_pipelines'}
            onClick={() => setCicdPlatform('azure_pipelines')}
            color="blue"
          />
          <PlatformCard
            icon={<GitBranch className="w-8 h-8" />}
            name="GitLab CI"
            description="GitLab CI/CD"
            selected={cicdPlatform === 'gitlab_ci'}
            onClick={() => setCicdPlatform('gitlab_ci')}
            color="orange"
          />
          <PlatformCard
            icon={<Server className="w-8 h-8" />}
            name="Jenkins"
            description="Automation Server"
            selected={cicdPlatform === 'jenkins'}
            onClick={() => setCicdPlatform('jenkins')}
            color="red"
          />
          <PlatformCard
            icon={<Circle className="w-8 h-8" />}
            name="CircleCI"
            description="Cloud CI/CD"
            selected={cicdPlatform === 'circleci'}
            onClick={() => setCicdPlatform('circleci')}
            color="green"
          />
        </div>
      </section>

      {/* Deployment Platform Section */}
      <section className="mb-6 bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="p-2 bg-purple-600 rounded-lg">
            <Rocket className="w-4.5 h-4.5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Deployment Platform</h2>
            <p className="text-xs text-gray-600">Where do you deploy your applications?</p>
          </div>
        </div>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <PlatformCard
            icon={<Cloud className="w-8 h-8" />}
            name="Azure"
            description="Microsoft Azure"
            selected={deploymentPlatform === 'azure'}
            onClick={() => setDeploymentPlatform('azure')}
            color="blue"
          />
          <PlatformCard
            icon={<Cloud className="w-8 h-8" />}
            name="AWS"
            description="Amazon Web Services"
            selected={deploymentPlatform === 'aws'}
            onClick={() => setDeploymentPlatform('aws')}
            color="orange"
          />
          <PlatformCard
            icon={<Cloud className="w-8 h-8" />}
            name="GCP"
            description="Google Cloud Platform"
            selected={deploymentPlatform === 'gcp'}
            onClick={() => setDeploymentPlatform('gcp')}
            color="blue"
          />
          <PlatformCard
            icon={<Server className="w-8 h-8" />}
            name="On-Premise"
            description="Self-Hosted"
            selected={deploymentPlatform === 'on_premise'}
            onClick={() => setDeploymentPlatform('on_premise')}
            color="gray"
          />
          <PlatformCard
            icon={<Box className="w-8 h-8" />}
            name="Kubernetes"
            description="Container Orchestration"
            selected={deploymentPlatform === 'kubernetes'}
            onClick={() => setDeploymentPlatform('kubernetes')}
            color="blue"
          />
        </div>
      </section>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pt-5 border-t border-gray-200">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 px-4 py-2.5 text-gray-600 font-medium text-sm rounded-lg hover:bg-gray-100 transition-colors"
        >
          ← Back to Home
        </button>
        <button
          onClick={handleContinue}
          disabled={!isFormComplete}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold text-sm rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg disabled:shadow-none"
        >
          Continue to Email
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {!isFormComplete && (
        <p className="text-center text-gray-600 mt-4 text-sm">
          Please complete all selections to continue
        </p>
      )}
    </div>
  )
}

// Component: Step Indicator
function StepIndicator({ active, label }: { active: boolean; label: string }) {
  return (
    <div className="flex flex-col items-center">
      <div
        className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${
          active
            ? 'bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-lg'
            : 'bg-gray-200 text-gray-500'
        }`}
      >
        {active ? <CheckCircle2 className="w-6 h-6" /> : <Circle className="w-5 h-5" />}
      </div>
      <span className={`text-xs mt-1 font-medium ${active ? 'text-blue-600' : 'text-gray-500'}`}>
        {label}
      </span>
    </div>
  )
}

// Component: Platform Card
function PlatformCard({
  icon,
  name,
  description,
  selected,
  onClick,
  color,
}: {
  icon: React.ReactNode
  name: string
  description: string
  selected: boolean
  onClick: () => void
  color: 'gray' | 'orange' | 'blue' | 'red' | 'green'
}) {
  const colorClasses = {
    gray: { 
      bg: 'bg-gray-700', 
      border: 'border-gray-600',
      hover: 'hover:border-gray-500'
    },
    orange: { 
      bg: 'bg-orange-600', 
      border: 'border-orange-600',
      hover: 'hover:border-orange-500'
    },
    blue: { 
      bg: 'bg-blue-600', 
      border: 'border-blue-600',
      hover: 'hover:border-blue-500'
    },
    red: { 
      bg: 'bg-red-600', 
      border: 'border-red-600',
      hover: 'hover:border-red-500'
    },
    green: { 
      bg: 'bg-green-600', 
      border: 'border-green-600',
      hover: 'hover:border-green-500'
    },
  }

  return (
    <button
      onClick={onClick}
      className={`p-4 rounded-lg border-2 transition-all text-center hover:shadow-md ${
        selected
          ? `${colorClasses[color].border} bg-gradient-to-br from-blue-50 to-indigo-50 shadow-md border-blue-500`
          : `border-gray-200 bg-white hover:border-gray-300`
      }`}
    >
      <div
        className={`inline-flex items-center justify-center w-11 h-11 rounded-lg mb-2.5 transition-all ${
          selected ? `${colorClasses[color].bg} text-white shadow-sm` : 'bg-gray-50 text-gray-500'
        }`}
      >
        {icon}
      </div>
      <h3 className={`font-semibold text-sm mb-0.5 ${selected ? 'text-gray-900' : 'text-gray-700'}`}>
        {name}
      </h3>
      <p className={`text-xs ${selected ? 'text-gray-600' : 'text-gray-500'}`}>{description}</p>
      {selected && (
        <div className="mt-2 flex items-center justify-center gap-1 text-blue-600 font-medium text-xs">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Selected</span>
        </div>
      )}
    </button>
  )
}
