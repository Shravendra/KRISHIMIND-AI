import { useState } from 'react'
import { TrendingUp, TrendingDown, DollarSign, BarChart2, Loader, Store } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import api from '../services/api'
import useAuthStore from '../store/authStore'

const COMMODITIES = ['Tomato', 'Onion', 'Potato', 'Wheat', 'Rice', 'Cotton', 'Soybean',
                     'Maize', 'Groundnut', 'Sugarcane', 'Chilli', 'Turmeric', 'Garlic', 'Pulses']

const MOCK_PRICES = {
  Tomato:    { current: 1850, change: +12, unit: 'quintal', msp: null },
  Onion:     { current: 2200, change: -5,  unit: 'quintal', msp: null },
  Wheat:     { current: 2275, change: +1,  unit: 'quintal', msp: 2275 },
  Rice:      { current: 2183, change: 0,   unit: 'quintal', msp: 2183 },
  Cotton:    { current: 6825, change: +3,  unit: 'quintal', msp: 6620 },
  Soybean:   { current: 4600, change: -2,  unit: 'quintal', msp: 4600 },
  Maize:     { current: 2090, change: +4,  unit: 'quintal', msp: 2090 },
  Groundnut: { current: 6377, change: +6,  unit: 'quintal', msp: 6377 },
}

const TREND_DATA = [
  { week: 'W1', price: 1650 },
  { week: 'W2', price: 1720 },
  { week: 'W3', price: 1680 },
  { week: 'W4', price: 1800 },
  { week: 'W5', price: 1850 },
  { week: 'W6', price: 1920 },
]

function PriceCard({ crop, data }) {
  const isUp = data.change > 0
  const TrendIcon = isUp ? TrendingUp : TrendingDown

  return (
    <div className="card hover:shadow-farm transition-shadow cursor-pointer">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-semibold text-gray-900">{crop}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1 font-display">
            ₹{data.current.toLocaleString('en-IN')}
            <span className="text-sm font-body text-gray-400 font-normal">/{data.unit}</span>
          </p>
          {data.msp && (
            <p className="text-xs text-gray-500 mt-1">MSP: ₹{data.msp.toLocaleString('en-IN')}</p>
          )}
        </div>
        <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-sm font-bold ${
          isUp ? 'bg-leaf-100 text-leaf-700' : 'bg-red-100 text-red-600'
        }`}>
          <TrendIcon className="w-3.5 h-3.5" />
          {Math.abs(data.change)}%
        </div>
      </div>
    </div>
  )
}

export default function MarketIntelligence() {
  const { user } = useAuthStore()
  const [selectedCrop, setSelectedCrop] = useState(user?.primary_crops?.[0] || 'Tomato')
  const [quantity, setQuantity] = useState('')
  const [storage, setStorage] = useState('0')
  const [urgency, setUrgency] = useState('medium')
  const [advice, setAdvice] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const getAdvice = async () => {
    setIsLoading(true)
    setAdvice(null)
    try {
      const { data } = await api.post('/chat', {
        message: `Market advice for ${selectedCrop}: When should I sell? I have ${quantity || 'some'} quintals. Storage available for ${storage} months.`,
        farmer_id: user?.farmer_id || 'anonymous',
        crop: selectedCrop,
        conversation_history: [],
      })
      setAdvice(data)
    } catch (_) {
      setAdvice({ answer: 'Unable to fetch market advice at this time. Please try again.' })
    } finally {
      setIsLoading(false)
    }
  }

  const priceEntries = Object.entries(MOCK_PRICES)
  const currentPrice = MOCK_PRICES[selectedCrop]

  return (
    <div className="space-y-6 animate-fade-slide">
      <div>
        <h2 className="section-title">Market Intelligence</h2>
        <p className="section-subtitle">Real-time mandi prices, trends & AI selling strategy</p>
      </div>

      {/* Price grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {priceEntries.map(([crop, data]) => (
          <div key={crop} onClick={() => setSelectedCrop(crop)}>
            <PriceCard crop={crop} data={data} />
          </div>
        ))}
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Price trend chart */}
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-1">{selectedCrop} Price Trend</h3>
          <p className="text-xs text-gray-400 mb-4">₹/quintal · Last 6 weeks · Your region</p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={TREND_DATA}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0fdf4" />
              <XAxis dataKey="week" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} domain={['auto', 'auto']} />
              <Tooltip
                formatter={v => [`₹${v.toLocaleString('en-IN')}`, 'Price']}
                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
              />
              <Line type="monotone" dataKey="price" stroke="#16a34a" strokeWidth={2.5}
                    dot={{ fill: '#16a34a', r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* AI Selling Strategy */}
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Store className="w-5 h-5 text-earth-500" />
            AI Selling Strategy
          </h3>

          <div className="space-y-3 mb-4">
            <div>
              <label className="label">Crop</label>
              <select value={selectedCrop} onChange={e => setSelectedCrop(e.target.value)} className="input">
                {COMMODITIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Quantity (quintals)</label>
                <input type="number" value={quantity} onChange={e => setQuantity(e.target.value)}
                       className="input" placeholder="e.g., 50" min="0" />
              </div>
              <div>
                <label className="label">Storage (months)</label>
                <select value={storage} onChange={e => setStorage(e.target.value)} className="input">
                  {['0','1','2','3','4','6'].map(m => <option key={m} value={m}>{m} months</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className="label">Financial Urgency</label>
              <select value={urgency} onChange={e => setUrgency(e.target.value)} className="input">
                <option value="low">Low — can wait for best price</option>
                <option value="medium">Medium — flexible</option>
                <option value="high">High — need cash soon</option>
              </select>
            </div>
          </div>

          <button onClick={getAdvice} disabled={isLoading}
                  className="btn-primary w-full flex items-center justify-center gap-2">
            {isLoading ? (
              <><Loader className="w-4 h-4 animate-spin" /> Analyzing market...</>
            ) : (
              <><TrendingUp className="w-4 h-4" /> Get Selling Strategy</>
            )}
          </button>

          {advice && (
            <div className="mt-4 p-4 bg-earth-50 rounded-xl border border-earth-200 text-sm text-earth-900 leading-relaxed animate-fade-slide">
              {advice.answer}
            </div>
          )}
        </div>
      </div>

      {/* Market comparison bar chart */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-1">Current Prices Comparison</h3>
        <p className="text-xs text-gray-400 mb-4">₹/quintal across major commodities</p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={priceEntries.map(([crop, d]) => ({ crop, price: d.current, msp: d.msp || 0 }))}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0fdf4" />
            <XAxis dataKey="crop" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={v => `₹${v.toLocaleString('en-IN')}`}
              contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
            />
            <Bar dataKey="price" fill="#16a34a" radius={[4,4,0,0]} name="Market Price" />
            <Bar dataKey="msp" fill="#86efac" radius={[4,4,0,0]} name="MSP" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
