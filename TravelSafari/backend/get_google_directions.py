# backend/get_google_directions.py
import requests
from typing import List, Dict, Any


def get_google_directions(api_key: str, locations: List[str]) -> Dict[str, Any]:
    if len(locations) < 2:
        return {"error": "At least 2 locations are required"}

    origin = locations[0]
    destination = locations[-1]
    waypoints = "|".join(locations[1:-1]) if len(locations) > 2 else ""

    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "waypoints": waypoints,
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return {"error": f"Failed to fetch directions: {response.status_code}"}

    data = response.json()
    if data.get("status") != "OK":
        return {"error": data.get("error_message", "API Error")}

    # Extract coordinates (polyline of route)
    route_points = []
    for leg in data["routes"][0]["legs"]:
        for step in leg["steps"]:
            start = step["start_location"]
            route_points.append({"lat": start["lat"], "lng": start["lng"]})
        # Add last point of leg
        end = leg["end_location"]
        route_points.append({"lat": end["lat"], "lng": end["lng"]})

    return {"route": route_points}
