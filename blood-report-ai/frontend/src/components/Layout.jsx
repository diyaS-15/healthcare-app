/**
 * Layout Component - Main App Layout with Navigation
 * Sidebar and header for the entire application
 */
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function Layout({ children }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = React.useState(true)

  const handleLogout = async () => {
    if (confirm('Are you sure you want to logout?')) {
      await logout()
      navigate('/login')
    }
  }

  const navItems = [
    { id: 'dashboard', label: '📊 Dashboard', path: '/dashboard', icon: '📊' },
    { id: 'upload', label: '📤 Upload Report', path: '/upload', icon: '📤' },
    { id: 'analyze', label: '🔍 Analysis', path: '/analysis', icon: '🔍' },
    { id: 'trends', label: '📈 Trends', path: '/analytics', icon: '📈' },
    { id: 'chat', label: '💬 Chat', path: '/chat', icon: '💬' },
    { id: 'settings', label: '⚙️ Settings', path: '/settings', icon: '⚙️' },
  ]

  const isActive = (path) => location.pathname.startsWith(path)

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-gradient-to-b from-indigo-600 to-indigo-700 text-white p-4 overflow-y-auto hidden md:block">
        {/* Logo */}
        <div className="flex items-center gap-3 mb-8 p-3 bg-white bg-opacity-10 rounded-lg">
          <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
            <span className="text-indigo-600 font-bold text-lg">BR</span>
          </div>
          <div>
            <h1 className="font-bold">Blood Report</h1>
            <p className="text-xs opacity-80">Health AI</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="space-y-2 mb-8">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => navigate(item.path)}
              className={`w-full text-left px-4 py-3 rounded-lg transition font-medium ${
                isActive(item.path)
                  ? 'bg-white bg-opacity-20 text-white'
                  : 'text-indigo-100 hover:bg-white hover:bg-opacity-10'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* User Info */}
        <div className="border-t border-indigo-400 pt-4 mt-auto">
          <div className="px-4 py-3 rounded-lg bg-white bg-opacity-10 mb-3">
            <p className="text-xs opacity-80">Logged in as</p>
            <p className="font-semibold text-sm truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="w-full px-4 py-3 rounded-lg bg-red-600 hover:bg-red-700 transition font-medium text-center"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {children}
      </div>
    </div>
  )
}

import React from 'react'
