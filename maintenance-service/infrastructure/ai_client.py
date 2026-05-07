import os
import json
from groq import Groq
from domain.models import CarRequest
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if api_key:
    client = Groq(api_key=api_key)
else:
    client = None

prediction_cache = {}

def get_ai_prediction(car: CarRequest):
    cache_key = f"{car.year}_{car.make}_{car.model}_{car.mileage}"
    
    if cache_key in prediction_cache:
        print(f"CACHE HIT: Returning saved AI prediction for {cache_key}")
        return prediction_cache[cache_key]

    # Updated prompt to prevent the AI from hardcoding 450 or 1200
    prompt = f"""
    Act as a Master Auto Mechanic and Automotive Data Expert.
    I need a deep, highly specific diagnostic prediction for this exact vehicle:
    - Year: {car.year}
    - Make: {car.make}
    - Model: {car.model}
    - Current Mileage: {car.mileage} miles

    Based on historical reliability data, known manufacturer recalls, and the specific mileage milestone of this car, provide a realistic maintenance prediction. 
    Do NOT give generic advice (like 'check oil'). You MUST mention specific engine types, transmissions, or common structural failures historically known for the {car.year} {car.model}.

    CRITICAL COST INSTRUCTION: Calculate a highly specific estimated repair cost in USD. 
    Factor in {car.make} parts pricing and labor. Do NOT output a rounded number or default to a generic number.

    Return ONLY a raw JSON object (no markdown, no backticks) in this exact format:
    {{
        "issues": ["Highly specific issue 1", "Highly specific issue 2"],
        "cost": <integer representing calculated reasonable cost>,
        "note": "A personalized, expert explanation referencing the specific car's history and why these parts fail at this mileage."
    }}
    """

    if not client:
        return {
            "issues": ["CRITICAL ERROR: NO API KEY"],
            "cost": 0,
            "note": "The GROQ_API_KEY is missing from the environment variables."
        }

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,    # <-- ADDED THE MISSING COMMA HERE
            temperature=0.7    
        )

        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        raw_text = raw_text.strip("` \n")

        result_data = json.loads(raw_text)
        print(f"AI SUCCESS: Master mechanic analyzed {cache_key}")

        prediction_cache[cache_key] = result_data
        return result_data

    except Exception as e:
        error_message = str(e)
        print(f"AI FAILURE: {error_message}")

        return {
            "issues": ["AI GENERATION FAILED"],
            "cost": 9999,
            "note": f"The Groq API refused the connection or returned bad data. Exact Error: {error_message}"
        }