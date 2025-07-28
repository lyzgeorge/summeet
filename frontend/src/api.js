import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Token management
const TOKEN_KEY = 'summeet_access_token'
const USER_EMAIL_KEY = 'summeet_user_email'

export const tokenManager = {
  getToken: () => localStorage.getItem(TOKEN_KEY),
  setToken: (token) => localStorage.setItem(TOKEN_KEY, token),
  removeToken: () => localStorage.removeItem(TOKEN_KEY),
  getUserEmail: () => localStorage.getItem(USER_EMAIL_KEY),
  setUserEmail: (email) => localStorage.setItem(USER_EMAIL_KEY, email),
  removeUserEmail: () => localStorage.removeItem(USER_EMAIL_KEY),
  isAuthenticated: () => !!localStorage.getItem(TOKEN_KEY),
  clearAuth: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_EMAIL_KEY)
  }
}

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = tokenManager.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      tokenManager.clearAuth()
      // Redirect to login or emit event
      window.dispatchEvent(new CustomEvent('auth-expired'))
    }
    return Promise.reject(error)
  }
)

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

export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/login', { email, password })
    const { access_token, user_email } = response.data
    
    // Store token and user info
    tokenManager.setToken(access_token)
    tokenManager.setUserEmail(user_email)
    
    return response.data
  },
  
  logout: () => {
    tokenManager.clearAuth()
  },
  
  isAuthenticated: () => tokenManager.isAuthenticated(),
  
  getCurrentUser: () => tokenManager.getUserEmail()
}

export const appAPI = {
  getStatus: async () => {
    const response = await api.get('/')
    return response.data
  },
}

export default api