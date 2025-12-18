# 🕵️‍♀️ AI Forensic Reconstruction Analyst

**A Multimodal Forensic Dashboard for Digital Evidence Verification**

## 📖 Overview
The **AI Forensic Analyst** is a professional-grade investigative dashboard designed to assist digital forensic experts. It combines **Computer Vision**, **Generative AI**, and **Astrophysics** to validate digital evidence (CCTV footage, photographs) for authenticity, physical consistency, and behavioral threats.

Unlike standard analysis tools, this system implements a "Trust but Verify" architecture: it detects objects using AI, explains *why* it detected them (XAI), and cross-references the scene with the laws of physics (Shadow Analysis).

---

## 🔬 Key Features & Modules

### 1. 💀 Behavioral Profiling (Pose Estimation)
* **Function:** Extracts skeletal landmarks from human subjects in the frame.
* **Purpose:** To identify aggressive stances, weapons, or incapacitated subjects.
* **Tech:** **YOLOv8-Pose** (Ultralytics).

### 2. 👁️ Forensic Explainability (XAI)
* **Function:** Generates "Attention Heatmaps" to visualize exactly which pixels the AI is focusing on.
* **Purpose:** To prove in a legal setting that the AI is detecting the actual subject and not background noise (avoiding "Hallucinations").
* **Tech:** **EigenCAM** (Principle Component Analysis for Computer Vision). *Note: We use EigenCAM instead of standard Grad-CAM as it performs significantly better on object detection models like YOLO.*

### 3. ☀️ Chronos: Temporal Integrity Check
* **Function:** Verifies the validity of the timestamp by calculating the sun's position.
* **Purpose:** To detect "Temporal Spoofing" (e.g., claiming a video is from Noon when shadows suggest 5:00 PM).
* **Tech:** **PyEphem**. This library performs high-precision astronomical calculations (using VSOP87 algorithms comparable to those used by NASA) to determine the exact Azimuth and Altitude of the sun for any specific Lat/Lon and time.

### 4. 🔐 Digital Integrity Suite
* **Function:** Performs deep file analysis to detect tampering.
* **Sub-features:**
    * **Chain of Custody:** Generates **SHA-256** hash fingerprints.
    * **Metadata Extraction:** Scans for hidden EXIF data (Camera model, Software tags).
    * **ELA (Error Level Analysis):** Visualizes JPEG compression differences to spot "Deepfakes" or spliced objects.

### 5. 📝 Automated Case Report
* **Function:** Aggregates all mathematical findings into a formal Police Report.
* **Tech:** **Google Gemini 2.5 Flash** (Multimodal LLM).
* **Output:** Downloadable PDF Dossier with dynamic timestamps.

---

## 🛠️ Technology Stack (Under the Hood)

This project relies on a robust stack of Python libraries:

| Category | Library | specific Usage |
| :--- | :--- | :--- |
| **Frontend** | `streamlit` | Interactive web dashboard and UI state management. |
| **Computer Vision** | `ultralytics` | **YOLOv8** model for human detection and pose estimation. |
| **Explainability** | `grad-cam` | Implementation of **EigenCAM** (Eigen Class Activation Maps) for heatmap generation. |
| **Astrophysics** | `ephem` | High-precision astronomy library for solar positioning. |
| **LLM Reasoning** | `google-generativeai` | Interface for **Gemini 2.5 Flash** to analyze visual context and logic. |
| **Forensics** | `hashlib`, `PIL` | SHA-256 hashing, Metadata extraction, and Error Level Analysis (ELA). |
| **Reporting** | `fpdf` | Programmatic generation of forensic PDF reports. |
| **Image Processing** | `opencv-python` | Image manipulation and tensor preprocessing. |

---

## 🚀 Installation & Setup

### 1. Prerequisites
* Python 3.9+
* A Google Cloud API Key (for Gemini 2.5)

### 2. Install Dependencies
```bash
pip install streamlit ultralytics google-generativeai opencv-python-headless ephem grad-cam fpdf

```

### 3. Configure API Key
* Create a .streamlit/secrets.toml file in the root directory:

```bash
GOOGLE_API_KEY = "your_actual_api_key_here"
```

### 4. Run the Application

```bash
streamlit run main.py
```

### 📂 Project Structure

```bash
├── main.py                 # The central dashboard logic
├── modules/
│   ├── profiler.py         # YOLO Skeleton tracking
│   ├── explainability.py   # EigenCAM Heatmap engine
│   ├── chronos.py          # Sun/Shadow Physics engine
│   ├── integrity.py        # ELA, Hashing, Metadata tools
│   └── llm_analyzer.py     # Gemini Report generator
├── assets/                 # Storage for evidence and temp files
└── README.md               # Documentation

```

### ⚖️ Disclaimer

This tool is a Proof of Concept (PoC) designed for educational and research purposes in the field of Digital Forensics and AI Safety. While it utilizes professional-grade algorithms, the results (especially Shadow Analysis and ELA) should be used as corroborating evidence, not definitive proof in a court of law.
