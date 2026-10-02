# Suez Canal Official Tonnage Measurement Calculator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![SCA Compliant](https://img.shields.io/badge/compliance-SCA%20Rules%20of%20Navigation-green.svg)](https://www.suezcanal.gov.eg)
[![ReportLab](https://img.shields.io/badge/reports-ReportLab%20A4%20PDF-orange.svg)](https://www.reportlab.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An official, regulation-grade marine software application for computing **Suez Canal Gross Tonnage (SCGT)** and **Suez Canal Net Tonnage (SCNT)** in strict compliance with the **Suez Canal Authority (SCA) Rules of Navigation (Articles 92–94 and Appendix 1)**.

---

### 🌐 Live Public Link
You can test and use the application directly online at:  
👉 **[https://7d08c23f8ee025.lhr.life](https://7d08c23f8ee025.lhr.life)**

---

## 📌 Key Capabilities & Calculation Modules

1. **Underdeck Tonnage (UDT) Calculation**:
   - Simpson's 1st Rule longitudinal integration across **21 transverse stations** (Stations 0 to 20, with half-stations at ends).
   - 16 vertical intervals per station ($h = D / 16$) using Simpson's multipliers `[1, 4, 2, 4, ... , 1]`.
   - Transom stern volume integration aft of AP.
   - Exact conversion using the statutory Suez Moorsom standard:
     $$\text{Suez Moorsom Tonnage} = \frac{\text{Volume in m}^3}{2.832}$$

2. **Bulbous Bow Appendage (SCA Method A)**:
   - Longitudinal Simpson integration through transverse stations ($St.\ 20$, $St.\ A$, and $St.\ B$).
   - Forward conical/ellipsoidal nose cap volume:
     $$V_{\text{nose}} = \frac{\pi}{6} \times A_B \times L_{\text{nose}}$$

3. **Forecastle Deck Tonnage**:
   - Integration of enclosed forecastle space forward of the collision bulkhead with camber corrections.

4. **Cargo Hatchways Excess (SCA 0.5% Rule)**:
   - Aggregates all weather deck cargo hatch coamings.
   - Automatically computes statutory exemption:
     $$V_{\text{allowance}} = 0.5\% \times \text{Gross Tonnage Volume}$$
     $$\text{Excess Tonnage Volume} = \max(0,\, V_{\text{hatch}} - V_{\text{allowance}})$$

5. **Enclosed Superstructures & Round Houses**:
   - Complete 53-compartment scheduler including navigation bridge, crew quarters, officer accommodations, galley, workshops, and engine casing with form factors ($k$).

6. **Statutory Deductions & Net Tonnage**:
   - Master, officers, and crew accommodation spaces.
   - Spaces used in working the ship (chart room, radio room, wheelhouse, steering gear, boatswain's stores).
   - Propelling power deduction adhering to SCA statutory caps ($\le 50\%$ Gross Tonnage).

7. **Official A4 Portrait PDF & HTML Report Generator**:
   - Standardized **100% Times New Roman** typography.
   - Proper superscript scientific units ($\text{m}^2, \text{m}^3$).
   - Compact multi-table natural layout (zero empty pages).
   - Summary note detailing **"What was done"** (engineering procedures) and **"What was obtained"** (exact volumes and tonnages).

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/rokibul-mist/Suez-Canal-Tonnage-Calculator.git
cd Suez-Canal-Tonnage-Calculator
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python app.py
```
Or double-click `run_tool.bat` on Windows.

Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 📂 Sample Calculation Workbooks Included

The `sample_data/` folder contains reference Excel workbooks matching official shipyard data (e.g. *M/V TERVEL*):
- `Bulbous_Bow_Tonnage_Calculation.xlsx`
- `Forecastle_Deck_Tonnage_Calculation.xlsx`
- `Hatch_Coaming_Tonnage_Calculation.xlsx`
- `Superstructure_Tonnage_Calculation.xlsx`
- `Suez_Shipyard_Offsets_Calculator.xlsx`
- `Suez_Offset_Template_M_V_TERVEL.xlsx`
- `Suez_Canal_Official_Calculation_Report_Sample.pdf` (Pre-generated 19-page official report)

---

## 🌐 Deploy to Cloud (Free 1-Click Hosting)

You can easily deploy this tool to cloud hosting platforms like **Render**, **Railway**, or **Hugging Face Spaces**:

### Deploy on Render:
1. Fork or push this repository to GitHub.
2. Sign in to [Render](https://render.com) and click **New Web Service**.
3. Select this repository.
4. Set:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Click **Deploy Web Service** to get a public URL for your application.

---

## 📜 Regulatory Standards & References
- **Suez Canal Authority (SCA)**: *Rules of Navigation*, Part IV: Tonnage Measurement (Arts. 92–94 & Appendix 1).
- **International Commission of Constantinople (1873)**: Standard Suez Moorsom Measurement Rules.
- **IMO International Convention on Tonnage Measurement of Ships (1969)**.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
