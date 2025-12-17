# 🧠 AI Life Analytics Dashboard

An AI-powered full-stack life analytics dashboard that helps users track daily habits like **sleep, mood, and productivity**, while providing **burnout detection, trends, predictions, and personalized insights**.

This project combines **FastAPI (Python backend)** with a **React frontend** and basic **machine learning logic** to turn everyday data into meaningful insights.

---

## 🚀 Features

### 📊 Daily Life Tracking

* Log daily **sleep hours**, **mood**, and **productivity**
* Edit, delete, or clear entries easily
* Date-based logging support

### 🔥 Burnout Analysis

* Burnout **status detection**
* Burnout **risk score (0–100)**
* **Burnout trend graph** over time

### 📈 Analytics & Visualizations

* Sleep vs Productivity trend (line chart)
* Sleep frequency heatmap
* Mood vs Productivity comparison
* Best sleep range analysis

### 🤖 AI Insights

* Natural-language insights based on your data
* Smart observations instead of static messages

### 🔮 Productivity Prediction

* Predict productivity based on sleep hours
* Includes prediction mode and confidence score

### 🎯 Personalized Recommendations

* Actionable suggestions based on patterns
* Updates dynamically as more data is added

### 📤 Export Reports

* Export data as **CSV**
* Export data as **JSON**
* (PDF support ready to extend)

---

## 🛠️ Tech Stack

### Frontend

* **React**
* **Recharts** (data visualization)
* CSS (custom dark UI)

### Backend

* **FastAPI**
* **SQLAlchemy**
* **SQLite**
* **NumPy**
* Basic ML logic for predictions

---

## 📁 Project Structure

```
ai-life-analytics/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── predict.py
│   ├── ai_insights.py
│   └── life_analytics.db
│
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── public/
│   └── package.json
│
├── README.md
```

---

## ▶️ How to Run the Project Locally

### 1️⃣ Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend will run at:

```
http://localhost:8000
```

---

### 2️⃣ Frontend (React)

```bash
cd frontend
npm install
npm start
```

Frontend will run at:

```
http://localhost:3000
```

---

## 🧪 API Highlights

* `POST /add-entry` → Add daily entry
* `GET /entries` → Fetch all entries
* `GET /analysis/burnout` → Burnout status
* `GET /analysis/burnout-trend` → Burnout trend
* `GET /ml/predict` → Productivity prediction
* `GET /export/csv` → Export CSV
* `GET /export/json` → Export JSON

---

## 💡 Why This Project?

This project was built to:

* Practice **full-stack development**
* Apply **AI concepts** to real-life data
* Learn **data visualization**
* Build a **resume-worthy dashboard**

It simulates how AI can assist in **mental health awareness and productivity analysis**.

---

## 🔮 Future Improvements

* User authentication
* Cloud database
* PDF report export
* Deployment (Vercel + Render)
* More advanced ML models

---

## 👤 Author

**Kanan Sharma**
GitHub: [@KanannSharmaa25](https://github.com/KanannSharmaa25)

---

