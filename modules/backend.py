import garth
import datetime
import os
from typing import List, Dict, Any, Optional
from garminconnect import Garmin

SESSION_DIR = os.path.expanduser("~/.garth")
garmin_client = None

def login(email: str = None, password: str = None) -> bool:
    """
    Authenticates with Garmin Connect using both garth and garminconnect.
    """
    global garmin_client
    try:
        # 1. Garth Login (for steps)
        try:
            garth.resume(SESSION_DIR)
            garth.client.username # Verify validity
        except:
            if email and password:
                garth.login(email, password)
                garth.save(SESSION_DIR)
            else:
                return False

        # 2. GarminConnect Login (for activities)
        # We need email/password for this as it doesn't share garth's session dir directly in this context
        # If we resumed garth, we might not have email/pass if not provided.
        # But app.py asks for them if not logged in.
        # If we are resuming, we might have an issue if we don't have credentials for Garmin()
        # For now, we assume if we are logging in via UI, we have them.
        # If we are resuming, we might need to rely on garth for everything OR fail if we can't init Garmin.
        
        # Limitation: Garmin library needs password to login. 
        # If we only have garth session, we can't init Garmin client without prompting user.
        # However, for this implementation, let's assume we have credentials or we fail.
        
        if email and password:
            garmin_client = Garmin(email, password)
            garmin_client.login()
            return True
        elif garth.client.oauth2_token:
            # If we are here, we resumed garth but don't have creds for Garmin.
            # This is a tricky state. 
            # Ideally we should store creds securely or use garth for everything.
            # But user specifically asked for Garmin client for activities.
            # We will return False to force re-login in UI if we don't have garmin_client ready.
            return False
            
        return False
    except Exception as e:
        print(f"Login failed: {e}")
        return False

def get_daily_data(date: datetime.date) -> Dict[str, Any]:
    """
    Fetches steps and activities for a specific date.
    """
    global garmin_client
    try:
        # Ensure we have clients ready
        if not garth.client.oauth2_token or not garmin_client:
             return {"date": date, "steps": 0, "activities": [], "error": "Not logged in"}

        # 1. Fetch Activities using GarminConnect
        # The user wants to use client.get_activities(start=0, limit=limit)
        # We'll fetch a batch and filter.
        try:
            activities_list = garmin_client.get_activities(start=0, limit=50)
        except Exception as e:
             print(f"Error fetching activities with Garmin client: {e}")
             activities_list = []

        day_activities = []
        for act in activities_list:
            start_time_str = act.get('startTimeLocal', '')
            if start_time_str.startswith(str(date)):
                day_activities.append(act)

        # 2. Fetch Steps using Garth
        # garth.DailySteps.list(period=N) returns the last N days.
        today = datetime.date.today()
        days_diff = (today - date).days
        
        steps = 0
        
        if days_diff >= 0:
            period = days_diff + 2 
            try:
                daily_steps_list = garth.DailySteps.list(period=period)
                for daily_step in daily_steps_list:
                    if daily_step.calendar_date == date:
                        steps = daily_step.total_steps
                        break
            except Exception as e:
                print(f"Error fetching steps for {date}: {e}")
        
        # Ensure steps is not None
        if steps is None:
            steps = 0
            
        return {
            "date": date,
            "steps": steps,
            "activities": day_activities
        }

    except Exception as e:
        print(f"Error fetching data for {date}: {e}")
        return {"date": date, "steps": 0, "activities": [], "error": str(e)}

def calculate_points(steps: int, activities: List[Dict[str, Any]]) -> int:
    """
    Calculates activity points based on the user's rules.
    """
    points = 0
    
    # Ensure steps is valid
    if steps is None:
        steps = 0
    
    # 1. Steps
    if steps >= 12500:
        points += 8
    elif steps >= 10000:
        points += 5
    elif steps >= 7000:
        points += 3
        
    # 2. Activities
    for act in activities:
        activity_type = act.get('activityType', {}).get('typeKey', '')
        duration_sec = act.get('duration', 0)
        avg_hr = act.get('averageHR', 0)
        
        if not avg_hr:
            continue
            
        duration_mins = duration_sec / 60
        
        # Strength Training (Any HR) OR No HR Data
        if 'strength' in activity_type.lower() or not avg_hr:
            points += int(duration_mins / 30) * 8
        else:
            # Other activities (Cardio etc) with HR data
            # 8 points for every 30 mins with avg HR > 110
            if avg_hr > 110:
                points += int(duration_mins / 30) * 8
            # 5 points for every 30 mins with 90 <= avg HR <= 110
            elif 90 <= avg_hr <= 110:
                points += int(duration_mins / 30) * 5
                
    return points

from modules import database

# ... (existing imports)

# Initialize DB on module load (or call explicitly in app)
database.init_db()

# ... (existing login, get_daily_data, calculate_points functions)

def sync_data(status_callback=None):
    """
    Synchronizes data from Garmin Connect to local DB.
    - If DB empty: fetch from 2025-02-01.
    - If DB has data: fetch from latest_date + 1 day.
    - Stops at yesterday (today's data is fetched live or handled separately).
    """
    latest_date = database.get_latest_date()
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    start_date = datetime.date(2025, 2, 1)
    if latest_date:
        start_date = latest_date + datetime.timedelta(days=1)
        
    if start_date > yesterday:
        if status_callback:
            status_callback("Data is up to date.")
        return

    current_date = start_date
    total_days = (yesterday - start_date).days + 1
    processed = 0

    while current_date <= yesterday:
        if status_callback:
            status_callback(f"Syncing {current_date} ({processed + 1}/{total_days})...")
            
        # Fetch data
        data = get_daily_data(current_date)
        
        # Calculate points
        points = calculate_points(data["steps"], data["activities"])
        
        # Save to DB
        database.save_daily_data(current_date, data["steps"], points, data["activities"])
        
        current_date += datetime.timedelta(days=1)
        processed += 1
        
    if status_callback:
        status_callback("Sync complete!")

