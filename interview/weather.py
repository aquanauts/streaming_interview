from typing import Any, Iterable, Generator


def process_events(events: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    weather_stations = {}
    recent_timestamp = None

    for line in events:
        if line["type"] == "sample":
            station = line["stationName"]
            timestamp = line["timestamp"]
            temp = line["temperature"]

            if recent_timestamp is None or timestamp > recent_timestamp:
                recent_timestamp = timestamp

            if station not in weather_stations:
                weather_stations[station] = {
                    "high": temp,
                    "low": temp,
                    "timestamp": timestamp
                }
            else:
                if temp < weather_stations[station]["low"]:
                    weather_stations[station]["low"] = temp
                if temp > weather_stations[station]["high"]:
                    weather_stations[station]["high"] = temp
                weather_stations[station]["timestamp"] = timestamp

        elif line["type"] == "control":
            if line["command"] == "snapshot":
                if recent_timestamp is not None:
                    snapshot = {
                        "type": "snapshot",
                        "asOf": recent_timestamp,
                        "stations": {
                            station: {
                                "high": data["high"],
                                "low": data["low"]
                            } for station, data in weather_stations.items()
                        }
                    }
                    yield snapshot

            elif line["command"] == "reset":
                if recent_timestamp is not None:
                    reset = {
                        "type": "reset",
                        "asOf": recent_timestamp,
                    }
                    yield reset

                weather_stations.clear()
                recent_timestamp = None

            else:
                raise ValueError(
                    f"Unknown control command: {line['command']}. \n"
                    "Please verify input.")
        else:
            raise ValueError(f"Unknown message type: {line['type']}. \n"
                             "Please verify input.")
        