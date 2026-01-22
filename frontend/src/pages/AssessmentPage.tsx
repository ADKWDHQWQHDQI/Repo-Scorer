import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle2, Loader2, CheckSquare, Square, Sparkles, AlertCircle } from 'lucide-react'
import { useAssessmentStore } from '../store/assessmentStore'
import { useAssessmentProgressStore } from '../store/assessmentProgressStore'
import { useQuery } from '@tanstack/react-query'
import { assessmentService } from '../services/assessmentService'
import { getImportanceLabel, getImportanceColor } from '../lib/utils'
import { QuestionInfoButton } from '../components/QuestionInfoButton'
import type { StartAssessmentRequest } from '../types'

export function AssessmentPage() {
  const navigate = useNavigate()
  const { tool, setResults, setShareInfo } = useAssessmentStore()
  const { setProgress } = useAssessmentProgressStore()
  
  const [questionAnswers, setQuestionAnswers] = useState<Record<string, 'yes' | 'no' | null>>({})
  const [sessionId, setSessionId] = useState<string>('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showProgressModal, setShowProgressModal] = useState(false)
  const [progressValue, setProgressValue] = useState(0)

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [])

  // Load questions from API with platform selections
  const { data: assessmentData, isLoading } = useQuery({
    queryKey: ['assessment', tool],
    queryFn: () => {
      // Get platform selections from session storage
      const cicdPlatform = sessionStorage.getItem('cicd_platform') || undefined
      const deploymentPlatform = sessionStorage.getItem('deployment_platform') || undefined
      
      return assessmentService.startAssessment({ 
        tool: tool!,
        cicd_platform: cicdPlatform as StartAssessmentRequest['cicd_platform'],
        deployment_platform: deploymentPlatform as StartAssessmentRequest['deployment_platform']
      })
    },
    enabled: !!tool,
  })

  const questions = assessmentData?.questions ?? []
  
  // Store session ID when assessment data is loaded
  useEffect(() => {
    if (assessmentData?.session_id) {
      setSessionId(assessmentData.session_id)
    }
  }, [assessmentData])
  
  // Calculate progress
  const answeredCount = Object.values(questionAnswers).filter(a => a !== null).length

  // Update progress store whenever answers change
  useEffect(() => {
    setProgress(answeredCount, questions.length)
  }, [answeredCount, questions.length, setProgress])

  const handleAnswerChange = (questionId: string, answer: 'yes' | 'no') => {
    setQuestionAnswers(prev => ({
      ...prev,
      [questionId]: prev[questionId] === answer ? null : answer
    }))
  }

  const handleSubmitAssessment = async () => {
    // Check if all questions are answered
    const allAnswered = questions.every(q => questionAnswers[q.id])
    if (!allAnswered) {
      alert('Please answer all questions before submitting.')
      return
    }

    setIsSubmitting(true)

    try {
      // Submit all answers and get analysis
      const answersWithAnalysis: Record<string, {
        question_id: string
        answer: string
        classification: "yes" | "no" | "unsure"
        score: number
        analysis: string
      }> = {}
      
      for (const question of questions) {
        const answer = questionAnswers[question.id]
        if (answer) {
          const response = await assessmentService.submitAnswer({
            session_id: sessionId,
            question_id: question.id,
            question_text: question.text,
            answer: answer === 'yes' ? 'Yes' : 'No',
            importance: question.importance,
          })
          
          answersWithAnalysis[question.id] = {
            question_id: question.id,
            answer: answer === 'yes' ? 'Yes' : 'No',
            classification: response.classification as "yes" | "no" | "unsure",
            score: response.score,
            analysis: response.analysis,
          }
        }
      }

      // Complete assessment
      const userEmail = sessionStorage.getItem('user_email') || ''
      const completeResponse = await assessmentService.completeAssessment({
        session_id: sessionId,
        tool: tool!,
        answers: answersWithAnalysis,
        email: userEmail,
      })

      // Store results and share information
      setResults(completeResponse.results)
      setShareInfo(
        completeResponse.share_token,
        completeResponse.email_sent,
        completeResponse.email_message
      )
      
      // Processing complete - now hide submitting state and show progress modal
      setIsSubmitting(false)
      
      // Small delay to ensure smooth transition, then show modal
      await new Promise(resolve => setTimeout(resolve, 300))
      
      setShowProgressModal(true)
      
      // Animate progress bar
      let progress = 0
      const targetScore = completeResponse.results.final_score
      const duration = 2500 // 2.5 seconds
      const steps = 60
      const increment = targetScore / steps
      const intervalTime = duration / steps
      
      const interval = setInterval(() => {
        progress += increment
        if (progress >= targetScore) {
          setProgressValue(targetScore)
          clearInterval(interval)
          // Navigate after animation completes, keeping modal visible
          setTimeout(() => {
            navigate('/results', { state: { showScoreAnimation: true, animatedScore: targetScore } })
          }, 500)
        } else {
          setProgressValue(progress)
        }
      }, intervalTime)
    } catch (error) {
      console.error('Error submitting assessment:', error)
      alert('Failed to submit assessment. Please try again.')
    } finally {
      // Don't set isSubmitting to false here, we do it after getting results
    }
  }

  if (!tool) {
    navigate('/')
    return null
  }

  if (isLoading || questions.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading assessment questions...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      {/* Progress Modal */}
      {showProgressModal && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 transform transition-all">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 mb-6 shadow-lg">
                <Sparkles className="w-8 h-8 text-white animate-pulse" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Calculating Your Score</h3>
              <p className="text-slate-600 mb-6">Analyzing your DevSecOps practices...</p>
              
              {/* Progress Bar */}
              <div className="relative w-full h-8 bg-slate-100 rounded-full overflow-hidden mb-4 shadow-inner">
                <div 
                  className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 transition-all duration-300 ease-out flex items-center justify-end px-3"
                  style={{ width: `${progressValue}%` }}
                >
                  <span className="text-white font-bold text-sm drop-shadow">
                    {Math.round(progressValue)}%
                  </span>
                </div>
              </div>
              
              {/* Score Display */}
              <div className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">
                {Math.round(progressValue)}<span className="text-2xl">/100</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-5xl mx-auto py-6 sm:py-8 px-4 sm:px-6 pb-28">
      {/* Questions Form */}
      <div className="space-y-4 mb-6">
        {questions.map((question, index) => {
          const isAnswered = questionAnswers[question.id] !== null && questionAnswers[question.id] !== undefined
          const selectedAnswer = questionAnswers[question.id]

          return (
            <div
              key={question.id}
              className={`bg-white rounded-xl p-5 shadow-sm border-2 transition-all ${
                isAnswered 
                  ? 'border-blue-200 bg-blue-50/30' 
                  : 'border-gray-200 hover:border-blue-100'
              }`}
            >
              <div className="flex items-start gap-4">
                {/* Question Number Badge */}
                <div className="flex-shrink-0">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-semibold text-sm ${
                    isAnswered 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {index + 1}
                  </div>
                </div>

                <div className="flex-1">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    {/* Priority Badge */}
                    <span
                      className={`inline-block px-2.5 py-1 rounded-full text-xs font-semibold ${getImportanceColor(
                        question.importance
                      )} bg-white border`}
                    >
                      {getImportanceLabel(question.importance)} Priority
                    </span>
                    
                    {/* Info Button in top-right */}
                    <QuestionInfoButton 
                      description={question.description} 
                      docUrl={question.doc_url} 
                    />
                  </div>

                  {/* Question Text */}
                  <h3 className="text-base font-semibold text-gray-900 mb-3">
                    <span className="text-gray-500 font-medium">Question {index + 1}:</span> {question.text}
                  </h3>

                  {/* Yes/No Options */}
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleAnswerChange(question.id, 'yes')}
                      className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg border-2 font-medium text-sm transition-all ${
                        selectedAnswer === 'yes'
                          ? 'bg-green-600 border-green-600 text-white shadow-md'
                          : 'bg-white border-gray-300 text-gray-700 hover:border-green-400 hover:bg-green-50'
                      }`}
                    >
                      {selectedAnswer === 'yes' ? (
                        <CheckSquare className="w-4 h-4" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                      Yes
                    </button>
                    <button
                      onClick={() => handleAnswerChange(question.id, 'no')}
                      className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg border-2 font-medium text-sm transition-all ${
                        selectedAnswer === 'no'
                          ? 'bg-red-600 border-red-600 text-white shadow-md'
                          : 'bg-white border-gray-300 text-gray-700 hover:border-red-400 hover:bg-red-50'
                      }`}
                    >
                      {selectedAnswer === 'no' ? (
                        <CheckSquare className="w-4 h-4" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                      No
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Incomplete Warning */}
      {answeredCount < questions.length && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-900">
              Please answer all questions before submitting
            </p>
            <p className="text-xs text-amber-700 mt-1">
              {questions.length - answeredCount} question{questions.length - answeredCount !== 1 ? 's' : ''} remaining
            </p>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <div className="sticky bottom-4 sm:bottom-6 bg-white rounded-xl p-4 shadow-lg border border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">
              Ready to submit your assessment?
            </p>
            <p className="text-xs text-gray-600">
              All answers will be analyzed using AI to generate your comprehensive report
            </p>
          </div>
          <button
            onClick={handleSubmitAssessment}
            disabled={answeredCount < questions.length || isSubmitting}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold text-sm rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg disabled:shadow-none whitespace-nowrap"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                Submit Assessment
                <CheckCircle2 className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
    </>
  )
}
