from typing import Any, Iterable, Generator


def process_events(events: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    # Dictionary to store per-station temperature extremes
    temp_extremes = {}
    # Track the latest timestamp seen in any sample
    most_recent_ts = None

    def handle_sample(event):
        nonlocal most_recent_ts
        station = event["stationName"]
        ts = event["timestamp"]
        temp = event["temperature"]
        if (most_recent_ts is None) or (ts > most_recent_ts):
            most_recent_ts = ts
        if station not in temp_extremes:
            temp_extremes[station] = {"high": temp, "low": temp}
        else:
            if temp > temp_extremes[station]["high"]:
                temp_extremes[station]["high"] = temp
            if temp < temp_extremes[station]["low"]:
                temp_extremes[station]["low"] = temp

    def handle_control(event):
        nonlocal most_recent_ts
        command = event.get("command")
        if most_recent_ts is None:
            return None
        if command == "snapshot":
            # Emit a snapshot of the current state for all stations
            return {
                "type": "snapshot",
                "asOf": most_recent_ts,
                "stations": {
                    station: dict(extremes)
                    for station, extremes in temp_extremes.items()
                }
            }
        if command == "reset":
            # Confirm reset and clear all accumulated data
            result = {
                "type": "reset",
                "asOf": most_recent_ts
            }
            temp_extremes.clear()
            most_recent_ts = None
            return result
        # Raise for unknown control commands, as required by the assignment
        raise ValueError(
            f"Unknown control command encountered: {command}. "
            "Please verify input."
        )

    for event in events:
        msg_type = event.get("type")
        if msg_type == "sample":
            handle_sample(event)
        elif msg_type == "control":
            result = handle_control(event)
            if result is not None:
                yield result
        else:
            # Raise for unknown message types, as required by the assignment
            raise ValueError(
                f"Unrecognized message type: {msg_type}. Please verify input."
            )
