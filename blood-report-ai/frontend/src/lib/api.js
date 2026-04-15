/**
 * API Client for Blood Report AI Backend
 * All requests include JWT token in Authorization header
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    try {
      const { getSession } = await import('./supabase.js').then(m => ({ getSession: m.auth.getSession }))
      const session = await getSession()
      
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers
      }

      if (session?.access_token) {
        headers.Authorization = `Bearer ${session.access_token}`
      }

      const response = await fetch(url, {
        ...options,
        headers
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.error || `API Error: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API Request Failed: ${endpoint}`, error)
      throw error
    }
  }

  // ━━━━━━━━━ AUTH ━━━━━━━━━
  async signup(email, password, fullName) {
    return this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName })
    })
  }

  async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    })
  }

  async getCurrentUser() {
    return this.request('/auth/me', { method: 'GET' })
  }

  // ━━━━━━━━━ REPORTS ━━━━━━━━━
  async uploadReport(file, reportDate) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('report_date', reportDate)

    const { getSession } = await import('./supabase.js').then(m => ({ getSession: m.auth.getSession }))
    const session = await getSession()

    const headers = {}
    if (session?.access_token) {
      headers.Authorization = `Bearer ${session.access_token}`
    }

    const response = await fetch(`${this.baseURL}/reports/upload`, {
      method: 'POST',
      headers,
      body: formData
    })

    if (!response.ok) {
      throw new Error('Failed to upload report')
    }

    return await response.json()
  }

  async getReports(limit = 50) {
    return this.request(`/reports/history?limit=${limit}`)
  }

  async analyzeReport(reportId, simpleMode = false) {
    return this.request(`/reports/analyze/${reportId}?simple_mode=${simpleMode}`)
  }

  async deleteReport(reportId) {
    return this.request(`/reports/${reportId}`, { method: 'DELETE' })
  }

  // ━━━━━━━━━ TRENDS ━━━━━━━━━
  async getTrendAnalysis() {
    return this.request('/trends/analysis')
  }

  async getMarkerTrend(markerName) {
    return this.request(`/trends/marker/${markerName}`)
  }

  async getStabilityScore() {
    return this.request('/trends/stability-score')
  }

  async getPatterns() {
    return this.request('/trends/patterns')
  }

  // ━━━━━━━━━ CHAT ━━━━━━━━━
  async sendMessage(message, sessionId, simpleMode = false) {
    return this.request('/chat/message', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
        simple_mode: simpleMode
      })
    })
  }

  async getChatHistory(sessionId) {
    return this.request(`/chat/history/${sessionId}`)
  }

  async askSimpleExplanation(markerName) {
    return this.request(`/chat/ask-simple?marker_name=${markerName}`)
  }

  async sendFollowUp(sessionId, context) {
    return this.request('/chat/follow-up', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        context
      })
    })
  }

  // ━━━━━━━━━ VOICE ━━━━━━━━━
  async transcribeAudio(audioBase64, language = 'en') {
    return this.request('/voice/transcribe', {
      method: 'POST',
      body: JSON.stringify({
        audio_base64: audioBase64,
        language
      })
    })
  }

  async synthesizeSpeech(text, voiceId) {
    return this.request('/voice/synthesize', {
      method: 'POST',
      body: JSON.stringify({
        text,
        voice_id: voiceId
      })
    })
  }

  async voiceChat(audioBase64, returnAudio = true) {
    return this.request('/voice/chat', {
      method: 'POST',
      body: JSON.stringify({
        audio_base64: audioBase64,
        return_audio: returnAudio
      })
    })
  }

  async getVoices() {
    return this.request('/voice/voices')
  }
}

export const api = new APIClient(API_BASE_URL)
