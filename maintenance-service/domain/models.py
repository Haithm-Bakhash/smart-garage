from pydantic import BaseModel
from typing import List

class CarRequest(BaseModel):
    make: str
    model: str
    year: int
    mileage: int
    engine_type: str
    transmission: str
    driving_environment: str
    current_symptoms: str

class MaintenanceResponse(BaseModel):
    upcoming_issues: List[str]
    estimated_cost_usd: int
    ai_notes: str