import sys
import json
from datetime import datetime, timedelta, date
from typing import Optional, Any

import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.prompt import Prompt
from rich.align import Align

console = Console()

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
SEASONAL_URL = "https://seasonal-api.open-meteo.com/v1/seasonal"

WMO_CODES: dict[int, dict[str, Any]] = {
    0: {"icon": "☀️", "label": "Clear Sky", "color": "yellow"},
    1: {"icon": "🌤️", "label": "Mainly Clear", "color": "yellow"},
    2: {"icon": "⛅", "label": "Partly Cloudy", "color": "light_cyan"},
    3: {"icon": "☁️", "label": "Overcast", "color": "grey58"},
    45: {"icon": "🌫️", "label": "Foggy", "color": "grey62"},
    48: {"icon": "🌫️", "label": "Depositing Rime Fog", "color": "grey62"},
    51: {"icon": "🌦️", "label": "Light Drizzle", "color": "cyan"},
    53: {"icon": "🌦️", "label": "Moderate Drizzle", "color": "cyan"},
    55: {"icon": "🌧️", "label": "Dense Drizzle", "color": "cyan"},
    56: {"icon": "🌧️", "label": "Light Freezing Drizzle", "color": "cyan"},
    57: {"icon": "🌧️", "label": "Dense Freezing Drizzle", "color": "cyan"},
    61: {"icon": "🌧️", "label": "Slight Rain", "color": "cyan"},
    63: {"icon": "🌧️", "label": "Moderate Rain", "color": "cyan"},
    65: {"icon": "🌧️", "label": "Heavy Rain", "color": "blue"},
    66: {"icon": "🌧️", "label": "Light Freezing Rain", "color": "cyan"},
    67: {"icon": "🌧️", "label": "Heavy Freezing Rain", "color": "blue"},
    71: {"icon": "🌨️", "label": "Slight Snow", "color": "white"},
    73: {"icon": "🌨️", "label": "Moderate Snow", "color": "white"},
    75: {"icon": "❄️", "label": "Heavy Snow", "color": "bright_white"},
    77: {"icon": "🌨️", "label": "Snow Grains", "color": "white"},
    80: {"icon": "🌦️", "label": "Slight Rain Showers", "color": "cyan"},
    81: {"icon": "🌧️", "label": "Moderate Rain Showers", "color": "cyan"},
    82: {"icon": "🌧️", "label": "Violent Rain Showers", "color": "blue"},
    85: {"icon": "🌨️", "label": "Slight Snow Showers", "color": "white"},
    86: {"icon": "🌨️", "label": "Heavy Snow Showers", "color": "bright_white"},
    95: {"icon": "⛈️", "label": "Thunderstorm", "color": "yellow"},
    96: {"icon": "⛈️", "label": "Thunderstorm with Slight Hail", "color": "yellow"},
    99: {"icon": "⛈️", "label": "Thunderstorm with Heavy Hail", "color": "red"},
}

DEFAULT_WMO = {"icon": "❓", "label": "Unknown", "color": "white"}


def get_wmo_info(code: int) -> dict[str, Any]:
    return WMO_CODES.get(code, DEFAULT_WMO)


