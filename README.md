# AUTO PDI — Smart Pre-Delivery Vehicle Inspection Platform
> **"Inspect Before You Accept."**  
> *An intelligent marketplace and inspection management platform connecting Car Buyers, Certified PDI Diagnostic Masters, and Dealerships.*

---

## 🌟 Executive Overview & Key Differentiators

**AUTO PDI** transforms the traditional car buying experience by enabling professional, independent Pre-Delivery Inspection (PDI) before customers sign delivery acceptance papers or release remaining financing payments.

Unlike standard car maintenance apps, **AUTO PDI** delivers:
1. **6-Factor Smart Inspector Matching**: Recommends the optimal inspector based on Skill (30%), Verified Equipment (25%), Distance (15%), Experience (10%), Customer Rating (10%), and Real-time Availability (10%).
2. **Vehicle-Specific Dynamic Checklists**: Dynamically adapts inspection items based on vehicle powertrain:
   - **ICE**: Internal combustion engine, transmission fluid, belts, exhaust emissions.
   - **EV**: High-voltage traction battery casing, Battery State of Health (SOH), Type-2 & CCS2 DC fast charging handshake, regenerative braking, high-voltage cable insulation.
   - **Hybrid**: Power split device, high-voltage battery ventilation, EV-mode switch transition.
3. **AI-Assisted Damage & Defect Detection**: Pluggable Computer Vision service detecting clear-coat scratches, panel dents, paint thickness anomalies (orange peel/repaints), glass stress chips, and uneven panel gaps.
4. **Human-in-the-Loop Verification**: Clearly designated *"AI-Assisted Finding — Requires Inspector Verification"* requiring certified inspector confirmation (**CONFIRM** / **REJECT**) before altering vehicle scores.
5. **Timestamped & Geotagged Evidence**: High-resolution evidence capture with browser GPS latitude/longitude and EXIF timestamps.
6. **Weighted Vehicle Readiness Score**: Automotive engineering weighted formula:
   $$\text{Readiness Score} = (\text{Ext} \times 0.20) + (\text{Int} \times 0.15) + (\text{Mech} \times 0.25) + (\text{Elec} \times 0.15) + (\text{Safety} \times 0.15) + (\text{Docs} \times 0.10)$$
   - **90–100**: `DELIVERY_READY` (Green)
   - **75–89**: `ATTENTION_REQUIRED` (Amber/Yellow)
   - **Below 75**: `HOLD_DELIVERY` (Red)
7. **Dealer Issue Resolution Workflow**: Automatically logs issues for flagged checkpoints through an actionable timeline: `OPEN` → `DEALER_NOTIFIED` → `IN_PROGRESS` → `RESOLVED` → `CUSTOMER_VERIFIED`.
8. **Cryptographically Hashed Digital Certificate**: Generates tamper-proof PDF reports using **ReportLab** embedded with SHA-256 integrity hashes and unique verification codes.
9. **Public Verification Portal**: Instant authenticity verification at `/verify/<verification_code>` without exposing customer privacy.
10. **Offline-Friendly Checkpoint Storage**: LocalStorage caching allowing showroom floor inspection drafting during cellular blind spots.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Backend** | Python 3.11+, Flask 3.1, Flask-SQLAlchemy 3.1, Werkzeug (PBKDF2 Password Hashing), PyMySQL, ReportLab 5.0, Pillow 12.3 |
| **Frontend** | HTML5, CSS3, Vanilla Modern JavaScript (ES6+), Fetch API, Bootstrap 5.3 (CDN), Bootstrap Icons (CDN), Chart.js (CDN) |
| **Design System**| Custom Unique Light Theme (Clean Arctic White `#FFFFFF`, Slate `#F8FAFC`, Deep Obsidian Navy `#0F172A`, Electric Blue `#2563EB`) |
| **Database** | MySQL 8+ (or SQLite zero-friction local development) via SQLAlchemy ORM |
| **AI Subsystem** | `services/ai_service.py` (Heuristic demo engine + pluggable Vision API abstraction) |

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- **Python**: Version 3.11 or 3.12 installed (`python --version`)
- **MySQL 8+** (Optional if running on MySQL, or use built-in SQLite fallback)
- **Git**

