from typing import Any, Iterable, Generator


def process_events(events: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    stations = {}
    latest_ts = None

    for msg in events:
        msg_type = msg.get("type")
        if msg_type == "sample":
            station = msg["stationName"]
            ts = msg["timestamp"]
            temp = msg["temperature"]
            # Update latest timestamp
            if (latest_ts is None) or (ts > latest_ts):
                latest_ts = ts
            # Update station high/low
            if station not in stations:
                stations[station] = {"high": temp, "low": temp}
            else:
                stations[station]["high"] = max(stations[station]["high"], temp)
                stations[station]["low"] = min(stations[station]["low"], temp)
        elif msg_type == "control":
            cmd = msg.get("command")
            if latest_ts is None:
                # Ignore control messages if no sample data is present
                continue
            if cmd == "snapshot":
                yield {
                    "type": "snapshot",
                    "asOf": latest_ts,
                    "stations": {k: dict(v) for k, v in stations.items()}
                }
            elif cmd == "reset":
                yield {
                    "type": "reset",
                    "asOf": latest_ts
                }
                stations.clear()
                latest_ts = None
            else:
                raise ValueError(
                    f"Unknown control command: {cmd}. Please verify input."
                )
        else:
            raise ValueError(
                f"Unknown message type: {msg_type}. Please verify input."
            )
