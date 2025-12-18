import ephem
import math
import google.generativeai as genai
import streamlit as st
from PIL import Image

def calculate_sun_position(lat, lon, date_time_str):
    """
    Calculates the Sun's precise Azimuth and Altitude for a specific place & time.
    """
    try:
        observer = ephem.Observer()
        # Ephem expects string coordinates
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.date = date_time_str  # Format: YYYY/MM/DD HH:MM:SS

        sun = ephem.Sun()
        sun.compute(observer)

        # Convert radians to degrees
        azimuth_deg = math.degrees(sun.az)
        altitude_deg = math.degrees(sun.alt)

        return {
            "azimuth": round(azimuth_deg, 2),
            "altitude": round(altitude_deg, 2),
            "readable": f"Sun Position: {round(azimuth_deg, 2)}° (Compass) | Height: {round(altitude_deg, 2)}°"
        }
    except Exception as e:
        return {"error": str(e)}

# Updated function signature to accept 'location_desc'
def analyze_shadow_consistency(image_path, sun_data, api_key, location_desc="Unknown Location"):
    """
    Uses Gemini to look at the image and verify if the shadows match the physics.
    """
    if not api_key:
        return "⚠️ Missing API Key."
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    try:
        img = Image.open(image_path)
        
        # We inject the location_desc into the prompt
        prompt = f"""
        You are a Forensic Physics Expert. 
        
        CONTEXT:
        - Claimed Location: {location_desc}
        - Sun Position (calculated): Azimuth {sun_data['azimuth']}° / Altitude {sun_data['altitude']}°

        TASK:
        1. Explicitly mention the 'Claimed Location' and sun position in your opening statement.
        2. Look at the shadows in the image.
        3. VERDICT: Are the shadows consistent with this specific location and time?
           - If sun is East, shadows must point West.
        
        Output a verdict: "CONSISTENT", "INCONSISTENT", or "INCONCLUSIVE".
        """
        
        with st.spinner("🔭 Analyzing Shadow Physics..."):
            response = model.generate_content([prompt, img])
            return response.text
            
    except Exception as e:
        return f"Error: {str(e)}"