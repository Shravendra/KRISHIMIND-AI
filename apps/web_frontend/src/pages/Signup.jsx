import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, ArrowRight, ChevronLeft, Plus, X } from 'lucide-react'
import useAuthStore from '../store/authStore'
import Logo from '../components/Logo'

const CROP_SUGGESTIONS = [
  'Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane', 'Soybean',
  'Tomato', 'Onion', 'Potato', 'Groundnut', 'Chilli', 'Mango',
  'Banana', 'Grapes', 'Pomegranate', 'Turmeric', 'Pulses'
]

export default function Signup() {
  const { register, isLoading, error, clearError } = useAuthStore()
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [showPassword, setShowPassword] = useState(false)
  const [cropInput, setCropInput] = useState('')
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    phone: '',
    location: '',
    primary_crops: [],
    land_size_acres: '',
  })

  const handleChange = (e) => {
    clearError()
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const addCrop = (crop) => {
    if (!form.primary_crops.includes(crop)) {
      setForm(prev => ({ ...prev, primary_crops: [...prev.primary_crops, crop] }))
    }
  }

  const removeCrop = (crop) => {
    setForm(prev => ({ ...prev, primary_crops: prev.primary_crops.filter(c => c !== crop) }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = {
      ...form,
      land_size_acres: form.land_size_acres ? parseFloat(form.land_size_acres) : null,
    }
    const result = await register(payload)
    if (result.success) navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="w-full max-w-lg animate-fade-slide">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo size={44} />
          </div>
          <h1 className="font-display text-2xl font-bold text-gray-900">Join KrishiMind-AI</h1>
          <p className="text-gray-500 text-sm mt-1">
            Create your free farmer account in 2 minutes
          </p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center gap-2 mb-6">
          {[1, 2].map(s => (
            <div key={s} className="flex items-center gap-2 flex-1">
              <div className={`
                w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold
                transition-all duration-300
                ${step >= s ? 'bg-leaf-600 text-white' : 'bg-gray-200 text-gray-400'}
              `}>
                {s}
              </div>
              <span className="text-xs text-gray-500 hidden sm:block">
                {s === 1 ? 'Account Details' : 'Farm Profile'}
              </span>
              {s < 2 && <div className={`flex-1 h-0.5 ${step > s ? 'bg-leaf-400' : 'bg-gray-200'} transition-colors`} />}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-3xl shadow-deep p-8">
          {error && (
            <div className="mb-4 p-3.5 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Step 1: Account */}
            {step === 1 && (
              <div className="space-y-4 animate-fade-slide">
                <div>
                  <label className="label">Full Name *</label>
                  <input
                    type="text" name="name" value={form.name}
                    onChange={handleChange} className="input"
                    placeholder="Rajesh Kumar" required minLength={2}
                  />
                </div>

                <div>
                  <label className="label">Email Address *</label>
                  <input
                    type="email" name="email" value={form.email}
                    onChange={handleChange} className="input"
                    placeholder="rajesh@example.com" required
                  />
                </div>

                <div>
                  <label className="label">Password *</label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      name="password" value={form.password}
                      onChange={handleChange} className="input pr-10"
                      placeholder="Min. 8 characters" required minLength={8}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="label">Phone Number</label>
                  <input
                    type="tel" name="phone" value={form.phone}
                    onChange={handleChange} className="input"
                    placeholder="+91 98765 43210"
                  />
                </div>

                <button
                  type="button"
                  onClick={() => {
                    if (!form.name || !form.email || !form.password) return
                    setStep(2)
                  }}
                  className="btn-primary w-full flex items-center justify-center gap-2 py-3 mt-2"
                >
                  Continue <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Step 2: Farm Profile */}
            {step === 2 && (
              <div className="space-y-4 animate-fade-slide">
                <div>
                  <label className="label">Location (District, State)</label>
                  <input
                    type="text" name="location" value={form.location}
                    onChange={handleChange} className="input"
                    placeholder="Nashik, Maharashtra"
                  />
                </div>

                <div>
                  <label className="label">Land Size (acres)</label>
                  <input
                    type="number" name="land_size_acres"
                    value={form.land_size_acres}
                    onChange={handleChange} className="input"
                    placeholder="e.g., 5.5" min="0" step="0.5"
                  />
                </div>

                <div>
                  <label className="label">Primary Crops</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text" value={cropInput}
                      onChange={e => setCropInput(e.target.value)}
                      className="input flex-1"
                      placeholder="Type crop name..."
                      onKeyDown={e => {
                        if (e.key === 'Enter') { e.preventDefault(); addCrop(cropInput); setCropInput('') }
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => { addCrop(cropInput); setCropInput('') }}
                      className="btn-secondary px-3"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Quick-add chips */}
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {CROP_SUGGESTIONS.slice(0, 8).map(crop => (
                      <button
                        key={crop} type="button"
                        onClick={() => addCrop(crop)}
                        className={`text-xs px-2.5 py-1 rounded-full border transition-all ${
                          form.primary_crops.includes(crop)
                            ? 'bg-leaf-100 border-leaf-400 text-leaf-800'
                            : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-leaf-300'
                        }`}
                      >
                        {crop}
                      </button>
                    ))}
                  </div>

                  {/* Selected crops */}
                  {form.primary_crops.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {form.primary_crops.map(crop => (
                        <span key={crop}
                          className="inline-flex items-center gap-1 px-2.5 py-1 bg-leaf-600
                                     text-white text-xs rounded-full"
                        >
                          {crop}
                          <button type="button" onClick={() => removeCrop(crop)}>
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex gap-3 mt-2">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="btn-secondary flex items-center gap-1.5"
                  >
                    <ChevronLeft className="w-4 h-4" /> Back
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="btn-primary flex-1 flex items-center justify-center gap-2 py-3"
                  >
                    {isLoading ? (
                      <span className="loading-dots"><span /><span /><span /></span>
                    ) : (
                      <>Create Account <ArrowRight className="w-4 h-4" /></>
                    )}
                  </button>
                </div>
              </div>
            )}
          </form>

          <p className="text-center text-sm text-gray-500 mt-5">
            Already have an account?{' '}
            <Link to="/login" className="text-leaf-600 font-semibold hover:underline">Sign in</Link>
          </p>
        </div>

        <p className="text-center text-xs text-gray-400 mt-4">
          By registering, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  )
}
