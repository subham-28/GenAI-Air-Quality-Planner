# from datetime import datetime
# import math


# def format_hour_label(dt):
#     """
#     Convert datetime object to readable hour label.
#     Example: 18:00 -> 6 PM
#     """
#     return dt.strftime("%I %p").lstrip("0")


# def format_window(start_dt, end_dt):
#     """
#     Example: 6 PM–8 PM
#     """
#     return f"{format_hour_label(start_dt)}–{format_hour_label(end_dt)}"


# def pollution_score(pm25, pm10):
#     """
#     Lower score means cleaner air.

#     We normalize PM2.5 and PM10 roughly using CPCB-style breakpoint scale.
#     PM2.5 is weighted slightly more because it is usually more concerning
#     for outdoor exposure.
#     """
#     if pm25 is None and pm10 is None:
#         return None

#     if pm25 is None:
#         pm25 = 0

#     if pm10 is None:
#         pm10 = 0

#     pm25_score = pm25 / 60
#     pm10_score = pm10 / 100

#     return (0.6 * pm25_score) + (0.4 * pm10_score)


# def build_hourly_forecast_rows(pollution):
#     hourly = pollution.get("hourly", {})

#     times = hourly.get("time", [])
#     pm25_values = hourly.get("pm2_5", [])
#     pm10_values = hourly.get("pm10", [])
#     us_aqi_values = hourly.get("us_aqi", [])
#     european_aqi_values = hourly.get("european_aqi", [])

#     rows = []

#     for i, time_str in enumerate(times):
#         try:
#             dt = datetime.fromisoformat(time_str)
#         except Exception:
#             continue

#         pm25 = pm25_values[i] if i < len(pm25_values) else None
#         pm10 = pm10_values[i] if i < len(pm10_values) else None
#         us_aqi = us_aqi_values[i] if i < len(us_aqi_values) else None
#         european_aqi = european_aqi_values[i] if i < len(european_aqi_values) else None

#         score = pollution_score(pm25, pm10)

#         if score is None:
#             continue

#         rows.append({
#             "time": time_str,
#             "hour": format_hour_label(dt),
#             "pm2_5": pm25,
#             "pm10": pm10,
#             "us_aqi": us_aqi,
#             "european_aqi": european_aqi,
#             "score": score
#         })

#     return rows


# def find_best_and_worst_windows(pollution, duration_minutes=60):
#     """
#     Finds the cleanest and most polluted continuous windows for today.

#     Window size:
#     - Minimum 2 hours for useful outdoor planning
#     - If user activity duration is longer, use that duration rounded up to hours
#     """
#     rows = build_hourly_forecast_rows(pollution)

#     if not rows:
#         return {
#             "best_window": "Unavailable",
#             "worst_window": "Unavailable",
#             "best_avg_pm25": None,
#             "best_avg_pm10": None,
#             "worst_avg_pm25": None,
#             "worst_avg_pm10": None,
#             "hourly_forecast": []
#         }

#     today = rows[0]["datetime"].date()

#     today_rows = [
#         row for row in rows
#         if row["datetime"].date() == today
#     ]

#     if not today_rows:
#         return {
#             "best_window": "Unavailable",
#             "worst_window": "Unavailable",
#             "best_avg_pm25": None,
#             "best_avg_pm10": None,
#             "worst_avg_pm25": None,
#             "worst_avg_pm10": None,
#             "hourly_forecast": rows
#         }

#     window_hours = max(2, math.ceil(duration_minutes / 60))

#     if len(today_rows) < window_hours:
#         window_hours = len(today_rows)

#     windows = []

#     for start_idx in range(0, len(today_rows) - window_hours + 1):
#         window = today_rows[start_idx:start_idx + window_hours]

#         avg_score = sum(row["score"] for row in window) / len(window)

#         valid_pm25 = [
#             row["pm2_5"] for row in window
#             if row["pm2_5"] is not None
#         ]

#         valid_pm10 = [
#             row["pm10"] for row in window
#             if row["pm10"] is not None
#         ]

#         avg_pm25 = sum(valid_pm25) / len(valid_pm25) if valid_pm25 else None
#         avg_pm10 = sum(valid_pm10) / len(valid_pm10) if valid_pm10 else None

#         start_dt = window[0]["datetime"]
#         end_dt = window[-1]["datetime"]

#         # End label should represent the end of the final hour.
#         end_dt = end_dt.replace(hour=end_dt.hour)  # keep same datetime object
#         end_hour_label_dt = end_dt

#         # For display, add one hour by simple hour wrapping.
#         # Avoid importing timedelta repeatedly.
#         from datetime import timedelta
#         end_hour_label_dt = end_hour_label_dt + timedelta(hours=1)

#         windows.append({
#             "window": format_window(start_dt, end_hour_label_dt),
#             "avg_score": avg_score,
#             "avg_pm25": avg_pm25,
#             "avg_pm10": avg_pm10,
#             "start_time": start_dt.isoformat(),
#             "end_time": end_hour_label_dt.isoformat()
#         })

#     best = min(windows, key=lambda x: x["avg_score"])
#     worst = max(windows, key=lambda x: x["avg_score"])

#     return {
#         "best_window": best["window"],
#         "worst_window": worst["window"],
#         "best_avg_pm25": round(best["avg_pm25"], 2) if best["avg_pm25"] is not None else None,
#         "best_avg_pm10": round(best["avg_pm10"], 2) if best["avg_pm10"] is not None else None,
#         "worst_avg_pm25": round(worst["avg_pm25"], 2) if worst["avg_pm25"] is not None else None,
#         "worst_avg_pm10": round(worst["avg_pm10"], 2) if worst["avg_pm10"] is not None else None,
#         "best_start_time": best["start_time"],
#         "best_end_time": best["end_time"],
#         "worst_start_time": worst["start_time"],
#         "worst_end_time": worst["end_time"],
#         "hourly_forecast": rows
#     }



