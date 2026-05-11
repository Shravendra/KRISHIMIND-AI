import { useState } from "react";
import { Settings as SettingsIcon, User, Bell, Shield, Globe, Trash2, Save, CheckCircle } from "lucide-react";
import { useAuthStore } from "../store/authStore";

const LANGUAGES = [
  { code: "en", label: "English" }, { code: "hi", label: "हिंदी (Hindi)" },
  { code: "mr", label: "मराठी (Marathi)" }, { code: "pa", label: "ਪੰਜਾਬੀ (Punjabi)" },
  { code: "gu", label: "ગુજરાતી (Gujarati)" }, { code: "ta", label: "தமிழ் (Tamil)" },
  { code: "te", label: "తెలుగు (Telugu)" }, { code: "kn", label: "ಕನ್ನಡ (Kannada)" },
  { code: "bn", label: "বাংলা (Bengali)" }, { code: "or", label: "ଓଡ଼ିଆ (Odia)" },
];

const CROPS = [
  "Rice", "Wheat", "Maize", "Soybean", "Cotton", "Sugarcane",
  "Tomato", "Potato", "Onion", "Chilli", "Groundnut", "Mustard",
];

const IRRIGATION_TYPES = ["Rainfed", "Drip", "Flood", "Sprinkler", "Canal"];
const FARMING_TYPES = ["Conventional", "Organic", "Natural", "Integrated"];

