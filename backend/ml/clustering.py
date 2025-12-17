import numpy as np
from sklearn.cluster import KMeans

def cluster_days(data):
    if not data or len(data) < 3:
        return {}

    try:
        X = np.array([
            [float(d["sleep_hours"]), float(d["mood"]), float(d["productivity"])]
            for d in data
        ])

        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        clusters = {}

        for label, day in zip(labels, data):
            label = int(label)  # 🔥 convert numpy.int32 → int

            clusters.setdefault(str(label), []).append({
                "sleep_hours": float(day["sleep_hours"]),
                "mood": int(day["mood"]),
                "productivity": int(day["productivity"])
            })

        return clusters

    except Exception as e:
        print("❌ CLUSTERING ERROR:", e)
        return {}
