#!/usr/bin/env python3
"""
Database Update Scheduler
Automatically updates the quarterback database at regular intervals
"""

import schedule
import time
import sys
import os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from db_manager import DatabaseManager

def update_database_job():
    """Job to update the database"""
    print(f"\n[{datetime.now()}] Starting scheduled database update...")
    
    try:
        db_manager = DatabaseManager()
        db_manager.update_database()
        print(f"[{datetime.now()}] Database update completed successfully!")
    except Exception as e:
        print(f"[{datetime.now()}] Error updating database: {e}")

def main():
    print("🔄 ESPN QB Database Scheduler")
    print("=" * 40)
    
    # Set up scheduling
    print("Setting up scheduled updates...")
    
    # Update every 6 hours during the day
    schedule.every().day.at("06:00").do(update_database_job)
    schedule.every().day.at("12:00").do(update_database_job)
    schedule.every().day.at("18:00").do(update_database_job)
    
    # Update every hour during game days (Sunday, Monday, Thursday)
    schedule.every().sunday.at("13:00").do(update_database_job)
    schedule.every().sunday.at("14:00").do(update_database_job)
    schedule.every().sunday.at("15:00").do(update_database_job)
    schedule.every().sunday.at("16:00").do(update_database_job)
    schedule.every().sunday.at("17:00").do(update_database_job)
    schedule.every().sunday.at("18:00").do(update_database_job)
    schedule.every().sunday.at("19:00").do(update_database_job)
    schedule.every().sunday.at("20:00").do(update_database_job)
    schedule.every().sunday.at("21:00").do(update_database_job)
    schedule.every().sunday.at("22:00").do(update_database_job)
    schedule.every().sunday.at("23:00").do(update_database_job)
    
    schedule.every().monday.at("20:00").do(update_database_job)
    schedule.every().monday.at("21:00").do(update_database_job)
    schedule.every().monday.at("22:00").do(update_database_job)
    schedule.every().monday.at("23:00").do(update_database_job)
    
    schedule.every().thursday.at("20:00").do(update_database_job)
    schedule.every().thursday.at("21:00").do(update_database_job)
    schedule.every().thursday.at("22:00").do(update_database_job)
    schedule.every().thursday.at("23:00").do(update_database_job)
    
    print("Scheduled updates:")
    print("- Daily updates at 6:00 AM, 12:00 PM, and 6:00 PM")
    print("- Hourly updates during NFL game days (Sunday, Monday, Thursday)")
    print("- Press Ctrl+C to stop the scheduler")
    
    # Run initial update
    print(f"\n[{datetime.now()}] Running initial database update...")
    update_database_job()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] Scheduler stopped by user")
    except Exception as e:
        print(f"\n[{datetime.now()}] Scheduler error: {e}")
