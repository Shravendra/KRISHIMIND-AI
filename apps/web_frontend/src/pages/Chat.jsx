import { useState, useRef, useEffect, useCallback } from 'react'
import {
  Send, Paperclip, Mic, Camera, Leaf, Sprout,
  AlertTriangle, Droplets, TrendingUp, X, ChevronDown
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { chatService } from '../services/api'
import useAuthStore from '../store/authStore'

const QUICK_PROMPTS = [
  { icon: '🍂', text: 'My tomato leaves have yellow spots' },
  { icon: '💧', text: 'How much water does my wheat need?' },
  { icon: '🌤️', text: 'Weather risk for next week?' },
  { icon: '💰', text: 'Best time to sell onions?' },
  { icon: '🧪', text: 'NPK dose for cotton at flowering stage' },
  { icon: '🐛', text: 'White flies on my chilli crop' },
]

function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-slide">
      <div className="w-8 h-8 bg-leaf-600 rounded-full flex items-center justify-center text-white flex-shrink-0 self-end">
        <Sprout className="w-4 h-4" />
      </div>
      <div className="chat-bubble-ai flex items-center">
        <span className="loading-dots text-leaf-600">
          <span /><span /><span />
        </span>
      </div>
    </div>
  )
}

function ChatMessage({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} animate-fade-slide`}>
      {!isUser && (
        <div className="w-8 h-8 bg-leaf-600 rounded-full flex items-center justify-center
                        text-white flex-shrink-0 self-end shadow-sm">
          <Sprout className="w-4 h-4" />
        </div>
      )}

      <div className={isUser ? 'flex flex-col items-end' : 'flex flex-col items-start'}>
        {/* Image attachment */}
        {msg.images?.length > 0 && (
          <div className="flex gap-2 mb-2 flex-wrap justify-end">
            {msg.images.map((img, i) => (
              <img key={i} src={img} alt="crop" className="w-24 h-24 object-cover rounded-xl border-2 border-white shadow" />
            ))}
          </div>
        )}

        {/* Message bubble */}
        <div className={isUser ? 'chat-bubble-user' : 'chat-bubble-ai'}>
          {isUser ? (
            <p className="whitespace-pre-wrap">{msg.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none prose-headings:font-semibold">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Agent badges */}
        {msg.agents && msg.agents.length > 0 && (
          <div className="flex gap-1.5 mt-1.5 flex-wrap">
            {msg.agents.map(a => (
              <span key={a} className="badge badge-success text-[10px]">
                ✓ {a.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        )}

        {/* Recommendations */}
        {msg.recommendations?.length > 0 && (
          <div className="mt-3 p-3 bg-leaf-50 rounded-xl border border-leaf-200 max-w-sm">
            <p className="text-xs font-semibold text-leaf-800 mb-1.5">Recommended Actions</p>
            <ul className="space-y-1">
              {msg.recommendations.slice(0,4).map((r, i) => (
                <li key={i} className="text-xs text-leaf-700 flex gap-1.5">
                  <span className="text-leaf-500 shrink-0">{i+1}.</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Warnings */}
        {msg.warnings?.length > 0 && (
          <div className="mt-2 p-3 bg-earth-50 rounded-xl border border-earth-200 max-w-sm">
            {msg.warnings.map((w, i) => (
              <p key={i} className="text-xs text-earth-800 flex gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                {w}
              </p>
            ))}
          </div>
        )}

        {/* Follow-up */}
        {msg.follow_up && (
          <p className="mt-2 text-xs text-gray-500 italic max-w-sm">{msg.follow_up}</p>
        )}

        <p className="text-[10px] text-gray-400 mt-1">
          {new Date(msg.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>

      {isUser && (
        <div className="w-8 h-8 bg-earth-400 rounded-full flex items-center justify-center
                        text-white flex-shrink-0 self-end text-sm font-bold">
          {msg.userName?.[0] || 'F'}
        </div>
      )}
    </div>
  )
}

export default function Chat() {
  const { user } = useAuthStore()
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Namaste! 🌾 I'm **KrishiMind**, your personal farming AI assistant.\n\nI can help you with:\n- 🌿 **Crop disease diagnosis** (share photos!)\n- 🌤️ **Weather-based advisories**\n- 💰 **Market price insights**\n- 🧪 **Soil & fertilizer guidance**\n- 🌱 **Crop planning & rotation**\n\nWhat farming challenge can I help you with today?`,
      timestamp: Date.now(),
    }
  ])
  const [input, setInput] = useState('')
  const [images, setImages] = useState([])
  const [imageUrls, setImageUrls] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [crop, setCrop] = useState(user?.primary_crops?.[0] || '')
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files)
    files.forEach(file => {
      const url = URL.createObjectURL(file)
      setImageUrls(prev => [...prev, url])
      setImages(prev => [...prev, { url: file.name, caption: file.name }])
    })
  }

  const removeImage = (i) => {
    setImages(prev => prev.filter((_, idx) => idx !== i))
    setImageUrls(prev => prev.filter((_, idx) => idx !== i))
  }

  const sendMessage = useCallback(async (text = input) => {
    if (!text.trim() && images.length === 0) return
    setInput('')

    const userMsg = {
      role: 'user',
      content: text,
      images: imageUrls,
      userName: user?.name,
      timestamp: Date.now(),
    }
    setMessages(prev => [...prev, userMsg])
    setImages([])
    setImageUrls([])
    setIsLoading(true)

    try {
      const { data } = await chatService.sendMessage({
        message: text,
        farmer_id: user?.farmer_id || 'anonymous',
        crop: crop || undefined,
        conversation_id: conversationId,
        images: images,
        location: user?.location_coords,
        conversation_history: messages
          .filter(m => m.role !== 'assistant' || messages.indexOf(m) > 0)
          .map(m => ({ role: m.role, content: m.content }))
          .slice(-6),
      })

      setConversationId(data.conversation_id)

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        recommendations: data.recommendations,
        warnings: data.warnings,
        follow_up: data.follow_up_question,
        agents: data.agent_results?.filter(a => a.success).map(a => a.name),
        timestamp: Date.now(),
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '❌ I had trouble connecting to the server. Please check your internet connection and try again.',
        timestamp: Date.now(),
      }])
    } finally {
      setIsLoading(false)
    }
  }, [input, images, imageUrls, user, crop, conversationId, messages])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-2xl border border-leaf-100 shadow-card overflow-hidden">
      {/* Chat header */}
      <div className="px-5 py-4 border-b border-leaf-100 flex items-center justify-between bg-gradient-to-r from-leaf-50 to-white">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-leaf-600 rounded-full flex items-center justify-center">
            <Sprout className="w-4.5 h-4.5 text-white" />
          </div>
          <div>
            <p className="font-semibold text-gray-900 text-sm">KrishiMind Assistant</p>
            <p className="text-xs text-leaf-600 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-leaf-500 rounded-full inline-block animate-pulse" />
              Online · Powered by AI
            </p>
          </div>
        </div>
        {/* Crop selector */}
        <div className="flex items-center gap-2">
          <Leaf className="w-4 h-4 text-leaf-500" />
          <select
            value={crop}
            onChange={e => setCrop(e.target.value)}
            className="text-xs border border-leaf-200 rounded-lg px-2 py-1.5 bg-white text-gray-700 focus:ring-2 focus:ring-leaf-400"
          >
            <option value="">Any crop</option>
            {['Tomato', 'Wheat', 'Rice', 'Cotton', 'Soybean', 'Onion', 'Potato', 'Maize', 'Chilli'].map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 bg-gray-50/50">
        {messages.map((msg, i) => <ChatMessage key={i} msg={msg} />)}
        {isLoading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick prompts (show only if no messages besides welcome) */}
      {messages.length === 1 && !isLoading && (
        <div className="px-4 pb-2">
          <p className="text-xs text-gray-400 mb-2">Quick start:</p>
          <div className="flex flex-wrap gap-2">
            {QUICK_PROMPTS.map(({ icon, text }) => (
              <button
                key={text}
                onClick={() => sendMessage(text)}
                className="text-xs px-3 py-1.5 bg-white border border-leaf-200 rounded-full
                           hover:bg-leaf-50 hover:border-leaf-400 transition-colors text-gray-700"
              >
                {icon} {text}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Image preview */}
      {imageUrls.length > 0 && (
        <div className="px-4 py-2 flex gap-2 border-t border-gray-100">
          {imageUrls.map((url, i) => (
            <div key={i} className="relative">
              <img src={url} alt="" className="w-14 h-14 object-cover rounded-lg" />
              <button
                onClick={() => removeImage(i)}
                className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full
                           text-white flex items-center justify-center"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input area */}
      <div className="px-4 py-3 border-t border-leaf-100 bg-white">
        <div className="flex items-end gap-2">
          {/* Attach image */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2.5 rounded-xl hover:bg-leaf-50 text-gray-400 hover:text-leaf-600 transition-colors shrink-0"
            title="Upload crop photo"
          >
            <Camera className="w-5 h-5" />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleImageUpload}
            className="hidden"
          />

          {/* Text input */}
          <textarea
            ref={textareaRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about crop diseases, soil health, weather risks, market prices..."
            className="flex-1 resize-none border border-gray-200 rounded-xl px-4 py-3 text-sm
                       focus:outline-none focus:ring-2 focus:ring-leaf-400 focus:border-transparent
                       max-h-32 leading-relaxed"
            rows={1}
            style={{ minHeight: '44px' }}
          />

          {/* Send */}
          <button
            onClick={() => sendMessage()}
            disabled={isLoading || (!input.trim() && images.length === 0)}
            className="p-2.5 bg-leaf-600 text-white rounded-xl hover:bg-leaf-700
                       disabled:opacity-40 disabled:cursor-not-allowed transition-all
                       active:scale-95 shrink-0"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-[10px] text-gray-400 mt-1.5 text-center">
          Press Enter to send · Shift+Enter for new line · Upload photos for disease diagnosis
        </p>
      </div>
    </div>
  )
}
