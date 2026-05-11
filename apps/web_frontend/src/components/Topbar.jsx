import { Bell, Search, Sun, Cloud, Thermometer } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const PAGE_TITLES = {
  '/dashboard':  { title: 'Farm Dashboard', subtitle: 'Your agricultural intelligence hub' },
  '/chat':       { title: 'AI Assistant',   subtitle: 'Ask anything about your farm' },
  '/crop':       { title: 'Crop Analysis',  subtitle: 'Disease detection & crop health' },
  '/soil':       { title: 'Soil & Fertilizer', subtitle: 'Nutrient management & soil health' },
  '/weather':    { title: 'Weather Risk',   subtitle: 'Climate alerts & farm advisories' },
  '/market':     { title: 'Market Intelligence', subtitle: 'Prices, trends & selling strategy' },
  '/livestock':  { title: 'Livestock Health', subtitle: 'Animal health & management' },
  '/learn':      { title: 'Knowledge Base', subtitle: 'Learn from agricultural experts' },
  '/settings':   { title: 'Settings',       subtitle: 'Manage your account & preferences' },
}

export default function Topbar() {
  const location = useLocation()
  const { user } = useAuthStore()
  const page = PAGE_TITLES[location.pathname] || { title: 'KrishiMind-AI', subtitle: '' }
  const today = new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

  return (
    <header className="bg-white border-b border-leaf-100 px-6 py-4 flex items-center justify-between shrink-0">
      {/* Left: Page info */}
      <div>
        <h1 className="font-display text-xl font-bold text-gray-900">{page.title}</h1>
        <p className="text-xs text-gray-500 mt-0.5">{page.subtitle}</p>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        {/* Date */}
        <span className="hidden md:block text-xs text-gray-400 font-mono">{today}</span>

        {/* Notification bell */}
        <button className="relative p-2 rounded-xl hover:bg-leaf-50 transition-colors">
          <Bell className="w-5 h-5 text-gray-500" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-earth-500 rounded-full" />
        </button>

        {/* Avatar */}
        <div className="flex items-center gap-2 pl-3 border-l border-gray-100">
          <div className="w-8 h-8 bg-gradient-to-br from-leaf-400 to-leaf-700 rounded-full
                          flex items-center justify-center text-white text-sm font-bold">
            {user?.name?.[0]?.toUpperCase() || 'F'}
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-semibold text-gray-900 leading-none">
              {user?.name?.split(' ')[0] || 'Farmer'}
            </p>
            <p className="text-xs text-gray-400 mt-0.5 capitalize">{user?.role || 'farmer'}</p>
          </div>
        </div>
      </div>
    </header>
  )
}
