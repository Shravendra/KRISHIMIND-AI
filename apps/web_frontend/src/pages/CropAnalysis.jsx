import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  Upload, Camera, Leaf, AlertTriangle, CheckCircle,
  XCircle, Info, ChevronDown, Loader, Microscope
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import api from '../services/api'
import useAuthStore from '../store/authStore'

const CROPS = ['Tomato', 'Wheat', 'Rice', 'Cotton', 'Soybean', 'Maize',
               'Potato', 'Onion', 'Chilli', 'Brinjal', 'Cucumber', 'Mango', 'Banana', 'Grapes']
const SEASONS = ['Kharif (Jun-Nov)', 'Rabi (Nov-Apr)', 'Zaid (Mar-Jun)']
const STAGES  = ['Seedling', 'Vegetative', 'Flowering', 'Fruiting/Pod filling', 'Maturity']

const SEVERITY_CONFIG = {
  low:      { color: 'bg-leaf-100 text-leaf-800 border-leaf-300', icon: CheckCircle, label: 'Low Risk' },
  medium:   { color: 'bg-earth-100 text-earth-800 border-earth-300', icon: Info, label: 'Moderate' },
  high:     { color: 'bg-orange-100 text-orange-800 border-orange-300', icon: AlertTriangle, label: 'High Risk' },
  critical: { color: 'bg-red-100 text-red-800 border-red-300', icon: XCircle, label: 'Critical' },
}

