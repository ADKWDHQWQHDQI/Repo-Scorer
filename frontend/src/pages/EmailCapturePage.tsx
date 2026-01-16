import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, ArrowRight, CheckCircle2, Sparkles, Shield, AlertCircle } from 'lucide-react'
import { api } from '../services/api'

const PERSONAL_EMAIL_DOMAINS = [
  'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
  'aol.com', 'icloud.com', 'mail.com', 'protonmail.com',
  'zoho.com', 'yandex.com', 'gmx.com', 'live.com',
  'msn.com', 'rediffmail.com', 'inbox.com'
]

export function EmailCapturePage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [isValid, setIsValid] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [])

  const validateEmail = (email: string): { valid: boolean; error: string } => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    
    if (!emailRegex.test(email)) {
      return { valid: false, error: 'Please enter a valid email address' }
    }
    
    const domain = email.split('@')[1].toLowerCase()
    if (PERSONAL_EMAIL_DOMAINS.includes(domain)) {
      return { 
        valid: false, 
        error: 'Personal email addresses are not allowed. Please use your work email.' 
      }
    }
    
    return { valid: true, error: '' }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const validation = validateEmail(email)
    
    if (!validation.valid) {
      setIsValid(false)
      setErrorMessage(validation.error)
      return
    }
    
    setIsSubmitting(true)
    
    try {
      // Get platform selections from session storage
      const repositoryPlatform = sessionStorage.getItem('repository_platform') || ''
      const cicdPlatform = sessionStorage.getItem('cicd_platform') || ''
      const deploymentPlatform = sessionStorage.getItem('deployment_platform') || ''
      
      // Save email to database
      const response = await api.post('/api/email/save', {
        email,
        repository_platform: repositoryPlatform,
        cicd_platform: cicdPlatform,
        deployment_platform: deploymentPlatform
      })
      
      if (response.data.success) {
        // Store email in session storage
        sessionStorage.setItem('user_email', email)
        setIsValid(true)
        navigate('/assessment')
      }
    } catch (error) {
      setIsValid(false)
      const err = error as { response?: { data?: { detail?: string } } }
      if (err.response?.data?.detail) {
        setErrorMessage(err.response.data.detail)
      } else {
        setErrorMessage('Failed to save email. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value)
    if (!isValid) {
      setIsValid(true)
      setErrorMessage('')
    }
  }

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4 py-4 sm:py-6">
      <div className="max-w-xl w-full">
        {/* Header Section */}
        <div className="text-center mb-4 sm:mb-5">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 mb-2.5 shadow-md">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-blue-900 via-blue-700 to-indigo-700 bg-clip-text text-transparent mb-1.5 sm:mb-2">
            One Final Step
          </h1>
          <p className="text-sm text-gray-600">
            Enter your work email to receive detailed assessment results
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-xl p-5 sm:p-6 shadow-lg border border-gray-200">
          {/* Benefits Section */}
          <div className="mb-4 sm:mb-5">
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 mb-2.5 sm:mb-3 flex items-center gap-2">
              <Mail className="w-5 h-5 text-blue-600" />
              What you'll receive
            </h2>
            <div className="space-y-1.5 sm:space-y-2">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-gray-700">
                  <strong>Comprehensive PDF report</strong> with scores and recommendations
                </p>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-gray-700">
                  <strong>AI-generated action plan</strong> tailored to your stack
                </p>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-gray-700">
                  <strong>Progress tracking</strong> for future assessments
                </p>
              </div>
            </div>
          </div>

          {/* Email Form */}
          <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-gray-900 mb-2">
                Work Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={handleEmailChange}
                  placeholder="your.email@company.com"
                  className={`block w-full pl-10 pr-4 py-2.5 sm:py-3 text-sm sm:text-base border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                    !isValid
                      ? 'border-red-400 focus:border-red-500 focus:ring-red-100'
                      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-100'
                  }`}
                  required
                />
              </div>
              {!isValid && errorMessage && (
                <div className="mt-2 flex items-start gap-2 text-red-600">
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <p className="text-xs font-medium">{errorMessage}</p>
                </div>
              )}
            </div>

            {/* Privacy Notice */}
            <div className="bg-blue-50 rounded-lg p-2.5 sm:p-3 border border-blue-100">
              <div className="flex items-start gap-2">
                <Shield className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-gray-700">
                  <strong className="text-gray-900">Your privacy is protected.</strong> We only use your email for assessment results. No spam, encrypted & secure.
                </p>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex gap-3 pt-1 sm:pt-2">
              <button
                type="button"
                onClick={() => navigate('/platform-selection')}
                className="px-4 py-2 text-sm text-gray-600 font-medium rounded-lg hover:bg-gray-100 transition-colors"
              >
                ← Back
              </button>
              <button
                type="submit"
                disabled={!email || isSubmitting}
                className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold text-sm rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg disabled:shadow-none"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    Start Assessment
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Footer Note */}
        <p className="text-center text-gray-500 mt-3 sm:mt-4 text-xs">
          Assessment takes approximately <strong>5-10 minutes</strong>
        </p>
      </div>
    </div>
  )
}
