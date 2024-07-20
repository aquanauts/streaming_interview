from . import weather

def test_weather_sample_handling():
    events = [
        {
            "type": "sample", "stationName": "Station1",
            "timestamp": 1672531200000, "temperature": 30.0
        },
        {
            "type": "sample", "stationName": "Station1",
            "timestamp": 1672534800000, "temperature": 32.0
        },
        {
            "type": "sample", "stationName": "Station1",
            "timestamp": 1672538400000, "temperature": 28.0
        },
    ]
    expected_output = [
        {
            "type": "snapshot", "asOf": 1672538400000,
            "stations": {"Station1": {"high": 32.0, "low": 28.0}}
        }
    ]
    events.append({"type": "control", "command": "snapshot"})
    output = list(weather.process_events(events))
    assert output == expected_output

def test_reset_handling():
    events = [
        {
            "type": "sample", "stationName": "Station1",
            "timestamp": 1672531200000, "temperature": 30.0
        },
        {"type": "control", "command": "reset"},
    ]
    expected_output = [
        {"type": "reset", "asOf": 1672531200000}
    ]
    output = list(weather.process_events(events))
    assert output == expected_output

def test_unknown_message_type():
    events = [
        {
            "type": "unknown", "stationName": "Station1",
            "timestamp": 1672531200000, "temperature": 30.0
        },
    ]
    try:
        list(weather.process_events(events))
        assert False, "Expected ValueError for unknown message type"
    except ValueError as e:
        assert str(e) == "Unknown message type: unknown"
