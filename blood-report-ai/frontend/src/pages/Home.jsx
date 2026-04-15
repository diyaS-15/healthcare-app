/**
 * Home Page - Welcome & Navigation Hub
 * Beautiful landing page with quick access to main features
 */
import { useNavigate } from 'react-router-dom'
import { Upload, BarChart3, MessageCircle, TestTube, FileText } from 'lucide-react'

export default function Home() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation Bar */}
      <nav className="border-b border-purple-700/30 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
                <TestTube className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-xl font-bold text-white">BloodReportAI</h1>
            </div>
            <p className="text-sm text-purple-300">AI-Powered Health Analysis</p>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-white mb-6">
            Understand Your<br/>
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
              Blood Report with AI
            </span>
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-8">
            Upload your blood test reports and get instant AI-powered analysis. 
            Track trends, understand your health markers, and chat with our AI assistant.
          </p>
          
          {/* Disclaimer */}
          <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-4 max-w-2xl mx-auto mb-8">
            <p className="text-sm text-amber-100">
              ⚠️ <strong>Medical Disclaimer:</strong> This tool provides educational analysis only. 
              It is <strong>NOT</strong> a substitute for professional medical diagnosis or treatment. 
              Always consult with a qualified healthcare provider for medical advice.
            </p>
          </div>

          <button
            onClick={() => navigate('/upload')}
            className="inline-block px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold text-lg hover:from-purple-700 hover:to-pink-700 transition-all transform hover:scale-105"
          >
            Upload Blood Report
          </button>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {/* Upload Card */}
          <div
            onClick={() => navigate('/upload')}
            className="group cursor-pointer bg-gradient-to-br from-slate-800 to-slate-900 border border-purple-700/30 rounded-xl p-8 hover:border-purple-500/50 transition-all transform hover:-translate-y-2"
          >
            <div className="p-3 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg w-fit mb-4 group-hover:bg-gradient-to-br group-hover:from-purple-500/40 group-hover:to-pink-500/40 transition-all">
              <Upload className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Upload Reports</h3>
            <p className="text-gray-400 text-sm">
              Upload PDF or image of your blood test reports for instant analysis
            </p>
          </div>

          {/* Analysis Card */}
          <div
            onClick={() => navigate('/analysis')}
            className="group cursor-pointer bg-gradient-to-br from-slate-800 to-slate-900 border border-purple-700/30 rounded-xl p-8 hover:border-purple-500/50 transition-all transform hover:-translate-y-2"
          >
            <div className="p-3 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg w-fit mb-4 group-hover:bg-gradient-to-br group-hover:from-purple-500/40 group-hover:to-pink-500/40 transition-all">
              <FileText className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">AI Analysis</h3>
            <p className="text-gray-400 text-sm">
              Get detailed explanations of your health markers by AI assistant
            </p>
          </div>

          {/* Trends Card */}
          <div
            onClick={() => navigate('/analytics')}
            className="group cursor-pointer bg-gradient-to-br from-slate-800 to-slate-900 border border-purple-700/30 rounded-xl p-8 hover:border-purple-500/50 transition-all transform hover:-translate-y-2"
          >
            <div className="p-3 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg w-fit mb-4 group-hover:bg-gradient-to-br group-hover:from-purple-500/40 group-hover:to-pink-500/40 transition-all">
              <BarChart3 className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Track Trends</h3>
            <p className="text-gray-400 text-sm">
              Monitor changes in your health markers over time with charts
            </p>
          </div>

          {/* Chat Card */}
          <div
            onClick={() => navigate('/chat')}
            className="group cursor-pointer bg-gradient-to-br from-slate-800 to-slate-900 border border-purple-700/30 rounded-xl p-8 hover:border-purple-500/50 transition-all transform hover:-translate-y-2 md:col-span-2 lg:col-span-1"
          >
            <div className="p-3 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg w-fit mb-4 group-hover:bg-gradient-to-br group-hover:from-purple-500/40 group-hover:to-pink-500/40 transition-all">
              <MessageCircle className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">AI Chat</h3>
            <p className="text-gray-400 text-sm">
              Ask questions about your health markers and get educational responses
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 border border-purple-700/30 rounded-xl p-8 mb-12">
          <h3 className="text-2xl font-bold text-white mb-8 text-center">How It Works</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-lg">1</span>
              </div>
              <h4 className="text-lg font-semibold text-white mb-2">Upload</h4>
              <p className="text-gray-400">
                Upload your blood test report as a PDF or image file
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-lg">2</span>
              </div>
              <h4 className="text-lg font-semibold text-white mb-2">Analyze</h4>
              <p className="text-gray-400">
                Our AI extracts and analyzes all your health markers
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-lg">3</span>
              </div>
              <h4 className="text-lg font-semibold text-white mb-2">Understand</h4>
              <p className="text-gray-400">
                Get clear explanations in easy-to-read language
              </p>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-4 gap-4 bg-slate-800/30 border border-purple-700/30 rounded-xl p-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400 mb-2">100%</div>
            <p className="text-sm text-gray-300">Private & Secure</p>
          </div>
          <div className="text-center border-l border-purple-700/30">
            <div className="text-3xl font-bold text-pink-400 mb-2">AI</div>
            <p className="text-sm text-gray-300">Powered Analysis</p>
          </div>
          <div className="text-center border-l border-purple-700/30">
            <div className="text-3xl font-bold text-purple-400 mb-2">Real</div>
            <p className="text-sm text-gray-300">Trend Tracking</p>
          </div>
          <div className="text-center border-l border-purple-700/30">
            <div className="text-3xl font-bold text-pink-400 mb-2">24/7</div>
            <p className="text-sm text-gray-300">Available Anytime</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-purple-700/30 bg-slate-900/50 backdrop-blur-md mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <h4 className="font-semibold text-white mb-4">About</h4>
              <p className="text-sm text-gray-400">
                BloodReportAI helps you understand your health markers with AI technology.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Disclaimer</h4>
              <p className="text-sm text-gray-400">
                This tool is for educational purposes only and not a medical diagnosis tool.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-4">Privacy</h4>
              <p className="text-sm text-gray-400">
                Your data is private and never stored or shared with third parties.
              </p>
            </div>
          </div>
          <div className="border-t border-purple-700/30 pt-8 text-center text-sm text-gray-400">
            <p>© 2026 BloodReportAI. All rights reserved. Made with ❤️</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
