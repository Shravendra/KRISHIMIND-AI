import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, MessageSquare, Leaf, FlaskConical,
  CloudRain, TrendingUp, Beef, BookOpen, Settings,
  LogOut, ChevronLeft, ChevronRight, Bell, User
} from 'lucide-react'
import Logo from './Logo'
import useAuthStore from '../store/authStore'
import { useState } from 'react'

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', color: 'text-leaf-600' },
  { to: '/chat',      icon: MessageSquare,   label: 'AI Assistant', color: 'text-sky-600' },
  { to: '/crop',      icon: Leaf,            label: 'Crop Analysis', color: 'text-leaf-500' },
  { to: '/soil',      icon: FlaskConical,    label: 'Soil & Fertilizer', color: 'text-earth-600' },
  { to: '/weather',   icon: CloudRain,       label: 'Weather Risk', color: 'text-sky-500' },
  { to: '/market',    icon: TrendingUp,      label: 'Market Intel', color: 'text-earth-500' },
  { to: '/livestock', icon: Beef,            label: 'Livestock', color: 'text-soil-500' },
  { to: '/learn',     icon: BookOpen,        label: 'Knowledge Base', color: 'text-leaf-700' },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <aside
      className={`
        relative flex flex-col h-screen bg-white border-r border-leaf-100
        transition-all duration-300 ease-in-out shadow-sm
        ${collapsed ? 'w-20' : 'w-64'}
      `}
    >
      {/* Toggle button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3.5 top-20 w-7 h-7 bg-white border border-leaf-200
                   rounded-full flex items-center justify-center shadow-sm z-10
                   hover:bg-leaf-50 transition-colors"
      >
        {collapsed
          ? <ChevronRight className="w-3.5 h-3.5 text-leaf-600" />
          : <ChevronLeft  className="w-3.5 h-3.5 text-leaf-600" />
        }
      </button>

      {/* Logo */}
      <div className={`
        flex items-center gap-2 px-4 py-5 border-b border-leaf-100
        ${collapsed ? 'justify-center' : ''}
      `}>
        <Logo size={36} showText={!collapsed} />
      </div>

      {/* User info */}
      {!collapsed && (
        <div className="mx-3 mt-4 p-3 bg-leaf-50 rounded-xl">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-leaf-600 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">
                {user?.name || 'Farmer'}
              </p>
              <p className="text-xs text-gray-500 truncate">{user?.location || 'India'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ to, icon: Icon, label, color }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `
              flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
              transition-all duration-150 group
              ${isActive
                ? 'bg-leaf-50 text-leaf-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }
              ${collapsed ? 'justify-center' : ''}
            `}
            title={collapsed ? label : undefined}
          >
            <Icon className={`w-5 h-5 flex-shrink-0 ${color}`} />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Bottom actions */}
      <div className="p-3 border-t border-leaf-100 space-y-1">
        <NavLink
          to="/settings"
          className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm
            text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-all
            ${collapsed ? 'justify-center' : ''}`}
          title={collapsed ? 'Settings' : undefined}
        >
          <Settings className="w-5 h-5 text-gray-400" />
          {!collapsed && <span>Settings</span>}
        </NavLink>

        <button
          onClick={handleLogout}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm
            text-red-600 hover:bg-red-50 transition-all
            ${collapsed ? 'justify-center' : ''}`}
          title={collapsed ? 'Logout' : undefined}
        >
          <LogOut className="w-5 h-5" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  )
}
