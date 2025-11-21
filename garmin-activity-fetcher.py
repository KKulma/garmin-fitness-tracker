"""
Garmin Connect Activity Data Fetcher

This script connects to the Garmin Connect service to download a user's latest
activity data. It prompts for a username and password, and then fetches a
specified number of recent activities, displaying key details for each one.

It uses the 'garth' library to handle authentication and API communication.
"""

import getpass
import json
from datetime import timedelta

try:
    import garth
except ImportError:
    print("The 'garth' library is not installed. Please install it by running:")
    print("pip install garth")
    exit()

def display_activities(activities):
    """Formats and prints a list of activities."""
    if not activities:
        print("\nNo activities found.")
        return

    print(f"\n--- Found {len(activities)} activities ---")
    for i, activity in enumerate(activities):
        # Extract key information, with fallbacks for missing data
        activity_name = activity.get('activityName', 'N/A')
        activity_type = activity.get('activityType', {}).get('typeKey', 'N/A').replace('_', ' ').title()
        start_time = activity.get('startTimeLocal', 'N/A')

        # Format duration from seconds to HH:MM:SS
        duration_sec = activity.get('duration', 0)
        duration_formatted = str(timedelta(seconds=round(duration_sec)))

        # Format distance from meters to kilometers
        distance_m = activity.get('distance', 0)
        distance_km = distance_m / 1000 if distance_m else 0

        print(f"\n#{i + 1}: {activity_name} ({activity_type})")
        print(f"  - Date: {start_time}")
        print(f"  - Duration: {duration_formatted}")
        print(f"  - Distance: {distance_km:.2f} km")

def main():
    """Main function to run the data fetching process."""
    print("--- Garmin Connect Data Fetcher ---")
    print("You will be prompted for your email and password.")
    print("Your credentials are used once for login and are not stored in this script.")

    try:
        # Prompt for user credentials
        email = input("Enter your Garmin Connect email: ")
        password = getpass.getpass("Enter your password: ")

        # Initialize the Garmin client and attempt to log in
        # The garth library will cache the session in ~/.garth to avoid future logins
        
        # client = garth.Client()
        # client.login(email, password)
        
        garth.login(email, password)
        garth.save("~/.garth")
        
        print("\nLogin successful!")
        
        # Get number of activities to fetch
        while True:
            try:
                limit = int(input("How many recent activities would you like to fetch? (e.g., 10): "))
                if limit > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        print(f"\nFetching the last {limit} activities...")
        
        # Fetch the activities from the Garmin Connect API
        recent_activities = garth.connectapi.get_activities(start=0, limit=limit)
        
        display_activities(recent_activities)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("This could be due to incorrect credentials or a change in the Garmin API.")
        print("If you have 2FA enabled, you may need to authenticate through the browser first.")

if __name__ == "__main__":
    main()
