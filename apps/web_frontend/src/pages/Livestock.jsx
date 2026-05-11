import { useState } from "react";
import { Heart, AlertTriangle, CheckCircle, Phone, Pill, Leaf } from "lucide-react";
import { agentService } from "../services/api";

const ANIMALS = ["Cattle", "Buffalo", "Goat", "Sheep", "Poultry", "Pig", "Other"];
const COMMON_SYMPTOMS = [
  "Loss of appetite", "Fever", "Diarrhoea", "Coughing", "Nasal discharge",
  "Limping/lameness", "Swollen joints", "Reduced milk", "Skin lesions",
  "Weight loss", "Lethargy", "Eye discharge", "Abdominal bloat",
];

const CONDITION_STYLE = {
  healthy: "bg-green-50 border-green-200 text-green-800",
  mild_issue: "bg-yellow-50 border-yellow-200 text-yellow-800",
  moderate_issue: "bg-orange-50 border-orange-200 text-orange-800",
  serious: "bg-red-50 border-red-200 text-red-800",
  critical: "bg-red-100 border-red-300 text-red-900",
};

export default function Livestock() {
  const [form, setForm] = useState({
    animalType: "Cattle",
    query: "",
    symptoms: [],
    animalCount: "",
    location: "",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const toggleSymptom = (s) =>
    setForm(p => ({
      ...p,
      symptoms: p.symptoms.includes(s) ? p.symptoms.filter(x => x !== s) : [...p.symptoms, s],
    }));

  const handleAssess = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await agentService.assessLivestockHealth(form);
      setResult(res.data);
    } catch {
      setResult({ error: "Assessment failed. Please check inputs and try again." });
    }
    setLoading(false);
  };

  const conditionStyle = CONDITION_STYLE[result?.condition_assessment] || CONDITION_STYLE.mild_issue;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
          <Heart className="w-5 h-5 text-amber-600" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-gray-900">Livestock Health</h1>
          <p className="text-sm text-gray-500">AI-powered veterinary guidance for your animals</p>
        </div>
      </div>

      {/* Emergency banner */}
      <div className="bg-red-50 border border-red-200 rounded-xl p-3 flex items-center gap-3">
        <Phone className="w-5 h-5 text-red-600 flex-shrink-0" />
        <p className="text-sm text-red-700">
          <span className="font-semibold">Emergency?</span> Call the free Livestock Helpline:{" "}
          <a href="tel:1962" className="font-bold underline">1962</a> — available 24×7
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input */}
        <div className="card space-y-4">
          <h2 className="font-semibold text-gray-800">Describe the Problem</h2>

          {/* Animal type */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">Animal Type</label>
            <div className="flex flex-wrap gap-2">
              {ANIMALS.map(a => (
                <button
                  key={a}
                  onClick={() => setForm(p => ({ ...p, animalType: a }))}
                  className={`px-3 py-1.5 rounded-full text-sm border transition-all ${
                    form.animalType === a
                      ? "bg-amber-500 text-white border-amber-500"
                      : "border-gray-200 text-gray-600 hover:border-amber-300"
                  }`}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>

          {/* Symptoms */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">Observed Symptoms</label>
            <div className="flex flex-wrap gap-2">
              {COMMON_SYMPTOMS.map(s => (
                <button
                  key={s}
                  onClick={() => toggleSymptom(s)}
                  className={`px-2.5 py-1 rounded-full text-xs border transition-all ${
                    form.symptoms.includes(s)
                      ? "bg-leaf-100 text-leaf-700 border-leaf-300"
                      : "border-gray-200 text-gray-500 hover:border-gray-300"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Additional Details</label>
            <textarea
              rows={4}
              placeholder="Describe the symptoms, duration, how many animals are affected, any recent changes in feed or environment…"
              value={form.query}
              onChange={e => setForm(p => ({ ...p, query: e.target.value }))}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-amber-400"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Number of Animals</label>
              <input
                type="number"
                placeholder="e.g. 5"
                value={form.animalCount}
                onChange={e => setForm(p => ({ ...p, animalCount: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Location</label>
              <input
                type="text"
                placeholder="District / State"
                value={form.location}
                onChange={e => setForm(p => ({ ...p, location: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
              />
            </div>
          </div>

          <button
            onClick={handleAssess}
            disabled={loading || (!form.query && form.symptoms.length === 0)}
            className="btn-primary w-full flex items-center justify-center gap-2 !bg-amber-500 hover:!bg-amber-600"
          >
            {loading ? <span className="loading-dots" /> : <><Heart className="w-4 h-4" /> Get Veterinary Advice</>}
          </button>
        </div>

        {/* Results */}
        <div className="space-y-4">
          {!result && !loading && (
            <div className="card flex flex-col items-center justify-center py-16 text-center">
              <Heart className="w-12 h-12 text-gray-200 mb-3" />
              <p className="text-gray-400 text-sm">Describe your animal's symptoms<br />for AI-powered veterinary guidance</p>
            </div>
          )}

          {loading && (
            <div className="card flex flex-col items-center justify-center py-16">
              <div className="w-8 h-8 border-4 border-amber-200 border-t-amber-500 rounded-full animate-spin mb-3" />
              <p className="text-sm text-gray-500">Consulting veterinary knowledge base…</p>
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
              {/* Condition badge */}
              <div className={`card border ${conditionStyle}`}>
                <p className="text-xs font-medium uppercase tracking-wide opacity-70 mb-1">Condition Assessment</p>
                <p className="text-xl font-bold capitalize">{(result.condition_assessment || "unknown").replace(/_/g, " ")}</p>
                {result.summary && <p className="text-sm mt-2 opacity-80">{result.summary}</p>}
              </div>

              {/* Possible conditions */}
              {result.possible_conditions?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">Possible Conditions</h3>
                  {result.possible_conditions.map((c, i) => (
                    <div key={i} className="border border-gray-100 rounded-lg p-3 mb-2">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-800">{c.name}</p>
                          {c.scientific_name && <p className="text-xs text-gray-400 italic">{c.scientific_name}</p>}
                        </div>
                        <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">
                          {Math.round((c.confidence || 0) * 100)}% match
                        </span>
                      </div>
                      {c.zoonotic && (
                        <div className="mt-2 flex items-center gap-1 text-xs text-red-600 bg-red-50 rounded px-2 py-1">
                          <AlertTriangle className="w-3 h-3" /> May be transmissible to humans
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Treatment */}
              {result.treatment?.medications?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <Pill className="w-4 h-4 text-amber-500" /> Treatment Plan
                  </h3>
                  {result.treatment.medications.map((m, i) => (
                    <div key={i} className="bg-amber-50 border border-amber-100 rounded-lg p-3 mb-2">
                      <p className="text-sm font-medium text-amber-800">{m.name}</p>
                      {m.dose && <p className="text-xs text-amber-700 mt-0.5">Dose: {m.dose}</p>}
                      {m.duration && <p className="text-xs text-amber-600">Duration: {m.duration}</p>}
                    </div>
                  ))}
                  {result.treatment.home_remedies?.length > 0 && (
                    <div className="mt-3">
                      <p className="text-xs font-medium text-gray-600 mb-2 flex items-center gap-1">
                        <Leaf className="w-3 h-3 text-leaf-500" /> Home Remedies
                      </p>
                      <ul className="space-y-1">
                        {result.treatment.home_remedies.map((r, i) => (
                          <li key={i} className="text-xs text-gray-600 flex items-start gap-1.5">
                            <CheckCircle className="w-3 h-3 text-leaf-500 mt-0.5 flex-shrink-0" />{r}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Immediate actions */}
              {result.immediate_actions?.length > 0 && (
                <div className="card border-orange-200 bg-orange-50">
                  <h3 className="font-semibold text-orange-800 mb-2 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Immediate Actions
                  </h3>
                  <ul className="space-y-1">
                    {result.immediate_actions.map((a, i) => (
                      <li key={i} className="text-sm text-orange-700 flex items-start gap-2">
                        <span className="font-bold">{i + 1}.</span>{a}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Government schemes */}
              {result.government_schemes?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-gray-800 mb-3">🏛️ Government Support</h3>
                  {result.government_schemes.map((s, i) => (
                    <div key={i} className="flex items-start gap-3 py-2 border-b border-gray-100 last:border-0">
                      <div>
                        <p className="text-sm font-medium text-gray-800">{s.scheme}</p>
                        <p className="text-xs text-gray-500">{s.benefit}</p>
                        {s.how_to_access && <p className="text-xs text-leaf-600 mt-0.5">{s.how_to_access}</p>}
                      </div>
                    </div>
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
