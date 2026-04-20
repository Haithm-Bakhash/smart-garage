from pydantic import BaseModel
from typing import List

class CarRequest(BaseModel):
    make: str
    model: str
    year: int
    mileage: int

class MaintenanceResponse(BaseModel):
    upcoming_issues: List[str]
    estimated_cost_usd: int
    ai_notes: str