function ImageDropzone({ onFiles }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: acceptedFiles => onFiles(acceptedFiles),
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
    maxFiles: 5,
    maxSize: 10 * 1024 * 1024,
  })

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all
        ${isDragActive
          ? 'border-leaf-500 bg-leaf-50 scale-[1.01]'
          : 'border-gray-300 hover:border-leaf-400 hover:bg-leaf-50/50'
        }
      `}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-3">
        <div className="w-16 h-16 bg-leaf-100 rounded-full flex items-center justify-center">
          <Camera className="w-7 h-7 text-leaf-600" />
        </div>
        <div>
          <p className="font-semibold text-gray-800">
            {isDragActive ? 'Drop your crop photos here' : 'Upload crop photos'}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            Drag & drop or click · JPG, PNG, WEBP · Up to 5 photos · 10MB each
          </p>
        </div>
        <p className="text-xs text-leaf-600 bg-leaf-50 px-3 py-1.5 rounded-full border border-leaf-200">
          💡 Best results: close-up of leaves showing symptoms (both sides)
        </p>
      </div>
    </div>
  )
}

function ResultCard({ result }) {
  const severity = result.severity?.toLowerCase() || 'medium'
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.medium
  const Icon = config.icon

  return (
    <div className="space-y-4 animate-fade-slide">
      {/* Primary diagnosis */}
      <div className={`p-5 rounded-2xl border-2 ${config.color}`}>
        <div className="flex items-center gap-3 mb-2">
          <Icon className="w-6 h-6" />
          <div>
            <p className="font-bold text-lg">{result.primary_diagnosis || 'Analysis Complete'}</p>
            <p className="text-sm opacity-75">
              Confidence: {Math.round((result.confidence || 0) * 100)}% · {config.label}
            </p>
          </div>
        </div>
        {result.symptoms_observed && (
          <p className="text-sm mt-2 opacity-90">{result.symptoms_observed}</p>
        )}
      </div>

      {/* Differential diagnoses */}
      {result.differential_diagnoses?.length > 0 && (
        <div className="card">
          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Microscope className="w-4 h-4 text-gray-400" />
            Other Possibilities
          </h4>
          <div className="space-y-1.5">
            {result.differential_diagnoses.slice(0,3).map((d, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-gray-700">
                <span className="w-5 h-5 bg-gray-100 rounded text-xs flex items-center justify-center font-mono text-gray-500">
                  {i+1}
                </span>
                {typeof d === 'string' ? d : d.name || JSON.stringify(d)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Immediate actions */}
      {result.immediate_actions?.length > 0 && (
        <div className="card border-leaf-200">
          <h4 className="font-semibold text-gray-900 mb-3">⚡ Immediate Actions (24-48 hours)</h4>
          <ol className="space-y-2">
            {result.immediate_actions.map((action, i) => (
              <li key={i} className="flex gap-3 text-sm">
                <span className="w-6 h-6 bg-leaf-600 text-white rounded-full flex items-center justify-center text-xs font-bold shrink-0">
                  {i+1}
                </span>
                <span className="text-gray-700">{action}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Treatment protocol */}
      {result.treatment_protocol && (
        <div className="card">
          <h4 className="font-semibold text-gray-900 mb-2">💊 Treatment Protocol</h4>
          <p className="text-sm text-gray-700 leading-relaxed">{result.treatment_protocol}</p>
        </div>
      )}

      {/* Organic alternatives */}
      {result.organic_alternatives?.length > 0 && (
        <div className="card bg-leaf-50 border-leaf-200">
          <h4 className="font-semibold text-leaf-800 mb-2">🌿 Organic Alternatives</h4>
          <ul className="space-y-1">
            {result.organic_alternatives.map((alt, i) => (
              <li key={i} className="text-sm text-leaf-700 flex gap-2">
                <span>•</span><span>{alt}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Warnings */}
      {result.warnings?.length > 0 && (
        <div className="p-4 bg-earth-50 rounded-xl border border-earth-200">
          <h4 className="font-semibold text-earth-800 mb-2 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />Warnings
          </h4>
          {result.warnings.map((w, i) => (
            <p key={i} className="text-sm text-earth-700">{w}</p>
          ))}
        </div>
      )}

      {/* Follow up */}
      {result.follow_up && (
        <div className="p-4 bg-sky-50 rounded-xl border border-sky-200 text-sm text-sky-800">
          📅 <strong>Follow-up:</strong> {result.follow_up}
        </div>
      )}
    </div>
  )
}

export default function CropAnalysis() {
  const { user } = useAuthStore()
  const [files, setFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [crop, setCrop] = useState(user?.primary_crops?.[0] || '')
  const [season, setSeason] = useState('')
  const [stage, setStage] = useState('')
  const [description, setDescription] = useState('')
  const [result, setResult] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState(null)

  const handleFiles = useCallback((accepted) => {
    setFiles(prev => [...prev, ...accepted])
    accepted.forEach(f => {
      const url = URL.createObjectURL(f)
      setPreviews(prev => [...prev, url])
    })
  }, [])

  const removeFile = (i) => {
    setFiles(prev => prev.filter((_, idx) => idx !== i))
    setPreviews(prev => prev.filter((_, idx) => idx !== i))
  }

  // ─── Helper: File → base64 string ────────────────────────────────────────────
  const fileToBase64 = (file) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result.split(',')[1]) // strip data:...;base64,
      reader.onerror = () => reject(new Error('Failed to read file'))
      reader.readAsDataURL(file)
    })

  // ─── Main analyze handler ─────────────────────────────────────────────────────
  const analyze = async () => {
    if (files.length === 0 && !description.trim()) return
    setIsAnalyzing(true)
    setResult(null)
    setError(null)

    try {
      // Bug 1 fix: convert files to base64 strings
      const base64Images = await Promise.all(files.map(fileToBase64))

      const { data } = await api.post('/chat', {
        message: description || 'Diagnose the crop issue visible in the uploaded images.',
        crop: crop || undefined,
        season: season.split(' ')[0]?.toLowerCase() || undefined,
        // Bug 2 fix: correct key is `history`, not `conversation_history`
        history: [],
        // Bug 3 fix: pass growth_stage through farm_context
        farm_context: {
          growth_stage: stage?.toLowerCase() || undefined,
        },
        // Bug 1 fix: send base64 strings, not { url: f.name } objects
        images: base64Images,
      })

      // Bug 4 fix: try both agent names, fall back gracefully to an empty object
      const diseaseResult =
        data.agent_results?.find(r => r.name === 'disease_detection' && r.success)?.data ||
        data.agent_results?.find(r => r.name === 'image_analysis' && r.success)?.data ||
        {}

      // Bug 5 fix: merge warnings from both the agent result and the top-level response
      const mergedWarnings = [
        ...(Array.isArray(diseaseResult.warnings) ? diseaseResult.warnings : []),
        ...(Array.isArray(data.warnings) ? data.warnings : []),
      ].filter((v, i, a) => a.indexOf(v) === i) // deduplicate

      setResult({
        ...diseaseResult,
        answer: data.answer,
        recommendations: data.recommendations ?? diseaseResult.recommendations ?? [],
        warnings: mergedWarnings,
        follow_up: diseaseResult.follow_up || data.follow_up_question,
      })
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-slide">
      {/* Left: Input */}
      <div className="space-y-5">
        <div>
          <h2 className="section-title">Crop Disease Analyzer</h2>
          <p className="section-subtitle">Upload photos or describe symptoms for AI diagnosis</p>
        </div>

        {/* Context selectors */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Crop', value: crop, setValue: setCrop, options: CROPS },
            { label: 'Season', value: season, setValue: setSeason, options: SEASONS },
            { label: 'Growth Stage', value: stage, setValue: setStage, options: STAGES },
          ].map(({ label, value, setValue, options }) => (
            <div key={label}>
              <label className="label">{label}</label>
              <select value={value} onChange={e => setValue(e.target.value)} className="input text-sm">
                <option value="">Select {label.toLowerCase()}</option>
                {options.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            </div>
          ))}
        </div>

        {/* Image upload */}
        <ImageDropzone onFiles={handleFiles} />

        {/* Image previews */}
        {previews.length > 0 && (
          <div className="flex gap-3 flex-wrap">
            {previews.map((url, i) => (
              <div key={i} className="relative group">
                <img src={url} alt="" className="w-20 h-20 object-cover rounded-xl border-2 border-leaf-200" />
                <button
                  onClick={() => removeFile(i)}
                  className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full
                             text-white opacity-0 group-hover:opacity-100 transition-opacity
                             flex items-center justify-center"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Description */}
        <div>
          <label className="label">Describe the symptoms (optional)</label>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            className="input min-h-[100px] resize-none"
            placeholder="e.g., Yellow spots on leaves starting from edges, some browning, affecting lower leaves first. Started 5 days ago..."
          />
        </div>

        {/* Analyze button */}
        <button
          onClick={analyze}
          disabled={isAnalyzing || (files.length === 0 && !description.trim())}
          className="btn-primary w-full flex items-center justify-center gap-2 py-4 text-base"
        >
          {isAnalyzing ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Analyzing with AI...
            </>
          ) : (
            <>
              <Microscope className="w-5 h-5" />
              Analyze Crop Health
            </>
          )}
        </button>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Tips */}
        <div className="card bg-leaf-50 border-leaf-200">
          <p className="text-xs font-semibold text-leaf-800 mb-2">📸 Photography Tips for Better Diagnosis</p>
          <ul className="text-xs text-leaf-700 space-y-1">
            <li>• Take photos in natural daylight (not direct sunlight)</li>
            <li>• Include close-up AND wide-angle shots</li>
            <li>• Photograph both top and underside of leaves</li>
            <li>• Include healthy leaves for comparison</li>
            <li>• Capture stem, roots if wilting is observed</li>
          </ul>
        </div>
      </div>

      {/* Right: Results */}
      <div>
        {isAnalyzing && (
          <div className="card h-64 flex flex-col items-center justify-center gap-4 animate-fade-slide">
            <div className="w-16 h-16 border-4 border-leaf-200 border-t-leaf-600 rounded-full animate-spin" />
            <div className="text-center">
              <p className="font-semibold text-gray-900">Analyzing your crop...</p>
              <p className="text-sm text-gray-500 mt-1">Running disease detection & advisory agents</p>
            </div>
          </div>
        )}

        {!isAnalyzing && !result && (
          <div className="card h-64 flex flex-col items-center justify-center text-center">
            <Leaf className="w-12 h-12 text-leaf-300 mb-3" />
            <p className="font-semibold text-gray-600">Analysis results appear here</p>
            <p className="text-sm text-gray-400 mt-1">Upload photos or describe symptoms to begin</p>
          </div>
        )}

        {result && !isAnalyzing && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-leaf-600" />
              Diagnosis Report
            </h3>
            {result.answer && (
              <div className="card mb-4 bg-leaf-50 border-leaf-200">
                <p className="text-sm font-semibold text-leaf-800 mb-1">AI Advisory</p>
                <div className="prose prose-sm max-w-none text-leaf-900">
                  <ReactMarkdown>{result.answer}</ReactMarkdown>
                </div>
              </div>
            )}
            <ResultCard result={result} />
          </div>
        )}
      </div>
    </div>
  )
}
