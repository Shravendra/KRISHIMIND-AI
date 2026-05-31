"""Application-wide constants for KrishiMind-AI."""

APP_NAME = "KrishiMind-AI"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Agricultural Intelligence Platform for Indian Farmers"

# ── Agent identifiers ────────────────────────────────────────────────────────
AGENT_DISEASE     = "disease_detection"
AGENT_SOIL        = "soil_analysis"
AGENT_FERTILIZER  = "fertilizer_optimization"
AGENT_WEATHER     = "weather_risk"
AGENT_CROP_PLAN   = "crop_planning"
AGENT_MARKET      = "market_intelligence"
AGENT_HARVEST     = "harvest_recommendation"
AGENT_POSTHARVEST = "postharvest_management"
AGENT_LIVESTOCK   = "livestock_health"
AGENT_KNOWLEDGE   = "knowledge_base"

ALL_AGENTS = [
    AGENT_DISEASE, AGENT_SOIL, AGENT_FERTILIZER, AGENT_WEATHER,
    AGENT_CROP_PLAN, AGENT_MARKET, AGENT_HARVEST, AGENT_POSTHARVEST, AGENT_LIVESTOCK, AGENT_KNOWLEDGE,
]

# ── Intent labels (must match intent_classifier output) ──────────────────────
INTENT_DISEASE        = "disease_detection"
INTENT_SOIL           = "soil_analysis"
INTENT_FERTILIZER     = "fertilizer_recommendation"
INTENT_WEATHER        = "weather_risk"
INTENT_CROP_PLANNING  = "crop_planning"
INTENT_MARKET         = "market_intelligence"
INTENT_HARVEST        = "harvest_recommendation"
INTENT_POSTHARVEST    = "postharvest_management"
INTENT_LIVESTOCK      = "livestock_health"
INTENT_KNOWLEDGE      = "general_knowledge"
INTENT_GREETING       = "greeting"
INTENT_UNKNOWN        = "unknown"

# ── Redis key prefixes ───────────────────────────────────────────────────────
REDIS_CHAT_HISTORY_PREFIX  = "chat:history:"
REDIS_FARM_PROFILE_PREFIX  = "farm:profile:"
REDIS_RATE_LIMIT_PREFIX    = "rate:limit:"

# ── Pagination / limits ──────────────────────────────────────────────────────
MAX_CHAT_HISTORY_MESSAGES = 20
DEFAULT_PAGE_SIZE         = 20

# ── Supported crops (used in UI chip selector too) ───────────────────────────
SUPPORTED_CROPS = [
    "Rice", "Wheat", "Maize", "Soybean", "Cotton", "Sugarcane",
    "Tomato", "Potato", "Onion", "Chilli", "Groundnut", "Mustard",
    "Bajra", "Jowar", "Chickpea", "Lentil", "Mango", "Banana",
]

# ── Indian states for location context ──────────────────────────────────────
INDIAN_STATES = [
    "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh", "Gujarat",
    "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Odisha", "Punjab", "Rajasthan",
    "Tamil Nadu", "Telangana", "Uttar Pradesh", "Uttarakhand", "West Bengal",
]

# ── HTTP status helpers ──────────────────────────────────────────────────────
HTTP_200_OK            = 200
HTTP_201_CREATED       = 201
HTTP_400_BAD_REQUEST   = 400
HTTP_401_UNAUTHORIZED  = 401
HTTP_403_FORBIDDEN     = 403
HTTP_404_NOT_FOUND     = 404
HTTP_422_UNPROCESSABLE = 422
HTTP_429_TOO_MANY      = 429
HTTP_500_SERVER_ERROR  = 500
