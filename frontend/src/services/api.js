import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const documentService = {
  async upload(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getStatus(documentId) {
    const response = await api.get(`/documents/status/${documentId}`)
    return response.data
  },

  async list() {
    const response = await api.get('/documents/')
    return response.data
  },

  async delete(documentId) {
    const response = await api.delete(`/documents/${documentId}`)
    return response.data
  },
}

export const chatService = {
  async ask(documentId, question, sessionId = null) {
    const response = await api.post('/chat/ask', {
      document_id: documentId,
      question,
      session_id: sessionId,
    })
    return response.data
  },

  async getHistory(sessionId) {
    const response = await api.get(`/chat/history/${sessionId}`)
    return response.data
  },
}

export default api
