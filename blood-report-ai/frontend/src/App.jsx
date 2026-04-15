/**
 * Main App Component
 * AI Health Report Analysis & Chat Tool
 * All routes are public - no authentication required
 */
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'

// Pages
import Home from './pages/Home'
import Upload from './pages/Upload'
import Analysis from './pages/Analysis'
import Analytics from './pages/Analytics'
import Chat from './pages/Chat'

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes - All accessible without auth */}
        <Route path="/" element={<Home />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/analysis/:reportId" element={<Analysis />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/chat" element={<Chat />} />

        {/* Catch all - redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App