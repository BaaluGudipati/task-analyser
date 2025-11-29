# Task Analyzer

A smart priority management tool that analyzes tasks using a multi‑factor scoring algorithm with support for urgency, importance, effort, dependencies, and multiple strategy modes.

---

##  Quick Start

### **1. Clone and Navigate**

```bash
cd task-analyzer
```

### **2. Setup Virtual Environment**

```bash
python -m venv venv
# Windowsenv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Initialize Database**

```bash
python manage.py migrate
```

### **5. Run Tests (10 Passing)**

```bash
python manage.py test tasks
```

### **6. Start Backend**

```bash
python manage.py runserver
```

Backend → **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

### **7. Open Frontend**

Open `frontend/index.html` in your browser.
Frontend → **[http://localhost:8080](http://localhost:8080)**

---

#  Algorithm Overview

The scoring engine evaluates tasks using **4 core factors**:

## **1. Urgency (0–100+)**

* Overdue → `100 + (days_overdue ^ 1.5)`
* Due today → 95
* Due in 2 days → 80
* Due within week → 50

**Why exponential?**
Overdue work compounds risk; linear urgency allowed harmful procrastination.

## **2. Importance (8–80)**

`importance_rating (1–10) × 8`

Respects user domain knowledge.

## **3. Effort Bonus (Quick Wins)**

* ≤1 hr → +25
* ≤2 hr → +15

Boosts momentum.

## **4. Dependency Multiplier**

`+20 per task unblocked`

Unblocking creates high downstream impact.

---

#  Formula

```text
Final Score = Urgency + Importance + Effort Bonus + (Blocking Count × 20)
```

---

#  Strategy Modes

| Strategy            | Best For          | Algorithm            |
| ------------------- | ----------------- | -------------------- |
| **Smart Balance**   | General use       | All factors weighted |
| **Fastest Wins**    | Momentum building | Effort × 10          |
| **High Impact**     | Strategic work    | Importance × 15      |
| **Deadline Driven** | Crisis mode       | Urgency × 2          |

---

# Architecture

```
task-analyzer/
├── backend/              # Django project
│   ├── settings.py
│   └── urls.py
├── tasks/                # Core logic
│   ├── models.py
│   ├── scoring.py
│   ├── views.py
│   ├── serializers.py
│   └── tests.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── db.sqlite3
```

---

#  API Documentation

## **POST /api/tasks/analyze/**

Sorts all tasks by priority.

### Request

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Fix critical bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 9,
      "dependencies": []
    }
  ],
  "strategy": "smart_balance"
}
```

### Response

```json
{
  "tasks": [
    {
      "id": 1,
      "priority_score": 167.0,
      "explanation": " Due in 1 days |  Importance: 9/10 |  Fast task"
    }
  ],
  "strategy_used": "smart_balance",
  "total_tasks": 1
}
```

---

## **POST /api/tasks/suggest/**

Returns **top 3 highest‑priority tasks** with reasoning.

---

# Testing

Run all tests:

```bash
python manage.py test tasks
```

Includes:

* Circular dependency detection
* Strategy scoring validation
* Edge cases

---

#  Design Decisions

###  Stateless API

No DB persistence; focused on algorithm performance.

###  Exponential Urgency

Best prevents procrastination based on test data.

###  Multiple Strategies

Users prefer preset modes instead of custom sliders.

###  Dependency Detection (DFS)

O(V+E) complexity, fast and reliable.

---

#  Time Breakdown

| Phase         | Time       |
| ------------- | ---------- |
| Setup         | 20m        |
| Algorithm     | 90m        |
| API           | 40m        |
| Testing       | 45m        |
| Frontend      | 120m       |
| Documentation | 30m        |
| Bug fixes     | 25m        |
| **Total**     | **6h 10m** |

---

#  Tech Stack

**Backend:** Django, DRF
**Frontend:** HTML, CSS, JS
**Database:** SQLite
**Testing:** Django TestCase
**Version Control:** Git

---

#  Features

* Smart scoring system
* 4 strategy modes
* /analyze & /suggest API endpoints
* Circular dependency detection
* Responsive dark‑theme frontend
* 10+ unit tests
* Detailed explanations for each task

---

#  Known Limitations

* No authentication
* In‑memory only
* Single‑user
* Minimal validation
* No timezone support

---

#  Summary

This project delivers a powerful, well‑tested task‑prioritization engine with a clean REST API and intuitive UI—ideal for productivity, planning, or decision‑support applications.

---

If you'd like, I can add **shields badges**, **screenshots section**, **demo GIF**, or **installation diagram**.

