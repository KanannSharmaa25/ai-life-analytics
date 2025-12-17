import numpy as np
from sklearn.linear_model import LinearRegression

def train_and_predict(entries, sleep_hours: float):
    data = [
        (e.sleep_hours, e.productivity)
        for e in entries
        if e.sleep_hours is not None and e.productivity is not None
    ]

    # CASE 1: No data
    if len(data) == 0:
        return {
            "predicted_productivity": 5.0,
            "mode": "no-data",
            "confidence": 20
        }

    # CASE 2: Limited data → statistical fallback
    if len(data) < 4:
        avg = np.mean([p for _, p in data])
        confidence = min(60, 30 + len(data) * 10)

        return {
            "predicted_productivity": round(float(avg), 2),
            "mode": "average",
            "confidence": confidence
        }

    # CASE 3: ML regression
    X = np.array([s for s, _ in data]).reshape(-1, 1)
    y = np.array([p for _, p in data])

    model = LinearRegression()
    model.fit(X, y)

    prediction = model.predict([[sleep_hours]])[0]
    prediction = max(1, min(10, prediction))

    return {
        "predicted_productivity": round(float(prediction), 2),
        "mode": "regression",
        "confidence": 75
    }
