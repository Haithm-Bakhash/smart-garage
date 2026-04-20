import os
import json
from google import genai
from domain.models import CarRequest
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Only initialize the client if we have a key
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None


prediction_cache = {}

def get_ai_prediction(car: CarRequest):
    # 1. Create a unique ID for this specific vehicle profile
    cache_key = f"{car.year}_{car.make}_{car.model}_{car.mileage}"
    
    # 2. Check the cache FIRST (This fulfills your report's claim!)
    if cache_key in prediction_cache:
        print(f"CACHE HIT: Returning saved AI prediction for {cache_key}")
        return prediction_cache[cache_key]

    prompt = f"Expert mechanic analysis: {car.year} {car.make} {car.model}, {car.mileage} miles. Return JSON with 'issues', 'cost', and 'note'."
    
    result_data = None

    # 3. Try to use the real AI
    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            clean_json = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            result_data = json.loads(clean_json)
        except Exception as e:
            print(f"AI API Blocked or Failed: {e}. Switching to Fallback System.")
    
    # 4. Fallback System (if AI fails)
    if not result_data:
        issues = []
        cost = 0
        note = f"Standard automated review for {car.make} {car.model}."

        if car.mileage > 100000:
            issues = ["Replace timing belt", "Check transmission fluid", "Inspect suspension"]
            cost = 850
            note = f"At {car.mileage} miles, preventative maintenance is recommended for {car.make}s."
        elif car.mileage > 50000:
            issues = ["Replace brake pads", "Perform wheel alignment", "Replace cabin filter"]
            cost = 320
            note = f"Your {car.model} is at a common milestone for brake maintenance."
        else:
            issues = ["Standard oil change", "Tire rotation", "Check wiper blades"]
            cost = 120
            note = f"Your {car.year} vehicle is relatively new. Keep up with routine checkups!"

        result_data = {
            "issues": issues,
            "cost": cost,
            "note": note
        }
    
    # 5. Save the final result to the cache before returning it
    prediction_cache[cache_key] = result_data
    return result_data