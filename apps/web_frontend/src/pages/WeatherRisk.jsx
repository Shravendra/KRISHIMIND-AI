import { useState } from "react";
import {
  Cloud, CloudRain, Sun, Wind, Droplets,
  AlertTriangle, CheckCircle, Thermometer, Eye
} from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { agentService } from "../services/api";

const RISK_COLORS = {
  low: "bg-green-100 text-green-800 border-green-200",
  moderate: "bg-yellow-100 text-yellow-800 border-yellow-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  critical: "bg-red-100 text-red-800 border-red-200",
};

const RISK_BAR_COLOR = { low: "#22c55e", moderate: "#eab308", high: "#f97316", critical: "#ef4444" };

const WEATHER_ICONS = { Clear: Sun, Rain: CloudRain, Clouds: Cloud, Wind };

export default function WeatherRisk() {
  const [form, setForm] = useState({
    location: "",
    cropType: "",
    growthStage: "vegetative",
    irrigationType: "rainfed",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAssess = async () => {
    if (!form.location) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await agentService.assessWeatherRisk(form);
      setResult(res.data);
    } catch {
      setResult({ error: "Unable to fetch weather risk data. Please try again." });
    }
    setLoading(false);
  };

  const overallRisk = result?.overall_risk || "low";
  const riskColor = RISK_COLORS[overallRisk] || RISK_COLORS.low;

  // Build 7-day forecast chart data
  const forecastData = (result?.forecast_7day || []).map((d, i) => ({
    day: d.date || `Day ${i + 1}`,
    rain: d.rainfall_mm || 0,
    tempMax: d.temp_max || 0,
    tempMin: d.temp_min || 0,
    humidity: d.humidity || 0,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-sky-100 rounded-xl flex items-center justify-center">
          <Cloud className="w-5 h-5 text-sky-600" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-gray-900">Weather Risk</h1>
          <p className="text-sm text-gray-500">7-day forecast, irrigation planning & spray windows</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Form */}
        <div className="card lg:col-span-1 h-fit">
          <h2 className="font-semibold text-gray-800 mb-4">Location & Crop</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Location *</label>
              <input
                type="text"
                placeholder="City, District or Coordinates"
                value={form.location}
                onChange={e => setForm(p => ({ ...p, location: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Crop Type</label>
              <input
                type="text"
                placeholder="e.g. Paddy, Wheat, Cotton"
                value={form.cropType}
                onChange={e => setForm(p => ({ ...p, cropType: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Growth Stage</label>
              <select
                value={form.growthStage}
                onChange={e => setForm(p => ({ ...p, growthStage: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
              >
                {["seedling", "vegetative", "flowering", "fruiting", "maturity", "post-harvest"].map(s => (
                  <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Irrigation Type</label>
              <select
                value={form.irrigationType}
                onChange={e => setForm(p => ({ ...p, irrigationType: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
              >
                {[["rainfed", "Rainfed"], ["drip", "Drip"], ["flood", "Flood"], ["sprinkler", "Sprinkler"]].map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </div>
            <button onClick={handleAssess} disabled={loading || !form.location} className="btn-primary w-full flex items-center justify-center gap-2">
              {loading ? <span className="loading-dots" /> : <><Cloud className="w-4 h-4" /> Get Weather Risk</>}
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="lg:col-span-2 space-y-4">
          {!result && !loading && (
            <div className="card flex flex-col items-center justify-center py-16 text-center">
              <CloudRain className="w-12 h-12 text-gray-200 mb-3" />
              <p className="text-gray-400 text-sm">Enter your location to get<br />weather-based farming advice</p>
            </div>
          )}

          {loading && (
            <div className="card flex flex-col items-center justify-center py-16">
              <div className="w-8 h-8 border-4 border-sky-200 border-t-sky-600 rounded-full animate-spin mb-3" />
              <p className="text-sm text-gray-500">Fetching weather data…</p>
            </div>
          )}

          {result?.error && (
            <div className="card border-red-200 bg-red-50">
              <div className="flex gap-2 text-red-700">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">{result.error}</p>
              </div>
            </div>
          )}

          {result && !result.error && (
            <>
              {/* Overall Risk Badge */}
              <div className={`card border ${riskColor}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide opacity-70">Overall Weather Risk</p>
                    <p className="text-2xl font-bold capitalize mt-1">{overallRisk}</p>
                    {result.risk_summary && <p className="text-sm mt-1 opacity-80">{result.risk_summary}</p>}
                  </div>
                  <AlertTriangle className="w-10 h-10 opacity-30" />
                </div>
              </div>

              {/* Current Conditions */}
              {result.current_conditions && (
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">Current Conditions</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {[
                      { icon: Thermometer, label: "Temperature", value: result.current_conditions.temperature, unit: "°C" },
                      { icon: Droplets, label: "Humidity", value: result.current_conditions.humidity, unit: "%" },
                      { icon: Wind, label: "Wind Speed", value: result.current_conditions.wind_speed, unit: "km/h" },
                      { icon: Eye, label: "Condition", value: result.current_conditions.description, unit: "" },
                    ].map(({ icon: Icon, label, value, unit }) => (
                      <div key={label} className="bg-gray-50 rounded-xl p-3 text-center">
                        <Icon className="w-5 h-5 text-sky-500 mx-auto mb-1" />
                        <p className="text-xs text-gray-500">{label}</p>
                        <p className="text-sm font-bold text-gray-800">{value ?? "—"}{unit}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 7-day forecast chart */}
              {forecastData.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">7-Day Rainfall Forecast (mm)</h3>
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={forecastData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip formatter={(v) => [`${v} mm`, "Rainfall"]} />
                      <Bar dataKey="rain" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Spray Window */}
              {result.spray_windows && (
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">🌿 Spray Windows</h3>
                  {result.spray_windows.map((w, i) => (
                    <div key={i} className={`flex items-center justify-between py-2 px-3 rounded-lg mb-2 ${w.suitable ? "bg-green-50" : "bg-red-50"}`}>
                      <span className="text-sm text-gray-700">{w.date || w.period}</span>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${w.suitable ? "bg-green-200 text-green-800" : "bg-red-200 text-red-800"}`}>
                        {w.suitable ? "✓ Suitable" : "✗ Avoid"}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Advisory */}
              {result.recommendations?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">Farming Advisory</h3>
                  <ul className="space-y-2">
                    {result.recommendations.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                        <CheckCircle className="w-4 h-4 text-leaf-500 flex-shrink-0 mt-0.5" />
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