export default function Settings() {
  const { user, updateProfile } = useAuthStore();
  const [activeTab, setActiveTab] = useState("profile");
  const [saved, setSaved] = useState(false);
  const [profile, setProfile] = useState({
    name: user?.name || "",
    email: user?.email || "",
    phone: user?.phone || "",
    language: user?.preferred_language || "en",
    state: user?.state || "",
    district: user?.district || "",
    farmSize: user?.farm_size_acres || "",
    primaryCrops: user?.primary_crops || [],
    soilType: user?.soil_type || "",
    irrigationType: user?.irrigation_type || "Rainfed",
    farmingType: user?.farming_type || "Conventional",
  });
  const [notifications, setNotifications] = useState({
    weatherAlerts: true,
    marketPrices: true,
    cropAdvisories: true,
    governmentSchemes: false,
    weeklyReport: true,
  });

  const toggleCrop = (crop) =>
    setProfile(p => ({
      ...p,
      primaryCrops: p.primaryCrops.includes(crop)
        ? p.primaryCrops.filter(c => c !== crop)
        : [...p.primaryCrops, crop],
    }));

  const handleSave = async () => {
    try {
      await updateProfile({
        name: profile.name,
        preferred_language: profile.language,
        state: profile.state,
        district: profile.district,
        farm_size_acres: parseFloat(profile.farmSize) || null,
        primary_crops: profile.primaryCrops,
        soil_type: profile.soilType,
        irrigation_type: profile.irrigationType,
        farming_type: profile.farmingType,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error("Profile update failed", err);
    }
  };

  const TABS = [
    { id: "profile", label: "Farm Profile", icon: User },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "language", label: "Language", icon: Globe },
    { id: "security", label: "Security", icon: Shield },
  ];

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center">
          <SettingsIcon className="w-5 h-5 text-gray-600" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-gray-900">Settings</h1>
          <p className="text-sm text-gray-500">Manage your farm profile and preferences</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl overflow-x-auto">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap flex-shrink-0 ${
              activeTab === id ? "bg-white text-gray-800 shadow-sm" : "text-gray-500 hover:text-gray-700"
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {activeTab === "profile" && (
        <div className="card space-y-5">
          <h2 className="font-semibold text-gray-800">Personal & Farm Details</h2>

          {/* Avatar */}
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-leaf-100 rounded-full flex items-center justify-center text-2xl font-bold text-leaf-700">
              {profile.name?.[0]?.toUpperCase() || "F"}
            </div>
            <div>
              <p className="font-medium text-gray-800">{profile.name || "Farmer"}</p>
              <p className="text-sm text-gray-500">{profile.email}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Full Name</label>
              <input
                type="text"
                value={profile.name}
                onChange={e => setProfile(p => ({ ...p, name: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Phone</label>
              <input
                type="tel"
                value={profile.phone}
                onChange={e => setProfile(p => ({ ...p, phone: e.target.value }))}
                placeholder="+91 XXXXX XXXXX"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">State</label>
              <input
                type="text"
                value={profile.state}
                onChange={e => setProfile(p => ({ ...p, state: e.target.value }))}
                placeholder="e.g. Maharashtra"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">District</label>
              <input
                type="text"
                value={profile.district}
                onChange={e => setProfile(p => ({ ...p, district: e.target.value }))}
                placeholder="e.g. Nashik"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Farm Size (acres)</label>
              <input
                type="number"
                value={profile.farmSize}
                onChange={e => setProfile(p => ({ ...p, farmSize: e.target.value }))}
                placeholder="e.g. 5"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Soil Type</label>
              <input
                type="text"
                value={profile.soilType}
                onChange={e => setProfile(p => ({ ...p, soilType: e.target.value }))}
                placeholder="e.g. Loamy"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Irrigation Type</label>
              <select
                value={profile.irrigationType}
                onChange={e => setProfile(p => ({ ...p, irrigationType: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
              >
                {IRRIGATION_TYPES.map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Farming Type</label>
              <select
                value={profile.farmingType}
                onChange={e => setProfile(p => ({ ...p, farmingType: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400"
              >
                {FARMING_TYPES.map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
          </div>

          {/* Primary Crops */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">Primary Crops</label>
            <div className="flex flex-wrap gap-2">
              {CROPS.map(crop => (
                <button
                  key={crop}
                  onClick={() => toggleCrop(crop)}
                  className={`px-3 py-1.5 rounded-full text-sm border transition-all ${
                    profile.primaryCrops.includes(crop)
                      ? "bg-leaf-500 text-white border-leaf-500"
                      : "border-gray-200 text-gray-600 hover:border-leaf-300"
                  }`}
                >
                  {crop}
                </button>
              ))}
            </div>
          </div>

          <button onClick={handleSave} className="btn-primary flex items-center gap-2">
            {saved ? <><CheckCircle className="w-4 h-4" /> Saved!</> : <><Save className="w-4 h-4" /> Save Changes</>}
          </button>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === "notifications" && (
        <div className="card space-y-4">
          <h2 className="font-semibold text-gray-800">Notification Preferences</h2>
          {[
            { key: "weatherAlerts", label: "Weather Alerts", desc: "Rain, drought, and frost warnings for your location" },
            { key: "marketPrices", label: "Market Price Updates", desc: "Daily mandi prices for your crops" },
            { key: "cropAdvisories", label: "Crop Advisories", desc: "Seasonal farming tips and stage-based advice" },
            { key: "governmentSchemes", label: "Government Schemes", desc: "New schemes and deadlines relevant to you" },
            { key: "weeklyReport", label: "Weekly Report", desc: "Summary of your farm's performance and AI insights" },
          ].map(({ key, label, desc }) => (
            <div key={key} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
              <div>
                <p className="text-sm font-medium text-gray-800">{label}</p>
                <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
              </div>
              <button
                onClick={() => setNotifications(p => ({ ...p, [key]: !p[key] }))}
                className={`relative w-11 h-6 rounded-full transition-colors ${notifications[key] ? "bg-leaf-500" : "bg-gray-200"}`}
              >
                <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${notifications[key] ? "translate-x-5" : ""}`} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Language Tab */}
      {activeTab === "language" && (
        <div className="card space-y-4">
          <h2 className="font-semibold text-gray-800">Language Preference</h2>
          <p className="text-sm text-gray-500">KrishiMind-AI will respond in your preferred language when possible.</p>
          <div className="grid grid-cols-2 gap-2">
            {LANGUAGES.map(lang => (
              <button
                key={lang.code}
                onClick={() => setProfile(p => ({ ...p, language: lang.code }))}
                className={`text-left px-4 py-3 rounded-xl border transition-all ${
                  profile.language === lang.code
                    ? "border-leaf-400 bg-leaf-50 text-leaf-700 font-medium"
                    : "border-gray-200 text-gray-600 hover:border-gray-300"
                }`}
              >
                {lang.label}
              </button>
            ))}
          </div>
          <button onClick={handleSave} className="btn-primary flex items-center gap-2">
            {saved ? <><CheckCircle className="w-4 h-4" /> Saved!</> : <><Save className="w-4 h-4" /> Save Language</>}
          </button>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === "security" && (
        <div className="card space-y-5">
          <h2 className="font-semibold text-gray-800">Security Settings</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Current Password</label>
              <input type="password" placeholder="••••••••" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">New Password</label>
              <input type="password" placeholder="••••••••" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Confirm New Password</label>
              <input type="password" placeholder="••••••••" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-leaf-400" />
            </div>
            <button className="btn-primary flex items-center gap-2">
              <Shield className="w-4 h-4" /> Update Password
            </button>
          </div>

          <div className="border-t border-gray-100 pt-4">
            <h3 className="text-sm font-semibold text-red-600 mb-2">Danger Zone</h3>
            <p className="text-xs text-gray-500 mb-3">Deleting your account is permanent and cannot be undone.</p>
            <button className="flex items-center gap-2 text-sm text-red-600 border border-red-200 rounded-lg px-4 py-2 hover:bg-red-50 transition-colors">
              <Trash2 className="w-4 h-4" /> Delete Account
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
