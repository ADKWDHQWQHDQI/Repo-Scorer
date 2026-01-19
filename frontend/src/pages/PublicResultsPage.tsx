import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Home, Gauge, Clock, Mail, TrendingUp } from 'lucide-react';
import type { AssessmentResult } from '../types';

interface SharedResultsData {
  results: AssessmentResult;
  platform: string;
  email: string;
  expires_at: string;
}

export const PublicResultsPage = () => {
  const { shareToken } = useParams<{ shareToken: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<SharedResultsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true);
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${API_URL}/api/results/shared/${shareToken}`);
        
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('Results not found or have expired. Shared links are valid for 48 hours.');
          }
          throw new Error('Failed to load results');
        }

        const jsonData = await response.json();
        setData(jsonData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    if (shareToken) {
      fetchResults();
    }
  }, [shareToken]);

  const formatAISummary = (summary: string) => {
    if (!summary) return null;

    const lines = summary.split('\n');
    const elements: React.ReactElement[] = [];

    let currentList: string[] = [];
    let paragraphText = '';

    lines.forEach((line, index) => {
      const trimmedLine = line.trim();

      // Handle bullet points
      if (trimmedLine.startsWith('-') || trimmedLine.startsWith('•') || trimmedLine.startsWith('*')) {
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
      } else if (trimmedLine === '') {
        if (currentList.length > 0) {
          elements.push(
            <ul key={`ul-${index}`} className="mb-4 space-y-2">
              {currentList.map((item, i) => (
                <li key={i} className="flex items-start">
                  <span className="text-indigo-600 mr-2">•</span>
                  <span className="text-gray-700" dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
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
      } else {
        if (currentList.length > 0) {
          elements.push(
            <ul key={`ul-${index}`} className="mb-4 space-y-2">
              {currentList.map((item, i) => (
                <li key={i} className="flex items-start">
                  <span className="text-indigo-600 mr-2">•</span>
                  <span className="text-gray-700" dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
                </li>
              ))}
            </ul>
          );
          currentList = [];
        }
        paragraphText += (paragraphText ? ' ' : '') + trimmedLine;
      }
    });

    if (currentList.length > 0) {
      elements.push(
        <ul key="ul-final" className="mb-4 space-y-2">
          {currentList.map((item, i) => (
            <li key={i} className="flex items-start">
              <span className="text-indigo-600 mr-2">•</span>
              <span className="text-gray-700" dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>') }} />
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

    return <div className="space-y-4">{elements}</div>;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Clock className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Results Not Available</h2>
          <p className="text-gray-600 mb-6">{error || 'Unable to load results'}</p>
          <button
            onClick={() => navigate('/')}
            className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Home className="w-5 h-5 mr-2" />
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  const { results, platform, email, expires_at } = data;
  const { final_score, breakdown, question_results, summary } = results;

  // Prepare chart data
  const chartData = Object.values(breakdown).map((pillar) => ({
    name: pillar.name,
    score: pillar.percentage,
    earned: pillar.earned,
    max: pillar.max,
  }));

  // Calculate expiry time remaining
  const expiresDate = new Date(expires_at);
  const hoursRemaining = Math.max(0, Math.round((expiresDate.getTime() - Date.now()) / (1000 * 60 * 60)));

  // Simple circular progress renderer
  const renderQualityScore = (score: number) => {
    const scoreColor = score >= 80 ? '#22c55e' : score >= 60 ? '#eab308' : score >= 40 ? '#f97316' : '#ef4444';
    const scoreLabel = score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : score >= 40 ? 'Needs Improvement' : 'Critical';
    const scoreBg = score >= 80 ? 'bg-green-100 text-green-800' : score >= 60 ? 'bg-yellow-100 text-yellow-800' : score >= 40 ? 'bg-orange-100 text-orange-800' : 'bg-red-100 text-red-800';
    const scoreText = score >= 80 ? 'text-green-600' : score >= 60 ? 'text-yellow-600' : score >= 40 ? 'text-orange-600' : 'text-red-600';
    
    return (
      <div className="relative w-56 h-56 sm:w-64 sm:h-64 mx-auto">
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
            stroke={scoreColor}
            strokeWidth="16"
            strokeDasharray={`${(score / 100) * 502.4} 502.4`}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        
        {/* Score Display - Centered */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={`text-6xl font-black ${scoreText} mb-2`}>
            {score.toFixed(1)}
          </div>
          <div className="text-sm text-gray-500 font-semibold uppercase tracking-wider">
            out of 100
          </div>
          <div className={`mt-4 px-6 py-2 rounded-full ${scoreBg} font-bold text-sm shadow-md`}>
            {scoreLabel}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center space-x-3 min-w-0">
            <Gauge className="w-5 sm:w-6 h-5 sm:h-6 text-indigo-600 flex-shrink-0" />
            <h1 className="text-base sm:text-lg lg:text-xl font-bold text-gray-900 truncate">Shared Assessment Report</h1>
          </div>
          <button
            onClick={() => navigate('/')}
            className="inline-flex items-center justify-center px-4 py-2 text-sm text-gray-700 hover:text-indigo-600 transition-colors w-full sm:w-auto"
          >
            <Home className="w-4 h-4 mr-2" />
            Create Your Own Assessment
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Info Banner */}
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6 flex items-start">
          <div className="flex-shrink-0">
            <Clock className="w-5 h-5 text-indigo-600 mt-0.5" />
          </div>
          <div className="ml-3 flex-1">
            <p className="text-sm text-indigo-900">
              This report was shared from <span className="font-semibold">{email}</span> for their <span className="font-semibold">{platform}</span> repository assessment.
              This link will expire in <span className="font-semibold">{hoursRemaining} hours</span>.
            </p>
          </div>
        </div>

        {/* Quality Score Display */}
        <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 rounded-2xl shadow-lg p-6 sm:p-8 lg:p-10 mb-6 hover:shadow-xl transition-shadow duration-300">
          <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 mb-6 sm:mb-8 text-center flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-3">
            <TrendingUp className="w-7 h-7 text-indigo-600" />
            Overall Quality Score
          </h2>
          {renderQualityScore(final_score)}
        </div>

        {/* Pillar Breakdown Chart */}
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-6">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6">Pillar Breakdown</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="name"
                angle={-45}
                textAnchor="end"
                height={120}
                interval={0}
              />
              <YAxis label={{ value: 'Score (%)', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
                        <p className="font-semibold text-gray-900">{data.name}</p>
                        <p className="text-sm text-gray-600">
                          Score: {data.earned.toFixed(2)} / {data.max.toFixed(2)}
                        </p>
                        <p className="text-sm text-indigo-600 font-medium">
                          {data.score.toFixed(1)}%
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend />
              <Bar dataKey="score" fill="#6366f1" name="Percentage" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* AI Summary */}
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 mb-6">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Executive Summary</h2>
          <div className="prose max-w-none">
            {formatAISummary(summary)}
          </div>
        </div>

        {/* Detailed Results */}
        <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6">Detailed Question Results</h2>
          <div className="space-y-6">
            {question_results.map((result, index) => (
              <div key={index} className="border-l-4 border-indigo-600 pl-3 sm:pl-4 py-2">
                <div className="flex flex-col sm:flex-row items-start sm:justify-between gap-2 mb-2">
                  <h3 className="text-base sm:text-lg font-semibold text-gray-900 flex-1">{result.question_text}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs sm:text-sm font-medium flex-shrink-0 ${
                    result.classification === 'yes'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {result.user_answer}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm text-gray-600 mb-2">
                  <span className="font-medium">{result.pillar_name}</span>
                  <span>Score: {result.score_earned.toFixed(2)} / {result.max_score.toFixed(2)}</span>
                </div>
                <p className="text-sm sm:text-base text-gray-700">{result.analysis}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Footer CTA */}
        <div className="mt-8 text-center">
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-6 sm:p-8 text-white">
            <Mail className="w-10 sm:w-12 h-10 sm:h-12 mx-auto mb-4" />
            <h3 className="text-xl sm:text-2xl font-bold mb-2">Want Your Own Assessment?</h3>
            <p className="text-sm sm:text-base text-indigo-100 mb-6">
              Get a comprehensive DevSecOps assessment for your repository
            </p>
            <button
              onClick={() => navigate('/')}
              className="inline-flex items-center px-6 py-3 bg-white text-indigo-600 rounded-lg hover:bg-gray-50 transition-colors font-semibold"
            >
              <Home className="w-5 h-5 mr-2" />
              Start Free Assessment
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