from datetime import datetime, timedelta
import math


def format_hour_label(dt):
    return dt.strftime("%I %p").lstrip("0")


def format_window(start_dt, end_dt):
    return f"{format_hour_label(start_dt)}–{format_hour_label(end_dt)}"


def pollution_score(pm25, pm10):
    if pm25 is None and pm10 is None:
        return None

    if pm25 is None:
        pm25 = 0

    if pm10 is None:
        pm10 = 0

    pm25_score = pm25 / 60
    pm10_score = pm10 / 100

    return (0.6 * pm25_score) + (0.4 * pm10_score)


def build_hourly_forecast_rows(pollution):
    hourly = pollution.get("hourly", {})

    times = hourly.get("time", [])
    pm25_values = hourly.get("pm2_5", [])
    pm10_values = hourly.get("pm10", [])
    us_aqi_values = hourly.get("us_aqi", [])
    european_aqi_values = hourly.get("european_aqi", [])

    rows = []

    for i, time_str in enumerate(times):
        try:
            dt = datetime.fromisoformat(time_str)
        except Exception:
            continue

        pm25 = pm25_values[i] if i < len(pm25_values) else None
        pm10 = pm10_values[i] if i < len(pm10_values) else None
        us_aqi = us_aqi_values[i] if i < len(us_aqi_values) else None
        european_aqi = european_aqi_values[i] if i < len(european_aqi_values) else None

        score = pollution_score(pm25, pm10)

        if score is None:
            continue

        rows.append({
            "time": time_str,
            "datetime": dt,          # needed internally for best/worst window calculation
            "hour": format_hour_label(dt),
            "pm2_5": pm25,
            "pm10": pm10,
            "us_aqi": us_aqi,
            "european_aqi": european_aqi,
            "score": score
        })

    return rows


def serialize_hourly_rows(rows):
    """
    Removes Python datetime object before saving into result.
    This prevents json.dumps() errors in Streamlit download button.
    """
    clean_rows = []

    for row in rows:
        clean_rows.append({
            "time": row.get("time"),
            "hour": row.get("hour"),
            "pm2_5": row.get("pm2_5"),
            "pm10": row.get("pm10"),
            "us_aqi": row.get("us_aqi"),
            "european_aqi": row.get("european_aqi"),
            "score": row.get("score")
        })

    return clean_rows


def find_best_and_worst_windows(pollution, duration_minutes=60):
    rows = build_hourly_forecast_rows(pollution)

    if not rows:
        return {
            "best_window": "Unavailable",
            "worst_window": "Unavailable",
            "best_avg_pm25": None,
            "best_avg_pm10": None,
            "worst_avg_pm25": None,
            "worst_avg_pm10": None,
            "hourly_forecast": []
        }

    today = rows[0]["datetime"].date()

    today_rows = [
        row for row in rows
        if row["datetime"].date() == today
    ]

    if not today_rows:
        return {
            "best_window": "Unavailable",
            "worst_window": "Unavailable",
            "best_avg_pm25": None,
            "best_avg_pm10": None,
            "worst_avg_pm25": None,
            "worst_avg_pm10": None,
            "hourly_forecast": serialize_hourly_rows(rows[:24])
        }

    window_hours = max(2, math.ceil(duration_minutes / 60))

    if len(today_rows) < window_hours:
        window_hours = len(today_rows)

    windows = []

    for start_idx in range(0, len(today_rows) - window_hours + 1):
        window = today_rows[start_idx:start_idx + window_hours]

        avg_score = sum(row["score"] for row in window) / len(window)

        valid_pm25 = [
            row["pm2_5"] for row in window
            if row["pm2_5"] is not None
        ]

        valid_pm10 = [
            row["pm10"] for row in window
            if row["pm10"] is not None
        ]

        avg_pm25 = sum(valid_pm25) / len(valid_pm25) if valid_pm25 else None
        avg_pm10 = sum(valid_pm10) / len(valid_pm10) if valid_pm10 else None

        start_dt = window[0]["datetime"]
        end_dt = window[-1]["datetime"] + timedelta(hours=1)

        windows.append({
            "window": format_window(start_dt, end_dt),
            "avg_score": avg_score,
            "avg_pm25": avg_pm25,
            "avg_pm10": avg_pm10,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat()
        })

    best = min(windows, key=lambda x: x["avg_score"])
    worst = max(windows, key=lambda x: x["avg_score"])

    return {
        "best_window": best["window"],
        "worst_window": worst["window"],

        "best_avg_pm25": round(best["avg_pm25"], 2) if best["avg_pm25"] is not None else None,
        "best_avg_pm10": round(best["avg_pm10"], 2) if best["avg_pm10"] is not None else None,

        "worst_avg_pm25": round(worst["avg_pm25"], 2) if worst["avg_pm25"] is not None else None,
        "worst_avg_pm10": round(worst["avg_pm10"], 2) if worst["avg_pm10"] is not None else None,

        "best_start_time": best["start_time"],
        "best_end_time": best["end_time"],
        "worst_start_time": worst["start_time"],
        "worst_end_time": worst["end_time"],

        # only clean JSON-safe rows go to Streamlit result
        "hourly_forecast": serialize_hourly_rows(rows[:24])
    }