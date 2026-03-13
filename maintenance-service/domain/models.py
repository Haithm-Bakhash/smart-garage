from pydantic import BaseModel
from typing import List

# This defines the exact format of the data the user will send to our API
class CarRequest(BaseModel):
    make: str
    model: str
    year: int
    mileage: int

# This defines the exact format of the response our API will send back
class MaintenanceResponse(BaseModel):
    upcoming_issues: List[str]
    estimated_cost_usd: int
    ai_notes: str