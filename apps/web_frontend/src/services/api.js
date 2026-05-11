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
    message: `Analyse my soil test results for ${payload.cropType || 'general crops'}.`
      + ` pH: ${payload.pH || 'not provided'},`
      + ` N: ${payload.nitrogen || 'not provided'} kg/ha,`
      + ` P: ${payload.phosphorus || 'not provided'} kg/ha,`
      + ` K: ${payload.potassium || 'not provided'} kg/ha,`
      + ` EC: ${payload.ec || 'not provided'} dS/m,`
      + ` Soil texture: ${payload.soilType || 'not specified'}.`,
    crop: payload.cropType || undefined,
    farm_context: {
      cropType: payload.cropType,
      // soil_test_data keys must match what SOIL_ANALYSIS_PROMPT.format() expects
      soil_test_data: {
        ph:           payload.pH          || null,
        nitrogen:     payload.nitrogen    || null,
        phosphorus:   payload.phosphorus  || null,
        potassium:    payload.potassium   || null,
        ec:           payload.ec          || null,
        texture:      payload.soilType    || null,
        organic_carbon: null,
        zinc:         null,
        iron:         null,
        boron:        null,
      },
    },
  }),
  optimizeFertilizer: (payload) => api.post('/chat', {
    message: `Generate a complete fertilizer plan for ${payload.cropType || 'my crop'}`
      + ` at ${payload.growthStage} growth stage.`
      + ` Farm size: ${payload.farmSize || 1} acres.`
      + ` Soil type: ${payload.soilType}.`
      + ` Budget: ${payload.budget}.`
      + ` Organic preferred: ${payload.organic ? 'yes' : 'no'}.`,
    crop: payload.cropType || undefined,
    farm_context: {
      cropType: payload.cropType,
      // All structured fields the orchestrator needs
      fertilizer_context: {
        growth_stage:      payload.growthStage   || null,
        land_size_acres:   payload.farmSize
                             ? parseFloat(payload.farmSize)
                             : null,
        soil_type:         payload.soilType      || null,
        budget:            payload.budget        || 'medium',
        organic_preferred: Boolean(payload.organic),
      },
    },
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
