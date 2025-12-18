import google.generativeai as genai
import streamlit as st
from PIL import Image
from datetime import datetime  # <--- NEW IMPORT

def generate_forensic_report(image_path, api_key, metrics=None):
    """
    Sends image + Mathematical Metrics to Gemini for a grounded analysis.
    """
    if not api_key:
        return "⚠️ API Key missing."

    genai.configure(api_key=api_key)
    # Using the working 2.5 model
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    try:
        img = Image.open(image_path)
    except Exception as e:
        return f"Error loading image: {e}"

    # --- THE UPGRADE: DYNAMIC DATE ---
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    # Metrics Context
    metrics_context = ""
    if metrics:
        # We try to safely extract data, handling cases where keys might be missing
        skel = metrics.get('skeletal_analysis', 'Not Run')
        shadow = metrics.get('shadow_verdict', 'Not Run')
        integrity = metrics.get('integrity_verdict', 'Not Run')
        
        metrics_context = f"""
        SYSTEM DETECTED METRICS (HARD DATA):
        - Skeletal Analysis Verdict: {skel}
        - Shadow/Physics Verdict: {shadow}
        - Digital Integrity Verdict: {integrity}
        """

    # The Prompt with Dynamic Date
    prompt = f"""
    You are a Senior Digital Forensic Investigator. 
    
    METADATA FOR REPORT:
    - Date of Report: {current_date}
    - Time of Report: {current_time}
    
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