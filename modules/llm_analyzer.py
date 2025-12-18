import google.generativeai as genai
import streamlit as st
from PIL import Image
from datetime import datetime
import pytz  # <--- NEW IMPORT

def generate_forensic_report(image_path, api_key, metrics=None, user_timezone="UTC"):
    """
    Sends image + Mathematical Metrics to Gemini.
    Now supports Timezone-aware timestamping.
    """
    if not api_key:
        return "⚠️ API Key missing."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    try:
        img = Image.open(image_path)
    except Exception as e:
        return f"Error loading image: {e}"

    # --- THE FIX: TIMEZONE AWARENESS ---
    try:
        # Get the timezone object from the string (e.g., 'Asia/Dhaka')
        tz = pytz.timezone(user_timezone)
        # Get current time in THAT timezone
        now = datetime.now(tz)
    except Exception:
        # Fallback to UTC if timezone string is bad
        now = datetime.now(pytz.utc)

    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S %Z") # %Z adds the timezone name (e.g., CST, CET)

    # Metrics Context
    metrics_context = ""
    if metrics:
        skel = metrics.get('skeletal_analysis', 'Not Run')
        shadow = metrics.get('shadow_verdict', 'Not Run')
        integrity = metrics.get('integrity_verdict', 'Not Run')
        
        metrics_context = f"""
        SYSTEM DETECTED METRICS (HARD DATA):
        - Skeletal Analysis Verdict: {skel}
        - Shadow/Physics Verdict: {shadow}
        - Digital Integrity Verdict: {integrity}
        """

    prompt = f"""
    You are a Senior Digital Forensic Investigator. 
    
    METADATA FOR REPORT:
    - Date of Report: {current_date}
    - Time of Report: {current_time} (Local Investigator Time)
    
    {metrics_context}

    Analyze the provided evidence image. 
    1. Start with a formal header using the Date/Time provided above.
    2. Validate the system metrics above. Do they match what you see visually?
    3. Provide a 'Behavioral Context' for any people in the frame.
    4. Generate a formal Threat Assessment.
    
    Output a professional Police Report.
    """

    try:
        with st.spinner("🤖 AI Analyst is writing the report..."):
            response = model.generate_content([prompt, img])
            return response.text
    except Exception as e:
        return f"API Error: {str(e)}"