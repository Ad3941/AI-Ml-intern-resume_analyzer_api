from pydantic import BaseModel, Field
from typing import List, Optional

class AnalysisResponse(BaseModel):
    summary: str
    key_skills: List[str]
    experience_years_estimated: Optional[float] = None
    recommended_roles: List[str]
    tokens_used: Optional[int] = None