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
      const chatResponse = res.data;   // this is ChatResponse

      // The soil score lives inside agent_results, NOT at the top level
      const soilAgentResult = chatResponse.agent_results?.find(
        r => r.name === 'soil_agent' && r.success
      );
      const soilData = soilAgentResult?.data || {};

      setResult({
        type: "soil",
        data: {
          ...soilData,
          // Attach the synthesized AI answer and top-level recommendations
          answer:          chatResponse.answer,
          recommendations: chatResponse.recommendations ?? soilData.recommendations ?? [],
          warnings: [
            ...(Array.isArray(soilData.warnings)            ? soilData.warnings            : []),
            ...(Array.isArray(chatResponse.warnings)        ? chatResponse.warnings        : []),
          ].filter((v, i, a) => a.indexOf(v) === i),
          follow_up: soilData.follow_up || chatResponse.follow_up_question,
        },
      });
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
      const chatResponse = res.data;   // ChatResponse — score is NOT here at root level

      // Extract fertilizer agent data from agent_results
      const fertAgentResult = chatResponse.agent_results?.find(
        r => r.name === 'fertilizer_agent' && r.success
      );
      const fertData = fertAgentResult?.data || {};

      setResult({
        type: "fertilizer",
        data: {
          ...fertData,
          answer:          chatResponse.answer,
          recommendations: chatResponse.recommendations?.length
                             ? chatResponse.recommendations
                             : (fertData.important_tips ?? []),
          warnings: [
            ...(Array.isArray(fertData.warnings)         ? fertData.warnings         : []),
            ...(Array.isArray(chatResponse.warnings)     ? chatResponse.warnings     : []),
          ].filter((v, i, a) => a.indexOf(v) === i),
          follow_up: fertData.follow_up || chatResponse.follow_up_question,
        },
      });
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
                {result.data.summary && (
                  <p className="text-sm text-gray-600 mt-2">{result.data.summary}</p>
                )}
              </div>

              {/* ── NEW: AI Suggestion block ───────────────────────────── */}
              {result.data.answer && (
                <div className="card border-leaf-200 bg-leaf-50">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">🤖</span>
                    <h3 className="font-semibold text-leaf-800">AI Fertility Suggestions</h3>
                  </div>
                  <div className="text-sm text-leaf-900 leading-relaxed whitespace-pre-line">
                    {result.data.answer}
                  </div>
                  {result.data.follow_up && (
                    <p className="mt-3 text-xs text-leaf-700 italic border-t border-leaf-200 pt-2">
                      💡 {result.data.follow_up}
                    </p>
                  )}
                </div>
              )}

              {/* Recommendations */}
              {result.data.recommendations?.length > 0 && (
                <div className="card">
                  <h4 className="font-semibold text-gray-800 mb-2">📋 Recommendations</h4>
                  <ul className="space-y-1">
                    {result.data.recommendations.map((rec, i) => (
                      <li key={i} className="flex gap-2 text-sm text-gray-700">
                        <CheckCircle className="w-4 h-4 text-leaf-500 shrink-0 mt-0.5" />
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Warnings */}
              {result.data.warnings?.length > 0 && (
                <div className="card border-earth-200 bg-earth-50">
                  <h4 className="font-semibold text-earth-800 mb-2 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Warnings
                  </h4>
                  {result.data.warnings.map((w, i) => (
                    <p key={i} className="text-sm text-earth-700">{w}</p>
                  ))}
                </div>
              )}

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
              {/* AI Summary */}
              {result.data.answer && (
                <div className="card border-leaf-200 bg-leaf-50">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">🤖</span>
                    <h3 className="font-semibold text-leaf-800">AI Fertilizer Advisory</h3>
                  </div>
                  <p className="text-sm text-leaf-900 leading-relaxed whitespace-pre-line">
                    {result.data.answer}
                  </p>
                  {result.data.follow_up && (
                    <p className="mt-3 text-xs text-leaf-700 italic border-t border-leaf-200 pt-2">
                      💡 {result.data.follow_up}
                    </p>
                  )}
                </div>
              )}

              {/* NPK Requirement */}
              {result.data.total_npk_requirement && (
                <div className="card">
                  <h4 className="font-semibold text-gray-800 mb-3">🧪 Total NPK Requirement</h4>
                  <div className="grid grid-cols-3 gap-3">
                    {Object.entries(result.data.total_npk_requirement).map(([nutrient, kg]) => (
                      <div key={nutrient} className="bg-leaf-50 rounded-xl p-3 text-center">
                        <p className="text-xl font-bold text-leaf-700">{kg}</p>
                        <p className="text-xs text-gray-500 mt-1">kg/acre</p>
                        <p className="text-sm font-semibold text-gray-700">{nutrient}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Cost & Yield Summary */}
              {(result.data.total_fertilizer_cost_inr_per_acre ||
                result.data.expected_yield_increase_percent) && (
                <div className="grid grid-cols-2 gap-3">
                  {result.data.total_fertilizer_cost_inr_per_acre && (
                    <div className="card text-center bg-earth-50 border-earth-200">
                      <p className="text-2xl font-bold text-earth-700">
                        ₹{result.data.total_fertilizer_cost_inr_per_acre.toLocaleString('en-IN')}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">Estimated cost / acre</p>
                    </div>
                  )}
                  {result.data.expected_yield_increase_percent && (
                    <div className="card text-center bg-leaf-50 border-leaf-200">
                      <p className="text-2xl font-bold text-leaf-700">
                        +{result.data.expected_yield_increase_percent}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">Expected yield increase</p>
                    </div>
                  )}
                </div>
              )}

              {/* Fertilizer Schedule */}
              {result.data.fertilizer_schedule?.length > 0 && (
                <div className="card">
                  <h4 className="font-semibold text-gray-800 mb-3">📅 Application Schedule</h4>
                  <div className="space-y-4">
                    {result.data.fertilizer_schedule.map((stage, i) => (
                      <div key={i} className="border border-gray-100 rounded-xl p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-sm text-gray-800 capitalize">
                            {stage.stage}
                          </span>
                          <span className="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
                            {stage.timing}
                          </span>
                        </div>
                        <div className="space-y-1">
                          {stage.products?.map((product, j) => (
                            <div key={j} className="flex items-start justify-between text-xs gap-2">
                              <div>
                                <span className="font-medium text-gray-700">{product.name}</span>
                                <span className="text-gray-400 ml-1">— {product.method}</span>
                                {product.notes && (
                                  <p className="text-gray-400 mt-0.5">{product.notes}</p>
                                )}
                              </div>
                              <div className="text-right shrink-0">
                                <p className="text-leaf-700 font-semibold">
                                  {product.quantity_kg_per_acre} kg/acre
                                </p>
                                {product.cost_per_acre_inr && (
                                  <p className="text-gray-400">
                                    ₹{product.cost_per_acre_inr}
                                  </p>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Bio-fertilizer Package */}
              {result.data.bio_fertilizer_package?.length > 0 && (
                <div className="card bg-leaf-50 border-leaf-200">
                  <h4 className="font-semibold text-leaf-800 mb-2">🌿 Bio-Fertilizer Package</h4>
                  <div className="space-y-2">
                    {result.data.bio_fertilizer_package.map((bio, i) => (
                      <div key={i} className="text-sm text-leaf-800">
                        <span className="font-medium">{bio.name}</span>
                        {bio.dose && <span className="text-leaf-600"> — {bio.dose}</span>}
                        {bio.benefit && (
                          <p className="text-xs text-leaf-600 mt-0.5">{bio.benefit}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations & Dos/Don'ts */}
              {(result.data.recommendations?.length > 0 ||
                result.data.dos_and_donts?.length > 0) && (
                <div className="card">
                  <h4 className="font-semibold text-gray-800 mb-2">📋 Tips & Best Practices</h4>
                  <ul className="space-y-1">
                    {[
                      ...(result.data.recommendations || []),
                      ...(result.data.dos_and_donts || []),
                    ].map((tip, i) => (
                      <li key={i} className="flex gap-2 text-sm text-gray-700">
                        <CheckCircle className="w-4 h-4 text-leaf-500 shrink-0 mt-0.5" />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Warnings */}
              {result.data.warnings?.length > 0 && (
                <div className="card border-earth-200 bg-earth-50">
                  <h4 className="font-semibold text-earth-800 mb-2 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Warnings
                  </h4>
                  {result.data.warnings.map((w, i) => (
                    <p key={i} className="text-sm text-earth-700">{w}</p>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
