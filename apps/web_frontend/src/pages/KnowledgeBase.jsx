import { useState } from "react";
import { BookOpen, Search, ChevronRight, ExternalLink, Bookmark, Star } from "lucide-react";
import { agentService } from "../services/api";

const CATEGORIES = [
  { id: "all", label: "All Topics", emoji: "📚" },
  { id: "crop", label: "Crop Management", emoji: "🌾" },
  { id: "soil", label: "Soil Health", emoji: "🌍" },
  { id: "pest", label: "Pest & Disease", emoji: "🐛" },
  { id: "market", label: "Market & Finance", emoji: "📈" },
  { id: "schemes", label: "Govt Schemes", emoji: "🏛️" },
  { id: "organic", label: "Organic Farming", emoji: "🌿" },
  { id: "technology", label: "Farm Technology", emoji: "💡" },
];

const FEATURED_ARTICLES = [
  {
    id: 1, category: "schemes", emoji: "🏛️",
    title: "PM-KISAN: Who qualifies and how to apply",
    summary: "₹6,000/year direct benefit transfer for eligible farmer families. Learn eligibility, documentation, and registration steps.",
    readTime: "4 min", popular: true,
  },
  {
    id: 2, category: "organic", emoji: "🌿",
    title: "Jeevamrut: Making natural liquid fertilizer at home",
    summary: "A step-by-step guide to preparing Jeevamrut using cow dung, cow urine, jaggery, and pulse flour to enrich your soil.",
    readTime: "6 min", popular: true,
  },
  {
    id: 3, category: "pest", emoji: "🐛",
    title: "Integrated Pest Management (IPM) for Kharif crops",
    summary: "Reduce pesticide use by 40–60% while maintaining crop health using biological controls, traps, and resistant varieties.",
    readTime: "8 min", popular: false,
  },
  {
    id: 4, category: "market", emoji: "📈",
    title: "How to register on eNAM for better crop prices",
    summary: "eNAM connects you to 1000+ mandis across India. Step-by-step registration guide and tips for getting the best price.",
    readTime: "5 min", popular: true,
  },
  {
    id: 5, category: "technology", emoji: "💡",
    title: "Drip irrigation: Setup cost, subsidy & ROI",
    summary: "Up to 90% reduction in water use. Learn about PMKSY subsidies covering 55–80% of setup costs and calculate your ROI.",
    readTime: "7 min", popular: false,
  },
  {
    id: 6, category: "soil", emoji: "🌍",
    title: "Reading your Soil Health Card",
    summary: "Your government-issued SHC contains 12 parameters. This guide explains each one and what action to take.",
    readTime: "5 min", popular: false,
  },
  {
    id: 7, category: "crop", emoji: "🌾",
    title: "Crop insurance: PMFBY coverage explained",
    summary: "Pradhan Mantri Fasal Bima Yojana covers sowing risk, standing crop loss & post-harvest losses. Know your rights.",
    readTime: "6 min", popular: true,
  },
  {
    id: 8, category: "organic", emoji: "🌿",
    title: "Panchagavya: Benefits and preparation method",
    summary: "Traditional bio-stimulant made from 5 cow-derived inputs. Boosts immunity and yield when applied as foliar spray.",
    readTime: "4 min", popular: false,
  },
];

const GOVT_HELPLINES = [
  { name: "Kisan Call Centre", number: "1800-180-1551", desc: "Free agri advice in 22 languages, 24×7", emoji: "📞" },
  { name: "Livestock Helpline", number: "1962", desc: "Veterinary emergency assistance", emoji: "🐄" },
  { name: "Soil Testing Labs", number: "1800-180-1551", desc: "Find nearest STL via KCC", emoji: "🧪" },
  { name: "PM-KISAN Helpline", number: "155261", desc: "Queries about direct benefit transfer", emoji: "💰" },
  { name: "eNAM Helpline", number: "1800-270-0224", desc: "Online mandi registration support", emoji: "🏪" },
];

