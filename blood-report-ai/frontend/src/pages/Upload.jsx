/**
 * Upload Page - Blood Report Upload
 * Drag-and-drop PDF/image upload with progress
 */
import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <button
          onClick={() => navigate('/dashboard')}
          className="mb-8 inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700"
        >
          ← Back to Dashboard
        </button>

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Upload Blood Report</h1>
          <p className="text-gray-600">Upload a PDF or image of your blood test report for AI analysis</p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Date Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Report Date
              </label>
              <input
                type="date"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Blood Report File
              </label>

              {file ? (
                // File Selected
                <div className="p-6 bg-green-50 border-2 border-green-300 rounded-xl">
                  <div className="flex items-center gap-3">
                    <div className="text-3xl">✓</div>
                    <div>
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-600">{(file.size / 1024 / 1024).toFixed(2)}MB</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setFile(null)
                        setError('')
                      }}
                      className="ml-auto text-gray-600 hover:text-gray-900 text-xl"
                    >
                      ✕
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
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-300 hover:border-indigo-400'
                  }`}
                >
                  <div className="text-5xl mb-3">📄</div>
                  <p className="font-medium text-gray-900">Drag your report here</p>
                  <p className="text-sm text-gray-600 mt-1">or click to browse</p>
                  <p className="text-xs text-gray-500 mt-3">PDF, JPG, PNG, TIFF up to 20MB</p>

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
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !file}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium py-3 rounded-lg hover:from-indigo-700 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
                  Processing...
                </>
              ) : (
                <>
                  <span>📤</span> Upload and Analyze
                </>
              )}
            </button>
          </form>

          {/* Info Box */}
          <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-medium text-blue-900 mb-2">📋 What we extract:</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>✓ All blood markers with values</li>
              <li>✓ Reference ranges (normal/abnormal)</li>
              <li>✓ Report date and lab name</li>
              <li>✓ AI-powered trend analysis</li>
            </ul>
          </div>
        </div>

        {/* Security Info */}
        <div className="mt-6 p-4 bg-white border border-gray-200 rounded-lg text-center text-sm text-gray-600">
          🔐 Your data is encrypted end-to-end with AES-256 and never shared with third parties
        </div>
      </div>
    </div>
  )
}
