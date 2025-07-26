import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const transcriptionAPI = {
  upload: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  saveDirectTranscript: async (filename, transcript, speakers = '[]') => {
    const response = await api.post('/transcript', {
      filename,
      transcript,
      speakers
    })
    return response.data
  },

  get: async (id) => {
    const response = await api.get(`/transcription/${id}`)
    return response.data
  },

  summarize: async (id, language = 'en', temperature = 0.8) => {
    const response = await api.post(`/summarize/${id}`, null, {
      params: { language, temperature }
    })
    return response.data
  },

  export: async (id) => {
    const response = await api.get(`/export/${id}`, {
      responseType: 'blob',
    })
    return response.data
  },
}

export const appAPI = {
  getStatus: async () => {
    const response = await api.get('/')
    return response.data
  },
}

export default api