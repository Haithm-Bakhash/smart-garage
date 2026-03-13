from domain.models import CarRequest, MaintenanceResponse
from infrastructure.ai_client import get_ai_prediction

def analyze_car(car_data: CarRequest) -> MaintenanceResponse:
    ai_data = get_ai_prediction(car_data)
    
    return MaintenanceResponse(
        upcoming_issues=ai_data.get('issues', ["Unknown"]),
        estimated_cost_usd=ai_data.get('cost', 0),
        ai_notes=ai_data.get('note', "No notes available")
    )