def search_location(query: str) -> Optional[list[dict[str, Any]]]:
    params = {"name": query, "count": 10, "language": "en", "format": "json"}
    try:
        resp = requests.get(GEOCODING_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results")
    except requests.RequestException:
        return None


def fetch_forecast(lat: float, lon: float, days: int = 28) -> Optional[dict[str, Any]]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "sunrise",
            "sunset",
            "daylight_duration",
            "sunshine_duration",
            "uv_index_max",
            "precipitation_sum",
            "rain_sum",
            "showers_sum",
            "snowfall_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "wind_direction_10m_dominant",
        ],
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation_probability",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "forecast_days": days,
        "timezone": "auto",
    }
    try:
        resp = requests.get(FORECAST_URL, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


def fetch_archive(lat: float, lon: float, start_date: str, end_date: str) -> Optional[dict[str, Any]]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "sunrise",
            "sunset",
            "daylight_duration",
            "precipitation_sum",
            "rain_sum",
            "snowfall_sum",
            "wind_speed_10m_max",
        ],
        "timezone": "auto",
    }
    try:
        resp = requests.get(ARCHIVE_URL, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


def fetch_seasonal(lat: float, lon: float, days: int = 28) -> Optional[dict[str, Any]]:
    today = date.today()
    end_date = today + timedelta(days=days)
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": today.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_direction_10m_dominant",
            "uv_index_max",
        ],
        "timezone": "auto",
    }
    try:
        resp = requests.get(SEASONAL_URL, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


def choose_location(query: str) -> Optional[dict[str, Any]]:
    results = search_location(query)
    if not results:
        console.print("[red]No locations found. Try a different search.[/red]")
        return None

    if len(results) == 1:
        loc = results[0]
        name = f"{loc.get('name', 'Unknown')}, {loc.get('admin1', '')}, {loc.get('country', '')}"
        console.print(f"[green]Found:[/green] {name}")
        return loc

    table = Table(title="Select a Location", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Name", style="bold")
    table.add_column("Region")
    table.add_column("Country")
    table.add_column("Latitude", justify="right")
    table.add_column("Longitude", justify="right")

    for i, loc in enumerate(results, 1):
        table.add_row(
            str(i),
            loc.get("name", "Unknown"),
            loc.get("admin1", "") or "",
            loc.get("country", ""),
            f"{loc['latitude']:.2f}",
            f"{loc['longitude']:.2f}",
        )
    console.print(table)

    choice = Prompt.ask("Enter number", default="1")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(results):
            return results[idx]
    except ValueError:
        pass
    console.print("[red]Invalid choice.[/red]")
    return None


def weather_bar(value: float, max_val: float, width: int = 15, color: str = "cyan") -> str:
    if max_val <= 0:
        return " " * width
    filled = min(int((value / max_val) * width), width)
    bar = "\u2588" * filled + "\u2591" * (width - filled)
    return f"[{color}]{bar}[/{color}]"


def wind_direction_arrow(deg: float) -> str:
    directions = ["\u2193 N", "\u2199 NE", "\u2190 E", "\u2197 SE",
                   "\u2191 S", "\u2198 SW", "\u2192 W", "\u2196 NW"]
    idx = round(deg / 45) % 8
    return directions[idx]


def build_daily_row(day_data: dict[str, Any], is_forecast: bool = True) -> list[str]:
    date_str = day_data.get("date", "")
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    day_label = dt.strftime("%a %d %b")

    wmo = get_wmo_info(day_data.get("weather_code", 0))
    icon = wmo["icon"]
    label = wmo["label"]

    t_max = day_data.get("temperature_max", "N/A")
    t_min = day_data.get("temperature_min", "N/A")
    feels_like_max = day_data.get("apparent_temperature_max", "")
    feels_like_min = day_data.get("apparent_temperature_min", "")

    temp_text = f"{t_max}/{t_min}"
    if feels_like_max and feels_like_min:
        temp_text += f" (feels {feels_like_max}/{feels_like_min})"

    precip = day_data.get("precipitation_sum", 0)
    precip_prob = day_data.get("precipitation_probability_max")
    precip_text = f"{precip} mm"
    if is_forecast and precip_prob is not None:
        precip_text += f" ({precip_prob}%)"

    wind_speed = day_data.get("wind_speed_max", 0)
    wind_dir = day_data.get("wind_direction", 0)
    wind_text = f"{wind_speed} km/h {wind_direction_arrow(wind_dir)}" if wind_dir else f"{wind_speed} km/h"

    sunrise = day_data.get("sunrise", "")
    sunset = day_data.get("sunset", "")
    if sunrise and sunset:
        sunrise_t = sunrise.split("T")[1] if "T" in sunrise else sunrise
        sunset_t = sunset.split("T")[1] if "T" in sunset else sunset
        sun_text = f"\u2b06{sunrise_t} \u2b07{sunset_t}"
    else:
        sun_text = ""

    return [f"{icon} {day_label}", temp_text, precip_text, wind_text, sun_text]


def display_today_summary(data: dict[str, Any], location_name: str):
    daily = data.get("daily", {})
    if not daily:
        return

    idx = 0
    date_str = daily["time"][idx]
    dt = datetime.strptime(date_str, "%Y-%m-%d")

    wmo_code = daily["weather_code"][idx]
    wmo = get_wmo_info(wmo_code)
    icon = wmo["icon"]
    label = wmo["label"]

    t_max = daily["temperature_2m_max"][idx]
    t_min = daily["temperature_2m_min"][idx]
    feels_max = daily.get("apparent_temperature_max", [None])[idx]
    feels_min = daily.get("apparent_temperature_min", [None])[idx]
    precip = daily["precipitation_sum"][idx]
    rain = daily.get("rain_sum", [0])[idx]
    snow = daily.get("snowfall_sum", [0])[idx]
    precip_prob = daily.get("precipitation_probability_max", [None])[idx]
    wind = daily["wind_speed_10m_max"][idx]
    wind_gust = daily.get("wind_gusts_10m_max", [None])[idx]
    wind_dir = daily.get("wind_direction_10m_dominant", [0])[idx]
    uv = daily.get("uv_index_max", [None])[idx]
    sunrise = daily.get("sunrise", [""])[idx]
    sunset = daily.get("sunset", [""])[idx]
    daylight = daily.get("daylight_duration", [0])[idx]
    sunshine = daily.get("sunshine_duration", [0])[idx]

    if isinstance(sunrise, str) and "T" in sunrise:
        sunrise = sunrise.split("T")[1]
    if isinstance(sunset, str) and "T" in sunset:
        sunset = sunset.split("T")[1]

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=5),
        Layout(name="main"),
    )
    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )

    layout["header"].update(
        Panel(
            Align.center(
                Text(f"{icon}  {location_name}", style=f"bold {wmo['color']}"),
            ),
            style="bold",
        )
    )

    today_str = dt.strftime("%A, %B %d, %Y")
    header_info = f"[bold]{today_str}[/bold]\n{icon} [bold]{label}[/bold]"

    temp_info = (
        f"[bold]Temperature[/bold]\n"
        f"  High: {t_max}C\n"
        f"  Low:  {t_min}C\n"
    )
    if feels_max is not None and feels_min is not None:
        temp_info += f"  Feels like: {feels_max} / {feels_min}C\n"

    sun_info = ""
    if sunrise:
        sun_info = (
            f"[bold]Sun[/bold]\n"
            f"  \u2b06 Rise: {sunrise}\n"
            f"  \u2b07 Set:  {sunset}\n"
        )
        if daylight:
            hours = int(daylight // 3600)
            mins = int((daylight % 3600) // 60)
            sun_info += f"  Daylight: {hours}h {mins}m\n"
        if sunshine:
            hours = int(sunshine // 3600)
            mins = int((sunshine % 3600) // 60)
            sun_info += f"  Sunshine: {hours}h {mins}m\n"

    precip_info = f"[bold]Precipitation[/bold]\n  Total: {precip} mm\n  Rain: {rain} mm\n  Snow: {snow} cm\n"
    if precip_prob is not None:
        precip_info += f"  Probability: {precip_prob}%\n"

    wind_info = f"[bold]Wind[/bold]\n  Speed: {wind} km/h {wind_direction_arrow(wind_dir)}\n"
    if wind_gust is not None:
        wind_info += f"  Gusts: {wind_gust} km/h\n"

    uv_info = ""
    if uv is not None:
        uv_level = "Low"
        if uv >= 11:
            uv_level = "Extreme"
        elif uv >= 8:
            uv_level = "Very High"
        elif uv >= 6:
            uv_level = "High"
        elif uv >= 3:
            uv_level = "Moderate"
        uv_info = f"[bold]UV Index[/bold]\n  Max: {uv} ({uv_level})\n"

    left_content = Panel(header_info + "\n\n" + temp_info + "\n" + sun_info, box=box.ROUNDED)
    right_content = Panel(precip_info + "\n" + wind_info + "\n" + uv_info, box=box.ROUNDED)

    layout["left"].update(left_content)
    layout["right"].update(right_content)

    console.print(layout)


def display_weather_table(daily_data: dict[str, Any], title: str, is_forecast: bool = True):
    times = daily_data["time"]
    weather_codes = daily_data["weather_code"]
    t_maxs = daily_data["temperature_2m_max"]
    t_mins = daily_data["temperature_2m_min"]
    feels_maxs = daily_data.get("apparent_temperature_max", [None] * len(times))
    feels_mins = daily_data.get("apparent_temperature_min", [None] * len(times))
    precips = daily_data.get("precipitation_sum", [0] * len(times))
    precip_probs = daily_data.get("precipitation_probability_max", [None] * len(times))
    winds = daily_data.get("wind_speed_10m_max", [0] * len(times))
    wind_gusts = daily_data.get("wind_gusts_10m_max", [None] * len(times))
    wind_dirs = daily_data.get("wind_direction_10m_dominant", [0] * len(times))
    sunrises = daily_data.get("sunrise", [""] * len(times))
    sunsets = daily_data.get("sunset", [""] * len(times))
    rains = daily_data.get("rain_sum", [0] * len(times))
    snows = daily_data.get("snowfall_sum", [0] * len(times))

    table = Table(title=title, box=box.ROUNDED, header_style="bold cyan", show_lines=True)
    table.add_column("Day", style="bold", width=13)
    table.add_column("Condition", width=22)
    table.add_column("Temp (High/Low)", width=32)
    table.add_column("Precip", width=14)
    table.add_column("Wind", width=22)
    table.add_column("Sun", width=26)

    max_precip = max(precips) if precips else 1

    for i in range(len(times)):
        date_str = times[i]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day_label = dt.strftime("%a %d %b")

        wmo = get_wmo_info(weather_codes[i])
        icon = wmo["icon"]
        label = wmo["label"]

        t_max = t_maxs[i]
        t_min = t_mins[i]

        feels_line = ""
        if feels_maxs[i] is not None and feels_mins[i] is not None:
            feels_line = f"\n[dim]feels {feels_maxs[i]}/{feels_mins[i]}[/dim]"

        temp_text = f"{t_max} / {t_min}{feels_line}"

        precip_text = f"{precips[i]} mm"
        if is_forecast and precip_probs[i] is not None:
            precip_text += f" ({precip_probs[i]}%)"
        precip_text += f"\n{weather_bar(precips[i], max_precip)}"

        wind_text = f"{winds[i]} km/h"
        if wind_dirs[i]:
            wind_text += f"\n{wind_direction_arrow(wind_dirs[i])}"
        if wind_gusts[i] is not None:
            wind_text += f"\n[dim]gust {wind_gusts[i]} km/h[/dim]"

        sun_text = ""
        if sunrises[i]:
            sr = sunrises[i].split("T")[1] if "T" in sunrises[i] else sunrises[i]
            ss = sunsets[i].split("T")[1] if "T" in sunsets[i] else sunsets[i]
            sun_text = f"\u2b06{sr}\n\u2b07{ss}"
        else:
            sun_text = ""

        table.add_row(
            day_label,
            f"{icon} {label}",
            temp_text,
            precip_text,
            wind_text,
            sun_text,
        )

    console.print(table)


def display_hourly(data: dict[str, Any], day_index: int = 0):
    hourly = data.get("hourly", {})
    if not hourly:
        return

    times = hourly["time"]
    target_date = data["daily"]["time"][day_index]

    indices = [i for i, t in enumerate(times) if t.startswith(target_date)]
    if not indices:
        return

    table = Table(title=f"Hourly Forecast - {target_date}", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Time", style="bold", width=8)
    table.add_column("Condition", width=6)
    table.add_column("Temp", width=10)
    table.add_column("Feels", width=10)
    table.add_column("Humidity", width=10)
    table.add_column("Precip %", width=9)
    table.add_column("Wind", width=14)

    for i in indices:
        time_str = times[i].split("T")[1][:5]

        weather_code = hourly["weather_code"][i]
        wmo = get_wmo_info(weather_code)
        icon = wmo["icon"]

        temp = hourly["temperature_2m"][i]
        feels = hourly["apparent_temperature"][i]
        humidity = hourly["relative_humidity_2m"][i]
        precip_prob = hourly["precipitation_probability"][i]
        wind_speed = hourly["wind_speed_10m"][i]
        wind_dir = hourly["wind_direction_10m"][i]

        table.add_row(
            time_str,
            icon,
            f"{temp}C",
            f"{feels}C",
            f"{humidity}%",
            f"{precip_prob}%",
            f"{wind_speed} km/h {wind_direction_arrow(wind_dir)}",
        )

    console.print(table)


def display_archive_summary(data: dict[str, Any], location_name: str, start: str, end: str):
    daily = data.get("daily", {})
    if not daily:
        console.print("[red]No historical data available for this period.[/red]")
        return

    console.print()
    console.print(Panel(
        Align.center(f"[bold]Historical Weather: {location_name}[/bold]\n{start} to {end}"),
        box=box.DOUBLE,
    ))

    times = daily["time"]
    weather_codes = daily["weather_code"]
    t_maxs = daily["temperature_2m_max"]
    t_mins = daily["temperature_2m_min"]
    feels_maxs = daily.get("apparent_temperature_max", [None] * len(times))
    feels_mins = daily.get("apparent_temperature_min", [None] * len(times))
    precips = daily.get("precipitation_sum", [0] * len(times))
    winds = daily.get("wind_speed_10m_max", [0] * len(times))
    rains = daily.get("rain_sum", [0] * len(times))
    snows = daily.get("snowfall_sum", [0] * len(times))

    t_max_all = [t for t in t_maxs if t is not None]
    t_min_all = [t for t in t_mins if t is not None]
    avg_high = sum(t_max_all) / len(t_max_all) if t_max_all else 0
    avg_low = sum(t_min_all) / len(t_min_all) if t_min_all else 0
    total_precip = sum(precips)
    avg_wind = sum(winds) / len(winds) if winds else 0

    summary = Panel(
        f"[bold]Period Summary[/bold]\n"
        f"  Avg High: {avg_high:.1f}C  |  Avg Low: {avg_low:.1f}C\n"
        f"  Total Precipitation: {total_precip:.1f} mm  |  Avg Wind: {avg_wind:.1f} km/h\n"
        f"  Days recorded: {len(times)}",
        box=box.ROUNDED,
    )
    console.print(summary)
    console.print()

    table = Table(box=box.ROUNDED, header_style="bold cyan", show_lines=True)
    table.add_column("Date", style="bold", width=12)
    table.add_column("Condition", width=22)
    table.add_column("High/Low", width=20)
    table.add_column("Precip", width=10)
    table.add_column("Wind", width=12)

    max_precip = max(precips) if precips else 1

    for i in range(len(times)):
        date_str = times[i]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day_label = dt.strftime("%a %d %b")

        wmo = get_wmo_info(weather_codes[i])
        icon = wmo["icon"]

        t_max = t_maxs[i]
        t_min = t_mins[i]
        temp_text = f"{t_max} / {t_min}"

        precip_text = f"{precips[i]} mm\n{weather_bar(precips[i], max_precip)}"

        wind_text = f"{winds[i]} km/h"

        table.add_row(day_label, f"{icon} {wmo['label']}", temp_text, precip_text, wind_text)

    console.print(table)


def run():
    console.print()
    title = Panel(
        Align.center(
            Text("Weather Forecast App", style="bold cyan"),
        ),
        box=box.DOUBLE,
        subtitle="Powered by Open-Meteo API",
    )
    console.print(title)
    console.print()

    query = Prompt.ask("[bold]Search for a location[/bold]")
    if not query:
        console.print("[red]No location entered. Exiting.[/red]")
        return

    location = choose_location(query)
    if not location:
        return

    loc_name = f"{location.get('name', 'Unknown')}, {location.get('admin1', '')}, {location.get('country', '')}"
    lat = location["latitude"]
    lon = location["longitude"]

    while True:
        console.print()
        console.print(Panel(
            Align.center(Text(f"{loc_name}  ({lat:.2f}, {lon:.2f})", style="bold")),
        ))
        console.print()

        menu = Panel(
            "[1] Today's Weather\n"
            "[2] 7-Day Forecast\n"
            "[3] 4-Week Forecast\n"
            "[4] Historical Weather\n"
            "[5] Search New Location\n"
            "[6] Exit",
            title="Menu",
            box=box.ROUNDED,
        )
        console.print(menu)

        choice = Prompt.ask("Select an option", default="1")

        if choice == "1":
            console.print("[dim]Fetching today's weather...[/dim]")
            data = fetch_forecast(lat, lon, days=1)
            if data:
                display_today_summary(data, loc_name)
                console.print()
                display_hourly(data, 0)
            else:
                console.print("[red]Failed to fetch weather data.[/red]")

        elif choice == "2":
            console.print("[dim]Fetching 7-day forecast...[/dim]")
            data = fetch_forecast(lat, lon, days=7)
            if data:
                daily = data["daily"]
                display_hourly(data, 0)
                console.print()
                display_weather_table(daily, f"7-Day Forecast - {loc_name}")
            else:
                console.print("[red]Failed to fetch forecast data.[/red]")

        elif choice == "3":
            console.print("[dim]Fetching 4-week forecast...[/dim]")
            data = fetch_seasonal(lat, lon, days=28)
            if data:
                daily = data["daily"]
                for week in range(4):
                    start = week * 7
                    end = min(start + 7, len(daily["time"]))
                    week_data = {k: v[start:end] for k, v in daily.items()}
                    display_weather_table(week_data, f"Week {week + 1} - {loc_name}")
                    console.print()
            else:
                console.print("[red]Failed to fetch 4-week forecast data.[/red]")

        elif choice == "4":
            console.print()
            console.print("[bold]Historical Weather Lookup[/bold]")
            console.print("Enter date range (or press Enter for last 30 days):")
            start_input = Prompt.ask("Start date [YYYY-MM-DD]", default="")
            end_input = Prompt.ask("End date [YYYY-MM-DD]", default="")

            today = date.today()
            if not start_input and not end_input:
                end_date = today - timedelta(days=1)
                start_date = end_date - timedelta(days=29)
            else:
                try:
                    start_date = datetime.strptime(start_input, "%Y-%m-%d").date()
                    end_date = datetime.strptime(end_input, "%Y-%m-%d").date()
                except ValueError:
                    console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")

            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            console.print(f"[dim]Fetching historical data from {start_str} to {end_str}...[/dim]")
            data = fetch_archive(lat, lon, start_str, end_str)
            if data:
                display_archive_summary(data, loc_name, start_str, end_str)
            else:
                console.print("[red]Failed to fetch historical data.[/red]")

        elif choice == "5":
            console.print()
            query = Prompt.ask("[bold]Search for a location[/bold]")
            if query:
                location = choose_location(query)
                if location:
                    loc_name = f"{location.get('name', 'Unknown')}, {location.get('admin1', '')}, {location.get('country', '')}"
                    lat = location["latitude"]
                    lon = location["longitude"]
            continue

        elif choice == "6":
            console.print("[yellow]Goodbye![/yellow]")
            break

        else:
            console.print("[red]Invalid option.[/red]")

        console.print()
        continue_choice = Prompt.ask("Press Enter to continue or [q] to quit", default="")
        if continue_choice.lower() == "q":
            console.print("[yellow]Goodbye![/yellow]")
            break


def main():
    try:
        run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
