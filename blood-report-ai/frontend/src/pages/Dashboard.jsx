/**
 * Dashboard - User home page
 * Shows latest report, quick stats, navigation
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuthStore } from '../store/authStore'

export default function Dashboard() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [reports, setReports] = useState([])
  const [trends, setTrends] = useState(null)
  const [stabilityScore, setStabilityScore] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const reportsData = await api.getReports(5)
      setReports(reportsData.reports || [])

      try {
        const trendsData = await api.getTrendAnalysis()
        setTrends(trendsData)
      } catch (e) {
        // Trends may not be available yet
      }

      try {
        const scoreData = await api.getStabilityScore()
        setStabilityScore(scoreData)
      } catch (e) {
        // Score may not be available yet
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  if (loading) return <LoadingScreen />

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">BR</span>
              </div>
              <div>
                <h2 className="font-bold text-gray-900">Blood Report AI</h2>
                <p className="text-xs text-gray-500">Health Intelligence Platform</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.email}</p>
                <button
                  onClick={handleLogout}
                  className="text-xs text-indigo-600 hover:text-indigo-700"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Greeting */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome back!</h1>
          <p className="text-gray-600 mt-1">Here's your health overview</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Reports"
            value={reports.length}
            icon="📄"
            color="blue"
          />
          <StatCard
            title="Markers Tracked"
            value={trends?.markers?.length || 0}
            icon="📊"
            color="indigo"
          />
          <StatCard
            title="Stability Score"
            value={stabilityScore?.score?.toFixed(1) || '--'}
            icon="✓"
            color="green"  
          />
          <StatCard
            title="Last Report"
            value={reports[0]?.report_date || 'Never'}
            icon="📅"
            color="purple"
          />
        </div>

        {/* Recent Reports */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Reports</h3>
              
              {reports.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-500">No reports yet</p>
                  <button
                    onClick={() => navigate('/upload')}
                    className="mt-4 inline-block text-indigo-600 hover:text-indigo-700 font-medium"
                  >
                    Upload your first report →
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {reports.map(report => (
                    <div
                      key={report.id}
                      className="p-4 border border-gray-200 rounded-lg hover:border-indigo-300 hover:bg-indigo-50 transition cursor-pointer"
                      onClick={() => navigate(`/analysis/${report.id}`)}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-gray-900">{report.report_date}</p>
                          <p className="text-sm text-gray-600">{report.marker_count || 0} markers</p>
                        </div>
                        <span className="text-2xl">→</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-4">
            <button
              onClick={() => navigate('/upload')}
              className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium py-3 rounded-lg hover:from-indigo-700 hover:to-purple-700 transition flex items-center justify-center gap-2"
            >
              <span>📤</span> Upload Report
            </button>
            <button
              onClick={() => navigate('/analysis')}
              className="flex-1 border-2 border-indigo-600 text-indigo-600 font-medium py-3 rounded-lg hover:bg-indigo-50 transition flex items-center justify-center gap-2"
            >
              <span>📊</span> View Analysis
            </button>
            <button
              onClick={() => navigate('/analytics')}
              className="flex-1 border-2 border-gray-300 text-gray-700 font-medium py-3 rounded-lg hover:bg-gray-50 transition flex items-center justify-center gap-2"
            >
              <span>📈</span> Analytics
            </button>
          </div>
        </div>

        {/* Trends Preview */}
        {trends && trends.trends.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Marker Trends</h3>
            <div className="space-y-3">
              {trends.trends.slice(0, 3).map(trend => (
                <div key={trend.marker_name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{trend.marker_name}</p>
                    <p className="text-sm text-gray-600">{trend.direction}</p>
                  </div>
                  <div className="text-right">
                    <p className={`font-bold ${
                      trend.direction === 'increasing' ? 'text-amber-600' :
                      trend.direction === 'decreasing' ? 'text-green-600' :
                      'text-gray-600'
                    }`}>
                      {trend.change_percent > 0 ? '+' : ''}{trend.change_percent.toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500">{trend.data_points} data points</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

function StatCard({ title, value, icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    indigo: 'bg-indigo-50 text-indigo-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className={`text-3xl mb-3 p-3 rounded-lg ${colorClasses[color]} inline-block`}>
        {icon}
      </div>
      <p className="text-gray-600 text-sm">{title}</p>
      <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
    </div>
  )
}

function LoadingScreen() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full mx-auto"></div>
        <p className="text-gray-600 mt-4">Loading your dashboard...</p>
      </div>
    </div>
  )
}
