/**
 * Analytics Page - Global Health Insights
 * Shows user statistics and global population trends
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

export default function Analytics() {
  const navigate = useNavigate()
  const [trends, setTrends] = useState(null)
  const [stability, setStability] = useState(null)
  const [patterns, setPatterns] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      const trendsData = await api.getTrendAnalysis()
      setTrends(trendsData)

      const stabilityData = await api.getStabilityScore()
      setStability(stabilityData)

      const patternsData = await api.getPatterns()
      setPatterns(patternsData.patterns || [])
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <button
          onClick={() => navigate('/dashboard')}
          className="mb-6 inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700"
        >
          ← Back to Dashboard
        </button>

        <h1 className="text-3xl font-bold text-gray-900 mb-2">Health Analytics</h1>
        <p className="text-gray-600 mb-8">Track your health patterns over time</p>

        {/* Stability Score */}
        {stability && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl shadow-md p-6 mb-8 border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Health Stability Score</h2>
                <p className="text-gray-600 mt-1">{stability.interpretation}</p>
              </div>
              <div className="text-6xl font-bold text-green-600">{stability.score}</div>
            </div>
          </div>
        )}

        {/* Trends Grid */}
        {trends && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Marker Trends</h3>
              <div className="space-y-3">
                {trends.trends.map(trend => (
                  <div key={trend.marker_name} className="pb-3 border-b border-gray-200 last:border-0">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-gray-900 capitalize">{trend.marker_name.replace('_', ' ')}</p>
                        <p className="text-sm text-gray-600">{trend.direction}</p>
                      </div>
                      <div className="text-right">
                        <p className={`font-bold ${
                          trend.direction === 'increasing' ? 'text-amber-600' :
                          trend.direction === 'decreasing' ? 'text-green-600' :
                          'text-gray-600'
                        }`}>
                          {trend.change_percent > 0 ? '+' : ''}{trend.change_percent}%
                        </p>
                        <p className="text-xs text-gray-500">{trend.data_points} data points</p>
                      </div>
                    </div>
                    {/* Simple progress bar */}
                    <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          trend.direction === 'increasing' ? 'bg-amber-500' :
                          trend.direction === 'decreasing' ? 'bg-green-500' :
                          'bg-gray-500'
                        }`}
                        style={{ width: `${Math.min(Math.abs(trend.change_percent), 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Patterns */}
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Health Patterns</h3>
              {patterns.length === 0 ? (
                <p className="text-gray-600">No cross-marker patterns detected yet</p>
              ) : (
                <div className="space-y-3">
                  {patterns.map((pattern, idx) => (
                    <div key={idx} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-gray-900">{pattern}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Data Summary */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Summary</h3>
          {trends && (
            <p className="text-gray-700">
              You have been tracking <strong>{trends.report_count}</strong> reports with 
              <strong> {trends.trends.length}</strong> unique markers. Your health patterns show
              <strong> {patterns.length}</strong> cross-marker correlations.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
