import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const stored = localStorage.getItem('krishimind-auth')
    if (stored) {
      try {
        const { state } = JSON.parse(stored)
        if (state?.token) {
          config.headers.Authorization = `Bearer ${state.token}`
        }
      } catch (_) {}
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('krishimind-auth')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const chatService = {
  sendMessage: (payload) => api.post('/chat', payload),
  getHistory: (conversationId) => api.get(`/chat/${conversationId}`),
}

export const agentService = {
  listAgents: () => api.get('/agents'),

  // Image / crop disease
  analyzeImage: (payload) => api.post('/agents/analyze-image', payload),

  // Soil & Fertilizer
  analyzeSoil: (payload) => api.post('/chat', {
    message: `Analyse my soil: ${JSON.stringify(payload)}`,
    farm_context: payload,
  }),
  optimizeFertilizer: (payload) => api.post('/chat', {
    message: `Optimise fertilizer plan for ${payload.cropType} at ${payload.growthStage} stage. Farm size: ${payload.farmSize} acres. Soil: ${payload.soilType}. Budget: ${payload.budget}. Organic preferred: ${payload.organic}.`,
    farm_context: payload,
  }),

  // Weather Risk
  assessWeatherRisk: (payload) => api.post('/chat', {
    message: `Assess weather risk for ${payload.cropType || 'my crops'} at ${payload.location}. Growth stage: ${payload.growthStage}. Irrigation: ${payload.irrigationType}.`,
    farm_context: payload,
  }),

  // Livestock
  assessLivestockHealth: (payload) => api.post('/chat', {
    message: `My ${payload.animalType} has these symptoms: ${payload.symptoms.join(', ')}. ${payload.query}`,
    farm_context: { ...payload, livestock: [payload.animalType] },
  }),

  // Knowledge / RAG
  askKnowledge: (query) => api.post('/chat', {
    message: query,
    farm_context: {},
  }),
}

export default api
