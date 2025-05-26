# Health & Fitness Tracker

A comprehensive Python web application to track sleep, gym attendance, water intake, and calculate opportunity loss from missed gym sessions.

## Quick Setup

1. **Install Python** (3.7 or higher)

2. **Install Flask:**
   ```bash
   pip install flask
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   Go to http://localhost:5000

## Features

- **Sleep Tracking**: Log bedtime, wake time, duration, and quality ratings
- **Gym Attendance**: Track workouts with type, duration, and calories burned
- **Water Intake**: Monitor daily hydration with quick-add buttons
- **Opportunity Loss**: Calculate financial impact of missed gym sessions
- **Reports**: View detailed analytics and progress over time
- **Settings**: Customize goals and membership costs

## Database

The app automatically creates a SQLite database (`health_tracker.db`) to store your data locally.

## Files Structure

- `health_tracker.py` - Core tracking logic and database operations
- `app.py` - Flask web application and routes
- `templates/` - HTML templates for the web interface
  - `base.html` - Base template with navigation
  - `dashboard.html` - Main dashboard with weekly summary
  - `log_sleep.html` - Sleep tracking form
  - `log_gym.html` - Gym attendance form
  - `log_water.html` - Water intake logging
  - `reports.html` - Detailed reports and analytics
  - `settings.html` - Application settings

## Usage Tips

1. Start by setting your goals in the Settings page
2. Use the quick water buttons for fast logging
3. Check the Reports page to see your progress trends
4. The opportunity loss calculation helps motivate gym attendance

Enjoy tracking your health journey! 🏋️💧😴
