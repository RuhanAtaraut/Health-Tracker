#!/usr/bin/env python3
"""
Health Tracker Web Application

A Flask web application for tracking sleep, gym attendance, water intake,
and calculating opportunity loss from missed gym sessions.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import datetime
import json
from health_tracker import HealthTracker

app = Flask(__name__)
app.secret_key = 'health_tracker_secret_key_2025'

# Initialize the health tracker
tracker = HealthTracker()

@app.route('/')
def dashboard():
    """Main dashboard showing weekly summary"""
    today = datetime.date.today().strftime("%Y-%m-%d")
    try:
        weekly_summary = tracker.get_weekly_summary(today)
        
        # Get daily water goal for progress calculation
        water_goal = int(tracker.get_setting('daily_water_goal_ml') or 2500)
        
        return render_template('dashboard.html', 
                             summary=weekly_summary, 
                             water_goal=water_goal,
                             today=today)
    except Exception as e:
        flash(f"Error loading dashboard: {e}", 'error')
        return render_template('dashboard.html', summary=None, water_goal=2500, today=today)

@app.route('/log-sleep', methods=['GET', 'POST'])
def log_sleep():
    """Log sleep data"""
    if request.method == 'POST':
        try:
            date = request.form['date']
            bedtime = request.form['bedtime']
            wake_time = request.form['wake_time']
            sleep_quality = int(request.form['sleep_quality']) if request.form.get('sleep_quality') else None
            notes = request.form['notes']
            
            success = tracker.log_sleep(date, bedtime, wake_time, sleep_quality, notes)
            
            if success:
                flash('Sleep data logged successfully!', 'success')
            else:
                flash('Error logging sleep data. Please check your inputs.', 'error')
                
        except Exception as e:
            flash(f'Error: {e}', 'error')
        
        return redirect(url_for('log_sleep'))
    
    # GET request - show form with today's date
    today = datetime.date.today().strftime("%Y-%m-%d")
    return render_template('log_sleep.html', today=today)

@app.route('/log-gym', methods=['GET', 'POST'])
def log_gym():
    """Log gym attendance"""
    if request.method == 'POST':
        try:
            date = request.form['date']
            attended = request.form['attended'] == 'true'
            workout_type = request.form['workout_type']
            duration = int(request.form['duration']) if request.form.get('duration') else None
            calories = int(request.form['calories']) if request.form.get('calories') else None
            notes = request.form['notes']
            
            success = tracker.log_gym_attendance(date, attended, workout_type, duration, calories, notes)
            
            if success:
                flash('Gym attendance logged successfully!', 'success')
            else:
                flash('Error logging gym attendance.', 'error')
                
        except Exception as e:
            flash(f'Error: {e}', 'error')
        
        return redirect(url_for('log_gym'))
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    return render_template('log_gym.html', today=today)

@app.route('/log-water', methods=['GET', 'POST'])
def log_water():
    """Log water intake"""
    if request.method == 'POST':
        try:
            amount = int(request.form['amount'])
            date = request.form.get('date') or None
            time_logged = request.form.get('time') or None
            notes = request.form['notes']
            
            success = tracker.log_water_intake(amount, date, time_logged, notes)
            
            if success:
                flash(f'Water intake logged: {amount}ml', 'success')
            else:
                flash('Error logging water intake.', 'error')
                
        except Exception as e:
            flash(f'Error: {e}', 'error')
        
        return redirect(url_for('log_water'))
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%H:%M")
    
    # Get today's water total for display
    today_total = tracker.get_daily_water_total(today)
    water_goal = int(tracker.get_setting('daily_water_goal_ml') or 2500)
    
    return render_template('log_water.html', 
                         today=today, 
                         now=now, 
                         today_total=today_total,
                         water_goal=water_goal)

@app.route('/reports')
def reports():
    """Show detailed reports and analytics"""
    # Get date range from query params or default to last 30 days
    end_date = request.args.get('end_date', datetime.date.today().strftime("%Y-%m-%d"))
    start_date = request.args.get('start_date', 
                                (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
    
    try:
        # Get data for the date range
        sleep_data = tracker.get_sleep_data(start_date, end_date)
        gym_data = tracker.get_gym_attendance_data(start_date, end_date)
        opportunity_loss = tracker.calculate_opportunity_loss(start_date, end_date)
        
        # Calculate some statistics
        total_sleep_hours = sum(s['sleep_duration_hours'] for s in sleep_data if s['sleep_duration_hours'])
        avg_sleep = total_sleep_hours / len(sleep_data) if sleep_data else 0
        
        gym_sessions_attended = sum(1 for g in gym_data if g['attended'])
        total_gym_entries = len(gym_data)
        gym_attendance_rate = (gym_sessions_attended / total_gym_entries * 100) if total_gym_entries > 0 else 0
        
        stats = {
            'avg_sleep_hours': round(avg_sleep, 2),
            'total_sleep_hours': round(total_sleep_hours, 1),
            'gym_attendance_rate': round(gym_attendance_rate, 1),
            'gym_sessions_attended': gym_sessions_attended,
            'total_gym_entries': total_gym_entries
        }
        
        return render_template('reports.html',
                             sleep_data=sleep_data,
                             gym_data=gym_data,
                             opportunity_loss=opportunity_loss,
                             stats=stats,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        flash(f"Error generating reports: {e}", 'error')
        return render_template('reports.html', 
                             sleep_data=[], 
                             gym_data=[], 
                             opportunity_loss={},
                             stats={},
                             start_date=start_date,
                             end_date=end_date)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Manage application settings"""
    if request.method == 'POST':
        try:
            # Update settings
            settings_to_update = [
                'daily_water_goal_ml',
                'weekly_gym_goal',
                'target_sleep_hours',
                'gym_membership_cost_monthly',
                'missed_workout_opportunity_cost'
            ]
            
            for setting in settings_to_update:
                if setting in request.form:
                    tracker.update_setting(setting, request.form[setting])
            
            flash('Settings updated successfully!', 'success')
            
        except Exception as e:
            flash(f'Error updating settings: {e}', 'error')
        
        return redirect(url_for('settings'))
    
    # GET request - load current settings
    current_settings = {}
    setting_names = [
        'daily_water_goal_ml',
        'weekly_gym_goal',
        'target_sleep_hours',
        'gym_membership_cost_monthly',
        'missed_workout_opportunity_cost'
    ]
    
    for setting in setting_names:
        current_settings[setting] = tracker.get_setting(setting)
    
    return render_template('settings.html', settings=current_settings)

@app.route('/api/daily-water/<date>')
def api_daily_water(date):
    """API endpoint to get daily water total"""
    try:
        total = tracker.get_daily_water_total(date)
        return jsonify({'total': total, 'date': date})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick-water', methods=['POST'])
def api_quick_water():
    """API endpoint for quick water logging"""
    try:
        data = request.get_json()
        amount = data.get('amount', 250)  # Default 250ml
        
        success = tracker.log_water_intake(amount)
        
        if success:
            today = datetime.date.today().strftime("%Y-%m-%d")
            new_total = tracker.get_daily_water_total(today)
            return jsonify({'success': True, 'new_total': new_total, 'amount_added': amount})
        else:
            return jsonify({'success': False, 'error': 'Failed to log water intake'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)