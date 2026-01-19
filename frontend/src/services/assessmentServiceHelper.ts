import apiClient from './api'
import type {
  StartAssessmentResponse,
  SubmitAnswerRequest,
  SubmitAnswerResponse,
  CompleteAssessmentRequest,
  AssessmentResult,
} from '../types'

// Start assessment
export const startAssessment = async (tool: string): Promise<StartAssessmentResponse> => {
  const response = await apiClient.post<StartAssessmentResponse>('/start-assessment', { tool })
  return response.data
}

// Submit answer
export const submitAnswer = async (data: SubmitAnswerRequest): Promise<SubmitAnswerResponse> => {
  const response = await apiClient.post<SubmitAnswerResponse>('/submit-answer', data)
  return response.data
}

// Complete assessment
export const completeAssessment = async (data: CompleteAssessmentRequest): Promise<AssessmentResult> => {
  const response = await apiClient.post<AssessmentResult>('/complete-assessment', data)
  return response.data
}

// Save email
export const saveEmail = async (data: {
  email: string
  repository_platform?: string
  cicd_platform?: string
  deployment_platform?: string
}) => {
  const response = await apiClient.post('/save-email', data)
  return response.data
}

// Share results
export const shareResults = async (data: {
  email: string
  results: AssessmentResult
  platform: string
}) => {
  const response = await apiClient.post('/share-results', data)
  return response.data
}

// Get shared results
export const getSharedResults = async (shareToken: string) => {
  const response = await apiClient.get(`/shared-results/${shareToken}`)
  return response.data
}

// Get statistics
export const getStatistics = async () => {
  const response = await apiClient.get('/statistics')
  return response.data
}
