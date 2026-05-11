import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import useAuthStore from './store/authStore'

// Pages
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import CropAnalysis from './pages/CropAnalysis'
import SoilFertilizer from './pages/SoilFertilizer'
import WeatherRisk from './pages/WeatherRisk'
import MarketIntelligence from './pages/MarketIntelligence'
import Livestock from './pages/Livestock'
import KnowledgeBase from './pages/KnowledgeBase'
import Settings from './pages/Settings'
import Layout from './components/Layout'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function PublicRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  return !isAuthenticated ? children : <Navigate to="/dashboard" replace />
}

export default function App() {
  const { initAuth } = useAuthStore()

  useEffect(() => {
    initAuth()
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login"  element={<PublicRoute><Login  /></PublicRoute>} />
        <Route path="/signup" element={<PublicRoute><Signup /></PublicRoute>} />

        {/* Protected routes inside Layout */}
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"  element={<Dashboard />} />
          <Route path="chat"       element={<Chat />} />
          <Route path="crop"       element={<CropAnalysis />} />
          <Route path="soil"       element={<SoilFertilizer />} />
          <Route path="weather"    element={<WeatherRisk />} />
          <Route path="market"     element={<MarketIntelligence />} />
          <Route path="livestock"  element={<Livestock />} />
          <Route path="learn"      element={<KnowledgeBase />} />
          <Route path="settings"   element={<Settings />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
