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

def get_ai_prediction(car: CarRequest):
    prompt = f"Expert mechanic analysis: {car.year} {car.make} {car.model}, {car.mileage} miles. Return JSON with 'issues', 'cost', and 'note'."

    # 1. Try to use the real AI first
    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            clean_json = response.text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"AI API Blocked or Failed: {e}. Switching to Fallback System.")
    
    # 2. THE GRACEFUL FALLBACK (Runs if the AI is out of quota)
    # We calculate a realistic response based on the car's mileage
    issues = []
    cost = 0
    note = f"Standard automated review for {car.make} {car.model}."

    if car.mileage > 100000:
        issues = ["Replace timing belt", "Check transmission fluid", "Inspect suspension"]
        cost = 850
        note = f"At {car.mileage} miles, major preventative maintenance is highly recommended for older {car.make}s."
    elif car.mileage > 50000:
        issues = ["Replace brake pads", "Perform wheel alignment", "Replace cabin filter"]
        cost = 320
        note = f"Your {car.model} is at a common milestone for brake and tire maintenance."
    else:
        issues = ["Standard oil change", "Tire rotation", "Check wiper blades"]
        cost = 120
        note = f"Your {car.year} vehicle is relatively new. Keep up with routine checkups!"

    return {
        "issues": issues,
        "cost": cost,
        "note": note
    }