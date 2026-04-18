/**
 * Main App Component
 * Blood Report AI - Health Intelligence Platform
 * Handles routing with authentication
 */
import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Pages
import Home from './pages/Home'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Analysis from './pages/Analysis'
import Analytics from './pages/Analytics'
import Chat from './pages/Chat'
import Settings from './pages/Settings'

// Protected Route Wrapper
function ProtectedRoute({ children, isAuthenticated, isLoading }) {
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return isAuthenticated ? children : <Navigate to="/signin" replace />
}

function App() {
  const { user, loading, initialize, subscribeToAuth } = useAuthStore()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    // Initialize auth on app load
    initialize()
    setMounted(true)
  }, [initialize])

  useEffect(() => {
    if (mounted) {
      // Subscribe to real-time auth changes
      const unsubscribe = subscribeToAuth()
      return () => unsubscribe()
    }
  }, [mounted, subscribeToAuth])

  const isAuthenticated = !!user

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />

        {/* Protected Routes - Require Authentication */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated} isLoading={loading}>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/upload"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated} isLoading={loading}>
              <Upload />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analysis/:reportId"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated} isLoading={loading}>
              <Analysis />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analysis"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated} isLoading={loading}>
              <Analysis />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated} isLoading={loading}>
              <Analytics />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated} isLoading={loading}>
              <Chat />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated} isLoading={loading}>
              <Settings />
            </ProtectedRoute>
          }
        />

        {/* Catch all - redirect based on auth state */}
        <Route
          path="*"
          element={<Navigate to={isAuthenticated ? "/dashboard" : "/"} replace />}
        />
      </Routes>
    </Router>
  )
}

export default App