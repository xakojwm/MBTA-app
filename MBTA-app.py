import requests
from datetime import datetime, timezone
import display_mbta_lines
import os

MBTA_BASE_URL = "https://api-v3.mbta.com"

# Routes to search (Red Line + all Green Line branches)
ROUTE_IDS = ["Red", "Green-B", "Green-C", "Green-D", "Green-E"]

def fetch_api_key(filename="secrets.txt"):
    """
    Reads the contents of a file located in the user's home directory.

    Args:
        filename (str): The name of the file (relative to the home directory).

    Returns:
        str: The contents of the file, or an error message if something goes wrong.
    """
    try:
        home_dir = os.path.expanduser("~")
        file_path = os.path.join(home_dir, filename)

        with open(file_path, 'r', encoding='utf-8') as file:
            key = file.read()

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found in {home_dir}")
        raise
    except PermissionError:
        print(f"Error: Permission denied when accessing '{filename}'")
        raise
    except Exception as e:
        print( f"Unexpected error: {e}")
        raise


def find_stop_id_by_name(station_name,key):
    """
    Find the stop ID for a given station name by searching Red and Green Lines.
    Returns (stop_id, route_id) tuple.
    """
    for route_id in ROUTE_IDS:
        url = f"{MBTA_BASE_URL}/stops"
        params = {"filter[route]": route_id, "page[limit]": 100, "api_key":key}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        for stop in data["data"]:
            name = stop["attributes"]["name"].lower()
            if station_name.lower() in name:
                return stop["id"], route_id
    return None, None


def get_next_trains(stop_id,key):
    """
    Fetch the next inbound and outbound train departures for a given MBTA stop.
    """
    url = f"{MBTA_BASE_URL}/predictions"
    params = {
        "filter[stop]": stop_id,
        "sort": "departure_time",
        "page[limit]": 20,
        "include": "route,trip,stop",
         "api_key":key,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if not data["data"]:
        print("No upcoming predictions for this stop.")
        return

    now = datetime.now(timezone.utc)
    next_departures = {0: None, 1: None}  # inbound, outbound

    for prediction in data["data"]:
        attrs = prediction["attributes"]
        dep_time = attrs.get("departure_time")
        if not dep_time:
            continue

        dep = datetime.fromisoformat(dep_time.replace("Z", "+00:00"))
        if dep <= now:
            continue

        direction = attrs.get("direction_id", 0)
        if next_departures[direction] is None:
            next_departures[direction] = {
                "time": dep,
                "route_id": prediction["relationships"]["route"]["data"]["id"],
                "trip_id": prediction["relationships"]["trip"]["data"]["id"]
            }

        if all(next_departures.values()):
            break

    res = []
    # Print results
    for direction_id, direction_name in [(0, "Inbound"), (1, "Outbound")]:
        info = next_departures[direction_id]
        if info:
            res.append(f"{direction_name}: Next {info['route_id']} Line train departs at "
                  f"{info['time'].strftime('%I:%M:%S %p')} (Trip ID: {info['trip_id']})")
        else:
            res.append(f"{direction_name}: No upcoming departures found.")
    
    return res

def main():
    try:
        key = fetch_api_key()
    except Exception as e:
        return f"Unexpected error: {e}"

    station_name = input("Enter MBTA station name (e.g. 'Kendall', 'Park Street', 'Copley'): ").strip()
    stop_id, route_id = find_stop_id_by_name(station_name, key)

    if not stop_id:
        print(f"Could not find a stop matching '{station_name}' on the Red or Green Line.")
        return

    print(f"Found stop ID: {stop_id} (Route: {route_id})")
    res = get_next_trains(stop_id, key)

    station_name = input("Enter MBTA station name (e.g. 'Kendall', 'Park Street', 'Copley'): ").strip()
    stop_id, route_id = find_stop_id_by_name(station_name, key)

    if not stop_id:
        print(f"Could not find a stop matching '{station_name}' on the Red or Green Line.")
        return

    print(f"Found stop ID: {stop_id} (Route: {route_id})")
    res += get_next_trains(stop_id, key)

    display_mbta_lines.display_lines(res)

if __name__ == "__main__":
    main()

