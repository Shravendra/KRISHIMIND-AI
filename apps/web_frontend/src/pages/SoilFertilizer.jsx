import { useState } from "react";
import {
  FlaskConical, Leaf, TrendingUp, AlertTriangle,
  CheckCircle, ChevronDown, ChevronUp, Send
} from "lucide-react";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
         BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { agentService } from "../services/api";

const SOIL_TYPES = ["Sandy", "Loamy", "Clay", "Silty", "Peaty", "Chalky", "Loamy Sand"];

const NPK_DEFAULTS = { nitrogen: "", phosphorus: "", potassium: "", pH: "", ec: "" };

const HEALTH_COLOR = { excellent: "text-green-600", good: "text-leaf-600", fair: "text-yellow-600", poor: "text-red-600" };

export default function SoilFertilizer() {
  const [tab, setTab] = useState("soil"); // "soil" | "fertilizer"
  const [soilForm, setSoilForm] = useState({ ...NPK_DEFAULTS, soilType: "Loamy", cropType: "" });
  const [fertForm, setFertForm] = useState({ cropType: "", growthStage: "vegetative", farmSize: "", soilType: "Loamy", budget: "medium", organic: false });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const handleSoilAnalysis = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await agentService.analyzeSoil(soilForm);
      setResult({ type: "soil", data: res.data });
    } catch {
      setResult({ type: "error", message: "Analysis failed. Please check your inputs and try again." });
    }
    setLoading(false);
  };

  const handleFertilizerOptimize = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await agentService.optimizeFertilizer(fertForm);
      setResult({ type: "fertilizer", data: res.data });
    } catch {
      setResult({ type: "error", message: "Optimization failed. Please try again." });
    }
    setLoading(false);
  };

  // Build radar chart data from soil nutrients
  const radarData = result?.type === "soil" && result.data?.nutrient_status
    ? Object.entries(result.data.nutrient_status).map(([k, v]) => ({
        subject: k.charAt(0).toUpperCase() + k.slice(1),
        value: typeof v === "number" ? Math.min(v, 100) : 50,
        fullMark: 100,
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-earth-100 rounded-xl flex items-center justify-center">
          <FlaskConical className="w-5 h-5 text-earth-600" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-gray-900">Soil & Fertilizer</h1>
          <p className="text-sm text-gray-500">Analyse soil health and optimise fertilizer schedules</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl w-fit">
        {[
          { id: "soil", label: "Soil Analysis", icon: Leaf },
          { id: "fertilizer", label: "Fertilizer Planner", icon: TrendingUp },
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => { setTab(id); setResult(null); }}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === id ? "bg-white text-leaf-700 shadow-sm" : "text-gray-500 hover:text-gray-700"
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Panel */}
        <div className="card">
          {tab === "soil" ? (
            <>
              <h2 className="font-semibold text-gray-800 mb-4">Enter Soil Test Results</h2>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { key: "nitrogen", label: "Nitrogen (N)", unit: "kg/ha" },
                    { key: "phosphorus", label: "Phosphorus (P)", unit: "kg/ha" },
                    { key: "potassium", label: "Potassium (K)", unit: "kg/ha" },
                    { key: "pH", label: "Soil pH", unit: "6.0–8.5" },
                    { key: "ec", label: "EC", unit: "dS/m" },
                  ].map(({ key, label, unit }) => (
                    <div key={key}>
                      <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
                      <input
                        type="number"
                        placeholder={unit}
                        value={soilForm[key]}
                        onChange={e => setSoilForm(p => ({ ...p, [key]: e.target.value }))}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
                      />
                    </div>
                  ))}
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Soil Type</label>
                    <select
                      value={soilForm.soilType}
                      onChange={e => setSoilForm(p => ({ ...p, soilType: e.target.value }))}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
                    >
                      {SOIL_TYPES.map(s => <option key={s}>{s}</option>)}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Intended Crop</label>
                  <input
                    type="text"
                    placeholder="e.g. Rice, Wheat, Tomato"
                    value={soilForm.cropType}
                    onChange={e => setSoilForm(p => ({ ...p, cropType: e.target.value }))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
                  />
                </div>
                <button onClick={handleSoilAnalysis} disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
                  {loading ? <span className="loading-dots" /> : <><FlaskConical className="w-4 h-4" /> Analyse Soil</>}
                </button>
              </div>
            </>
          ) : (
            <>
              <h2 className="font-semibold text-gray-800 mb-4">Fertilizer Planner</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Crop Type *</label>
                  <input
                    type="text"
                    placeholder="e.g. Paddy, Sugarcane"
                    value={fertForm.cropType}
                    onChange={e => setFertForm(p => ({ ...p, cropType: e.target.value }))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Growth Stage</label>
                    <select
                      value={fertForm.growthStage}
                      onChange={e => setFertForm(p => ({ ...p, growthStage: e.target.value }))}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
                    >
                      {["seedling", "vegetative", "flowering", "fruiting", "maturity"].map(s => (
                        <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Farm Size (acres)</label>
                    <input
                      type="number"
                      placeholder="e.g. 2.5"
                      value={fertForm.farmSize}
                      onChange={e => setFertForm(p => ({ ...p, farmSize: e.target.value }))}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Soil Type</label>
                    <select
                      value={fertForm.soilType}
                      onChange={e => setFertForm(p => ({ ...p, soilType: e.target.value }))}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
                    >
                      {SOIL_TYPES.map(s => <option key={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">Budget</label>
                    <select
                      value={fertForm.budget}
                      onChange={e => setFertForm(p => ({ ...p, budget: e.target.value }))}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
                    >
                      <option value="low">Low (focus on essential)</option>
                      <option value="medium">Medium (balanced)</option>
                      <option value="high">High (optimal yield)</option>
                    </select>
                  </div>
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={fertForm.organic}
                    onChange={e => setFertForm(p => ({ ...p, organic: e.target.checked }))}
                    className="w-4 h-4 text-leaf-600 rounded"
                  />
                  <span className="text-sm text-gray-700">Prefer organic / bio-fertilizers</span>
                </label>
                <button onClick={handleFertilizerOptimize} disabled={loading || !fertForm.cropType} className="btn-primary w-full flex items-center justify-center gap-2">
                  {loading ? <span className="loading-dots" /> : <><TrendingUp className="w-4 h-4" /> Generate Schedule</>}
                </button>
              </div>
            </>
          )}
        </div>

        {/* Results Panel */}
        <div className="space-y-4">
          {!result && !loading && (
            <div className="card flex flex-col items-center justify-center py-16 text-center">
              <FlaskConical className="w-12 h-12 text-gray-200 mb-3" />
              <p className="text-gray-400 text-sm">Enter your data and run the analysis<br />to see AI-powered recommendations</p>
            </div>
          )}

          {loading && (
            <div className="card flex flex-col items-center justify-center py-16">
              <div className="w-8 h-8 border-4 border-leaf-200 border-t-leaf-600 rounded-full animate-spin mb-3" />
              <p className="text-sm text-gray-500">Analysing with AI…</p>
            </div>
          )}

          {result?.type === "error" && (
            <div className="card border-red-200 bg-red-50">
              <div className="flex gap-2 text-red-700">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">{result.message}</p>
              </div>
            </div>
          )}

          {result?.type === "soil" && result.data && (
            <>
              {/* Health Score */}
              <div className="card">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-800">Soil Health Score</h3>
                  <span className={`text-2xl font-bold ${HEALTH_COLOR[result.data.health_rating] || "text-gray-600"}`}>
                    {result.data.soil_health_score ?? "—"}/100
                  </span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-3 mb-2">
                  <div
                    className="bg-leaf-500 h-3 rounded-full transition-all"
                    style={{ width: `${result.data.soil_health_score ?? 0}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 capitalize">{result.data.health_rating} condition</p>
              </div>

              {/* Radar chart */}
              {radarData.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">Nutrient Balance</h3>
                  <ResponsiveContainer width="100%" height={220}>
                    <RadarChart data={radarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12 }} />
                      <Radar dataKey="value" stroke="#4a7c59" fill="#4a7c59" fillOpacity={0.25} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Recommendations */}
              {result.data.amendments?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">Recommended Amendments</h3>
                  <ul className="space-y-2">
                    {result.data.amendments.map((a, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                        <CheckCircle className="w-4 h-4 text-leaf-500 flex-shrink-0 mt-0.5" />
                        {a}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}

          {result?.type === "fertilizer" && result.data && (
            <>
              <div className="card">
                <h3 className="font-semibold text-gray-800 mb-3">Fertilizer Schedule</h3>
                {result.data.schedule?.map((phase, i) => (
                  <div key={i} className="border border-gray-100 rounded-lg p-3 mb-2">
                    <p className="text-sm font-medium text-gray-800">{phase.phase || phase.timing}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{phase.application || phase.description}</p>
                    {phase.products?.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {phase.products.map((p, j) => (
                          <li key={j} className="text-xs text-leaf-700 bg-leaf-50 rounded px-2 py-0.5 inline-block mr-1">{p}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
              {result.data.estimated_cost && (
                <div className="card bg-earth-50 border-earth-200">
                  <p className="text-sm font-medium text-earth-800">Estimated Cost</p>
                  <p className="text-xl font-bold text-earth-600 mt-1">{result.data.estimated_cost}</p>
                  {result.data.expected_yield_increase && (
                    <p className="text-xs text-earth-600 mt-1">Expected yield increase: {result.data.expected_yield_increase}</p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
