import { create } from 'zustand'
import type { AssessmentState, Answer, AssessmentResult, RepositoryTool } from '../types'

interface AssessmentStore extends AssessmentState {
  shareToken: string | null
  emailSent: boolean
  emailMessage: string
  setTool: (tool: RepositoryTool) => void
  addAnswer: (questionId: string, answer: Answer) => void
  nextQuestion: () => void
  previousQuestion: () => void
  setResults: (results: AssessmentResult) => void
  setShareInfo: (shareToken: string, emailSent: boolean, emailMessage: string) => void
  setQuestions: () => void
  reset: () => void
}

const initialState: AssessmentState = {
  tool: null,
  currentQuestionIndex: 0,
  answers: {},
  isComplete: false,
  results: null,
}

export const useAssessmentStore = create<AssessmentStore>((set) => ({
  ...initialState,
  shareToken: null,
  emailSent: false,
  emailMessage: '',

  setTool: (tool) => set({ tool }),

  addAnswer: (questionId, answer) =>
    set((state) => ({
      answers: { ...state.answers, [questionId]: answer },
    })),

  nextQuestion: () =>
    set((state) => ({
      currentQuestionIndex: state.currentQuestionIndex + 1,
    })),

  previousQuestion: () =>
    set((state) => ({
      currentQuestionIndex: Math.max(0, state.currentQuestionIndex - 1),
    })),

  setResults: (results) =>
    set({
      results,
      isComplete: true,
    }),

  setShareInfo: (shareToken, emailSent, emailMessage) =>
    set({
      shareToken,
      emailSent,
      emailMessage,
    }),

  setQuestions: () =>
    set({
      currentQuestionIndex: 0,
    }),

  reset: () => set({ ...initialState, shareToken: null, emailSent: false, emailMessage: '' }),
}))
