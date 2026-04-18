/**
 * Upload Page - Blood Report Upload
 * Drag-and-drop PDF/image upload with processing
 * IMPORTANT: Analysis is educational only, not for diagnosis
 */
import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload as UploadIcon, AlertCircle, Home, FileUp, CheckCircle, Lock, Shield } from 'lucide-react'
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
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b border-gray-200 sticky top-0 z-50 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 transition font-medium"
            >
              <Home className="w-5 h-5" />
              <span>Back Home</span>
            </button>
            <h1 className="text-lg font-semibold text-gray-900">Upload Your Report</h1>
            <div className="w-32"></div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Medical Disclaimer */}
        <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-900">
              <strong>Important Disclaimer:</strong> The analysis provided is for educational purposes only and does NOT replace professional medical diagnosis. Always consult with a qualified healthcare provider.
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-12">
          {/* Upload Section */}
          <div className="lg:col-span-2">
            {/* Upload Card */}
            <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
              {/* Header */}
              <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-2">Upload Blood Report</h2>
                <p className="text-gray-600">Upload a PDF or image of your blood test report for AI analysis</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Date Picker */}
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-3">
                    Report Date
                  </label>
                  <input
                    type="date"
                    value={reportDate}
                    onChange={(e) => setReportDate(e.target.value)}
                    className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                  />
                </div>

                {/* File Upload */}
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-3">
                    Blood Report File
                  </label>

                  {file ? (
                    // File Selected
                    <div className="p-6 bg-green-50 border-2 border-green-300 rounded-lg">
                      <div className="flex items-center gap-4">
                        <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="font-semibold text-gray-900">{file.name}</p>
                          <p className="text-sm text-gray-600">{(file.size / 1024 / 1024).toFixed(2)}MB</p>
                        </div>
                        <button
                          type="button"
                          onClick={() => {
                            setFile(null)
                            setError('')
                          }}
                          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg transition font-medium"
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
                      className={`p-12 border-2 border-dashed rounded-lg text-center cursor-pointer transition ${
                        dragActive
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'
                      }`}
                    >
                      <FileUp className="w-12 h-12 mx-auto mb-4 text-blue-600" />
                      <p className="font-semibold text-gray-900 mb-1">Drag your report here</p>
                      <p className="text-sm text-gray-600 mb-3">or click to browse files</p>
                      <p className="text-xs text-gray-500">
                        Supported formats: PDF, JPG, PNG, TIFF (Max 20MB)
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
                  <div className="p-4 bg-red-50 border border-red-300 rounded-lg text-red-900 text-sm flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    {error}
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading || !file}
                  className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
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
            </div>
          </div>

          {/* Sidebar - What We Extract & Security */}
          <div className="lg:col-span-1 space-y-6">
            {/* What We Extract */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-4">What We Extract</h3>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">All blood markers and values</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">Reference ranges (normal/abnormal)</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">Lab information and test date</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">AI-powered analysis and insights</span>
                </li>
              </ul>
            </div>

            {/* Security Features */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Security & Privacy</h3>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-3">
                  <Lock className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">AES-256 end-to-end encryption</span>
                </li>
                <li className="flex items-start gap-3">
                  <Shield className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">Data never shared with third parties</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">Full control - delete anytime</span>
                </li>
              </ul>
            </div>

            {/* Supported Formats */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Supported Formats</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>✓ PDF files</li>
                <li>✓ JPEG images</li>
                <li>✓ PNG images</li>
                <li>✓ TIFF images</li>
              </ul>
              <p className="text-xs text-gray-600 mt-4">Maximum file size: 20MB</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
