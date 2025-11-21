import sqlite3
import datetime
import json
import os
from typing import List, Dict, Any, Optional

DB_FILE = "activities.db"

def init_db():
    """Initializes the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            steps INTEGER,
            points INTEGER,
            activities_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_daily_data(date: datetime.date, steps: int, points: int, activities: List[Dict[str, Any]]):
    """Saves or updates daily data."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO daily_stats (date, steps, points, activities_json)
        VALUES (?, ?, ?, ?)
    ''', (str(date), steps, points, json.dumps(activities)))
    conn.commit()
    conn.close()

def get_data_for_date(date: datetime.date) -> Optional[Dict[str, Any]]:
    """Retrieves data for a specific date."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT steps, points, activities_json FROM daily_stats WHERE date = ?', (str(date),))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "date": date,
            "steps": row[0],
            "points": row[1],
            "activities": json.loads(row[2])
        }
    return None

def get_data_range(start_date: datetime.date, end_date: datetime.date) -> Dict[datetime.date, Dict[str, Any]]:
    """Retrieves data for a date range."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT date, steps, points, activities_json 
        FROM daily_stats 
        WHERE date >= ? AND date <= ?
    ''', (str(start_date), str(end_date)))
    rows = c.fetchall()
    conn.close()
    
    result = {}
    for row in rows:
        date_obj = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
        result[date_obj] = {
            "steps": row[1],
            "points": row[2],
            "activities": json.loads(row[3])
        }
    return result

def get_latest_date() -> Optional[datetime.date]:
    """Returns the latest date stored in the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT MAX(date) FROM daily_stats')
    row = c.fetchone()
    conn.close()
    
    if row and row[0]:
        return datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
    return None
