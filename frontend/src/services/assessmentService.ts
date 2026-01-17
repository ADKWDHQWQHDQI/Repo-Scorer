import apiClient from './api'
import type {
  StartAssessmentRequest,
  StartAssessmentResponse,
  SubmitAnswerRequest,
  SubmitAnswerResponse,
  CompleteAssessmentRequest,
  CompleteAssessmentResponse,
  HealthCheckResponse,
} from '../types'

export const assessmentService = {
  checkHealth: async (): Promise<HealthCheckResponse> => {
    const response = await apiClient.get<HealthCheckResponse>('/api/health')
    return response.data
  },

  startAssessment: async (data: StartAssessmentRequest): Promise<StartAssessmentResponse> => {
    const response = await apiClient.post<StartAssessmentResponse>('/api/assessment/start', data)
    return response.data
  },

  submitAnswer: async (data: SubmitAnswerRequest): Promise<SubmitAnswerResponse> => {
    const response = await apiClient.post<SubmitAnswerResponse>('/api/assessment/answer', data)
    return response.data
  },

  completeAssessment: async (
    data: CompleteAssessmentRequest
  ): Promise<CompleteAssessmentResponse> => {
    const response = await apiClient.post<CompleteAssessmentResponse>(
      '/api/assessment/complete',
      data
    )
    return response.data
  },
}
