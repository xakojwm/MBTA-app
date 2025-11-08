import requests
from datetime import datetime, timezone

MBTA_BASE_URL = "https://api-v3.mbta.com"

# Routes to search (Red Line + all Green Line branches)
ROUTE_IDS = ["Red", "Green-B", "Green-C", "Green-D", "Green-E"]

def direction_shortener( direction_str ):
    if 'in' in direction_str.lower():
        return 'IN :'
    elif 'out' in direction_str.lower():
        return 'OUT:'
    else:
        return ":( "


def res_string_formatter( info, direction_name ):
    if info:
        s = f"{direction_shortener(direction_name)} {info['time'].strftime('%I:%M %p')}"
    else:
        s = ":( ... kys"

    return s

def normalize_text_lengths( lines_dicts ):
    max_text_len = 0
    for line in lines_dicts:
        max_text_len = max(max_text_len, len(line['moving_text']))

    for line in lines_dicts:
        line['moving_text'] = line['moving_text'] + ( ' ' * ( max_text_len - len(line['moving_text'])))

    return lines_dicts

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


def get_next_trains(stop_id, station_name, route_id_arg, key):
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

    res = []
    if not data["data"]:
        for direction_id, direction_name in [(0, "Inbound"), (1, "Outbound")]:
            if info:
                res.append({"route_id": route_id_arg, "static_text": station_name[:4] + ':', "moving_text": res_string_formatter( None, direction_name, station_name ) })
            else:
                res.append({"route_id": route_id_arg, "static_text": station_name[:4] + ':', "moving_text": res_string_formatter( None, direction_name, station_name)})
        
        return res

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
    for direction_id, direction_name in [(0, "Inbound"), (1, "Outbound")]:
        info = next_departures[direction_id]
        if info:
            res.append({"route_id": route_id_arg, "static_text": station_name[:4] + ':', "moving_text": res_string_formatter( info, direction_name ) })
        else:
            res.append({"route_id": route_id_arg, "static_text": station_name[:4] + ':', "moving_text": res_string_formatter( info, direction_name )})
    
    # Add spaces to end of line text
    res = normalize_text_lengths( res )

    return res