---

# 🧠 SHL Assessment Recommendation Engine

### **FastAPI + FAISS + Streamlit + PostgreSQL**

### Intelligent Assessment Recommendation System (Built with Python)

---

## 📌 Overview

This project is an end-to-end **Assessment Recommendation Engine** that recommends SHL-style assessments based on:

✔ Job role
✔ Job family / job level
✔ Required constructs (cognitive ability, personality, SJT, motivation, etc.)
✔ Hiring volume
✔ Time constraints
✔ Job description text / uploaded resume
✔ Language & delivery constraints

The engine combines:

* **Rule-based I/O Psychology logic**
* **Semantic similarity (FAISS + Sentence Transformers)**
* **Database-backed product catalog (PostgreSQL)**
* **Interactive web UI (Streamlit)**
* **PDF export, logs, analytics & admin panel**

This is designed as a **production-ready prototype** that can easily be extended with real SHL product data.

---

# 🏗 Architecture

```
                   ┌───────────────┐
                   │   Streamlit   │
                   │ (User Frontend│
                   │ + Admin + PDF │
                   └───────┬───────┘
                           │ REST calls
                           ▼
                ┌────────────────────────┐
                │        FastAPI          │
                │  Recommendation Engine  │
                └───────┬────────────────┘
                        │
     ┌──────────────────┼────────────────────┐
     ▼                  ▼                    ▼
FAISS Vector Store   Rule Engine       PostgreSQL (Products + Logs)
 (Semantic Match)   (Blueprinting)        (Persistent Storage)
```

---

# 🌟 Key Features

### 🔍 **AI-Semantic Matching (FAISS)**

Matches job descriptions / resumes with relevant SHL assessments using vector search.

### 🎯 **Assessment Blueprinting Engine**

I/O psychology rules determine:

* Cognitive tests
* SJTs
* Personality (OPQ)
* Motivation (MQ)

### 🧮 **Scoring & Ranking Engine**

Each assessment is scored using:

* Construct match
* Job family relevance
* Job level
* Use case (selection/development)
* Duration vs constraints
* Semantic similarity

### 📊 **Interactive Web Frontend (Streamlit)**

* Upload job descriptions or resumes (PDF/TXT)
* Enter role requirements
* View recommended SHL-style assessment bundle
* Download PDF
* Admin: View products, analytics

### 🗄 **PostgreSQL Database**

* Stores assessments
* Logs all recommendations
* Powers analytics dashboard

### 📄 **PDF Report Export**

Generates a professional PDF summarising the assessment bundle.

### 🐳 **Docker & Docker Compose**

One-command deployment of:

* API
* DB
* Frontend

---

# 🚀 Quickstart

## **1. Clone Repo**

```bash
git clone https://github.com/<your-username>/shl-recommender.git
cd shl-recommender
```

---

## **2. Run with Docker (recommended)**

```bash
docker-compose up --build
```

### 🌐 Access the system:

| Service                  | URL                                                      |
| ------------------------ | -------------------------------------------------------- |
| **Frontend (Streamlit)** | [http://localhost:8501](http://localhost:8501)           |
| **Backend API**          | [http://localhost:8000](http://localhost:8000)           |
| **API Docs (Swagger)**   | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Database (Postgres)**  | localhost:5432                                           |

---

## **3. Run Locally (without Docker)**

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Start backend:

```bash
uvicorn app.main:app --reload
```

### Start frontend:

```bash
streamlit run frontend/streamlit_app.py
```

---

# 🧱 Project Structure

```
shl-recommender/
├─ app/
│  ├─ main.py              # FastAPI entrypoint
│  ├─ models.py            # Pydantic schemas
│  ├─ db.py                # SQLAlchemy engine + session
│  ├─ orm_models.py        # Database ORM models
│  ├─ catalogue.py         # Initial mock SHL seed products
│  ├─ vector_store.py      # FAISS semantic search index
│  ├─ recommender.py       # Rule engine + matching logic
│  ├─ pdf_utils.py         # PDF export utilities
│
├─ frontend/
│  ├─ streamlit_app.py     # Streamlit user/admin/analytics UI
│
├─ docker-compose.yml
├─ Dockerfile
├─ requirements.txt
├─ .env.example
└─ README.md
```

---

# 📦 Backend – API Routes

### **Health Check**

```
GET /health
```

### **Recommend assessments**

```
POST /recommend
```

Input: job info + constraints
Output: recommended products + reasons + scores

### **Download recommendation PDF**

```
POST /recommend/pdf
```

### **Admin – list products**

```
GET /admin/products
```

### **Admin – recommendation analytics**

```
GET /admin/analytics
```

---

# 🎨 Frontend Screens (Streamlit)

### ✔ Recommender UI

* Upload resume/JD
* Enter job metadata
* Choose constructs
* Generate bundle
* Download PDF

### ✔ Admin View

* View all stored SHL products

### ✔ Analytics View

* Total recommendations
* Stats by job family

---

# 🔧 Tech Stack

### Backend

* **Python FastAPI**
* **FAISS** (semantic nearest-neighbor search)
* **Sentence Transformers** (MiniLM-L6-v2)
* **SQLAlchemy + PostgreSQL**
* **Uvicorn**

### Frontend

* **Streamlit**

### DevOps

* **Docker**
* **docker-compose**

---

# 📚 Future Improvements

* Add **authentication** for admin routes
* Replace mock catalogue with **real SHL product dataset**
* Add **client-specific configuration**
* Add **ML model** (e.g., LightGBM) trained on historical outcomes
* Add **role ontology + competency models**
* Add **report styling (logos, theming)**
* Add **multi-language UI**

---

# 🤝 Contributing

Pull requests are welcome!
If you’d like new features (AI scoring, embeddings retraining, etc.), feel free to open an issue.

---

# 📝 License

This project is licensed under the **MIT License**.
You may modify and use it for personal or commercial purposes.
