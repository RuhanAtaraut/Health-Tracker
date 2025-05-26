#!/usr/bin/env python3
"""
Personal Health & Fitness Tracker

A comprehensive application to track:
- Sleep duration
- Gym attendance
- Water intake
- Opportunity loss calculations for missed gym sessions
"""

import sqlite3
import datetime
from typing import Dict, List, Optional, Tuple
import json


class HealthTracker:
    def __init__(self, db_path: str = "health_tracker.db"):
        """Initialize the health tracker with database connection"""
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sleep tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sleep_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                bedtime TIME,
                wake_time TIME,
                sleep_duration_hours REAL,
                sleep_quality INTEGER CHECK(sleep_quality BETWEEN 1 AND 10),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Gym attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gym_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                attended BOOLEAN NOT NULL,
                workout_type TEXT,
                duration_minutes INTEGER,
                calories_burned INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Water intake table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS water_intake (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                time_logged TIME NOT NULL,
                amount_ml INTEGER NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings table for goals and preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_name TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize default settings
        self._init_default_settings()
    
    def _init_default_settings(self):
        """Initialize default settings if they don't exist"""
        default_settings = {
            'daily_water_goal_ml': '2500',
            'weekly_gym_goal': '4',
            'target_sleep_hours': '8',
            'gym_membership_cost_monthly': '50',
            'missed_workout_opportunity_cost': '15'
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for setting_name, setting_value in default_settings.items():
            cursor.execute('''
                INSERT OR IGNORE INTO settings (setting_name, setting_value)
                VALUES (?, ?)
            ''', (setting_name, setting_value))
        
        conn.commit()
        conn.close()
    
    def log_sleep(self, date: str, bedtime: str, wake_time: str, 
                  sleep_quality: Optional[int] = None, notes: str = "") -> bool:
        """Log sleep data for a specific date"""
        try:
            # Calculate sleep duration
            bedtime_obj = datetime.datetime.strptime(f"{date} {bedtime}", "%Y-%m-%d %H:%M")
            wake_time_obj = datetime.datetime.strptime(f"{date} {wake_time}", "%Y-%m-%d %H:%M")
            
            # Handle cases where wake time is next day
            if wake_time_obj <= bedtime_obj:
                wake_time_obj += datetime.timedelta(days=1)
            
            sleep_duration = (wake_time_obj - bedtime_obj).total_seconds() / 3600
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sleep_records 
                (date, bedtime, wake_time, sleep_duration_hours, sleep_quality, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, bedtime, wake_time, sleep_duration, sleep_quality, notes))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging sleep: {e}")
            return False
    
    def log_gym_attendance(self, date: str, attended: bool, workout_type: str = "",
                          duration_minutes: Optional[int] = None, calories_burned: Optional[int] = None,
                          notes: str = "") -> bool:
        """Log gym attendance for a specific date"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO gym_attendance 
                (date, attended, workout_type, duration_minutes, calories_burned, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, attended, workout_type, duration_minutes, calories_burned, notes))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging gym attendance: {e}")
            return False
    
    def log_water_intake(self, amount_ml: int, date: Optional[str] = None, 
                        time_logged: Optional[str] = None, notes: str = "") -> bool:
        """Log water intake"""
        try:
            if date is None:
                date = datetime.date.today().strftime("%Y-%m-%d")
            if time_logged is None:
                time_logged = datetime.datetime.now().strftime("%H:%M")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO water_intake (date, time_logged, amount_ml, notes)
                VALUES (?, ?, ?, ?)
            ''', (date, time_logged, amount_ml, notes))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging water intake: {e}")
            return False
    
    def get_daily_water_total(self, date: str) -> int:
        """Get total water intake for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(amount_ml) FROM water_intake WHERE date = ?
        ''', (date,))
        
        result = cursor.fetchone()[0]
        conn.close()
        
        return result if result else 0
    
    def get_sleep_data(self, start_date: str, end_date: str) -> List[Dict]:
        """Get sleep data for a date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, bedtime, wake_time, sleep_duration_hours, sleep_quality, notes
            FROM sleep_records 
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'date': row[0],
                'bedtime': row[1],
                'wake_time': row[2],
                'sleep_duration_hours': row[3],
                'sleep_quality': row[4],
                'notes': row[5]
            }
            for row in rows
        ]
    
    def get_gym_attendance_data(self, start_date: str, end_date: str) -> List[Dict]:
        """Get gym attendance data for a date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, attended, workout_type, duration_minutes, calories_burned, notes
            FROM gym_attendance 
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        ''', (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'date': row[0],
                'attended': bool(row[1]),
                'workout_type': row[2],
                'duration_minutes': row[3],
                'calories_burned': row[4],
                'notes': row[5]
            }
            for row in rows
        ]
    
    def calculate_opportunity_loss(self, start_date: str, end_date: str) -> Dict:
        """Calculate opportunity loss from missed gym sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get settings
        cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', 
                      ('gym_membership_cost_monthly',))
        monthly_cost = float(cursor.fetchone()[0])
        
        cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', 
                      ('missed_workout_opportunity_cost',))
        opportunity_cost_per_session = float(cursor.fetchone()[0])
        
        # Count missed sessions
        cursor.execute('''
            SELECT COUNT(*) FROM gym_attendance 
            WHERE date BETWEEN ? AND ? AND attended = 0
        ''', (start_date, end_date))
        
        missed_sessions = cursor.fetchone()[0]
        
        # Calculate date range in days
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        days_in_range = (end - start).days + 1
        
        # Calculate costs
        daily_membership_cost = monthly_cost / 30.44  # Average days per month
        membership_cost_for_period = daily_membership_cost * days_in_range
        opportunity_loss = missed_sessions * opportunity_cost_per_session
        total_loss = membership_cost_for_period + opportunity_loss
        
        conn.close()
        
        return {
            'missed_sessions': missed_sessions,
            'membership_cost_for_period': round(membership_cost_for_period, 2),
            'opportunity_loss': round(opportunity_loss, 2),
            'total_loss': round(total_loss, 2),
            'days_in_range': days_in_range
        }
    
    def get_weekly_summary(self, date: str = None) -> Dict:
        """Get weekly summary for the week containing the given date"""
        if date is None:
            date = datetime.date.today().strftime("%Y-%m-%d")
        
        # Calculate week start (Monday) and end (Sunday)
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        week_start = date_obj - datetime.timedelta(days=date_obj.weekday())
        week_end = week_start + datetime.timedelta(days=6)
        
        start_str = week_start.strftime("%Y-%m-%d")
        end_str = week_end.strftime("%Y-%m-%d")
        
        # Get data for the week
        sleep_data = self.get_sleep_data(start_str, end_str)
        gym_data = self.get_gym_attendance_data(start_str, end_str)
        opportunity_loss = self.calculate_opportunity_loss(start_str, end_str)
        
        # Calculate averages and totals
        avg_sleep = sum(s['sleep_duration_hours'] for s in sleep_data if s['sleep_duration_hours']) / len(sleep_data) if sleep_data else 0
        gym_attendance_count = sum(1 for g in gym_data if g['attended'])
        
        # Get daily water totals
        water_totals = []
        current_date = week_start
        while current_date <= week_end:
            daily_total = self.get_daily_water_total(current_date.strftime("%Y-%m-%d"))
            water_totals.append(daily_total)
            current_date += datetime.timedelta(days=1)
        
        avg_water = sum(water_totals) / len(water_totals) if water_totals else 0
        
        return {
            'week_start': start_str,
            'week_end': end_str,
            'average_sleep_hours': round(avg_sleep, 2),
            'gym_sessions_attended': gym_attendance_count,
            'average_daily_water_ml': round(avg_water, 0),
            'opportunity_loss': opportunity_loss,
            'sleep_data': sleep_data,
            'gym_data': gym_data,
            'daily_water_totals': water_totals
        }
    
    def update_setting(self, setting_name: str, setting_value: str) -> bool:
        """Update a setting value"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO settings (setting_name, setting_value)
                VALUES (?, ?)
            ''', (setting_name, setting_value))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating setting: {e}")
            return False
    
    def get_setting(self, setting_name: str) -> Optional[str]:
        """Get a setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT setting_value FROM settings WHERE setting_name = ?', 
                      (setting_name,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None


if __name__ == "__main__":
    # Example usage
    tracker = HealthTracker()
    
    # Example data logging
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    print("Health Tracker initialized successfully!")
    print(f"Database created at: health_tracker.db")
    print("\nExample usage:")
    print("- tracker.log_sleep('2025-05-26', '23:00', '07:00', sleep_quality=8)")
    print("- tracker.log_gym_attendance('2025-05-26', True, 'Strength Training', 60, 300)")
    print("- tracker.log_water_intake(500)  # 500ml")
    print("- tracker.get_weekly_summary()")