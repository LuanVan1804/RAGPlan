import requests
import json
from datetime import datetime
from typing import Optional
from langsmith.run_trees import RunTree

def get_weather(destination: str, start_date: str, end_date: str) -> dict:
    """Fetch weather forecast using Open-Meteo API (free, no auth required)."""
    try:
        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": destination, "count": 1, "language": "en", "format": "json"}
        geo_resp = requests.get(geocoding_url, params=geo_params, timeout=5)
        geo_resp.raise_for_status()

        if not geo_resp.json().get("results"):
            return {"error": f"Could not find location: {destination}", "status": "not_found"}

        location = geo_resp.json()["results"][0]
        lat, lon = location["latitude"], location["longitude"]

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "temperature_unit": "celsius"
        }
        weather_resp = requests.get(weather_url, params=weather_params, timeout=5)
        weather_resp.raise_for_status()

        weather_data = weather_resp.json()
        return {
            "destination": destination,
            "latitude": lat,
            "longitude": lon,
            "forecast": weather_data["daily"],
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


def calculate_trip_cost(
    destination: str,
    num_days: int,
    num_people: int,
    accommodation_type: str = "mid-range"
) -> dict:
    """Estimate trip costs (flights, hotels, meals)."""
    cost_estimates = {
        "budget": {"hotel": 30, "meals": 20, "activities": 15},
        "mid-range": {"hotel": 80, "meals": 40, "activities": 30},
        "luxury": {"hotel": 200, "meals": 100, "activities": 80}
    }

    rates = cost_estimates.get(accommodation_type, cost_estimates["mid-range"])

    accommodation_cost = rates["hotel"] * num_days * num_people
    meals_cost = rates["meals"] * num_days * num_people
    activities_cost = rates["activities"] * num_days * num_people
    flight_estimate = 200 * num_people

    total = accommodation_cost + meals_cost + activities_cost + flight_estimate

    return {
        "destination": destination,
        "days": num_days,
        "people": num_people,
        "breakdown": {
            "flights": flight_estimate,
            "accommodation": accommodation_cost,
            "meals": meals_cost,
            "activities": activities_cost
        },
        "total": total,
        "per_person": total / num_people if num_people > 0 else 0
    }


def parse_user_query(query: str) -> dict:
    """Extract travel details from user query."""
    query_lower = query.lower()

    num_days = 5
    num_people = 1
    budget = 3000
    accommodation_type = "mid-range"

    if "days" in query_lower or "day" in query_lower:
        import re
        match = re.search(r'(\d+)\s*-?\s*days?', query_lower)
        if match:
            num_days = int(match.group(1))

    if "people" in query_lower or "person" in query_lower:
        import re
        match = re.search(r'(\d+)\s*people?', query_lower)
        if match:
            num_people = int(match.group(1))

    if "$" in query or "budget" in query_lower:
        import re
        match = re.search(r'\$(\d+)', query)
        if match:
            budget = int(match.group(1))

    if "luxury" in query_lower or "5-star" in query_lower:
        accommodation_type = "luxury"
    elif "budget" in query_lower or "cheap" in query_lower:
        accommodation_type = "budget"

    words = query.split()
    destination = ""
    for i, word in enumerate(words):
        if word.lower() in ["to", "in", "at"]:
            if i + 1 < len(words):
                destination = " ".join(words[i+1:i+3]).strip(".,!?")
                break

    if not destination:
        destination = "Paris"

    return {
        "destination": destination,
        "days": num_days,
        "people": num_people,
        "budget": budget,
        "accommodation_type": accommodation_type
    }


def format_response(plan_data: dict) -> str:
    """Format travel plan for display."""
    result = f"## 🌍 Travel Plan: {plan_data.get('destination', 'Unknown')}\n\n"

    if "cost" in plan_data:
        cost = plan_data["cost"]
        result += "### 💰 Budget Breakdown\n"
        result += f"- **Flights**: ${cost.get('breakdown', {}).get('flights', 0)}\n"
        result += f"- **Accommodation**: ${cost.get('breakdown', {}).get('accommodation', 0)}\n"
        result += f"- **Meals**: ${cost.get('breakdown', {}).get('meals', 0)}\n"
        result += f"- **Activities**: ${cost.get('breakdown', {}).get('activities', 0)}\n"
        result += f"- **Total**: ${cost.get('total', 0)} (${cost.get('per_person', 0)}/person)\n\n"

    if "weather" in plan_data and plan_data["weather"].get("status") == "success":
        forecast = plan_data["weather"].get("forecast", {})
        result += "### 🌤️ Weather Forecast\n"
        temps = forecast.get("temperature_2m_max", [])
        if temps:
            avg_temp = sum(temps) / len(temps)
            result += f"- **Average Temperature**: {avg_temp:.1f}°C\n"
        result += "\n"

    if "documents" in plan_data:
        result += "### 📚 Travel Tips\n"
        result += plan_data["documents"] + "\n\n"

    result += "### ✈️ Itinerary\n"
    result += "- Day 1-2: Arrival & exploration\n"
    result += f"- Day 3-{plan_data.get('days', 5)-1}: Main activities\n"
    result += f"- Day {plan_data.get('days', 5)}: Departure\n"

    return result
