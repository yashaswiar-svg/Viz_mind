# VizMind

**AI-Powered Data Visualization and Pattern Discovery**

VizMind is an intelligent data analysis platform designed to automatically transform raw datasets into an understandable data story through data profiling, preprocessing, automated chart recommendations, pattern discovery, anomaly detection, predictive analytics, and natural-language AI insights.

---

## 1. Problem & Vision

### Problem
Users struggle to understand large complex datasets, choose appropriate visualizations, discover hidden patterns or anomalies, and translate statistical findings into clear, actionable business narratives.

### Vision
VizMind aims to streamline the entire data journey:

```text
```text
Data Upload (Phase 2 - COMPLETED)
    ↓
Data Profiling & Quality Engine (Phase 3 - COMPLETED)
    ↓
Automated Preprocessing Engine (Phase 4 - COMPLETED)
    ↓
Smart Visualization Recommendation (Phase 5 - COMPLETED)
    ↓
Pattern Discovery Intelligence (Phase 6 - COMPLETED)
    ↓
Anomaly Detection & Prediction (Phase 7 - COMPLETED)
    ↓
AI Insight Engine (Phase 8 - COMPLETED)
    ↓
Natural Language Querying (Phase 9 - COMPLETED)
    ↓
Productionization, Security & Auth (Phase 10 - COMPLETED)
```


---

## 2. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.x Async (AsyncPG), Alembic, Pytest, Pandas, NumPy, Scikit-learn, Passlib (Argon2 / bcrypt), PyJWT
- **Frontend**: React 18+, Vite, React Router DOM, Lucide React, Auth Context, Vanilla CSS (Glassmorphism, Dark Mode)
- **Database & Services**: PostgreSQL 16 Alpine Docker Container
- **DevOps**: Docker, Docker Compose, Nginx Reverse Proxy, GitHub Actions CI Workflow

---

## 3. Production Quickstart with Docker

Launch the complete VizMind stack (Frontend SPA + FastAPI Backend + PostgreSQL DB) in containers:

```bash
# 1. Clone repository & configure environment
cp .env.example .env

# 2. Launch production container stack
docker compose up -d --build
```

- Web UI: `http://localhost`
- API Health Check: `http://localhost/api/v1/health/ready`

---

## 4. Local Development Quickstart

### 1. Start PostgreSQL Database
```bash
docker compose up -d db
```

### 2. Run Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/api/v1/docs`

### 3. Run Frontend
```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 5. Running Automated Tests

Run backend test suite:
```bash
cd backend
python -m pytest tests/ -v
```

---

## 6. Key API Endpoints (v1)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new user account | No |
| `POST` | `/api/v1/auth/login` | Login & receive JWT access + refresh tokens | No |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | No |
| `GET` | `/api/v1/auth/me` | Get active user profile | Yes |
| `DELETE` | `/api/v1/auth/me` | Delete user account & purge all data | Yes |
| `POST` | `/api/v1/datasets` | Upload CSV dataset file | Yes |
| `GET` | `/api/v1/datasets` | List owned datasets | Yes |
| `GET` | `/api/v1/datasets/{id}` | Get dataset details | Yes (Owned) |
| `DELETE` | `/api/v1/datasets/{id}` | Delete dataset & storage | Yes (Owned) |
| `POST` | `/api/v1/datasets/{id}/profile` | Generate data quality profile | Yes (Owned) |
| `POST` | `/api/v1/datasets/{id}/preprocess` | Run automated cleaning pipeline | Yes (Owned) |
| `POST` | `/api/v1/datasets/{id}/visualizations` | Recommend Plotly visualizations | Yes (Owned) |
| `POST` | `/api/v1/datasets/{id}/patterns` | Discover statistical patterns | Yes (Owned) |
| `POST` | `/api/v1/datasets/{id}/anomalies` | Detect dataset anomalies | Yes (Owned) |
| `POST` | `/api/v1/datasets/{id}/predictions` | Run forecasting & predictions | Yes (Owned) |
| `POST` | `/api/v1/datasets/{id}/insights` | Generate AI insights narrative | Yes (Owned) |
| `POST` | `/api/v1/datasets/{id}/analyst/conversations` | Create NL query conversation | Yes (Owned) |

---

## 7. Documentation

- [Architecture Guide](file:///c:/Users/Yashaswi%20A%20R/OneDrive/Desktop/vizmind/docs/architecture.md)
- [Deployment Guide](file:///c:/Users/Yashaswi%20A%20R/OneDrive/Desktop/vizmind/docs/deployment.md)
- [Security Guide](file:///c:/Users/Yashaswi%20A%20R/OneDrive/Desktop/vizmind/docs/security.md)
- [Operations Guide](file:///c:/Users/Yashaswi%20A%20R/OneDrive/Desktop/vizmind/docs/operations.md)

---

## 8. License

This project is licensed under the MIT License - see the [LICENSE](file:///c:/Users/Yashaswi%20A%20R/OneDrive/Desktop/vizmind/LICENSE) file for details.


