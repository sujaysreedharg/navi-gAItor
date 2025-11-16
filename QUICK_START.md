# QUICK START GUIDE - Mission Debrief AI

## ⚡ 30-SECOND SETUP

```bash
# 1. Clone/navigate to project
cd mission-debrief-ai

# 2. Set API keys
echo "GEMINI_API_KEY=AIza..." > .env
echo "YOUCOM_API_KEY=you_..." >> .env

# 3. Start backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000 &

# 4. Start frontend (new terminal)
cd frontend
npm install
npm run dev

# 5. Open browser
open http://localhost:5173
```

---

## 📋 PREREQUISITES

### Required:
- **Python 3.9+** → [Download](https://www.python.org/downloads/)
- **Node.js 18+** → [Download](https://nodejs.org/)
- **Git** → [Download](https://git-scm.com/)

### API Keys:
1. **Gemini API Key**
   - Go to: https://aistudio.google.com/apikey
   - Click "Create API key"
   - Copy key starting with `AIza...`

2. **You.com Search API Key**
   - Go to: https://you.com/api
   - Sign up for API access
   - Copy key starting with `you_...`

---

## 🚀 STEP-BY-STEP SETUP

### Step 1: Project Structure

```bash
mkdir mission-debrief-ai
cd mission-debrief-ai

mkdir -p backend/app
mkdir -p frontend/src/{components,types,utils}
mkdir -p data/sample_flights
```

### Step 2: Environment Variables

Create `.env` in project root:
```env
GEMINI_API_KEY=AIza_your_actual_key_here
YOUCOM_API_KEY=you_your_actual_key_here
```

### Step 3: Backend Setup

#### Install Dependencies
```bash
cd backend

# Create requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
pandas==2.1.3
python-dotenv==1.0.0
requests==2.31.0
google-genai==0.2.0
python-multipart==0.0.6
EOF

# Create virtual environment
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
# venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

#### Copy Backend Code

**From the full build prompt** (`COMPLETE_BUILD_PROMPT.md`), copy:
- `backend/app/flight_parser.py` → Section 1.2
- `backend/app/events.py` → Section 1.3
- `backend/app/you_client.py` → Section 1.4
- `backend/app/gemini_client.py` → Section 1.5
- `backend/app/main.py` → Section 1.6

**Quick extraction**:
```bash
# If you have the COMPLETE_BUILD_PROMPT.md file
# Extract code blocks programmatically or manually copy
```

#### Test Backend
```bash
# Run server
uvicorn app.main:app --reload --port 8000

# Test in browser
open http://localhost:8000/docs
```

### Step 4: Frontend Setup

#### Install Dependencies
```bash
cd frontend

# Initialize Vite + React + TypeScript
npm create vite@latest . -- --template react-ts
npm install

# Install additional packages
npm install recharts axios
```

#### Copy Frontend Code

**From the full build prompt**, copy:
- `frontend/src/types/index.ts` → Section 2.2
- `frontend/src/App.tsx` → Section 2.3
- `frontend/src/components/FlightChart.tsx` → Section 2.4
- `frontend/src/components/EventsList.tsx` → Section 2.5
- `frontend/src/components/DebriefPanel.tsx` → Section 2.6
- `frontend/src/App.css` → Section 2.7

#### Test Frontend
```bash
# Run dev server
npm run dev

# Open in browser
open http://localhost:5173
```

---

## 🧪 TEST WITH SAMPLE DATA

### Option 1: Use Provided Sample

```bash
# Copy from your navi-gAItor folder
cp /Users/sujay/Documents/navi-gAItor/100_flights_avionics_only/data_log/log_231113_191632_KSQL.csv ./data/sample_flights/

# Or any flight with actual movement:
# Look for files where altitude changes significantly
```

### Option 2: Find Best Test Files

```bash
# List available flights
ls -lh /Users/sujay/Documents/navi-gAItor/100_flights_avionics_only/data_log/

# Good candidates (based on naming):
# - log_240428_095032_KSFO.csv (SFO departure)
# - log_240409_125301_KSQL.csv (San Carlos)
# - Any with recognizable airport codes
```

### Upload via UI

1. Open http://localhost:5173
2. Click file input
3. Select CSV file
4. Click "Analyze Flight"
5. Wait 10-30 seconds for processing
6. Review results!

---

## 🐛 COMMON ISSUES & FIXES

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Activate venv first
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Error**: `ValueError: Gemini API key not found`
```bash
# Solution: Load environment variables
export $(cat .env | xargs)
# or add to run command:
uvicorn app.main:app --reload --port 8000 --env-file ../.env
```

### Frontend Won't Start

**Error**: `Cannot find module 'recharts'`
```bash
# Solution: Install dependencies
cd frontend
npm install
```

**Error**: CORS error in browser console
```bash
# Solution: Ensure backend is running on port 8000
# Check CORS middleware in backend/app/main.py is configured
```

### API Errors

**Error**: `Gemini API error: 403 Forbidden`
```bash
# Solution: Verify API key is correct
# Check quota at: https://aistudio.google.com/
```

**Error**: `You.com API timeout`
```bash
# Solution: This is handled gracefully
# The app will continue without references
# Check YOUCOM_API_KEY is valid
```

---

## 📦 FILE STRUCTURE REFERENCE

```
mission-debrief-ai/
├── .env                          # API keys (DO NOT COMMIT)
├── .gitignore                    # Ignore venv, .env, etc.
├── README.md                     # Project documentation
├── COMPLETE_BUILD_PROMPT.md      # Full build instructions
├── DATA_ANALYSIS_SUMMARY.md      # Data analysis details
├── QUICK_START.md                # This file
│
├── backend/
│   ├── requirements.txt          # Python dependencies
│   ├── venv/                     # Virtual environment (git ignored)
│   └── app/
│       ├── __init__.py           # Package marker
│       ├── main.py               # FastAPI app
│       ├── flight_parser.py      # CSV parsing logic
│       ├── events.py             # Event detection
│       ├── you_client.py         # You.com API client
│       └── gemini_client.py      # Gemini AI client
│
├── frontend/
│   ├── package.json              # NPM dependencies
│   ├── package-lock.json         # Locked versions
│   ├── vite.config.ts            # Vite configuration
│   ├── tsconfig.json             # TypeScript config
│   ├── index.html                # Entry HTML
│   ├── public/                   # Static assets
│   └── src/
│       ├── main.tsx              # React entry point
│       ├── App.tsx               # Main App component
│       ├── App.css               # Styling
│       ├── types/
│       │   └── index.ts          # TypeScript interfaces
│       └── components/
│           ├── FlightChart.tsx   # Chart component
│           ├── EventsList.tsx    # Events display
│           └── DebriefPanel.tsx  # AI debrief display
│
└── data/
    └── sample_flights/           # Test CSV files
        └── *.csv
```

---

## 🎯 VERIFICATION CHECKLIST

### Backend Running ✅
- [ ] Navigate to http://localhost:8000
- [ ] See: `{"service":"Mission Debrief AI","version":"1.0.0","status":"operational"}`
- [ ] Navigate to http://localhost:8000/docs
- [ ] See: Interactive API documentation

### Frontend Running ✅
- [ ] Navigate to http://localhost:5173
- [ ] See: "✈️ Mission Debrief AI" header
- [ ] See: File upload interface
- [ ] No console errors

### Full Integration ✅
- [ ] Upload a CSV file
- [ ] Click "Analyze Flight"
- [ ] See loading state
- [ ] See results after ~10-30 seconds:
  - [ ] Summary cards with stats
  - [ ] Flight profile chart
  - [ ] Events list
  - [ ] AI-generated debrief

---

## 🚢 DEPLOYMENT (Optional)

### Local Docker (Recommended for Testing)

```bash
# Build and run with docker-compose
docker-compose up --build

# Access at: http://localhost
```

### Google Cloud Run (For Hackathon Submission)

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project (use your GCP project ID)
gcloud config set project YOUR_PROJECT_ID

# Deploy backend
cd backend
gcloud run deploy mission-debrief-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,YOUCOM_API_KEY=$YOUCOM_API_KEY

# Note the URL (e.g., https://mission-debrief-backend-xxx-uc.a.run.app)

# Update frontend API URL
# In frontend/src/App.tsx, change:
# const API_URL = 'http://localhost:8000';
# to:
# const API_URL = 'https://mission-debrief-backend-xxx-uc.a.run.app';

# Deploy frontend
cd frontend
npm run build
gcloud run deploy mission-debrief-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Note the frontend URL for demo!
```

---

## 💡 NEXT STEPS

1. **Test thoroughly** with multiple CSV files
2. **Customize event detection** thresholds
3. **Refine AI prompts** for better debriefs
4. **Add error handling** for edge cases
5. **Optimize performance** (caching, async)
6. **Prepare demo** (select best sample flight)
7. **Create presentation** (slides + talking points)
8. **Deploy online** (for hackathon submission)

---

## 📞 HELP & RESOURCES

### Documentation:
- **Full Build Instructions**: `COMPLETE_BUILD_PROMPT.md`
- **Data Analysis**: `DATA_ANALYSIS_SUMMARY.md`
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Recharts**: https://recharts.org/

### Debugging:
1. **Check logs**: Both backend and frontend consoles
2. **Test API endpoints**: Use http://localhost:8000/docs
3. **Verify data**: Print/log parsed DataFrames
4. **Simplify**: Comment out AI calls to test parsing alone

### Getting Unstuck:
1. Read error messages carefully
2. Check environment variables are loaded
3. Verify API keys are valid
4. Test with simplest possible CSV first
5. Check network requests in browser DevTools

---

## 🎉 SUCCESS!

If you can:
1. ✅ Upload a CSV
2. ✅ See a chart with flight data
3. ✅ See detected events
4. ✅ See an AI-generated debrief

**You're ready to demo! 🚀**

---

**Total setup time**: ~30-60 minutes (first time)  
**Rebuild time**: ~5 minutes (with code already written)

Good luck at the hackathon! ✈️

