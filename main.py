import streamlit as st
import os
import shutil
from PIL import Image
from fpdf import FPDF
from modules import profiler, llm_analyzer, explainability, chronos, integrity
import pytz

# 1. Page Config
st.set_page_config(
    page_title="AI Forensic Crime Footage Analyst",
    page_icon="🕵️‍♀️",
    layout="wide"
)

# --- SESSION STATE INITIALIZATION ---
# We use this to store findings from each module so the Final Report can see them.
if 'case_data' not in st.session_state:
    st.session_state['case_data'] = {
        "skeletal_analysis": "Not Run",
        "shadow_verdict": "Not Run",
        "integrity_hash": "Not Run",
        "integrity_verdict": "Not Run",
        "vision_metrics": {}
    }

# --- HELPER FUNCTIONS ---
def reset_app():
    """Clears all evidence and resets state."""
    if os.path.exists("assets"):
        shutil.rmtree("assets")
    os.makedirs("assets")
    st.session_state['case_data'] = {
        "skeletal_analysis": "Not Run",
        "shadow_verdict": "Not Run",
        "integrity_hash": "Not Run",
        "integrity_verdict": "Not Run",
        "vision_metrics": {}
    }
    st.rerun()

def create_pdf(report_text, image_path):
    """Generates a PDF Case File with safe image handling."""
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Digital Forensic Case Report", ln=True, align='C')
    pdf.ln(10)
    
    # Evidence Image (Sanitized)
    if os.path.exists(image_path):
        try:
            # 1. Open image with PIL to verify format
            img = Image.open(image_path)
            
            # 2. Convert to RGB (removes Transparency/Alpha channel which breaks PDFs)
            rgb_img = img.convert('RGB')
            
            # 3. Save as a temporary verified JPEG
            temp_img_path = "assets/temp_report_img.jpg"
            rgb_img.save(temp_img_path, "JPEG")
            
            # 4. Embed the temp image
            pdf.image(temp_img_path, x=10, y=30, w=100)
            pdf.ln(85)
            
        except Exception as e:
            # If image fails, just write the error in the PDF instead of crashing
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 10, txt=f"[Image Could Not Be Rendered: {str(e)}]", ln=True)
    
    # Report Content
    pdf.set_font("Arial", size=11)
    safe_text = report_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, safe_text)
    
    return pdf.output(dest='S').encode('latin-1')
# 2. Sidebar Setup
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1022/1022331.png", width=100)
st.sidebar.title("Forensic Dashboard")

# API Key Check
api_key = None
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.sidebar.success("✅ System Online")
    else:
        st.sidebar.error("❌ API Key Missing!")
except:
    st.sidebar.error("❌ Config Error!")

st.sidebar.markdown("---")
# Timezone Selector
# We get a list of common timezones
timezones = pytz.common_timezones
# Set a default (you can change 'UTC' to your actual preference)
selected_timezone = st.sidebar.selectbox("Investigator Timezone:", timezones, index=timezones.index('UTC'))
# Navigation
mode = st.sidebar.radio("Select Module:", 
    [
        "0. Case Overview",
        "1. Evidence Upload", 
        "2. Body Language Profiler", 
        "3. Visual Explainability (XAI)",
        "4. Shadow & Time Analysis",
        "5. Digital Integrity Check",
        "6. Final AI Case Report" # <--- Moved to End
    ]
)

st.sidebar.markdown("---")
# Reset Button
if st.sidebar.button("🗑️ Reset Case Evidence", type="primary"):
    reset_app()

# 3. Main Logic

# Ensure assets exist
if not os.path.exists('assets'):
    os.makedirs('assets')

evidence_path = os.path.join("assets", "evidence.jpg")

# --- MODULE 0: INTRO ---
if mode == "0. Case Overview":
    st.title("🕵️‍♀️ AI Forensic Crime Footage Reconstruction Tool")
    st.markdown("""
    ### Welcome to the Digital Forensics Lab
    This tool utilizes **Multimodal AI** to analyze digital evidence for authenticity, content, and physical consistency.
    
    #### 🔬 Capabilities:
    * **Pose Estimation:** Analyze suspect behavior via skeletal tracking.
    * **Explainable AI (XAI):** visualize exactly what the AI "sees" (Heatmaps).
    * **Chronos Physics:** Verify timestamps using solar astronomy (Shadow Analysis).
    * **Integrity Suite:** Detect "Deepfakes" and splicing using Error Level Analysis (ELA).
    
    **Get Started:** Go to **'1. Evidence Upload'** to begin a new case.
    """)

