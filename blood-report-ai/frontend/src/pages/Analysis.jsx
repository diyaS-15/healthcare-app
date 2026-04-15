/**
 * Analysis Page - Detailed Report Analysis
 * Shows AI explanation, trends, and chat functionality
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

export default function Analysis() {
  const navigate = useNavigate()
  const { reportId } = useParams()
  const [report, setReport] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [simpleMode, setSimpleMode] = useState(false)
  const [chatMessage, setChatMessage] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [sendingMessage, setSendingMessage] = useState(false)

  useEffect(() => {
    loadAnalysis()
  }, [reportId, simpleMode])

  const loadAnalysis = async () => {
    try {
      setLoading(true)
      const data = await api.analyzeReport(reportId, simpleMode)
      setAnalysis(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!chatMessage.trim()) return

    setSendingMessage(true)
    try {
      const response = await api.sendMessage(chatMessage, reportId, simpleMode)
      setChatHistory([
        ...chatHistory,
        { role: 'user', content: chatMessage },
        { role: 'assistant', content: response.reply }
      ])
      setChatMessage('')
    } catch (err) {
      console.error('Failed to send message:', err)
    } finally {
      setSendingMessage(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full mx-auto"></div>
          <p className="text-gray-600 mt-4">Analyzing your report...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <button
          onClick={() => navigate('/dashboard')}
          className="mb-6 inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700"
        >
          ← Back to Dashboard
        </button>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Toggle Simple Mode */}
        <div className="mb-6 flex items-center gap-4">
          <h1 className="text-3xl font-bold text-gray-900">Report Analysis</h1>
          <label className="flex items-center gap-2 cursor-pointer ml-auto">
            <input
              type="checkbox"
              checked={simpleMode}
              onChange={(e) => setSimpleMode(e.target.checked)}
              className="w-4 h-4"
            />
            <span className="text-sm text-gray-600">Explain like I'm 15</span>
          </label>
        </div>

        {/* AI Explanation */}
        {analysis && (
          <div className="bg-white rounded-xl shadow-md p-8 mb-6 border border-gray-200">
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-gray-700">
                {analysis.marker_details}
              </div>
            </div>
          </div>
        )}

        {/* Chat Section */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
          <div className="h-96 overflow-y-auto p-6 bg-gray-50 flex flex-col gap-4">
            {chatHistory.length === 0 && (
              <div className="text-center text-gray-500 py-12">
                <p className="text-lg mb-2">💬 Ask questions about your report</p>
                <p className="text-sm">Start a conversation with our AI health assistant</p>
              </div>
            )}
            
            {chatHistory.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white border border-gray-200 text-gray-900'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200">
            <div className="flex gap-2">
              <input
                type="text"
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="Ask a question about your markers..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
              <button
                type="submit"
                disabled={sendingMessage || !chatMessage.trim()}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {sendingMessage ? '...' : 'Send'}
              </button>
            </div>
          </form>
        </div>

        {/* Questions */}
        {analysis && analysis.questions && analysis.questions.length > 0 && (
          <div className="mt-6 bg-white rounded-xl shadow-md p-6 border border-gray-200">
            <h3 className="font-bold text-gray-900 mb-4">Follow-up Questions</h3>
            <div className="space-y-2">
              {analysis.questions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => setChatMessage(q) }
                  className="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-indigo-50 hover:border-indigo-300 transition"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
