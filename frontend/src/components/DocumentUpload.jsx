import { useState, useRef, useEffect } from 'react'
import { Upload, File, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Button } from './ui/Button'
import { documentService } from '@/services/api'
import { useDocumentStatus } from '@/hooks/useDocumentStatus'

export function DocumentUpload({ onDocumentReady }) {
  const [file, setFile] = useState(null)
  const [uploadedDocId, setUploadedDocId] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const { status, error: statusError } = useDocumentStatus(uploadedDocId)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files?.[0]
    if (droppedFile) {
      setFile(droppedFile)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    try {
      setError(null)
      const result = await documentService.upload(file)
      setUploadedDocId(result.id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload document')
    }
  }

  const handleReset = () => {
    setFile(null)
    setUploadedDocId(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  useEffect(() => {
    if (status?.status === 'completed') {
      const timer = setTimeout(() => onDocumentReady(uploadedDocId), 500)
      return () => clearTimeout(timer)
    }
  }, [status?.status, uploadedDocId, onDocumentReady])

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-lg sm:text-xl">Upload Document</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer"
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleFileChange}
            className="hidden"
          />
          
          {!file ? (
            <div className="flex flex-col items-center gap-2">
              <Upload className="h-12 w-12 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                Click to upload or drag and drop
              </p>
              <p className="text-xs text-muted-foreground">
                PDF, DOC, DOCX, or TXT (Max 10MB)
              </p>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-center gap-2"
            >
              <File className="h-8 w-8 text-primary" />
              <span className="font-medium">{file.name}</span>
            </motion.div>
          )}
        </div>

        {file && !uploadedDocId && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-2 mt-4"
          >
            <Button onClick={handleUpload} className="flex-1">
              Upload Document
            </Button>
            <Button onClick={handleReset} variant="outline">
              Cancel
            </Button>
          </motion.div>
        )}

        {status && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 rounded-lg bg-muted"
          >
            {status.status === 'processing' && (
              <div className="flex items-center gap-2 text-primary">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Processing document...</span>
              </div>
            )}
            {status.status === 'completed' && (
              <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                <CheckCircle className="h-5 w-5" />
                <span>Document ready!</span>
              </div>
            )}
            {status.status === 'failed' && (
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                <span>Processing failed: {status.error_message}</span>
              </div>
            )}
          </motion.div>
        )}

        {(error || statusError) && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 rounded-lg bg-destructive/10 text-destructive"
          >
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              <span>{error || statusError}</span>
            </div>
          </motion.div>
        )}
      </CardContent>
    </Card>
  )
}
