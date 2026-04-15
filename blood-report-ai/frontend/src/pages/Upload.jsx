/**
 * Upload Page - Blood Report Upload
 * Drag-and-drop PDF/image upload with processing
 * IMPORTANT: Analysis is educational only, not for diagnosis
 */
import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload as UploadIcon, AlertCircle, Home, FileUp } from 'lucide-react'
import { api } from '../lib/api'

export default function Upload() {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0])

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(e.type !== 'dragleave')
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const droppedFiles = e.dataTransfer.files
    if (droppedFiles[0]) {
      handleFileSelect(droppedFiles[0])
    }
  }

  const handleFileSelect = (selectedFile) => {
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff']
    
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Please upload a PDF or image file (JPG, PNG, TIFF)')
      return
    }

    if (selectedFile.size > 20 * 1024 * 1024) {
      setError('File must be smaller than 20MB')
      return
    }

    setFile(selectedFile)
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setError('')

    try {
      const result = await api.uploadReport(file, reportDate)
      navigate(`/analysis/${result.report_id}`)
    } catch (err) {
      setError(err.message || 'Failed to upload report')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-purple-700/30 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-purple-400 hover:text-purple-300 transition"
            >
              <Home className="w-5 h-5" />
              <span>Home</span>
            </button>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <UploadIcon className="w-6 h-6 text-purple-400" />
              Upload Report
            </h1>
            <div className="w-20"></div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Medical Disclaimer */}
        <div className="mb-8 bg-amber-900/30 border border-amber-700/50 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-amber-100">
              <strong>Important:</strong> The analysis provided is for educational purposes only and NOT a medical diagnosis. Always consult a healthcare provider for medical advice.
            </div>
          </div>
        </div>

        {/* Upload Card */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-purple-700/30 rounded-2xl p-8 shadow-2xl">
          {/* Header */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">Upload Your Blood Report</h2>
            <p className="text-gray-300">Upload a PDF or image of your latest blood test report</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Date Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Report Date
              </label>
              <input
                type="date"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
                className="w-full px-4 py-3 bg-slate-700 border border-purple-700/30 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition"
              />
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Blood Report File
              </label>

              {file ? (
                // File Selected
                <div className="p-6 bg-green-900/30 border-2 border-green-700/50 rounded-xl">
                  <div className="flex items-center gap-4">
                    <div className="text-3xl">✓</div>
                    <div className="flex-1">
                      <p className="font-medium text-white">{file.name}</p>
                      <p className="text-sm text-gray-300">{(file.size / 1024 / 1024).toFixed(2)}MB</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setFile(null)
                        setError('')
                      }}
                      className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition font-medium"
                    >
                      Change
                    </button>
                  </div>
                </div>
              ) : (
                // Drop Zone
                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`p-12 border-2 border-dashed rounded-xl text-center cursor-pointer transition ${
                    dragActive
                      ? 'border-purple-500 bg-purple-500/10'
                      : 'border-purple-700/30 hover:border-purple-500/50'
                  }`}
                >
                  <FileUp className="w-12 h-12 mx-auto mb-4 text-purple-400" />
                  <p className="font-medium text-white mb-1">Drag your report here</p>
                  <p className="text-sm text-gray-400 mb-3">or click to browse</p>
                  <p className="text-xs text-gray-500">
                    Supported: PDF, JPG, PNG, TIFF (max 20MB)
                  </p>

                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png,.tiff"
                    onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                    className="hidden"
                  />
                </div>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-900/30 border border-red-700/50 rounded-lg text-red-200 text-sm flex items-start gap-3">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !file}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-medium py-4 rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2 text-lg transform hover:scale-105"
            >
              {loading ? (
                <>
                  <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
                  Processing your report...
                </>
              ) : (
                <>
                  <UploadIcon className="w-5 h-5" />
                  Upload & Analyze
                </>
              )}
            </button>
          </form>

          {/* Info Box */}
          <div className="mt-8 p-4 bg-purple-900/30 border border-purple-700/50 rounded-lg">
            <h3 className="font-medium text-purple-200 mb-3">📊 What we extract:</h3>
            <ul className="text-sm text-purple-100 space-y-2">
              <li className="flex items-center gap-2">
                <span className="text-purple-400">✓</span> All blood markers with values
              </li>
              <li className="flex items-center gap-2">
                <span className="text-purple-400">✓</span> Reference ranges (normal/abnormal)
              </li>
              <li className="flex items-center gap-2">
                <span className="text-purple-400">✓</span> Report date and lab information
              </li>
              <li className="flex items-center gap-2">
                <span className="text-purple-400">✓</span> AI-powered educational analysis
              </li>
            </ul>
          </div>
        </div>

        {/* Security & Privacy */}
        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className="bg-slate-800 border border-purple-700/30 rounded-lg p-4 text-center">
            <div className="text-2xl mb-2">🔒</div>
            <p className="text-sm text-gray-300">AES-256 Encrypted</p>
            <p className="text-xs text-gray-500">End-to-end security</p>
          </div>
          <div className="bg-slate-800 border border-purple-700/30 rounded-lg p-4 text-center">
            <div className="text-2xl mb-2">🚫</div>
            <p className="text-sm text-gray-300">Not Shared</p>
            <p className="text-xs text-gray-500">Private & confidential</p>
          </div>
        </div>
      </div>
    </div>
  )
}
