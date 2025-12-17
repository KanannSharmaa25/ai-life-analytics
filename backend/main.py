from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from collections import defaultdict
from datetime import datetime
import numpy as np
from scipy.stats import pearsonr

from database import (
    SessionLocal,
    Entry,
    User,
    hash_password,
    verify_password,
)

from ml.predict import train_and_predict
from pydantic import BaseModel

# ================= APP =================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= DB =================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= BASIC =================

@app.get("/")
def home():
    return {"message": "Backend running"}

# ================= SCHEMA =================

class EntryCreate(BaseModel):
    date: str
    sleep_hours: float
    mood: int
    productivity: int

# ================= ADD ENTRY =================

@app.post("/add-entry")
def add_entry(entry: EntryCreate, db: Session = Depends(get_db)):
    try:
        parsed_date = datetime.strptime(entry.date, "%Y-%m-%d").date()

        new_entry = Entry(
            date=parsed_date,
            sleep_hours=float(entry.sleep_hours),
            mood=int(entry.mood),
            productivity=int(entry.productivity),
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        return {"message": "Entry added", "id": new_entry.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ================= GET ENTRIES =================

@app.get("/entries")
def get_entries(db: Session = Depends(get_db)):
    return db.query(Entry).order_by(Entry.date).all()

@app.get("/entries/by-date/{date}")
def get_entries_by_date(date: str, db: Session = Depends(get_db)):
    selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    return db.query(Entry).filter(Entry.date == selected_date).all()

# ================= AI INSIGHTS (SMART) =================

@app.get("/ai/insights")
def ai_insights(db: Session = Depends(get_db)):
    entries = db.query(Entry).order_by(Entry.date).all()

    if len(entries) < 3:
        return {
            "insights": [
                "You’re just getting started. Add a few more daily entries and I’ll begin spotting meaningful patterns for you."
            ]
        }

    sleep_vals = [e.sleep_hours for e in entries]
    prod_vals = [e.productivity for e in entries]
    mood_vals = [e.mood for e in entries]

    avg_sleep = round(np.mean(sleep_vals), 2)
    avg_prod = round(np.mean(prod_vals), 2)
    avg_mood = round(np.mean(mood_vals), 2)

    recent_sleep = np.mean(sleep_vals[-3:])
    recent_prod = np.mean(prod_vals[-3:])

    insights = []

    # 💤 Sleep vs Productivity
    if avg_sleep < 6:
        insights.append(
            f"Your average sleep is around {avg_sleep} hours, which is below the recommended range. This could be quietly impacting your focus and energy levels."
        )
    elif avg_sleep >= 7:
        insights.append(
            f"You’re averaging about {avg_sleep} hours of sleep — that’s a solid foundation for sustained productivity."
        )

    # 📉 Burnout pattern
    if recent_sleep < avg_sleep and recent_prod < avg_prod:
        insights.append(
            "In the last few days, both sleep and productivity have dipped together. This pattern often appears just before burnout — it might be a good time to slow down and reset."
        )

    # 🚀 Productivity trend
    if avg_prod >= 7:
        insights.append(
            "Your productivity levels are consistently strong. Whatever routine you’re following lately seems to be working well — try to protect it."
        )
    elif avg_prod < 5:
        insights.append(
            "Productivity has been on the lower side overall. Small changes like better sleep timing or short breaks could make a noticeable difference."
        )

    # 😊 Mood correlation
    if avg_mood >= 6 and avg_prod >= 6:
        insights.append(
            "There’s a positive link between your mood and productivity — on days you feel better mentally, you tend to perform better too."
        )

    # 🧠 Gentle coaching insight
    insights.append(
        "Remember: trends matter more than single days. Consistency beats perfection — keep tracking, and the patterns will become clearer over time."
    )

    return {"insights": insights}


# ================= ML =================

@app.get("/ml/predict")
def predict(sleep_hours: float, db: Session = Depends(get_db)):
    entries = db.query(Entry).all()
    return train_and_predict(entries, sleep_hours)

# ================= HEATMAP =================

@app.get("/analysis/sleep-productivity-heatmap")
def sleep_productivity_heatmap(db: Session = Depends(get_db)):
    entries = db.query(Entry).all()
    heatmap = defaultdict(int)

    for e in entries:
        heatmap[int(round(e.sleep_hours))] += 1

    return {"data": [{"sleep": k, "count": v} for k, v in sorted(heatmap.items())]}

# ================= BEST SLEEP =================

@app.get("/analysis/best-sleep-range")
def best_sleep_range(db: Session = Depends(get_db)):
    entries = db.query(Entry).all()
    if not entries:
        return {}

    buckets = defaultdict(list)
    for e in entries:
        buckets[round(e.sleep_hours, 1)].append(e.productivity)

    best = max(buckets.items(), key=lambda x: sum(x[1]) / len(x[1]))

    return {
        "best_sleep_range": f"{best[0]} hours",
        "average_productivity": round(sum(best[1]) / len(best[1]), 2),
    }

# ================= BURNOUT STATUS =================

@app.get("/analysis/burnout")
def burnout_analysis(db: Session = Depends(get_db)):
    entries = db.query(Entry).all()
    if not entries:
        return {}

    avg_sleep = np.mean([e.sleep_hours for e in entries])
    avg_prod = np.mean([e.productivity for e in entries])

    if avg_sleep < 6 and avg_prod < 5:
        message = "High burnout risk detected. Your body and mind may need recovery time."
    elif avg_sleep < 6:
        message = "Sleep deprivation detected. This may affect focus and mood."
    else:
        message = "Burnout risk appears manageable. Keep maintaining healthy habits."

    return {
        "average_sleep": round(avg_sleep, 2),
        "average_productivity": round(avg_prod, 2),
        "message": message,
    }

# ================= BURNOUT SCORE (NEW) =================

@app.get("/analysis/burnout-score")
def burnout_score(db: Session = Depends(get_db)):
    entries = db.query(Entry).all()
    if not entries:
        return {"score": 0, "level": "Unknown", "message": "Not enough data"}

    avg_sleep = np.mean([e.sleep_hours for e in entries])
    avg_prod = np.mean([e.productivity for e in entries])

    score = int(max(0, min(100, (10 - avg_sleep) * 8 + (10 - avg_prod) * 6)))

    if score > 70:
        level = "High"
        msg = "You're at high risk of burnout. Consider rest and workload adjustment."
    elif score > 40:
        level = "Moderate"
        msg = "Some signs of fatigue detected. Small changes could help."
    else:
        level = "Low"
        msg = "Burnout risk is low. You're managing things well."

    return {"score": score, "level": level, "message": msg}

# ================= MOOD ↔ PRODUCTIVITY =================

@app.get("/analysis/mood-productivity-correlation")
def mood_productivity_correlation(db: Session = Depends(get_db)):
    entries = db.query(Entry).all()
    if len(entries) < 3:
        return {
            "correlation": None,
            "message": "Not enough data to analyze mood and productivity relationship.",
        }

    moods = [e.mood for e in entries]
    prods = [e.productivity for e in entries]

    corr, _ = pearsonr(moods, prods)

    strength = (
        "Strong" if abs(corr) > 0.6 else
        "Moderate" if abs(corr) > 0.3 else
        "Weak"
    )

    return {
        "correlation": round(corr, 2),
        "strength": strength,
        "message": f"{strength} relationship between mood and productivity detected.",
    }

# ================= RECOMMENDATIONS =================

@app.get("/analysis/recommendations")
def recommendations(db: Session = Depends(get_db)):
    entries = db.query(Entry).order_by(Entry.date).all()

    if len(entries) < 3:
        return {
            "recommendations": [
                "Track your sleep, mood, and productivity for a few more days to unlock personalized recommendations."
            ]
        }

    avg_sleep = np.mean([e.sleep_hours for e in entries])
    avg_prod = np.mean([e.productivity for e in entries])
    recent_sleep = np.mean([e.sleep_hours for e in entries[-3:]])

    recs = []

    if avg_sleep < 6:
        recs.append(
            "You’ve been sleeping less than ideal. Try going to bed 30–45 minutes earlier for the next few days and see how your energy responds."
        )

    if avg_prod < 5:
        recs.append(
            "Productivity has been lower recently. Consider breaking tasks into smaller chunks or scheduling demanding work during your most alert hours."
        )

    if recent_sleep < avg_sleep:
        recs.append(
            "Your sleep has dipped recently compared to your average. This could explain recent fatigue — prioritizing rest now may prevent burnout later."
        )

    if not recs:
        recs.append(
            "Your habits look balanced overall. Focus on maintaining consistency rather than pushing harder."
        )

    return {"recommendations": recs}


# ================= DELETE =================

@app.delete("/entries/{entry_id}")
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if entry:
        db.delete(entry)
        db.commit()
    return {"message": "Entry deleted"}

@app.delete("/entries")
def delete_all(db: Session = Depends(get_db)):
    db.query(Entry).delete()
    db.commit()
    return {"message": "All entries deleted"}

# ================= AUTH =================

@app.post("/auth/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email exists")

    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    return {"message": "Registered"}

@app.post("/auth/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login success", "email": user.email}
@app.get("/analysis/burnout-trend")
def burnout_trend(db: Session = Depends(get_db)):
    entries = db.query(Entry).order_by(Entry.date).all()

    trend = []
    for e in entries:
        score = 0

        # Sleep penalty
        if e.sleep_hours < 6:
            score += (6 - e.sleep_hours) * 10

        # Productivity penalty
        if e.productivity < 5:
            score += (5 - e.productivity) * 10

        trend.append({
            "date": e.date.strftime("%Y-%m-%d"),
            "burnout_score": min(100, int(score))
        })

    return {"trend": trend}
from fastapi.responses import StreamingResponse
import csv
import io

# ================= EXPORT CSV =================

@app.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    entries = db.query(Entry).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Date", "Sleep Hours", "Mood", "Productivity"])

    for e in entries:
        writer.writerow([
            e.date,
            e.sleep_hours,
            e.mood,
            e.productivity
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=life_analytics_report.csv"}
    )

# ================= EXPORT JSON =================

@app.get("/export/json")
def export_json(db: Session = Depends(get_db)):
    entries = db.query(Entry).all()

    return {
        "entries": [
            {
                "date": e.date,
                "sleep_hours": e.sleep_hours,
                "mood": e.mood,
                "productivity": e.productivity,
            }
            for e in entries
        ]
    }
