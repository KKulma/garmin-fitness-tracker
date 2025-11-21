# garmin_points.py
import datetime
from typing import Dict
import os
from dotenv import load_dotenv
import garth
from garminconnect import Garmin

load_dotenv()

# Login to Garmin Connect (with caching via garth)
def garmin_login():
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    # garth login saves session for reuse
    garth.login(email, password)
    garth.save("~/.garth")
    client = Garmin(email=email, password=password)
    client.login()
    return client

# Calculate points from steps
def points_from_steps(steps: int) -> int:
    if steps >= 12500:
        return 8
    elif steps >= 10000:
        return 5
    elif steps >= 7000:
        return 3
    return 0

# Calculate points from activity (non-strength)
def points_from_activity(active_seconds: int, avg_hr: float) -> int:
    points = 0
    intervals_30min = active_seconds // 1800  # number of full 30-min intervals
    if avg_hr > 110:
        points += intervals_30min * 8
    elif 90 <= avg_hr <= 110:
        points += intervals_30min * 5
    return points

# Calculate points from strength training
def points_from_strength(strength_seconds: int, avg_hr: float) -> int:
    intervals_30min = strength_seconds // 1800
    if avg_hr > 105:
        return intervals_30min * 8
    return 0

# Fetch and calculate points for a given date
def fetch_points_by_date(target_date: datetime.date) -> int:
    client = garmin_login()
    
    # Steps
    daily_steps_list = garth.DailySteps.list(period=2)
    steps_points = 0
    for ds in daily_steps_list:
        if ds.calendar_date == target_date:
            steps_points = points_from_steps(ds.total_steps)
            break

    # Activity
    stats = client.get_stats(str(target_date))
    active_seconds = stats.get("activeSeconds", 0)
    highly_active_seconds = stats.get("highlyActiveSeconds", 0)
    avg_hr = stats.get("restingHeartRate", 0)  # fallback if no session HR available
    activity_points = points_from_activity(active_seconds, avg_hr)

    # Strength training (if any)
    strength_points = points_from_strength(highly_active_seconds, avg_hr)

    total_points = steps_points + activity_points + strength_points
    return total_points

# Optional: fetch multiple days at once
def fetch_points_for_range(start_date: datetime.date, end_date: datetime.date) -> Dict[datetime.date, int]:
    result = {}
    current = start_date
    while current <= end_date:
        result[current] = fetch_points_by_date(current)
        current += datetime.timedelta(days=1)
    return result
