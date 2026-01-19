import { describe, it, expect, vi, beforeEach } from 'vitest'
import MockAdapter from 'axios-mock-adapter'
import { apiClient } from '../../src/services/api'
import {
  startAssessment,
  submitAnswer,
  completeAssessment,
  saveEmail,
  shareResults,
  getSharedResults,
  getStatistics
} from '../../src/services/assessmentService'

describe('Assessment Service', () => {
  let mock: MockAdapter

  beforeEach(() => {
    mock = new MockAdapter(apiClient)
  })

  afterEach(() => {
    mock.restore()
  })

  describe('startAssessment', () => {
    it('should start assessment successfully', async () => {
      const mockResponse = {
        session_id: 'session123',
        questions: [
          { id: 'q1', text: 'Question 1?', max_score: 10, importance: 8, pillar: 'security' }
        ],
        pillars: {
          security: { id: 'security', name: 'Security', total_weight: 10, question_count: 1 }
        },
        message: 'Assessment started'
      }

      mock.onPost('/start-assessment').reply(200, mockResponse)

      const result = await startAssessment('github')
      expect(result.session_id).toBe('session123')
      expect(result.questions).toHaveLength(1)
    })

    it('should handle start assessment error', async () => {
      mock.onPost('/start-assessment').reply(500)

      await expect(startAssessment('github')).rejects.toThrow()
    })
  })

  describe('submitAnswer', () => {
    it('should submit answer successfully', async () => {
      const mockResponse = {
        classification: 'yes',
        score: 10,
        analysis: 'Good answer'
      }

      mock.onPost('/submit-answer').reply(200, mockResponse)

      const result = await submitAnswer({
        session_id: 'session123',
        question_id: 'q1',
        question_text: 'Question?',
        answer: 'Yes, we have this',
        importance: 8
      })

      expect(result.classification).toBe('yes')
      expect(result.score).toBe(10)
    })

    it('should handle submit answer error', async () => {
      mock.onPost('/submit-answer').reply(404)

      await expect(submitAnswer({
        session_id: 'invalid',
        question_id: 'q1',
        question_text: 'Q?',
        answer: 'A',
        importance: 5
      })).rejects.toThrow()
    })
  })

  describe('completeAssessment', () => {
    it('should complete assessment successfully', async () => {
      const mockResponse = {
        final_score: 75.5,
        breakdown: {},
        question_results: [],
        summary: 'Good work'
      }

      mock.onPost('/complete-assessment').reply(200, mockResponse)

      const result = await completeAssessment({
        session_id: 'session123',
        tool: 'github',
        answers: {}
      })

      expect(result.final_score).toBe(75.5)
    })

    it('should handle complete assessment error', async () => {
      mock.onPost('/complete-assessment').reply(500)

      await expect(completeAssessment({
        session_id: 'session123',
        tool: 'github',
        answers: {}
      })).rejects.toThrow()
    })
  })

  describe('saveEmail', () => {
    it('should save email successfully', async () => {
      const mockResponse = {
        message: 'Email saved successfully'
      }

      mock.onPost('/save-email').reply(200, mockResponse)

      const result = await saveEmail({
        email: 'test@company.com',
        repository_platform: 'GitHub'
      })

      expect(result.message).toBe('Email saved successfully')
    })

    it('should reject personal email', async () => {
      mock.onPost('/save-email').reply(400, {
        detail: 'Personal email domains are not allowed'
      })

      await expect(saveEmail({
        email: 'test@gmail.com',
        repository_platform: 'GitHub'
      })).rejects.toThrow()
    })
  })

  describe('shareResults', () => {
    it('should share results successfully', async () => {
      const mockResponse = {
        share_token: 'token123',
        public_url: 'http://example.com/shared/token123',
        email_sent: true,
        message: 'Results shared successfully'
      }

      mock.onPost('/share-results').reply(200, mockResponse)

      const result = await shareResults({
        email: 'test@company.com',
        results: {
          final_score: 75,
          breakdown: {},
          question_results: [],
          summary: 'Good'
        },
        platform: 'GitHub'
      })

      expect(result.share_token).toBe('token123')
      expect(result.email_sent).toBe(true)
    })
  })

  describe('getSharedResults', () => {
    it('should get shared results successfully', async () => {
      const mockResponse = {
        final_score: 75,
        breakdown: {},
        question_results: [],
        summary: 'Good',
        email: 'test@company.com',
        platform: 'GitHub'
      }

      mock.onGet('/shared-results/token123').reply(200, mockResponse)

      const result = await getSharedResults('token123')
      expect(result.final_score).toBe(75)
      expect(result.platform).toBe('GitHub')
    })

    it('should handle invalid token', async () => {
      mock.onGet('/shared-results/invalid').reply(404)

      await expect(getSharedResults('invalid')).rejects.toThrow()
    })
  })

  describe('getStatistics', () => {
    it('should get statistics successfully', async () => {
      const mockResponse = {
        total_assessments: 100,
        platform_distribution: {
          GitHub: 50,
          GitLab: 30,
          'Azure DevOps': 20
        },
        average_score: 72.5
      }

      mock.onGet('/statistics').reply(200, mockResponse)

      const result = await getStatistics()
      expect(result.total_assessments).toBe(100)
      expect(result.average_score).toBe(72.5)
    })
  })
})
