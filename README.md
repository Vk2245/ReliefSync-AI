# 🛡️ ReliefSync-AI

### AI-Powered Crisis Response & Volunteer Coordination Platform

> **Google Solution Challenge 2026** — Smart Resource Allocation Track  
> Data-Driven Volunteer Coordination for Social Impact

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-purple)](https://ai.google.dev)
[![Firebase](https://img.shields.io/badge/Firebase-Auth%20%2B%20Firestore-orange)](https://firebase.google.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🌍 Problem Statement

During disasters, **coordination chaos** kills more people than the disaster itself. NGOs, governments, and relief agencies struggle with:

- **No real-time volunteer matching** — wrong skills sent to wrong locations
- **Manual severity assessment** — delays critical response by hours
- **Resource misallocation** — supplies pile up in one area while others starve
- **Fake volunteers** — unverified individuals compromise relief operations
- **Language barriers** — multilingual communities can't communicate with responders

**ReliefSync-AI solves all of this** using AI-powered automation built on Google Cloud.

---

## 🚀 Key Features

| Feature | Technology | Description |
|---------|-----------|-------------|
| 🔴 **Crisis Severity Prediction** | Gemini 2.0 Flash | Auto-analyzes emergency reports using FEMA/UNDP frameworks |
| 🤝 **AI Volunteer Matching** | Gemini 2.0 Flash | Multi-factor matching: skills, proximity, trust, language |
| 📊 **Resource Demand Forecasting** | Gemini 2.0 Flash | WHO/SPHERE standard-based predictions with confidence scores |
| 🛡️ **Fraud Detection** | Gemini 2.0 Flash | Identifies fake registrations and suspicious behavior |
| 🌐 **Multilingual Communication** | Gemini 2.0 Flash | Crisis-context translation across 100+ languages |
| 🗺️ **Crisis Heatmap** | Google Maps | Real-time geospatial visualization of active emergencies |
| 📈 **Analytics Dashboard** | Chart.js + Firestore | Data-driven insights for strategic decision making |
| 🔐 **Role-Based Access** | Firebase Auth | Citizen, Volunteer, NGO Manager, Admin, Government roles |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (SPA)                        │
│   Dashboard │ Emergencies │ Volunteers │ Map │ AI │ Analytics │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────┐
│                 FASTAPI BACKEND                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │Emergency │ │Volunteer │ │  Task    │ │Analytics │   │
│  │ Router   │ │ Router   │ │ Router   │ │ Router   │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│       └──────┬─────┴──────┬─────┴─────────────┘         │
│              ▼            ▼                              │
│  ┌────────────────┐ ┌──────────────────┐                │
│  │ Gemini AI Svc  │ │ Security Layer   │                │
│  │ • Severity     │ │ • Firebase Auth  │                │
│  │ • Matching     │ │ • RBAC           │                │
│  │ • Forecasting  │ │ • Rate Limiting  │                │
│  │ • Fraud Detect │ │ • Fraud Detect   │                │
│  │ • Translation  │ │                  │                │
│  └────────────────┘ └──────────────────┘                │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                 GOOGLE CLOUD                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │Firestore │ │Firebase  │ │ Gemini   │ │ Google   │   │
│  │   DB     │ │  Auth    │ │2.0 Flash │ │  Maps    │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │Cloud Run │ │BigQuery  │ │Vision AI │ │Speech AI │   │
│  │(Deploy)  │ │(Analytics│ │(Images)  │ │(Voice)   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
ReliefSync-AI/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, Firebase, Security
│   │   ├── models/         # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Gemini AI service
│   │   └── main.py         # FastAPI entry point
│   ├── tests/              # Pytest test suite
│   ├── Dockerfile          # Cloud Run deployment
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
├── frontend/
│   ├── src/
│   │   ├── styles/         # CSS design system
│   │   ├── services/       # API client
│   │   └── app.js          # Main application
│   └── index.html          # SPA entry point
├── docs/                   # Architecture documentation
├── firestore.rules         # Firestore security rules
├── .github/workflows/      # CI/CD pipeline
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla), Chart.js |
| **Backend** | Python 3.12, FastAPI, Pydantic, Uvicorn |
| **AI Engine** | Google Gemini 2.0 Flash via `google-generativeai` SDK |
| **Database** | Cloud Firestore (NoSQL, real-time) |
| **Auth** | Firebase Authentication (email, Google OAuth) |
| **Maps** | Google Maps JavaScript API + Heatmap Layer |
| **Deployment** | Google Cloud Run (containerized) / Render |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Structured logging (structlog) |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.12+
- Google Cloud project with Firestore & Gemini API enabled
- Firebase project configured

### Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env    # Fill in your API keys
uvicorn app.main:app --reload --port 8080
```

### Frontend
```bash
cd frontend
# Open index.html in browser, or use any static server:
python -m http.server 3000
```

### Run Tests
```bash
cd backend
python -m pytest tests/ -v
```

---

## 🔒 Security

- **Firebase Auth** — JWT token verification on every request
- **Role-Based Access Control** — 5 roles with granular permissions
- **Rate Limiting** — Token bucket per IP (100 req/min)
- **Fraud Detection** — AI-powered fake volunteer identification
- **Firestore Rules** — Server-side data access enforcement
- **Input Validation** — Pydantic schemas with strict constraints
- **CORS** — Configurable origin whitelist

---

## 📊 Database Schema

| Collection | Key Fields | Purpose |
|-----------|-----------|---------|
| `users` | uid, role, skills, trust_score, location | Volunteer/user profiles |
| `emergencies` | id, type, severity, location, ai_prediction | Crisis reports |
| `tasks` | id, emergency_id, required_skills, status | Actionable work items |
| `resources` | id, type, quantity, location | Supply tracking |
| `organizations` | id, name, type, verified | NGO/gov registration |
| `escalations` | emergency_id, severity, acknowledged | Auto-escalation queue |

---

## 🤖 AI Capabilities Deep Dive

### 1. Crisis Severity Prediction
- **Input**: Emergency type, description, affected count, location
- **Output**: Severity (low/medium/high/critical), confidence score, recommended resources
- **Framework**: FEMA SLG-101, UNDP disaster classification
- **Fallback**: Deterministic heuristic when AI unavailable

### 2. Volunteer Skill Matching
- **Scoring**: Skills (40%), Trust (25%), Distance (20%), Experience (15%)
- **Geospatial**: Haversine distance filtering
- **Output**: Ranked matches with reasoning

### 3. Resource Demand Forecasting
- **Standards**: WHO/SPHERE humanitarian standards
- **Predictions**: Water (20L/person/day), Food (3 meals/day), Shelter (3.5m²/person)
- **Window**: 1-168 hours ahead

---

## 🚀 Deployment

### Google Cloud Run
```bash
cd backend
gcloud run deploy reliefsync-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=your-project,GEMINI_API_KEY=your-key"
```

### Render (Alternative)
- Connect GitHub repo → Auto-deploy on push
- Set environment variables in Render dashboard

---

## 👥 Team

Built for **Google Solution Challenge 2026** — Smart Resource Allocation Track

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.
