import requests
from datetime import datetime, timezone
import os

import display_mbta_lines
import libMBTA

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

def main():
    try:
        key = fetch_api_key()
    except Exception as e:
        return f"Unexpected error: {e}"

    station_name = input("Enter MBTA station name (e.g. 'Kendall', 'Park Street', 'Copley'): ").strip()
    stop_id, route_id = libMBTA.find_stop_id_by_name(station_name, key)

    if not stop_id:
        print(f"Could not find a stop matching '{station_name}' on the Red or Green Line.")
        return

    res = libMBTA.get_next_trains(stop_id, station_name, route_id, key)

    station_name = input("Enter MBTA station name (e.g. 'Kendall', 'Park Street', 'Copley'): ").strip()
    stop_id, route_id = libMBTA.find_stop_id_by_name(station_name, key)

    if not stop_id:
        print(f"Could not find a stop matching '{station_name}' on the Red or Green Line.")
        return

    res += libMBTA.get_next_trains(stop_id, station_name, route_id, key)

    display_mbta_lines.display_lines(res)

if __name__ == "__main__":
    main()

