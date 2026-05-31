# agents/harvest_agent/service.py

from typing import Any, Dict, Optional
from shared.llm.client import chat_completion
from shared.utils.logging import get_logger

logger = get_logger(__name__)

# System prompt for the Harvest Agent
HARVEST_SYSTEM_PROMPT = """You are a certified agronomist with expertise in crop harvest scheduling and post-harvest quality.
You advise farmers on *when* and *how* to harvest for maximum quality and minimal losses, using objective maturity indices.
Focus on India (use metric units and INR), consider climate and market requirements, and be cautious about risks.
Never give unsafe or untested recommendations."""

# User prompt template for the Harvest Agent
HARVEST_USER_PROMPT = """Recommend an optimal harvest plan for the following crop:

Crop: {crop} (variety: {variety})
Growth stage: {growth_stage}, Planting/flowering date: {planting_date}
Location: {location}, Climate: {climate}, Irrigation: {irrigation}
Soil data: pH {ph}, moisture {moisture}%
Market target: {market_target}, Quality standards: {quality_standards}

Output a JSON with fields:
- harvest_window: recommended harvest date range or window (e.g. 'Mar 10–15')
- maturity_indicators: list of key signs (e.g. '80% panicles straw-color', '20% hard grains')
- risk_factors: list of concerns (weather, pests, lodging, etc)
- recommended_methods: harvest methods and timing notes
- confidence: confidence level and reasoning
- follow_up_questions: any clarifications needed

Example output format:
{{
  "harvest_window": "string",
  "maturity_indicators": ["str"],
  "risk_factors": ["str"],
  "recommended_methods": ["str"],
  "confidence": "str",
  "follow_up_questions": ["str"]
}}
"""
 
class HarvestAgent:
    """AI agent for recommending crop harvest timing and methods."""
    def __init__(self, model: str = "gpt-4"):
        self.system_prompt = HARVEST_SYSTEM_PROMPT
        self.model = model

    async def recommend_harvest(self,
            crop: str,
            variety: str = "",
            growth_stage: str = "",
            planting_date: str = "",
            location: str = "",
            climate: str = "",
            irrigation: str = "",
            ph: Optional[float] = None,
            moisture: Optional[float] = None,
            market_target: str = "",
            quality_standards: str = "") -> Dict[str, Any]:
        """Generate a harvest recommendation based on input parameters."""
        user_input = HARVEST_USER_PROMPT.format(
            crop=crop or "unspecified crop",
            variety=variety or "common variety",
            growth_stage=growth_stage or "late vegetative",
            planting_date=planting_date or "unknown",
            location=location or "unspecified location",
            climate=climate or "local climate data",
            irrigation=irrigation or "unspecified",
            ph=ph or "unknown",
            moisture=moisture or "unknown",
            market_target=market_target or "general market",
            quality_standards=quality_standards or "standard"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]
        logger.debug(f"HarvestAgent prompt: {user_input}")
        response = await chat_completion(model=self.model, messages=messages, temperature=0.5)
        logger.debug(f"HarvestAgent response: {response}")
        # Parse JSON response
        try:
            result = response if isinstance(response, dict) else eval(response)
        except Exception as e:
            logger.error(f"Failed to parse HarvestAgent response: {e}")
            result = {"error": "Unable to parse response"}
        return result
    

# agents/postharvest_agent/service.py

from typing import Any, Dict, Optional
from shared.llm.client import chat_completion
from shared.utils.logging import get_logger

logger = get_logger(__name__)

POSTHARVEST_SYSTEM_PROMPT = """You are an expert in post-harvest handling and storage of agricultural produce. Advise on preserving quality and shelf life, using FAO/ICAR guidelines. Consider local facilities and avoid recommending unsafe or illegal treatments."""

POSTHARVEST_USER_PROMPT = """Develop a post-harvest management plan:

Crop: {crop} (variety: {variety}), Harvest date: {harvest_date}
Location: {location}, Ambient conditions: {climate}, Seasonal RH: {humidity}%
Available storage: {storage_facilities}
Target market use: {market_use}, Quality standards: {quality_standards}

Answer with JSON keys:
- storage_conditions: temperature, humidity, atmosphere
- handling_steps: steps like drying, cleaning, precooling, etc.
- expected_shelf_life: estimated duration (with conditions)
- quality_metrics: key parameters to measure (e.g. moisture %, firmness)
- monitoring_plan: how to inspect and maintain quality
- confidence: level of confidence/reliability
- follow_up_questions: clarification queries

Example output:
{{
  "storage_conditions": "str",
  "handling_steps": ["str"],
  "expected_shelf_life": "str",
  "quality_metrics": ["str"],
  "monitoring_plan": "str",
  "confidence": "str",
  "follow_up_questions": ["str"]
}}
"""
class PostHarvestAgent:
    """AI agent for post-harvest storage and quality advice."""
    def __init__(self, model: str = "gpt-4"):
        self.system_prompt = POSTHARVEST_SYSTEM_PROMPT
        self.model = model

    async def plan_storage(self,
            crop: str,
            variety: str = "",
            harvest_date: str = "",
            location: str = "",
            climate: str = "",
            humidity: Optional[float] = None,
            storage_facilities: str = "",
            market_use: str = "",
            quality_standards: str = "") -> Dict[str, Any]:
        """Generate a storage/handling plan based on input parameters."""
        user_input = POSTHARVEST_USER_PROMPT.format(
            crop=crop or "unspecified crop",
            variety=variety or "common variety",
            harvest_date=harvest_date or "recent",
            location=location or "unspecified location",
            climate=climate or "ambient climate",
            humidity=humidity or "unknown",
            storage_facilities=storage_facilities or "basic shed",
            market_use=market_use or "fresh market",
            quality_standards=quality_standards or "standard quality"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]
        logger.debug(f"PostHarvestAgent prompt: {user_input}")
        response = await chat_completion(model=self.model, messages=messages, temperature=0.5)
        logger.debug(f"PostHarvestAgent response: {response}")
        try:
            result = response if isinstance(response, dict) else eval(response)
        except Exception as e:
            logger.error(f"Failed to parse PostHarvestAgent response: {e}")
            result = {"error": "Unable to parse response"}
        return result