export default function KnowledgeBase() {
  const [category, setCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [askQuery, setAskQuery] = useState("");
  const [askResult, setAskResult] = useState(null);
  const [askLoading, setAskLoading] = useState(false);
  const [saved, setSaved] = useState(new Set());

  const filtered = FEATURED_ARTICLES.filter(a => {
    const matchCat = category === "all" || a.category === category;
    const matchSearch = !searchQuery || a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.summary.toLowerCase().includes(searchQuery.toLowerCase());
    return matchCat && matchSearch;
  });

  const toggleSave = (id) =>
    setSaved(p => { const n = new Set(p); n.has(id) ? n.delete(id) : n.add(id); return n; });

  const handleAsk = async () => {
    if (!askQuery.trim()) return;
    setAskLoading(true);
    setAskResult(null);
    try {
      const res = await agentService.askKnowledge(askQuery);
      setAskResult(res.answer || res.data?.answer || "No answer found. Please rephrase your question.");
    } catch {
      setAskResult("Unable to fetch an answer right now. Please try the Kisan Call Centre at 1800-180-1551.");
    }
    setAskLoading(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
          <BookOpen className="w-5 h-5 text-purple-600" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-gray-900">Knowledge Hub</h1>
          <p className="text-sm text-gray-500">Agricultural guides, government schemes & expert advice</p>
        </div>
      </div>

      {/* Ask AI */}
      <div className="card bg-gradient-to-br from-leaf-50 to-earth-50 border-leaf-200">
        <h2 className="font-semibold text-gray-800 mb-3">🤖 Ask KrishiMind-AI</h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="e.g. What are the symptoms of rice blast disease?"
            value={askQuery}
            onChange={e => setAskQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleAsk()}
            className="flex-1 border border-leaf-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-leaf-400"
          />
          <button onClick={handleAsk} disabled={askLoading || !askQuery.trim()} className="btn-primary px-4">
            {askLoading ? <span className="loading-dots" /> : <Search className="w-4 h-4" />}
          </button>
        </div>
        {askResult && (
          <div className="mt-3 bg-white rounded-lg p-3 border border-leaf-100">
            <p className="text-sm text-gray-700 leading-relaxed">{askResult}</p>
          </div>
        )}
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
        {CATEGORIES.map(cat => (
          <button
            key={cat.id}
            onClick={() => setCategory(cat.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm whitespace-nowrap border transition-all flex-shrink-0 ${
              category === cat.id
                ? "bg-leaf-600 text-white border-leaf-600"
                : "bg-white text-gray-600 border-gray-200 hover:border-leaf-300"
            }`}
          >
            <span>{cat.emoji}</span>
            <span>{cat.label}</span>
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search articles…"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
        />
      </div>

      {/* Article Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map(article => (
          <div key={article.id} className="card hover:shadow-md transition-shadow group cursor-pointer">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-xl">{article.emoji}</span>
                {article.popular && (
                  <span className="flex items-center gap-0.5 text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
                    <Star className="w-3 h-3 fill-amber-500 text-amber-500" /> Popular
                  </span>
                )}
              </div>
              <button
                onClick={() => toggleSave(article.id)}
                className={`p-1 rounded transition-colors ${saved.has(article.id) ? "text-leaf-600" : "text-gray-300 hover:text-gray-500"}`}
              >
                <Bookmark className={`w-4 h-4 ${saved.has(article.id) ? "fill-leaf-600" : ""}`} />
              </button>
            </div>
            <h3 className="font-semibold text-gray-800 group-hover:text-leaf-700 transition-colors mb-1 text-sm leading-snug">
              {article.title}
            </h3>
            <p className="text-xs text-gray-500 mb-3 leading-relaxed">{article.summary}</p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">📖 {article.readTime} read</span>
              <span className="text-xs text-leaf-600 flex items-center gap-1 group-hover:gap-2 transition-all">
                Read more <ChevronRight className="w-3 h-3" />
              </span>
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="col-span-2 text-center py-12 text-gray-400">
            <BookOpen className="w-10 h-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm">No articles found. Try a different search or category.</p>
          </div>
        )}
      </div>

      {/* Government Helplines */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 mb-4">📞 Government Helplines</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {GOVT_HELPLINES.map(h => (
            <div key={h.name} className="flex items-start gap-3 bg-gray-50 rounded-xl p-3">
              <span className="text-2xl">{h.emoji}</span>
              <div>
                <p className="text-sm font-medium text-gray-800">{h.name}</p>
                <a href={`tel:${h.number}`} className="text-leaf-600 font-bold text-sm hover:underline">{h.number}</a>
                <p className="text-xs text-gray-500 mt-0.5">{h.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
