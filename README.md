## Garmin Connect Activity Data Fetcher
This Python script connects to your Garmin Connect account to download and display your recent activity data directly in your terminal.

### Features
- Securely prompts for your Garmin Connect email and password.
- Fetches a user-specified number of the most recent activities.
- Displays key details for each activity, including name, type, date, duration, and distance.
- Uses session caching, so you only need to enter your password on the first run.

### Prerequisites
- Python 3.6 or newer.
- The pip package installer.

1. Installation
This script relies on the garth library to communicate with Garmin's services. You can install it using pip:

`pip install garth`

2. How to Run the Script
- Save the garmin-activity-fetcher.py file to your computer.
- Open a terminal or command prompt.
- Navigate to the directory where you saved the file.
- Run the script using the following command:

`python garmin-activity-fetcher.py`

The first time you run it, you will be prompted for your Garmin Connect email and password.

You will then be asked how many recent activities you wish to download. The script will fetch and display them.

### Subsequent Runs
The garth library securely saves your session token in a hidden directory in your user profile (~/.garth). This means you won't have to enter your password every time you run the script.

### Disclaimer
This application uses an unofficial API. Features may change or break if Garmin updates its services. Always be cautious when using third-party applications with your personal account credentials.# garmin-fitness-tracker