### 2. Clone or Navigate to Directory
```powershell
cd c:\Users\manid\Downloads\hackathon\AUTOPDI
```

### 3. Setup Virtual Environment (Recommended)
```powershell
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Configure Environment Variables (`.env`)
Copy `.env.example` to `.env` (or customize database connection):
```env
SECRET_KEY=autopdi-super-secret-production-key-2026-secure

# MySQL Database (Create database 'autopdi' first in MySQL):
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/autopdi

# Or Local SQLite Database (Default for zero-friction local testing):
DATABASE_URL=sqlite:///autopdi.db

AI_API_KEY=
UPLOAD_FOLDER=uploads
FLASK_ENV=development
DEBUG=True
PORT=5000
```

### 6. Initialize & Seed Realistic Automotive Demo Data
```powershell
python database/seed.py
```

### 7. Run the Application Server
```powershell
python app.py
```
Open **http://localhost:5000** in your browser.

---

## 🔑 Demo Login Credentials

| Role | Email | Password | Pre-seeded Context |
|---|---|---|---|
| **Customer** | `customer@autopdi.com` | `Customer@123` | Hyundai Creta, Tata Nexon EV, Completed PDI Report, Active Bookings |
| **Inspector** | `inspector@autopdi.com` | `Inspector@123` | Arun Kumar (8 yrs exp, 1,240 PDIs, 4.9★, Paint Gauge, OBD-II Scanner) |
| **Admin** | `admin@autopdi.com` | `Admin@123` | Full analytics dashboard, 5 Chart.js charts, inspector approval console |

---

## 🧠 Smart Algorithms & Technical Details

### A. 6-Factor Smart Inspector Matching Formula
The recommendation engine evaluates inspectors against a selected vehicle, showroom coordinates, and service package:

$$\text{Match Score} = (\text{Skill} \times 0.30) + (\text{Equipment} \times 0.25) + (\text{Distance} \times 0.15) + (\text{Experience} \times 0.10) + (\text{Rating} \times 0.10) + (\text{Availability} \times 0.10)$$

- **Skill Score (30%)**: Matches powertrain specialization (`EV`, `ICE`, `HYBRID`) and manufacturer brand expertise.
- **Equipment Score (25%)**: Validates verified inventory against package requirements (Paint Depth Gauge, OBD-II scanner, Battery tester, Thermal camera, EV Diagnostic Scanner).
- **Distance Score (15%)**: Computes Haversine great-circle distance between inspector GPS and showroom coordinates ($100\%$ at $\le 3\text{km}$).
- **Experience Score (10%)**: Scaled linearly ($10+\text{ years} = 100\%$).
- **Rating Score (10%)**: Scaled 0–5 stars to 0–100%.
- **Availability Score (10%)**: `AVAILABLE` ($100\%$), `BUSY` ($40\%$), `OFFLINE` ($10\%$).

### B. AI Damage Detection Service Architecture (`services/ai_service.py`)
```
+-------------------+      +-------------------------+      +-------------------------------+
| Checkpoint Image  | ---> |   services/ai_service   | ---> | Output: Finding, Confidence,  |
|  & Component Name |      |   (AIService Layer)     |      | Severity & Recommended Action |
+-------------------+      +-------------------------+      +-------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
     [Cloud Vision / Gemini AI]                  [Heuristic Hackathon Engine]
     (When API Key is Configured)                (Deterministic Demo Detection)
```
- **Deterministic Patterns**:
  - `*scratch*` → Clear-coat surface scratch detection (Confidence: 91%, Severity: `LOW`).
  - `*dent*` → Sheet metal contour pressure dent (Confidence: 88%, Severity: `MEDIUM`).
  - `*paint*` / `*mismatch*` → Paint thickness & texture orange peel variance (Confidence: 93%, Severity: `MEDIUM`).
  - `*crack*` / `*glass*` → Windshield radial stress chip (Confidence: 95%, Severity: `HIGH`).
  - `*gap*` / `*align*` → 2.4mm panel gap seam variance (Confidence: 86%, Severity: `MEDIUM`).

---

## 🗄️ Database Architecture & Relationships

```
 users (1) <---+--- (N) vehicles (1) <---+--- (N) bookings (1) <--- (1) inspections (1) <---+--- (N) checkpoints
               |                         |                                                  |
               +--- (1) inspectors (1) <-+                                                  +--- (N) media
                                                                                            |
                                                                                            +--- (N) ai_findings
                                                                                            |
                                                                                            +--- (1) reports
                                                                                            |
                                                                                            +--- (N) issue_resolution
