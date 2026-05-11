import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Leaf, ArrowRight, Sprout } from 'lucide-react'
import useAuthStore from '../store/authStore'
import Logo from '../components/Logo'

const FEATURES = [
  '🌿 AI crop disease detection',
  '🌤️ Hyper-local weather alerts',
  '💰 Commodity price forecasting',
  '🧪 Soil & fertilizer advice',
  '🐄 Livestock health monitoring',
  '📚 Expert agricultural knowledge',
]

export default function Login() {
  const { login, isLoading, error, clearError } = useAuthStore()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)

  const handleChange = (e) => {
    clearError()
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const result = await login(form.email, form.password)
    if (result.success) navigate('/dashboard')
  }

  const handleDemo = async () => {
    const result = await login('demo@krishimind.ai', 'demo1234')
    if (result.success) navigate('/dashboard')
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel: Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-leaf-800 via-leaf-700 to-leaf-900
                      relative flex-col justify-between p-12 overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-white rounded-full -translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 right-0 w-64 h-64 bg-earth-400 rounded-full translate-x-1/4 translate-y-1/4" />
          {/* Subtle field pattern */}
          <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        {/* Logo */}
        <Logo size={44} showText variant="light" />

        {/* Hero text */}
        <div className="relative z-10">
          <h2 className="font-display text-4xl font-bold text-white leading-tight mb-4">
            Smart Farming<br />
            <span className="text-earth-300">Powered by AI</span>
          </h2>
          <p className="text-leaf-200 text-lg mb-8 leading-relaxed">
            Join thousands of farmers making smarter decisions with 
            AI-powered crop intelligence, disease detection, and market insights.
          </p>

          {/* Feature list */}
          <ul className="space-y-2.5">
            {FEATURES.map(f => (
              <li key={f} className="flex items-center gap-2 text-leaf-100 text-sm">
                <span className="text-base">{f.split(' ')[0]}</span>
                <span>{f.split(' ').slice(1).join(' ')}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Bottom quote */}
        <div className="relative z-10 border-t border-leaf-600 pt-6">
          <p className="text-leaf-300 text-sm italic">
            "KrishiMind helped me identify early blight 2 weeks before it could spread.
            Saved my entire tomato crop!"
          </p>
          <p className="text-leaf-400 text-xs mt-2">— Rajesh Kumar, Nashik, Maharashtra</p>
        </div>
      </div>

      {/* Right panel: Login form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md animate-fade-slide">
          {/* Mobile logo */}
          <div className="lg:hidden mb-8 flex justify-center">
            <Logo size={40} />
          </div>

          <div className="bg-white rounded-3xl shadow-deep p-8">
            <h1 className="font-display text-2xl font-bold text-gray-900 mb-1">Welcome back</h1>
            <p className="text-gray-500 text-sm mb-7">Sign in to your farming dashboard</p>

            {error && (
              <div className="mb-4 p-3.5 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Email address</label>
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  className="input"
                  placeholder="your@email.com"
                  required
                  autoComplete="email"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="label mb-0">Password</label>
                  <button type="button" className="text-xs text-leaf-600 hover:underline">
                    Forgot password?
                  </button>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    className="input pr-10"
                    placeholder="••••••••"
                    required
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary w-full flex items-center justify-center gap-2 py-3 mt-2"
              >
                {isLoading ? (
                  <span className="loading-dots">
                    <span /><span /><span />
                  </span>
                ) : (
                  <>Sign In <ArrowRight className="w-4 h-4" /></>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="flex items-center gap-3 my-5">
              <div className="flex-1 h-px bg-gray-200" />
              <span className="text-xs text-gray-400">or</span>
              <div className="flex-1 h-px bg-gray-200" />
            </div>

            {/* Demo access */}
            <button
              onClick={handleDemo}
              disabled={isLoading}
              className="btn-secondary w-full flex items-center justify-center gap-2 py-3"
            >
              <Sprout className="w-4 h-4 text-leaf-600" />
              Try Demo Account
            </button>

            <p className="text-center text-sm text-gray-500 mt-5">
              New to KrishiMind?{' '}
              <Link to="/signup" className="text-leaf-600 font-semibold hover:underline">
                Create account
              </Link>
            </p>
          </div>

          {/* Trust badges */}
          <div className="flex items-center justify-center gap-6 mt-6 text-xs text-gray-400">
            <span>🔒 SSL Secured</span>
            <span>🇮🇳 Made for India</span>
            <span>🌱 10K+ Farmers</span>
          </div>
        </div>
      </div>
    </div>
  )
}
