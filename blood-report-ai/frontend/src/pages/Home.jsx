/**
 * Home Page - Professional Landing Page
 * Clean, professional design focused on blood report analysis
 */
import { useNavigate } from 'react-router-dom'
import { Upload, TrendingUp, MessageCircle, Shield, Lock, CheckCircle } from 'lucide-react'

export default function Home() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation Bar */}
      <nav className="border-b border-gray-200 sticky top-0 z-50 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">H</span>
              </div>
              <h1 className="text-lg font-semibold text-gray-900">HealthReport AI</h1>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 text-sm">Features</a>
              <a href="#how-it-works" className="text-gray-600 hover:text-gray-900 text-sm">How It Works</a>
              <a href="#security" className="text-gray-600 hover:text-gray-900 text-sm">Security</a>
            </div>
            <button
              onClick={() => navigate('/signup')}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-b from-blue-50 to-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-5xl font-bold text-gray-900 mb-6 leading-tight">
                Understand Your Blood Tests with AI
              </h2>
              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                Upload your blood report and get instant AI-powered analysis. Track your health trends, understand what your markers mean, and take informed decisions about your health.
              </p>
              
              {/* Medical Disclaimer */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
                <p className="text-sm text-blue-900">
                  <span className="font-semibold">Disclaimer:</span> This analysis is for educational purposes only and does not replace professional medical advice. Always consult with a healthcare provider.
                </p>
              </div>

              <button
                onClick={() => navigate('/signup')}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition inline-flex items-center gap-2"
              >
                <Upload className="w-5 h-5" />
                Get Started Free
              </button>
            </div>
            <div className="bg-gray-100 rounded-lg p-8 h-96 flex items-center justify-center">
              <div className="text-center">
                <div className="w-24 h-24 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Upload className="w-12 h-12 text-white" />
                </div>
                <p className="text-gray-600">Upload PDF or Image of Your Blood Report</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-900 mb-4">Key Features</h3>
            <p className="text-xl text-gray-600">Everything you need to understand your health better</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="p-8 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-lg transition">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Upload className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">Smart Upload</h4>
              <p className="text-gray-600">
                Upload PDFs or images of your blood reports. Our AI automatically extracts and analyzes marker data.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="p-8 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-lg transition">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">Track Trends</h4>
              <p className="text-gray-600">
                Monitor changes in your health markers over time with clear visualizations and trend analysis.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="p-8 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-lg transition">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <MessageCircle className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">AI Chat Assistant</h4>
              <p className="text-gray-600">
                Ask questions about your health markers. Get clear, educational explanations from our AI assistant.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="p-8 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-lg transition">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">Privacy First</h4>
              <p className="text-gray-600">
                Your health data is encrypted end-to-end. We never share your information with third parties.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="p-8 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-lg transition">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Lock className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">Secure Storage</h4>
              <p className="text-gray-600">
                All your reports are securely stored and accessible only to you. No ads, no tracking.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="p-8 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-lg transition">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <CheckCircle className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="text-xl font-semibold text-gray-900 mb-2">Educational Content</h4>
              <p className="text-gray-600">
                Learn what each health marker means and what factors influence its levels naturally.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-900 mb-4">How It Works</h3>
            <p className="text-xl text-gray-600">Get insights in three simple steps</p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">1</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Upload Report</h4>
              <p className="text-gray-600">Upload a PDF or image of your blood test report</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">2</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">AI Analysis</h4>
              <p className="text-gray-600">Our AI extracts and analyzes your health markers automatically</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">3</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Get Insights</h4>
              <p className="text-gray-600">Understand your results and chat with AI about your health</p>
            </div>
          </div>
        </div>
      </section>

      {/* Security & Privacy */}
      <section id="security" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-4xl font-bold text-gray-900 mb-6">Your Privacy Matters</h3>
              <p className="text-xl text-gray-600 mb-6">
                We take healthcare data security seriously. Your health information is protected with enterprise-grade encryption.
              </p>
              
              <div className="space-y-4">
                <div className="flex gap-3">
                  <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                  <div>
                    <p className="font-semibold text-gray-900">End-to-End Encryption</p>
                    <p className="text-gray-600">AES-256 encryption for all sensitive data</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                  <div>
                    <p className="font-semibold text-gray-900">No Data Sharing</p>
                    <p className="text-gray-600">Your data is never sold or shared with third parties</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                  <div>
                    <p className="font-semibold text-gray-900">Full Control</p>
                    <p className="text-gray-600">You can delete your data anytime</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                  <div>
                    <p className="font-semibold text-gray-900">Compliance</p>
                    <p className="text-gray-600">Designed with healthcare privacy standards in mind</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-blue-50 rounded-lg p-8 border border-blue-200">
              <div className="space-y-6">
                <div>
                  <p className="text-sm font-semibold text-blue-900 uppercase tracking-wide">Security Features</p>
                  <h4 className="text-2xl font-bold text-gray-900 mt-2">Enterprise Security</h4>
                </div>
                <div className="space-y-4 text-sm text-gray-700">
                  <p>✓ SSL/TLS encryption for all data in transit</p>
                  <p>✓ AES-256 encryption for data at rest</p>
                  <p>✓ Secure authentication with industry-standard protocols</p>
                  <p>✓ Regular security audits and penetration testing</p>
                  <p>✓ HIPAA-aligned privacy practices</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-4xl font-bold mb-4">Ready to Understand Your Health?</h3>
          <p className="text-xl mb-8 text-blue-100">
            Upload your blood report today and start getting AI-powered insights about your health markers.
          </p>
          <button
            onClick={() => navigate('/upload')}
            className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition"
          >
            Get Started Now
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h5 className="font-semibold text-white mb-4">Product</h5>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Upload Report</a></li>
                <li><a href="#" className="hover:text-white">AI Analysis</a></li>
                <li><a href="#" className="hover:text-white">Track Trends</a></li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold text-white mb-4">Company</h5>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold text-white mb-4">Legal</h5>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Privacy</a></li>
                <li><a href="#" className="hover:text-white">Terms</a></li>
                <li><a href="#" className="hover:text-white">Disclaimer</a></li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold text-white mb-4">Connect</h5>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Twitter</a></li>
                <li><a href="#" className="hover:text-white">LinkedIn</a></li>
                <li><a href="#" className="hover:text-white">GitHub</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-700 pt-8">
            <p className="text-center text-sm">
              Copyright 2026 HealthReport AI. All rights reserved.
            </p>
            <p className="text-center text-xs mt-2">
              Medical Disclaimer: This tool is for educational purposes only and not a substitute for professional medical advice.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
