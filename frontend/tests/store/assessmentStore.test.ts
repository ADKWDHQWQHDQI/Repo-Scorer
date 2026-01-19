import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAssessmentStore } from '../../src/store/assessmentStore'
import type { RepositoryTool, AssessmentResult, Answer } from '../../src/types'

describe('Assessment Store', () => {
  beforeEach(() => {
    // Reset store before each test
    useAssessmentStore.getState().reset()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      expect(result.current.tool).toBeNull()
      expect(result.current.currentQuestionIndex).toBe(0)
      expect(result.current.answers).toEqual({})
      expect(result.current.isComplete).toBe(false)
      expect(result.current.results).toBeNull()
      expect(result.current.shareToken).toBeNull()
      expect(result.current.emailSent).toBe(false)
    })
  })

  describe('setTool', () => {
    it('should set the tool', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      act(() => {
        result.current.setTool('github' as RepositoryTool)
      })
      
      expect(result.current.tool).toBe('github')
    })

    it('should handle different tools', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      act(() => {
        result.current.setTool('gitlab' as RepositoryTool)
      })
      expect(result.current.tool).toBe('gitlab')
      
      act(() => {
        result.current.setTool('azure_devops' as RepositoryTool)
      })
      expect(result.current.tool).toBe('azure_devops')
    })
  })

  describe('addAnswer', () => {
    it('should add an answer', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      const answer: Answer = {
        question_id: 'q1',
        answer: 'Yes, we have this',
        classification: 'yes',
        score: 10
      }
      
      act(() => {
        result.current.addAnswer('q1', answer)
      })
      
      expect(result.current.answers['q1']).toEqual(answer)
    })

    it('should handle multiple answers', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      const answer1: Answer = {
        question_id: 'q1',
        answer: 'Yes',
        classification: 'yes',
        score: 10
      }
      
      const answer2: Answer = {
        question_id: 'q2',
        answer: 'No',
        classification: 'no',
        score: 0
      }
      
      act(() => {
        result.current.addAnswer('q1', answer1)
        result.current.addAnswer('q2', answer2)
      })
      
      expect(Object.keys(result.current.answers)).toHaveLength(2)
      expect(result.current.answers['q1']).toEqual(answer1)
      expect(result.current.answers['q2']).toEqual(answer2)
    })

    it('should overwrite existing answer', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      const answer1: Answer = {
        question_id: 'q1',
        answer: 'Yes',
        classification: 'yes',
        score: 10
      }
      
      const answer2: Answer = {
        question_id: 'q1',
        answer: 'Updated answer',
        classification: 'no',
        score: 0
      }
      
      act(() => {
        result.current.addAnswer('q1', answer1)
        result.current.addAnswer('q1', answer2)
      })
      
      expect(result.current.answers['q1']).toEqual(answer2)
    })
  })

  describe('nextQuestion', () => {
    it('should increment question index', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      act(() => {
        result.current.nextQuestion()
      })
      
      expect(result.current.currentQuestionIndex).toBe(1)
    })

    it('should increment multiple times', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      act(() => {
        result.current.nextQuestion()
        result.current.nextQuestion()
        result.current.nextQuestion()
      })
      
      expect(result.current.currentQuestionIndex).toBe(3)
    })
  })

  describe('previousQuestion', () => {
    it('should decrement question index', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      act(() => {
        result.current.nextQuestion()
        result.current.nextQuestion()
        result.current.previousQuestion()
      })
      
      expect(result.current.currentQuestionIndex).toBe(1)
    })

    it('should not go below zero', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      act(() => {
        result.current.previousQuestion()
      })
      
      expect(result.current.currentQuestionIndex).toBe(0)
    })
  })

  describe('setResults', () => {
    it('should set results and mark as complete', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      const results: AssessmentResult = {
        final_score: 75.5,
        breakdown: {
          security: {
            id: 'security',
            name: 'Security',
            earned: 20,
            max: 30,
            percentage: 66.7
          }
        },
        question_results: [],
        summary: 'Good performance'
      }
      
      act(() => {
        result.current.setResults(results)
      })
      
      expect(result.current.results).toEqual(results)
      expect(result.current.isComplete).toBe(true)
    })
  })

  describe('setShareInfo', () => {
    it('should set share information', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      act(() => {
        result.current.setShareInfo('token123', true, 'Email sent successfully')
      })
      
      expect(result.current.shareToken).toBe('token123')
      expect(result.current.emailSent).toBe(true)
      expect(result.current.emailMessage).toBe('Email sent successfully')
    })
  })

  describe('reset', () => {
    it('should reset store to initial state', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      // Set some state
      act(() => {
        result.current.setTool('github' as RepositoryTool)
        result.current.addAnswer('q1', {
          question_id: 'q1',
          answer: 'Yes',
          classification: 'yes',
          score: 10
        })
        result.current.nextQuestion()
        result.current.setShareInfo('token', true, 'message')
      })
      
      // Reset
      act(() => {
        result.current.reset()
      })
      
      expect(result.current.tool).toBeNull()
      expect(result.current.currentQuestionIndex).toBe(0)
      expect(result.current.answers).toEqual({})
      expect(result.current.isComplete).toBe(false)
      expect(result.current.results).toBeNull()
      expect(result.current.shareToken).toBeNull()
      expect(result.current.emailSent).toBe(false)
      expect(result.current.emailMessage).toBe('')
    })
  })

  describe('setQuestions', () => {
    it('should reset question index', () => {
      const { result } = renderHook(() => useAssessmentStore())
      
      act(() => {
        result.current.nextQuestion()
        result.current.nextQuestion()
        result.current.setQuestions()
      })
      
      expect(result.current.currentQuestionIndex).toBe(0)
    })
  })
})
