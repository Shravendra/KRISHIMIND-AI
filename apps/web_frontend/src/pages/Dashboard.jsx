import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Leaf, CloudRain, TrendingUp, AlertTriangle,
  MessageSquare, Camera, ChevronRight, Activity,
  Droplets, Thermometer, Wind, CheckCircle
} from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar
} from 'recharts'
import useAuthStore from '../store/authStore'

// ── Mock data for demo ────────────────────────────────────────────────────────
const YIELD_DATA = [
  { month: 'Jan', yield: 42, target: 45 },
  { month: 'Feb', yield: 38, target: 40 },
  { month: 'Mar', yield: 55, target: 50 },
  { month: 'Apr', yield: 49, target: 48 },
  { month: 'May', yield: 62, target: 55 },
  { month: 'Jun', yield: 58, target: 60 },
]

const PRICE_DATA = [
  { crop: 'Tomato', price: 1850, change: +12 },
  { crop: 'Onion',  price: 2200, change: -5 },
  { crop: 'Cotton', price: 6800, change: +3 },
  { crop: 'Wheat',  price: 2150, change: +1 },
]

const ALERTS = [
  { type: 'warning', icon: AlertTriangle, color: 'text-earth-600 bg-earth-50', message: 'Heavy rainfall expected in next 48 hours — avoid spraying', time: '2h ago' },
  { type: 'info', icon: Leaf, color: 'text-leaf-600 bg-leaf-50', message: 'Tomato prices up 12% this week — good time to sell', time: '4h ago' },
  { type: 'success', icon: CheckCircle, color: 'text-sky-600 bg-sky-50', message: 'Soil test report analyzed: pH optimal for your crops', time: '1d ago' },
]

const QUICK_ACTIONS = [
  { icon: Camera, label: 'Diagnose Disease', desc: 'Upload crop photo', path: '/crop', color: 'bg-leaf-600' },
  { icon: MessageSquare, label: 'Ask AI Assistant', desc: 'Chat with KrishiMind', path: '/chat', color: 'bg-sky-600' },
  { icon: CloudRain, label: 'Check Weather', desc: 'Farm-specific forecast', path: '/weather', color: 'bg-earth-500' },
  { icon: TrendingUp, label: 'Market Prices', desc: 'Sell at right time', path: '/market', color: 'bg-soil-500' },
]

