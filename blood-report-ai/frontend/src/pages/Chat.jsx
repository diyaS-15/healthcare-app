/**
 * Chat Page - AI-Powered Health Assistant Chat
 * Ask questions about blood markers and general health education
 * IMPORTANT: NOT for medical diagnosis - educational only
 */
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageCircle, AlertCircle, Home } from 'lucide-react'
import { api } from '../lib/api'

export default function Chat() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'Hello! I\'m your health information AI assistant. I can help you understand your blood markers, health trends, and answer general health questions. Remember: this is for educational purposes only, not medical diagnosis. How can I help?'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(`session-${Date.now()}`)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: input
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await api.sendMessage(input, sessionId)
      const assistantMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: response.reply || response.message || 'I couldn\'t generate a response. Please try again.'
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again later.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col">
      {/* Header */}
      <header className="border-b border-purple-700/30 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/')}
                className="p-2 hover:bg-purple-700/30 rounded-lg transition text-gray-300 hover:text-white"
              >
                <Home className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                  <MessageCircle className="w-6 h-6 text-purple-400" />
                  Health Assistant
                </h1>
                <p className="text-sm text-gray-400">AI-powered health education</p>
              </div>
            </div>
          </div>

          {/* Disclaimer Banner */}
          <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-3 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-amber-100">
              <strong>Educational Use Only:</strong> This AI assistant provides general health information, NOT medical diagnosis. Always consult a qualified healthcare provider for medical concerns.
            </div>
          </div>
        </div>
      </header>

      {/* Messages Container */}
      <div className="flex-1 max-w-5xl mx-auto w-full px-4 py-6 overflow-y-auto">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-2xl px-5 py-4 rounded-xl ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-br-none shadow-lg'
                    : 'bg-slate-800 text-gray-100 border border-purple-700/30 rounded-bl-none'
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 text-gray-100 border border-purple-700/30 rounded-xl rounded-bl-none px-5 py-4">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-purple-700/30 bg-slate-900/50 backdrop-blur-md sticky bottom-0">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <form onSubmit={handleSendMessage} className="flex gap-2 mb-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your health markers..."
              disabled={loading}
              className="flex-1 px-4 py-3 bg-slate-800 border border-purple-700/30 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none disabled:opacity-50 transition"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition transform hover:scale-105"
            >
              Send
            </button>
          </form>
          <div className="flex gap-2 text-xs text-gray-400">
            <span>💡 Example: "What does high glucose mean?" or "Explain hemoglobin to me"</span>
          </div>
        </div>
      </div>
    </div>
  )
}
