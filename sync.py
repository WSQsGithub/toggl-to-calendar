import requests
import json
from datetime import datetime, timedelta
import subprocess
import sys
import hashlib

import json

import os

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
with open(config_path) as f:
    config = json.load(f)
TOGGL_API_TOKEN = config["TOGGL_API_TOKEN"]
TOGGL_WORKSPACE_ID = config["TOGGL_WORKSPACE_ID"]
id_to_name = config["id_to_name"]

def get_last_week_entries(start_date=None, end_date=None):
    """Fetch time entries from the last week using Toggl API"""

    print(f"Fetching entries from {start_date} to {end_date}")
    
    # Toggl API endpoint
    url = f"https://api.track.toggl.com/api/v9/me/time_entries"
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    # Make API request
    try:
        response = requests.get(
            url,
            params=params,
            auth=(TOGGL_API_TOKEN, "api_token")
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Toggl: {e}")
        return []


def get_yesterday_entries():
    """Fetch time entries from yesterday using Toggl API"""
    # Calculate yesterday's date range
    yesterday = datetime.now() - timedelta(days=1)
    start_date = yesterday.strftime("%Y-%m-%dT00:00:00.000Z")
    end_date = yesterday.strftime("%Y-%m-%dT23:59:59.999Z")
    
    # Toggl API endpoint
    url = f"https://api.track.toggl.com/api/v9/me/time_entries"
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    # Make API request
    try:
        response = requests.get(
            url,
            params=params,
            auth=(TOGGL_API_TOKEN, "api_token")
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Toggl: {e}")
        return []

def get_project_name(entry):
    """Extract project name from time entry"""
    if 'project_id' in entry and entry['project_id']:
        project_id = str(entry['project_id'])  # Ensure it's a string
        return id_to_name.get(project_id)
    return None

def get_tags(entry)-> str:
    """Extract tags from time entry to #tag1, #tag2 format"""
    if 'tags' in entry and entry['tags']:
        return ', '.join([f"#{tag}" for tag in entry['tags']])
    return ""

def parse_datetime(iso_string):
    """Parse ISO datetime string to AppleScript-compatible format"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        # Convert to local timezone
        return dt.astimezone()
    except ValueError as e:
        print(f"Error parsing datetime {iso_string}: {e}")
        return None

def generate_event_id(title, start_time, end_time):
    """Generate a unique ID for the event based on title and time"""
    # Create a unique string from event details
    event_string = f"{title}_{start_time.isoformat()}_{end_time.isoformat()}"
    # Generate a hash
    return hashlib.md5(event_string.encode()).hexdigest()[:8]

def check_existing_event(calendar_name, title, start_time, end_time):
    """Check if an event already exists in the calendar"""
    
    # Format dates for AppleScript
    start_year = start_time.year
    start_month = start_time.month
    start_day = start_time.day
    start_hour = start_time.hour
    start_minute = start_time.minute
    
    end_year = end_time.year
    end_month = end_time.month
    end_day = end_time.day
    end_hour = end_time.hour
    end_minute = end_time.minute
    
    # Escape quotes in title and calendar name for AppleScript
    safe_title = title.replace('"', '\\"')
    safe_calendar = calendar_name.replace('"', '\\"')
    
    # Generate unique event ID
    event_id = generate_event_id(title, start_time, end_time)
    
    # AppleScript to check for existing event
    applescript = f'''
tell application "Calendar"
    try
        set targetCalendar to calendar "{safe_calendar}"
        
        -- Create date objects for comparison
        set startDate to (current date)
        set year of startDate to {start_year}
        set month of startDate to {start_month}
        set day of startDate to {start_day}
        set hours of startDate to {start_hour}
        set minutes of startDate to {start_minute}
        set seconds of startDate to 0
        
        set endDate to (current date)
        set year of endDate to {end_year}
        set month of endDate to {end_month}
        set day of endDate to {end_day}
        set hours of endDate to {end_hour}
        set minutes of endDate to {end_minute}
        set seconds of endDate to 0
        
        -- Check for existing events with same title, start time, and end time
        set existingEvents to (every event of targetCalendar whose summary is "{safe_title}" and start date is startDate and end date is endDate)
        
        -- Also check for events with our unique ID in the description
        set existingEventsById to (every event of targetCalendar whose description contains "{event_id}")
        
        if (count of existingEvents) > 0 or (count of existingEventsById) > 0 then
            return "EXISTS"
        else
            return "NOT_EXISTS"
        end if
        
    on error errMsg
        return "ERROR: " & errMsg
    end try
end tell
'''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"ERROR: {result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return "ERROR: AppleScript timeout"
    except Exception as e:
        return f"ERROR: Subprocess error: {e}"

def create_calendar_event(calendar_name, title, start_time, end_time, tag_str=""):
    """Create calendar event using AppleScript"""
    
    # Format dates for AppleScript using proper date construction
    start_year = start_time.year
    start_month = start_time.month
    start_day = start_time.day
    start_hour = start_time.hour
    start_minute = start_time.minute
    
    end_year = end_time.year
    end_month = end_time.month
    end_day = end_time.day
    end_hour = end_time.hour
    end_minute = end_time.minute
    
    print(f"  Debug: Creating event from {start_time} to {end_time}")
    
    # Escape quotes in title and calendar name for AppleScript
    safe_title = title.replace('"', '\\"')
    safe_calendar = calendar_name.replace('"', '\\"')
    
    # Generate unique event ID
    event_id = generate_event_id(title, start_time, end_time)

    # Generate description with unique ID
    description = f"Imported from Toggl - ID: {event_id} \n{tag_str}"
    
    # AppleScript to create calendar event
    applescript = f'''
tell application "Calendar"
    try
        -- List all calendars first
        set calendarNames to name of every calendar
        log "Available calendars: " & (calendarNames as string)
        
        -- Try to find the calendar
        set targetCalendar to calendar "{safe_calendar}"
        log "Found calendar: " & name of targetCalendar
        
        -- Create proper date objects
        set startDate to (current date)
        set year of startDate to {start_year}
        set month of startDate to {start_month}
        set day of startDate to {start_day}
        set hours of startDate to {start_hour}
        set minutes of startDate to {start_minute}
        set seconds of startDate to 0
        
        set endDate to (current date)
        set year of endDate to {end_year}
        set month of endDate to {end_month}
        set day of endDate to {end_day}
        set hours of endDate to {end_hour}
        set minutes of endDate to {end_minute}
        set seconds of endDate to 0
        
        log "Start date: " & (startDate as string)
        log "End date: " & (endDate as string)
        
        -- Create the event
        set newEvent to make new event at end of events of targetCalendar with properties {{¬
            summary:"{safe_title}", ¬
            start date:startDate, ¬
            end date:endDate ¬
        }}
        
        log "Created event: " & summary of newEvent
        
        -- Set description with unique ID to prevent future duplicates
        try
            set description of newEvent to "Imported from Toggl - ID: {event_id}"
        on error
            -- Continue without description if it fails
        end try
        
        return "Success: Created event '" & "{safe_title}" & "'"
    on error errMsg
        return "Error: " & errMsg
    end try
end tell
'''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
            
    except subprocess.TimeoutExpired:
        return False, "AppleScript timeout"
    except Exception as e:
        return False, f"Subprocess error: {e}"

def format_duration(seconds):
    """Format duration in seconds to readable format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
    
def send_macos_notification(title, message):
    """Send a native macOS notification using AppleScript"""
    script = f'display notification "{message}" with title "{title}"'
    try:
        subprocess.run(["osascript", "-e", script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Notification failed: {e}")

def sync():
    print("Fetching last week's time entries from Toggl...")

    today = datetime.now()
    start_date = (today - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00.000Z")
    end_date = (today).strftime("%Y-%m-%dT23:59:59.999Z")


    send_macos_notification("Toggl → Calendar Sync", f"Syncing Toggl entries from 🗓️ {start_date[:10]} to 🗓️ {end_date[:10]}")
    
    # Get time entries
    entries = get_last_week_entries(start_date=start_date, end_date=end_date)
    
    if not entries:
        print("No time entries found for last week.")
        return
    
    print(f"Found {len(entries)} time entries")
    
    created_count = 0
    skipped_count = 0
    duplicate_count = 0
    error_count = 0
    
    for entry in entries:
        # Get project name
        project_name = get_project_name(entry)
        
        if not project_name:
            print(f"Skipping entry without project: {entry.get('description', 'No description')}")
            skipped_count += 1
            continue
        
        # Get entry details
        description = entry.get('description', 'No description')
        start_time = parse_datetime(entry.get('start', ''))
        end_time = parse_datetime(entry.get('stop', ''))
        duration = entry.get('duration', 0)
        tag_str = get_tags(entry)
        
        if not start_time or not end_time:
            print(f"Skipping entry with invalid time: {description}")
            skipped_count += 1
            continue
        
        # Check if event already exists
        print(f"Checking for existing event: '{description}' in '{project_name}' calendar")
        exists_result = check_existing_event(project_name, description, start_time, end_time)
        
        if exists_result == "EXISTS":
            print(f"  ⚠️  Event already exists, skipping")
            duplicate_count += 1
            continue
        elif exists_result.startswith("ERROR"):
            print(f"  ⚠️  Error checking for existing event: {exists_result}")
            # Continue to create the event anyway
        
        # Create calendar event
        print(f"Creating event: '{description}' in '{project_name}' calendar ({format_duration(duration)})")
        
        success, message = create_calendar_event(
            project_name,
            description,
            start_time,
            end_time,
            tag_str
        )
        
        if success:
            created_count += 1
            print(f"  ✓ Created successfully")
        else:
            error_count += 1
            print(f"  ✗ Failed: {message}")
    
    # Summary
    print("=" * 40)
    print(f"\nSummary:")
    print("=" * 40)
    print(f"  Created: {created_count}")
    print(f"  Duplicates found: {duplicate_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")
    print("-" * 40)

    summary_msg = f"Created: {created_count}, Skipped: {skipped_count}, Duplicates: {duplicate_count}, Errors: {error_count}"
    send_macos_notification("Toggl → Calendar Sync ✅", summary_msg)

if __name__ == "__main__":
    # Check if required libraries are installed
    try:
        import requests
    except ImportError:
        print("Error: 'requests' library not found. Install with: pip install requests")
        sys.exit(1)
    
    sync()