function StatCard({ icon: Icon, label, value, unit, sub, color, trend }) {
  return (
    <div className="card">
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2.5 rounded-xl ${color}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        {trend !== undefined && (
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
            trend > 0 ? 'bg-leaf-100 text-leaf-700' : 'bg-red-100 text-red-700'
          }`}>
            {trend > 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900 font-display">
          {value}<span className="text-sm font-body text-gray-400 ml-1">{unit}</span>
        </p>
        <p className="text-sm font-medium text-gray-700 mt-0.5">{label}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [greeting, setGreeting] = useState('Good morning')

  useEffect(() => {
    const h = new Date().getHours()
    if (h < 12) setGreeting('Good morning')
    else if (h < 17) setGreeting('Good afternoon')
    else setGreeting('Good evening')
  }, [])

  return (
    <div className="space-y-6 animate-fade-slide">
      {/* Welcome banner */}
      <div className="relative bg-gradient-to-r from-leaf-700 via-leaf-600 to-leaf-800
                      rounded-2xl p-6 text-white overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-48 h-48 bg-white/5 rounded-full -translate-y-1/4 translate-x-1/4" />
        <div className="absolute bottom-0 left-40 w-32 h-32 bg-earth-400/20 rounded-full translate-y-1/4" />

        <div className="relative z-10 flex items-center justify-between">
          <div>
            <p className="text-leaf-200 text-sm font-medium">{greeting}, 👋</p>
            <h2 className="font-display text-2xl font-bold mt-0.5 mb-2">
              {user?.name?.split(' ')[0] || 'Farmer'}
            </h2>
            <p className="text-leaf-200 text-sm max-w-md">
              {user?.primary_crops?.length
                ? `Your ${user.primary_crops.slice(0,2).join(' & ')} crops look healthy today. Check the latest advisories below.`
                : 'Your farm intelligence dashboard is ready. Start by analyzing your crops!'
              }
            </p>
          </div>
          <div className="hidden md:flex flex-col items-center gap-1">
            <div className="text-4xl">🌾</div>
            <span className="text-leaf-300 text-xs">
              {user?.land_size_acres ? `${user.land_size_acres} acres` : 'Your Farm'}
            </span>
          </div>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Leaf}        label="Crop Health Score"    value="87"    unit="%"      color="bg-leaf-600"  trend={+5}  />
        <StatCard icon={Thermometer} label="Avg Temperature"      value="28"    unit="°C"     color="bg-earth-500" sub="Feels like 31°C" />
        <StatCard icon={Droplets}    label="Soil Moisture"        value="62"    unit="%"      color="bg-sky-600"   trend={-2}  />
        <StatCard icon={TrendingUp}  label="Market Opportunity"   value="High"  unit=""       color="bg-soil-500"  sub="Tomato prices rising" />
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Yield chart */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="font-semibold text-gray-900">Yield Trend</h3>
              <p className="text-xs text-gray-400 mt-0.5">Quintals per acre · 2024</p>
            </div>
            <span className="badge badge-success">+8% vs target</span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={YIELD_DATA}>
              <defs>
                <linearGradient id="yieldGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#16a34a" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#16a34a" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0fdf4" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
              />
              <Area type="monotone" dataKey="target" stroke="#86efac" strokeWidth={1.5}
                    strokeDasharray="4 4" fill="none" name="Target" />
              <Area type="monotone" dataKey="yield" stroke="#16a34a" strokeWidth={2.5}
                    fill="url(#yieldGrad)" name="Actual Yield" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Alerts */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900">Farm Alerts</h3>
            <span className="badge badge-warning">{ALERTS.length} new</span>
          </div>
          <div className="space-y-3">
            {ALERTS.map((alert, i) => (
              <div key={i} className="flex gap-3 p-3 rounded-xl bg-gray-50">
                <div className={`p-1.5 rounded-lg ${alert.color} self-start shrink-0`}>
                  <alert.icon className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs text-gray-700 leading-relaxed">{alert.message}</p>
                  <p className="text-[10px] text-gray-400 mt-1">{alert.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">Quick Actions</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {QUICK_ACTIONS.map(({ icon: Icon, label, desc, path, color }) => (
            <button
              key={path}
              onClick={() => navigate(path)}
              className="card-hover group text-left"
            >
              <div className={`${color} w-10 h-10 rounded-xl flex items-center justify-center mb-3
                               group-hover:scale-110 transition-transform duration-200`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <p className="font-semibold text-gray-900 text-sm">{label}</p>
              <p className="text-xs text-gray-400 mt-0.5">{desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Market prices */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">Today's Mandi Prices</h3>
          <button onClick={() => navigate('/market')}
            className="text-xs text-leaf-600 hover:underline flex items-center gap-1">
            View all <ChevronRight className="w-3 h-3" />
          </button>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {PRICE_DATA.map(({ crop, price, change }) => (
            <div key={crop} className="p-3 bg-gray-50 rounded-xl">
              <p className="text-sm font-semibold text-gray-900">{crop}</p>
              <p className="text-lg font-bold text-gray-900 mt-1">
                ₹{price.toLocaleString('en-IN')}
                <span className="text-xs text-gray-400 font-normal">/qtl</span>
              </p>
              <p className={`text-xs font-semibold mt-0.5 ${change > 0 ? 'text-leaf-600' : 'text-red-500'}`}>
                {change > 0 ? '▲' : '▼'} {Math.abs(change)}%
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
