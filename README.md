# Garmin Activity Tracker

A Streamlit web application that fetches activity data from Garmin Connect, calculates custom "activity points" based on your daily movement, and visualizes your progress.

## Features

- **Garmin Connect Integration**: Securely logs in to your Garmin account to fetch steps and activity data.
- **Smart Data Sync**: Synchronizes historical data to a local SQLite database for fast access and offline viewing.
- **Custom Point System**: Calculates daily points based on:
    - **Steps**: Earn points for reaching 7,000, 10,000, and 12,500 steps.
    - **Activities**: Earn points for Strength Training and Cardio activities (weighted by duration and heart rate intensity).
- **Interactive Visualizations**:
    - **Home Dashboard**: View your current week's progress, daily status circles, and weekly goal completion.
    - **Calendar View**: Browse your activity history by month with a visual grid of your performance.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd garmin-activity-fetcher
    ```

2.  **Install dependencies**:
    It is recommended to use a virtual environment.
    ```bash
    # Create a virtual environment
    python -m venv .venv

    # Activate the virtual environment
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows:
    # .venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

## Usage

1.  **Login**: Upon first launch, enter your Garmin Connect email and password in the sidebar.
2.  **Sync**: The application will automatically sync your historical data (starting from Feb 1, 2025, by default).
3.  **Explore**:
    - Use the **Home** page to check your current week's standing.
    - Switch to the **Calendar** page via the sidebar to view past months.
4.  **Tooltips**: Hover over any day's circle to see a breakdown of steps and specific activities.

## Technologies

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python
- **APIs**: `garminconnect`, `garth`
- **Database**: SQLite

## Project Structure

- `app.py`: Main entry point and navigation logic.
- `modules/`: Contains core logic.
    - `backend.py`: Handles Garmin authentication, data fetching, and point calculations.
    - `database.py`: Manages SQLite database interactions.
    - `home.py`: Renders the weekly dashboard.
    - `calendar_page.py`: Renders the monthly calendar view.
- `assets/`: Static assets like CSS.
