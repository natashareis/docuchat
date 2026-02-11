import { useState, useEffect } from 'react'
import { documentService } from '@/services/api'

export function useDocumentStatus(documentId, interval = 2000) {
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!documentId) return

    let intervalId

    const checkStatus = async () => {
      try {
        const data = await documentService.getStatus(documentId)
        setStatus(data)
        setError(null)
        
        if (data.status === 'completed' || data.status === 'failed') {
          if (intervalId) {
            clearInterval(intervalId)
          }
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    checkStatus()
    intervalId = setInterval(checkStatus, interval)

    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [documentId, interval])

  return { status, error, loading }
}
