// TypeScript type definitions for DevSecOps Maturity Assessment

export const RepositoryTool = {
  GITHUB: 'github',
  GITLAB: 'gitlab',
  AZURE_DEVOPS: 'azure_devops',
  BITBUCKET: 'bitbucket',
} as const;

export type RepositoryTool = typeof RepositoryTool[keyof typeof RepositoryTool];

export const CICDPlatform = {
  GITHUB_ACTIONS: 'github_actions',
  AZURE_PIPELINES: 'azure_pipelines',
  GITLAB_CI: 'gitlab_ci',
  JENKINS: 'jenkins',
  CIRCLECI: 'circleci',
} as const;

export type CICDPlatform = typeof CICDPlatform[keyof typeof CICDPlatform];

export const DeploymentPlatform = {
  AZURE: 'azure',
  AWS: 'aws',
  GCP: 'gcp',
  ON_PREMISE: 'on_premise',
  KUBERNETES: 'kubernetes',
} as const;

export type DeploymentPlatform = typeof DeploymentPlatform[keyof typeof DeploymentPlatform];

export interface Question {
  id: string
  text: string
  max_score: number
  importance: number // 1-10 scale
  pillar: string // Pillar name
  pillar_id?: string // Pillar ID
  description?: string // Two-line explanation of how the feature works
  doc_url?: string // Official documentation URL for the feature
}

export interface Pillar {
  id: string
  name: string
  total_weight: number
  questions?: Question[]
  question_count: number
}

export interface QuestionResult {
  question_id: string
  question_text: string
  user_answer: string
  classification: 'yes' | 'no' | 'unsure'
  score_earned: number
  max_score: number
  analysis?: string
  pillar_id?: string
  pillar_name?: string
}

export interface PillarBreakdown {
  id: string
  name: string
  earned: number
  max: number
  percentage: number
}

export interface AssessmentResult {
  final_score: number
  breakdown: Record<string, PillarBreakdown>
  question_results: QuestionResult[]
  summary: string
}

export interface Answer {
  question_id: string
  answer: string
  classification: 'yes' | 'no' | 'unsure'
  score: number
  analysis?: string
}

export interface AssessmentState {
  tool: RepositoryTool | null
  currentQuestionIndex: number
  answers: Record<string, Answer>
  isComplete: boolean
  results: AssessmentResult | null
}

// API Request/Response types
export interface StartAssessmentRequest {
  tool: RepositoryTool
  cicd_platform?: CICDPlatform
  deployment_platform?: DeploymentPlatform
}

export interface StartAssessmentResponse {
  session_id: string
  questions: Question[]
  pillars: Record<string, Pillar>
  message: string
}

export interface SubmitAnswerRequest {
  session_id: string
  question_id: string
  question_text: string
  answer: string
  importance: number
}

export interface SubmitAnswerResponse {
  classification: 'yes' | 'no' | 'unsure'
  score: number
  analysis: string
}

export interface CompleteAssessmentRequest {
  session_id: string
  tool: RepositoryTool
  answers: Record<string, Answer>
  email: string
}

export interface CompleteAssessmentResponse {
  results: AssessmentResult
  share_token: string
  email_sent: boolean
  email_message: string
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy'
  service_connected: boolean
  deployment_available: boolean
  message: string
}