```

- `User`: Base user identity with secure PBKDF2 password hashes and roles (`CUSTOMER`, `INSPECTOR`, `ADMIN`).
- `Vehicle`: Customer vehicle records categorized by powertrain (`ICE`, `EV`, `HYBRID`) and unique VIN.
- `Showroom`: Dealership physical facilities with GPS coordinates.
- `Inspector`: Extended professional profile linked 1-to-1 with User, storing ratings, trust score, and availability.
- `Equipment` & `Certification`: Verified tool inventory and credentials linked to Inspector.
- `Booking`: Scheduled inspection appointment linking Customer, Vehicle, Showroom, and Inspector.
- `Inspection`: Live inspection workflow instance storing VIN verification flag, timestamps, overall score, final status, and verification code.
- `InspectionCheckpoint`: Individual inspection items dynamically instantiated per vehicle type.
- `InspectionMedia`: Evidence photographs stored with captured timestamps and GPS metadata.
- `AIFinding`: Defect predictions with human inspector confirmation status (`CONFIRMED` / `REJECTED`).
- `Report`: Finalized ReportLab PDF record with SHA-256 hash and unique verification code.
- `IssueResolution`: Automated dealer repair tickets for `ATTENTION` / `FAIL` findings.

---

## 📋 Complete REST API Documentation

### 1. Authentication
- `POST /api/auth/register` — Register a customer or inspector account.
- `POST /api/auth/login` — Authenticate and start secure session.
- `POST /api/auth/logout` — Terminate session.
- `GET /api/auth/me` — Retrieve current authenticated user profile.

### 2. Customer & Vehicles
- `GET /api/customer/dashboard` — Get customer KPI stats, upcoming bookings, and recent reports.
- `GET /api/vehicles` — List customer's vehicles.
- `POST /api/vehicles` — Register a new vehicle.
- `GET /api/vehicles/:id` — Get specific vehicle details.
- `DELETE /api/vehicles/:id` — Remove vehicle.

### 3. Bookings & Smart Matching
- `GET /api/showrooms` — List available dealership showrooms.
- `GET /api/inspectors/match` — Run 6-factor algorithm and rank recommended inspectors.
- `POST /api/bookings` — Create a new PDI inspection booking.
- `GET /api/bookings` — List bookings for current user role.
- `GET /api/bookings/:id` — Get booking details.
- `POST /api/bookings/:id/accept` — Inspector accepts booking and initializes inspection record.
- `POST /api/bookings/:id/reject` — Inspector declines booking.
- `PUT /api/bookings/:id/cancel` — Cancel booking.

### 4. Live Inspection Console
- `GET /api/inspections/:id` — Fetch live inspection state, grouped checklist, and score preview.
- `POST /api/inspections/:id/verify-vin` — Physically verify vehicle chassis VIN.
- `POST /api/inspections/:id/start` — Start inspection and activate timer.
- `PUT /api/inspections/:id/checkpoint` — Update checkpoint status (`PASS`/`ATTENTION`/`FAIL`) and remarks.
- `POST /api/inspections/:id/photo` — Upload geotagged evidence photograph.
- `POST /api/inspections/:id/ai-analysis` — Trigger AI computer vision analysis on photo.
- `POST /api/inspections/:id/ai-confirm` — Inspector confirms or rejects AI finding.
- `POST /api/inspections/:id/complete` — Finalize inspection, compute readiness score, and generate PDF report.

### 5. Reports & Public Verification
- `GET /api/verify/:code` — Public endpoint verifying report authenticity and integrity hash.
- `GET /reports/:inspection_id/pdf` — Download official ReportLab PDF certificate.
- `POST /api/ratings` — Customer submits inspector review and updates inspector trust score.

### 6. Dealer Issue Resolution
- `GET /api/issues` — List flagged issues for customer, inspector, or dealer.
- `PUT /api/issues/:id/status` — Update dealer repair status (`DEALER_NOTIFIED`, `IN_PROGRESS`, `RESOLVED`).
- `PUT /api/issues/:id/verify` — Customer verifies and signs off on corrected issue.

### 7. Admin Platform Governance
- `GET /api/admin/dashboard` — Platform KPIs and 5 Chart.js datasets.
- `GET /api/admin/inspectors` — List all inspectors with verification status.
- `PUT /api/admin/inspectors/:id/approve` — Approve inspector application.
- `PUT /api/admin/inspectors/:id/reject` — Reject inspector application.
- `PUT /api/admin/inspectors/:id/suspend` — Suspend inspector.
- `PUT /api/admin/equipment/:id/verify` — Verify inspector tool.
- `PUT /api/admin/certifications/:id/verify` — Verify inspector certificate.
- `GET /api/admin/users` — List platform users.

---

## 🎬 21-Step Complete Hackathon Demo Walkthrough

Follow these exact steps during the live demo presentation:

1. **Open App**: Visit `http://localhost:5000` to view the modern automotive light theme landing page.
2. **Customer Login**: Click "Sign In" and click the quick demo button **Customer** (`customer@autopdi.com` / `Customer@123`).
3. **Start Booking**: Click **Book New PDI** in the dashboard.
4. **Step 1 (Vehicle)**: Select the pre-seeded **Hyundai Creta SX(O)** (or click *Add New Vehicle*).
5. **Step 2 (Showroom)**: Select **ABC Hyundai Flagship** (Indiranagar, Bangalore).
6. **Step 3 (Schedule)**: Select inspection date and time slot (10:00 AM).
7. **Step 4 (Package)**: Select **Premium PDI** (AI-assisted with paint thickness check).
8. **Step 5 (Smart Matching)**: View the recommended inspectors ranked by the 6-factor algorithm. Note **Arun Kumar** at **96% Match**.
9. **Step 6 (Confirm)**: Click **Confirm & Book PDI**.
10. **Sign Out**: Sign out of the customer account.
11. **Inspector Login**: Sign in as **Inspector** (`inspector@autopdi.com` / `Inspector@123`).
12. **Accept Request**: View the incoming request on the Inspector Workspace and click **Accept**.
13. **Launch Console**: Click **Launch Inspection** to open the live console.
14. **VIN Verification**: Enter VIN `DEMOVIN123456` and click **Verify VIN** → Displays `Vehicle Verified ✓`.
15. **Start Inspection**: Click **START INSPECTION** → Timer begins ticking.
16. **Dynamic Checklist**: Cycle through categories (*Exterior, Paint, Glass, Engine, Road Test*). Set items to `PASS`, `ATTENTION`, and `FAIL`.
17. **Capture & AI Scan**: In *Paint*, upload `front_bumper_scratch.jpg` and click **Run AI Analyze**.
18. **Human Verification**: Observe the AI finding card: *"Possible Scratch (91% Confidence)"*. Click **Confirm Finding**.
19. **Complete Inspection**: Click **Complete Inspection** → System computes Readiness Score of **88/100 (ATTENTION REQUIRED)** and auto-generates the tamper-proof PDF report.
20. **Customer View & PDF**: Log in as Customer → Open the generated report, view scores, download the official PDF, and rate Arun Kumar 5 stars.
21. **Public Verification & Admin**: Visit `/verify/PDI-2026-X8Y9Z` to demonstrate public verification, then log in as Admin (`admin@autopdi.com`) to view live Chart.js analytics!

---

## 🧪 Running Automated Tests

Run the complete pytest test suite:
```powershell
python -m pytest tests/ -v
```
All unit tests covering Authentication, Booking Workflows, 6-Factor Smart Matching, EV Dynamic Checklists, and Readiness Scoring will execute and pass.

---

## 🔮 Future Enhancements
- **OBD-II Bluetooth Dongle Web-Serial API**: Direct telemetry live streaming into browser during road test.
- **Edge Vision AI on Mobile**: Client-side TensorFlow.js inference for offline real-time scratch contour segmentation.
- **Blockchain Certificate Notarization**: Polygon / Hyperledger anchoring for tamper-proof dealership PDI certificates.

---
*Built with ❤️ for the Automotive & Smart Systems Hackathon.*
