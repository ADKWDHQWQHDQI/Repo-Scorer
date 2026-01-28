import { create } from 'zustand'

interface AssessmentProgressState {
  answeredCount: number
  totalQuestions: number
  percentage: number
  setProgress: (answeredCount: number, totalQuestions: number) => void
  resetProgress: () => void
}

export const useAssessmentProgressStore = create<AssessmentProgressState>((set) => ({
  answeredCount: 0,
  totalQuestions: 0,
  percentage: 0,
  setProgress: (answeredCount, totalQuestions) =>
    set({
      answeredCount,
      totalQuestions,
      percentage: totalQuestions > 0 ? (answeredCount / totalQuestions) * 100 : 0,
    }),
  resetProgress: () => set({ answeredCount: 0, totalQuestions: 0, percentage: 0 }),
}))
