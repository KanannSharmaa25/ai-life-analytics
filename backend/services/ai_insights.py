def explain_clusters(clustered_data):
    # Case 1: clustering returned an error message
    if isinstance(clustered_data, dict):
        return clustered_data.get("message", "Not enough data to generate insights.")

    # Case 2: clustering returned an empty list
    if len(clustered_data) < 2:
        return "Not enough data to generate insights."

    insights = []
    cluster_summary = {}

    for day in clustered_data:
        c = day["cluster"]
        cluster_summary.setdefault(c, {"sleep": [], "productivity": []})
        cluster_summary[c]["sleep"].append(day["sleep_hours"])
        cluster_summary[c]["productivity"].append(day["productivity"])

    for c, values in cluster_summary.items():
        avg_sleep = sum(values["sleep"]) / len(values["sleep"])
        avg_prod = sum(values["productivity"]) / len(values["productivity"])

        if avg_sleep < 6:
            insights.append(
                f"Cluster {c}: These are low-energy days. Low sleep is linked to lower productivity."
            )
        else:
            insights.append(
                f"Cluster {c}: These are high-performance days. Good sleep supports better productivity."
            )

    return insights
