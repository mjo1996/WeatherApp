# Weather Forecast App

A powerful and visually rich Command Line Interface (CLI) application that provides comprehensive weather information for any location worldwide.

## 🚀 Features

- **🌍 Global Location Search**: Search for any city or region. If multiple matches are found, you can choose the exact location from a detailed list.
- **☀️ Today's Summary**: Get a detailed overview of the current day, including:
    - Maximum and minimum temperatures (and "feels like" temperatures).
    - Sunrise and sunset times, along with daylight and sunshine duration.
    - Precipitation totals, rain/snow breakdown, and probability.
    - Wind speed, gusts, and dominant direction (with directional arrows).
    - UV Index with descriptive levels (Low to Extreme).
- **🕒 Hourly Forecast**: A detailed hour-by-hour breakdown for the current day.
- **📅 Multi-Period Forecasts**:
    - **7-Day Forecast**: A clean table showing daily conditions, temperatures, precipitation, and wind.
    - **4-Week Forecast**: Extended seasonal forecasts split by week.
- **📜 Historical Weather**: Look up historical weather data for any custom date range or get a summary of the last 30 days.
- **🎨 Rich UI**: Built with the `rich` library for a modern terminal experience featuring panels, tables, and colors.

## 🛠️ Tech Stack

- **Language**: Python 3.12+
- **API**: [Open-Meteo API](https://open-meteo.com/) (No API key required)
- **Libraries**:
    - `requests`: For handling API communication.
    - `rich`: For the beautiful CLI layout and formatting.
    - `python-dateutil`: For date and time manipulations.

## 📦 Installation & Setup

### Prerequisites
Ensure you have Python 3.12 or later installed on your system.

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/mjo1996/WeatherApp.git
   cd WeatherApp
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 How to Run

Simply run the main script:
```bash
python3 weather.py
```

## 📖 Usage

1. **Search**: Enter the name of a city or region when prompted.
2. **Select**: Choose the correct location from the list (if multiple results appear).
3. **Explore**: Use the main menu to navigate between Today's Weather, Forecasts, and Historical data.
4. **Navigate**: Follow the on-screen prompts to search for new locations or exit the application.
