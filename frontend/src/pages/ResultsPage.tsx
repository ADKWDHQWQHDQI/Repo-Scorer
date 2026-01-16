import { useNavigate, useLocation } from 'react-router-dom'
import { Home, CheckCircle2, Gauge, Copy, Check, Mail, Share2 } from 'lucide-react'
import { useAssessmentStore } from '../store/assessmentStore'
import { getScoreLabel, getScoreClass, getScoreBgClass } from '../lib/utils'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useState, useEffect } from 'react'

export function ResultsPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { results, reset, shareToken, emailSent, emailMessage } = useAssessmentStore()
  const state = location.state as { showScoreAnimation?: boolean; animatedScore?: number } | null
  const [showFloatingScore, setShowFloatingScore] = useState(false)
  const [isAnimating, setIsAnimating] = useState(state?.showScoreAnimation ?? false)
  const [copied, setCopied] = useState(false)
  
  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [])
  
  useEffect(() => {
    if (state?.showScoreAnimation) {
      // Show floating modal for 800ms, then transform to speedometer
      const timer = setTimeout(() => {
        setIsAnimating(false)
        setShowFloatingScore(true)
      }, 800)
      return () => clearTimeout(timer)
    }
  }, [state?.showScoreAnimation])

  if (!results) {
    navigate('/')
    return null
  }

  const scoreLabel = getScoreLabel(results.final_score)
  const scoreClass = getScoreClass(results.final_score)
  const scoreBgClass = getScoreBgClass(results.final_score)

  // Prepare pillar chart data from breakdown
  const pillarData = Object.values(results.breakdown).map((pillar) => ({
    name: pillar.name,
    earned: pillar.earned,
    max: pillar.max,
    percentage: pillar.percentage,
  }))

  const handleReset = () => {
    reset()
    navigate('/')
  }

  const copyShareUrl = () => {
    if (shareToken) {
      const shareUrl = `${window.location.origin}/shared/${shareToken}`
      navigator.clipboard.writeText(shareUrl).then(() => {
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      })
    }
  }

  return (
    <div className="max-w-6xl mx-auto py-8 space-y-8">
      {/* Animated Floating Modal that transforms to speedometer */}
      {isAnimating && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 animate-scaleIn">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-green-600 to-emerald-700 mb-6 shadow-lg">
                <CheckCircle2 className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Assessment Complete!</h3>
              <div className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent mb-2">
                {results.final_score.toFixed(1)}<span className="text-3xl">/100</span>
              </div>
              <p className="text-slate-600 font-semibold">{scoreLabel}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Assessment Complete!</h1>
        <p className="text-gray-600">Here's your comprehensive repository governance analysis</p>
      </div>

      {/* Score Card */}
      <div className={`rounded-xl p-8 border-l-8 ${scoreBgClass}`}>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Final Score</h2>
            <p className="text-lg text-gray-600">Overall Repository Quality Assessment</p>
          </div>
          <div className="text-center">
            <div className={`text-7xl font-bold ${scoreClass}`}>{results.final_score.toFixed(1)}</div>
            <div className="text-2xl font-semibold text-gray-700">{scoreLabel}</div>
          </div>
        </div>
      </div>
            {/* Charts */}
      <div className="grid md:grid-cols-1 gap-8">

        {/* Quality Score Display */}
        <div className={`bg-gradient-to-br from-white to-indigo-50 border-2 border-indigo-200 rounded-2xl p-8 shadow-lg ${showFloatingScore ? 'animate-slideInRight' : ''}`}>
          <h1 className="text-2xl font-bold text-gray-900 mb-4 flex items-center justify-center gap-3">
            <div className="p-1 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl shadow-md">
              <Gauge className="w-8 h-8 text-white" />
            </div>
            Overall Quality Score
          </h1>
          
          {/* Simple Circular Progress */}
          <div className="flex items-center justify-center py-4">
            <div className="relative w-64 h-64">
              {/* Circular Progress Ring */}
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
                {/* Background Circle */}
                <circle
                  cx="100"
                  cy="100"
                  r="80"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="16"
                />
                {/* Progress Circle */}
                <circle
                  cx="100"
                  cy="100"
                  r="80"
                  fill="none"
                  stroke={results.final_score >= 80 ? '#22c55e' : results.final_score >= 60 ? '#eab308' : results.final_score >= 40 ? '#f97316' : '#ef4444'}
                  strokeWidth="16"
                  strokeDasharray={`${(results.final_score / 100) * 502.4} 502.4`}
                  strokeLinecap="round"
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              
              {/* Score Display - Centered */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className={`text-6xl font-black ${scoreClass} mb-2`}>
                  {results.final_score.toFixed(1)}
                </div>
                <div className="text-sm text-gray-500 font-semibold uppercase tracking-wider">
                  out of 100
                </div>
                <div className={`mt-4 px-6 py-2 rounded-full ${scoreBgClass} ${scoreClass} font-bold text-sm shadow-md`}>
                  {scoreLabel}
                </div>
              </div>
            </div>
          </div>
          
          {/* Score Details */}
          <div className="mt-4 text-center px-4">
            <p className="text-base text-gray-700 font-medium leading-relaxed">
              Your repository demonstrates <span className="font-bold text-indigo-600 text-lg">{results.final_score >= 80 ? 'excellent' : results.final_score >= 60 ? 'good' : results.final_score >= 40 ? 'moderate' : 'developing'}</span> DevSecOps maturity
            </p>
          </div>
        </div>
      </div>

      {/* Pillar Breakdown Bar Chart - Full Width */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <div className="h-1 w-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded"></div>
          Pillar Performance Analysis
        </h3>
        <ResponsiveContainer width="100%" height={500}>
          <BarChart data={pillarData} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="name" 
              angle={-35} 
              textAnchor="end" 
              height={120}
              interval={0}
              tick={{ fontSize: 12, fill: '#374151' }}
              stroke="#9ca3af"
            />
            <YAxis 
              label={{ value: 'Score', angle: -90, position: 'insideLeft', style: { fontSize: 14, fill: '#6b7280' } }}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              stroke="#9ca3af"
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
              labelStyle={{ fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}
            />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="rect"
            />
            <Bar dataKey="earned" fill="#6366f1" name="Earned Score" radius={[8, 8, 0, 0]} />
            <Bar dataKey="max" fill="#e5e7eb" name="Max Possible" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>


      {/* Executive Summary */}
      {results.summary && (
        <div className="bg-gradient-to-br from-white to-blue-50 border-2 border-blue-200 rounded-xl shadow-sm p-8">
          <div className="flex items-center gap-3 mb-6 pb-4 border-b-2 border-blue-200">
            <div className="w-1 h-8 bg-gradient-to-b from-indigo-600 to-purple-600 rounded-full"></div>
            <h3 className="text-2xl font-bold text-gray-900"> Executive Summary</h3>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
            <div className={`inline-block px-4 py-2 rounded-lg mb-4 ${scoreBgClass}`}>
              <span className={`text-sm font-bold ${scoreClass}`}>Assessment Status: {scoreLabel}</span>
            </div>
            <div className="prose max-w-none space-y-4">
            {(() => {
              const lines = results.summary.split('\n');
              const elements: React.ReactElement[] = [];
              let currentList: string[] = [];
              let paragraphText = '';

              lines.forEach((line, index) => {
                const trimmedLine = line.trim();

                // Check if line is a special formatted section heading (e.g., "•1. EXECUTIVE SUMMARY*")
                const specialHeadingMatch = trimmedLine.match(/^[•\-*]\s*(\d+\.\s+[A-Z\s&]+)\*$/);
                
                // Check if line is a numbered section heading (e.g., "1. EXECUTIVE SUMMARY")
                const isNumberedHeading = /^\d+\.\s+[A-Z\s&]+$/.test(trimmedLine);

                if (specialHeadingMatch) {
                  // Flush any pending content
                  if (currentList.length > 0) {
                    elements.push(
                      <ul key={`ul-${index}`} className="mb-4 space-y-2 pl-0">
                        {currentList.map((item, i) => (
                          <li key={i} className="flex items-start">
                            <span className="text-indigo-600 mr-2 mt-1">•</span>
                            <span className="text-gray-700 flex-1" dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                          </li>
                        ))}
                      </ul>
                    );
                    currentList = [];
                  }
                  if (paragraphText) {
                    elements.push(
                      <p key={`p-${index}`} className="mb-4 text-gray-700 leading-relaxed">
                        <span dangerouslySetInnerHTML={{ __html: paragraphText.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                      </p>
                    );
                    paragraphText = '';
                  }
                  // Add special formatted heading (bold, italic, larger font)
                  const headingText = specialHeadingMatch[1];
                  elements.push(
                    <h4 key={`sh-${index}`} className="text-xl font-bold italic text-gray-900 mt-6 mb-4">
                      {headingText}
                    </h4>
                  );
                }
                else if (isNumberedHeading) {
                  // Flush any pending content
                  if (currentList.length > 0) {
                    elements.push(
                      <ul key={`ul-${index}`} className="mb-4 space-y-2 pl-0">
                        {currentList.map((item, i) => (
                          <li key={i} className="flex items-start">
                            <span className="text-indigo-600 mr-2 mt-1">•</span>
                            <span className="text-gray-700 flex-1" dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                          </li>
                        ))}
                      </ul>
                    );
                    currentList = [];
                  }
                  if (paragraphText) {
                    elements.push(
                      <p key={`p-${index}`} className="mb-4 text-gray-700 leading-relaxed">
                        <span dangerouslySetInnerHTML={{ __html: paragraphText.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                      </p>
                    );
                    paragraphText = '';
                  }
                  // Add numbered heading
                  elements.push(
                    <h4 key={`h-${index}`} className="text-lg font-bold text-gray-900 mt-6 mb-3 flex items-center gap-2">
                      <div className="w-1.5 h-6 bg-gradient-to-b from-indigo-600 to-purple-600 rounded-full"></div>
                      {trimmedLine}
                    </h4>
                  );
                }
                // Handle bullet points
                else if (trimmedLine.startsWith('-') || trimmedLine.startsWith('•') || trimmedLine.startsWith('*')) {
                  if (paragraphText) {
                    elements.push(
                      <p key={`p-${index}`} className="mb-4 text-gray-700 leading-relaxed">
                        <span dangerouslySetInnerHTML={{ __html: paragraphText.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                      </p>
                    );
                    paragraphText = '';
                  }
                  const bulletText = trimmedLine.substring(1).trim();
                  currentList.push(bulletText);
                }
                // Handle empty lines
                else if (trimmedLine === '') {
                  if (currentList.length > 0) {
                    elements.push(
                      <ul key={`ul-${index}`} className="mb-4 space-y-2 pl-0">
                        {currentList.map((item, i) => (
                          <li key={i} className="flex items-start">
                            <span className="text-indigo-600 mr-2 mt-1">•</span>
                            <span className="text-gray-700 flex-1" dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                          </li>
                        ))}
                      </ul>
                    );
                    currentList = [];
                  }
                  if (paragraphText) {
                    elements.push(
                      <p key={`p-${index}`} className="mb-4 text-gray-700 leading-relaxed">
                        <span dangerouslySetInnerHTML={{ __html: paragraphText.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                      </p>
                    );
                    paragraphText = '';
                  }
                }
                // Handle regular text
                else {
                  if (currentList.length > 0) {
                    elements.push(
                      <ul key={`ul-${index}`} className="mb-4 space-y-2 pl-0">
                        {currentList.map((item, i) => (
                          <li key={i} className="flex items-start">
                            <span className="text-indigo-600 mr-2 mt-1">•</span>
                            <span className="text-gray-700 flex-1" dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                          </li>
                        ))}
                      </ul>
                    );
                    currentList = [];
                  }
                  paragraphText += (paragraphText ? ' ' : '') + trimmedLine;
                }
              });

              // Flush any remaining content
              if (currentList.length > 0) {
                elements.push(
                  <ul key="ul-final" className="mb-4 space-y-2 pl-0">
                    {currentList.map((item, i) => (
                      <li key={i} className="flex items-start">
                        <span className="text-indigo-600 mr-2 mt-1">•</span>
                        <span className="text-gray-700 flex-1" dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                      </li>
                    ))}
                  </ul>
                );
              }
              if (paragraphText) {
                elements.push(
                  <p key="p-final" className="mb-4 text-gray-700 leading-relaxed">
                    <span dangerouslySetInnerHTML={{ __html: paragraphText.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                  </p>
                );
              }

              return <>{elements}</>;
            })()}
          </div>
        </div>
        </div>
      )}

      {/* Info Message - Detailed Results Available via Email */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 p-3 bg-blue-600 rounded-lg">
            <Mail className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-2">View Detailed Question Analysis  {emailSent && (
                  <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                    <Mail className="w-3 h-3" />
                    Email Sent
                  </span>
                )}</h3> 
           
            <p className="text-gray-700 mb-3">
              Your complete assessment report with detailed question-by-question analysis has been sent to your email.
            </p>
            <div className="bg-white border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-2">
                <strong>Check your email</strong> for the full report link
              </p>
              <p className="text-sm text-gray-600">
                The email includes detailed analysis for each question with recommendations and insights
              </p>
            </div>
          </div>
        </div>
      </div>
            {/* Share URL Section */}
      {shareToken && (
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 p-3 bg-indigo-600 rounded-lg">
              <Share2 className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                Share Your Results
                {emailSent && (
                  <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                    <Mail className="w-3 h-3" />
                    Email Sent
                  </span>
                )}
              </h3>
              
              {emailSent ? (
                <p className="text-sm text-gray-600 mb-4">
                  A detailed report has been sent to your email with a shareable link. You can also copy the link below to share with your team.
                </p>
              ) : (
                <p className="text-sm text-gray-600 mb-4">
                  {emailMessage || 'Email could not be sent, but you can still share your results using the link below.'}
                </p>
              )}
              
              <div className="flex gap-2">
                <div className="flex-1 bg-white border border-gray-300 rounded-lg px-4 py-3 font-mono text-sm text-gray-700 overflow-x-auto">
                  {window.location.origin}/shared/{shareToken}
                </div>
                <button
                  onClick={copyShareUrl}
                  className={`flex items-center gap-2 px-4 py-3 rounded-lg font-semibold transition-all ${
                    copied
                      ? 'bg-green-600 text-white'
                      : 'bg-indigo-600 text-white hover:bg-indigo-700'
                  }`}
                >
                  {copied ? (
                    <>
                      <Check className="w-5 h-5" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-5 h-5" />
                      Copy Link
                    </>
                  )}
                </button>
              </div>
              
              <p className="text-xs text-gray-500 mt-3">
                 This link will remain active for 48 hours and can be accessed by anyone with the link.
              </p>
            </div>
          </div>
        </div>
      )}
      {/* Actions */}
      <div className="flex gap-4 justify-center pt-8">
        <button
          type="button"
          onClick={handleReset}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 transition-colors shadow-lg"
        >
          <Home className="w-5 h-5" />
          New Assessment
        </button>
      </div>
    </div>
  )
}


