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
    # Updated cache key to ensure different specs don't share the same cache
    cache_key = f"{car.year}_{car.make}_{car.model}_{car.mileage}_{car.engine_type}_{car.transmission}_{car.driving_environment}"
    
    if cache_key in prediction_cache:
        print(f"CACHE HIT: Returning saved AI prediction for {cache_key}")
        return prediction_cache[cache_key]

    
    prompt = f"""
    Act as a Master Auto Mechanic and Automotive Data Expert.
    I need a deep, highly specific diagnostic prediction for this exact vehicle:
    - Year: {car.year}
    - Make: {car.make}
    - Model: {car.model}
    - Engine Type: {car.engine_type}
    - Transmission: {car.transmission}
    - Current Mileage: {car.mileage} miles
    - Driving Environment: {car.driving_environment}
    - Current Symptoms: {car.current_symptoms}

    Based on historical reliability data, known manufacturer recalls, the specific powertrain configuration, and the driving environment, provide a realistic maintenance prediction. 
    If symptoms are reported, diagnose them. Do NOT give generic advice (like 'check oil'). You MUST mention specific engine types, transmissions, or common structural failures historically known for the {car.year} {car.model} with this powertrain.

    CRITICAL COST INSTRUCTION: Calculate a highly specific estimated repair cost in USD. 
    Factor in {car.make} parts pricing and labor. Do NOT output a rounded number or default to a generic number.

    CRITICAL JSON INSTRUCTION: Return ONLY a raw JSON object. Do NOT wrap it in markdown block quotes. 
    Do NOT use double quotes inside your text values (use single quotes instead to prevent JSON parsing crashes).
    Use this exact format:
    {{
        "issues": ["Highly specific issue 1", "Highly specific issue 2"],
        "cost": <integer representing calculated reasonable cost>,
        "note": "A personalized, expert explanation referencing the specific car's history, environment, and why these parts fail at this mileage. Remember to only use single quotes 'like this' if you need to quote something."
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
            max_tokens=1024,   
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