# --- MODULE 1: UPLOAD ---
elif mode == "1. Evidence Upload":
    st.header("📂 Evidence Acquisition")
    st.info("Supported Formats: JPG, PNG. Single file upload recommended for Chain of Custody.")
    
    uploaded_file = st.file_uploader("Upload CCTV Frame", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file:
        with open(evidence_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Evidence Logged: {evidence_path}")
        st.image(Image.open(uploaded_file), caption="Evidence #001", use_container_width=True)

# --- MODULE 2: PROFILER ---
elif mode == "2. Body Language Profiler":
    st.header("💀 Behavioral Profiling")
    if os.path.exists(evidence_path):
        if st.button("Run Skeleton Analysis"):
            with st.spinner('Tracking subjects...'):
                result = profiler.analyze_pose(evidence_path)
                
                # Unpack result
                if len(result) == 3:
                    processed_image, status, metrics = result
                else:
                    processed_image, status = result
                    metrics = {}
                
                # SAVE TO SESSION STATE
                st.session_state['case_data']['skeletal_analysis'] = status
                st.session_state['case_data']['vision_metrics'] = metrics

                col1, col2 = st.columns(2)
                with col1: st.image(evidence_path, caption="Original")
                with col2: 
                    if processed_image is not None:
                        st.image(processed_image, caption="Skeleton Output")
                
                st.success(status)
                if metrics: st.json(metrics)
    else:
        st.error("⚠️ No Evidence Found.")

# --- MODULE 3: EXPLAINABILITY ---
elif mode == "3. Visual Explainability (XAI)":
    st.header("👁️ Visual Attention (EigenCAM)")
    if os.path.exists(evidence_path):
        if st.button("Generate Heatmap"):
            heatmap, status = explainability.generate_heatmap(evidence_path)
            if heatmap is not None:
                col1, col2 = st.columns(2)
                with col1: st.image(evidence_path, caption="Original")
                with col2: st.image(heatmap, caption="AI Attention Map")
                st.success(status)
            else:
                st.error(status)
    else:
        st.error("⚠️ No Evidence Found.")

# --- MODULE 4: CHRONOS ---
elif mode == "4. Shadow & Time Analysis":
    st.header("☀️ Chronos: Physics Verification")
    if os.path.exists(evidence_path):
        col1, col2 = st.columns(2)
        with col1: st.image(evidence_path, use_container_width=True)
        with col2:
            d = st.date_input("Claimed Date")
            t = st.time_input("Claimed Time")
            
            # --- THE FIX: ADD min_value AND max_value ---
            lat = st.number_input("Lat", min_value=-90.0, max_value=90.0, value=23.8103, help="Latitude of the location (-90 to 90)")
            lon = st.number_input("Lon", min_value=-180.0, max_value=180.0, value=90.4125, help="Longitude of the location (-180 to 180)")
            
            if st.button("Verify Physics"):
                dt_str = f"{d.year}/{d.month}/{d.day} {t.hour}:{t.minute}:00"
                sun_data = chronos.calculate_sun_position(lat, lon, dt_str)
                
                if "error" not in sun_data:
                    st.info(f"Sun Position: Azimuth {sun_data['azimuth']}° | Altitude {sun_data['altitude']}°")
                    
                    if api_key:
                        # CREATE A LOCATION STRING
                        location_string = f"Latitude {lat}, Longitude {lon}"
                        
                        # PASS IT TO THE FUNCTION
                        verdict = chronos.analyze_shadow_consistency(
                            evidence_path, 
                            sun_data, 
                            api_key, 
                            location_desc=location_string # <--- NEW ARGUMENT
                        )
                        st.write(verdict)
                        st.session_state['case_data']['shadow_verdict'] = verdict
                    else:
                        st.error("No API Key")
    else:
        st.error("⚠️ No Evidence Found.")

# --- MODULE 5: INTEGRITY ---
elif mode == "5. Digital Integrity Check":
    st.header("🔐 Digital Integrity")
    if os.path.exists(evidence_path):
        f_hash = integrity.calculate_hash(evidence_path)
        st.success(f"SHA-256: `{f_hash}`")
        # SAVE TO SESSION
        st.session_state['case_data']['integrity_hash'] = f_hash
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Metadata")
            st.json(integrity.extract_metadata(evidence_path))
        with col2:
            st.subheader("ELA Scan")
            if st.button("Run ELA"):
                img, verdict, color = integrity.perform_ela(evidence_path)
                st.image(img, caption="Error Level Analysis")
                if color == "red": st.error(verdict)
                elif color == "green": st.success(verdict)
                else: st.info(verdict)
                
                # SAVE TO SESSION
                st.session_state['case_data']['integrity_verdict'] = verdict
    else:
        st.error("⚠️ No Evidence Found.")

# --- MODULE 6: FINAL REPORT ---
elif mode == "6. Final AI Case Report":
    st.header("📝 Comprehensive Forensic Report")
    
    if os.path.exists(evidence_path):
        st.markdown("This module aggregates findings from all previous steps into a final dossier.")
        
        # Display Current Gathered Intelligence
        with st.expander("View Gathered Intelligence (Debug)"):
            st.json(st.session_state['case_data'])
            
        # 1. GENERATE BUTTON
        if st.button("Generate Final Report"):
            if api_key:
                with st.spinner("Compiling Forensic Dossier..."):
                    # We pass the WHOLE session state to Gemini
                    context_data = st.session_state['case_data']
                    
                    # Generate the text ONCE
                    report_text = llm_analyzer.generate_forensic_report(
                        evidence_path, 
                        api_key, 
                        metrics=context_data,
                        user_timezone=selected_timezone
                    )
                    
                    # SAVE IT TO MEMORY (Crucial Step)
                    st.session_state['final_report_text'] = report_text
            else:
                st.error("API Key Missing")

        # 2. DISPLAY REPORT (Check memory)
        # We check if the report exists in memory, so it stays even after reload
        if 'final_report_text' in st.session_state:
            report = st.session_state['final_report_text']
            
            st.subheader("📁 Official Case File")
            st.write(report)
            
            # PDF Download Logic
            pdf_bytes = create_pdf(report, evidence_path)
            st.download_button(
                label="📥 Download Case Report (PDF)",
                data=pdf_bytes,
                file_name="Forensic_Report.pdf",
                mime="application/pdf"
            )
            
    else:
        st.error("⚠️ No Evidence Found.")