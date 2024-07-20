from typing import Any, Iterable, Generator, Dict

def process_events(events: Iterable[dict[str, Any]]) -> Generator[dict[str, Any], None, None]:
    weather_data: Dict[str, Dict[str, float]] = {}
    most_recent_timestamp: int | None = None

    for event in events:
        if event['type'] == 'sample':
            station = event['stationName']
            timestamp = event['timestamp']
            temperature = event['temperature']

            if station not in weather_data:
                weather_data[station] = {'high': temperature, 'low': temperature}
            else:
                weather_data[station]['high'] = max(weather_data[station]['high'], temperature)
                weather_data[station]['low'] = min(weather_data[station]['low'], temperature)

            if most_recent_timestamp is None or timestamp > most_recent_timestamp:
                most_recent_timestamp = timestamp

        elif event['type'] == 'control':
            command = event['command']
            if command == 'snapshot':
                if most_recent_timestamp is not None:
                    snapshot = {
                        'type': 'snapshot',
                        'asOf': most_recent_timestamp,
                        'stations': weather_data
                    }
                    yield snapshot
            elif command == 'reset':
                if most_recent_timestamp is not None:
                    reset_response = {
                        'type': 'reset',
                        'asOf': most_recent_timestamp
                    }
                    yield reset_response
                weather_data = {}
                most_recent_timestamp = None
        else:
            raise ValueError(f"Unknown message type: {event['type']}")
