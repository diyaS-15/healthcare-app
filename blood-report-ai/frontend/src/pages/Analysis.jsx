/**
 * Analysis Page - Professional Blood Test Analysis
 * Comprehensive report analysis with health insights and recommendations
 */
import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AlertCircle, TrendingUp, Heart, Home, MessageCircle, Download } from 'lucide-react'
import { api } from '../lib/api'

export default function Analysis() {
  const navigate = useNavigate()
  const { reportId } = useParams()
  const [report, setReport] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('overview')
  const [chatMessage, setChatMessage] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [sendingMessage, setSendingMessage] = useState(false)
  const chatEndRef = useRef(null)

  useEffect(() => {
    loadAnalysis()
  }, [reportId])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatHistory])

  const loadAnalysis = async () => {
    try {
      setLoading(true)
      const data = await api.analyzeReport(reportId)
      setAnalysis(data)
    } catch (err) {
      setError(err.message || 'Failed to analyze report')
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!chatMessage.trim()) return

    const userMessage = chatMessage
    setChatMessage('')
    setChatHistory([...chatHistory, { role: 'user', content: userMessage }])
    setSendingMessage(true)

    try {
      const response = await api.sendMessage(userMessage, reportId)
      setChatHistory((prev) => [
        ...prev,
        { role: 'assistant', content: response.reply }
      ])
    } catch (err) {
      setChatHistory((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }
      ])
    } finally {
      setSendingMessage(false)
    }
  }

  const getMarkerStatus = (marker) => {
    if (!marker.status) return 'normal'
    return marker.status
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'high':
        return 'text-red-600 bg-red-50'
      case 'low':
        return 'text-orange-600 bg-orange-50'
      case 'normal':
        return 'text-green-600 bg-green-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getStatusBadge = (status) => {
    const labels = {
      high: 'High',
      low: 'Low',
      normal: 'Normal',
      unknown: 'Not in range'
    }
    return labels[status] || 'Unknown'
  }

  const abnormalMarkers = analysis?.markers?.filter((m) => m.status !== 'normal') || []
  const normalMarkers = analysis?.markers?.filter((m) => m.status === 'normal') || []

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Analyzing your blood test report...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              <Home className="w-5 h-5" />
              <span>Back Home</span>
            </button>
            <h1 className="text-xl font-semibold text-gray-900">Blood Test Analysis</h1>
            <button className="px-4 py-2 text-gray-600 hover:text-gray-900">
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="text-red-800">{error}</div>
          </div>
        )}

        {analysis && (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Report Header */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      Report Analysis
                    </h2>
                    {analysis.report_date && (
                      <p className="text-gray-600">
                        Test Date: <span className="font-medium">{analysis.report_date}</span>
                      </p>
                    )}
                    {analysis.lab_name && (
                      <p className="text-gray-600">
                        Laboratory: <span className="font-medium">{analysis.lab_name}</span>
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-3xl font-bold text-gray-900">
                      {analysis.markers?.length || 0}
                    </p>
                    <p className="text-sm text-gray-600">Markers Detected</p>
                  </div>
                </div>

                {/* Medical Disclaimer */}
                <div className="bg-blue-50 border border-blue-200 rounded p-4 mt-4">
                  <p className="text-sm text-blue-900">
                    <span className="font-semibold">Disclaimer:</span> This analysis is for educational purposes only and does not replace professional medical advice. Always consult with a healthcare provider for medical interpretation.
                  </p>
                </div>
              </div>

              {/* Abnormal Markers Alert */}
              {abnormalMarkers.length > 0 && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
                  <div className="flex items-start gap-3 mb-4">
                    <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h3 className="font-semibold text-amber-900 mb-1">
                        Markers Needing Attention
                      </h3>
                      <p className="text-sm text-amber-800">
                        You have {abnormalMarkers.length} marker(s) outside the normal range. Review these carefully with your healthcare provider.
                      </p>
                    </div>
                  </div>

                  <div className="grid sm:grid-cols-2 gap-3">
                    {abnormalMarkers.map((marker) => (
                      <div
                        key={marker.name}
                        className="bg-white border border-amber-200 rounded p-3"
                      >
                        <p className="font-medium text-gray-900 text-sm">{marker.name}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          Value: {marker.value} {marker.unit}
                        </p>
                        <span
                          className={`inline-block mt-2 px-2 py-1 text-xs font-medium rounded ${getStatusColor(
                            marker.status
                          )}`}
                        >
                          {getStatusBadge(marker.status)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tabs */}
              <div className="border-b border-gray-200">
                <div className="flex gap-6">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`px-4 py-3 font-medium border-b-2 transition ${
                      activeTab === 'overview'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Overview
                  </button>
                  <button
                    onClick={() => setActiveTab('details')}
                    className={`px-4 py-3 font-medium border-b-2 transition ${
                      activeTab === 'details'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    All Markers
                  </button>
                  <button
                    onClick={() => setActiveTab('insights')}
                    className={`px-4 py-3 font-medium border-b-2 transition ${
                      activeTab === 'insights'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Health Insights
                  </button>
                </div>
              </div>

              {/* Tab Content */}
              {activeTab === 'overview' && (
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Analysis Summary
                  </h3>
                  <div className="prose prose-sm max-w-none text-gray-700">
                    <p className="whitespace-pre-wrap leading-relaxed">
                      {analysis.analysis || 'Loading analysis...'}
                    </p>
                  </div>
                </div>
              )}

              {activeTab === 'details' && (
                <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-200 bg-gray-50">
                          <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                            Marker
                          </th>
                          <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                            Your Value
                          </th>
                          <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                            Normal Range
                          </th>
                          <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {analysis.markers?.map((marker) => (
                          <tr
                            key={marker.name}
                            className="border-b border-gray-200 hover:bg-gray-50 transition"
                          >
                            <td className="px-6 py-4 text-sm font-medium text-gray-900">
                              {marker.name}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-700">
                              {marker.value} {marker.unit}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600">
                              {marker.reference_low &&
                                marker.reference_high &&
                                `${marker.reference_low} - ${marker.reference_high}`}
                            </td>
                            <td className="px-6 py-4 text-sm">
                              <span
                                className={`inline-block px-3 py-1 rounded font-medium text-xs ${getStatusColor(
                                  marker.status
                                )}`}
                              >
                                {getStatusBadge(marker.status)}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {activeTab === 'insights' && (
                <div className="space-y-4">
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Health Recommendations
                    </h3>
                    <div className="space-y-4">
                      <div className="flex gap-4">
                        <div className="flex-shrink-0">
                          <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-100">
                            <Heart className="h-5 w-5 text-blue-600" />
                          </div>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Lifestyle Support</p>
                          <p className="text-sm text-gray-600 mt-1">
                            Regular exercise, balanced diet, and adequate sleep support healthy marker levels.
                          </p>
                        </div>
                      </div>

                      <div className="flex gap-4">
                        <div className="flex-shrink-0">
                          <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-100">
                            <TrendingUp className="h-5 w-5 text-blue-600" />
                          </div>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Follow-up Testing</p>
                          <p className="text-sm text-gray-600 mt-1">
                            Consider scheduling a follow-up test to track changes in your markers over time.
                          </p>
                        </div>
                      </div>

                      <div className="flex gap-4">
                        <div className="flex-shrink-0">
                          <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-100">
                            <AlertCircle className="h-5 w-5 text-blue-600" />
                          </div>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Professional Consultation</p>
                          <p className="text-sm text-gray-600 mt-1">
                            Always discuss your results with a qualified healthcare provider for personalized advice.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Chat Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col h-96 sticky top-24">
                {/* Chat Header */}
                <div className="bg-gray-50 border-b border-gray-200 px-4 py-3">
                  <div className="flex items-center gap-2">
                    <MessageCircle className="w-5 h-5 text-blue-600" />
                    <h3 className="font-semibold text-gray-900">Ask Questions</h3>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">Get clarifications about your markers</p>
                </div>

                {/* Chat Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {chatHistory.length === 0 && (
                    <div className="h-full flex items-center justify-center text-center">
                      <div className="text-gray-500">
                        <p className="text-sm font-medium mb-1">No questions yet</p>
                        <p className="text-xs text-gray-400">
                          Ask about your markers or health
                        </p>
                      </div>
                    </div>
                  )}

                  {chatHistory.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] px-3 py-2 rounded-lg text-sm ${
                          msg.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>

                {/* Chat Input */}
                <form
                  onSubmit={handleSendMessage}
                  className="border-t border-gray-200 p-3 bg-gray-50"
                >
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={chatMessage}
                      onChange={(e) => setChatMessage(e.target.value)}
                      placeholder="Ask about markers..."
                      disabled={sendingMessage}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100"
                    />
                    <button
                      type="submit"
                      disabled={sendingMessage || !chatMessage.trim()}
                      className="px-3 py-2 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {sendingMessage ? '...' : 'Ask'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
