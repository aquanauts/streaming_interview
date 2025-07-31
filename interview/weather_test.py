from . import weather
import pytest

def test_basic_snapshot():
    events = [
        {"type": "sample", "stationName": "A", "timestamp": 1, "temperature": 10.0},
        {"type": "sample", "stationName": "A", "timestamp": 2, "temperature": 20.0},
        {"type": "sample", "stationName": "B", "timestamp": 3, "temperature": 5.0},
        {"type": "control", "command": "snapshot"},
    ]
    out = list(weather.process_events(events))
    assert out == [{
        "type": "snapshot",
        "asOf": 3,
        "stations": {
            "A": {"high": 20.0, "low": 10.0},
            "B": {"high": 5.0, "low": 5.0}
        }
    }]

def test_reset_and_ignore_control_before_sample():
    events = [
        {"type": "control", "command": "snapshot"},  # ignored
        {"type": "sample", "stationName": "A", "timestamp": 1, "temperature": 10.0},
        {"type": "sample", "stationName": "A", "timestamp": 2, "temperature": 20.0},
        {"type": "control", "command": "reset"},
        {"type": "control", "command": "snapshot"},  # ignored after reset
        {"type": "sample", "stationName": "A", "timestamp": 3, "temperature": 30.0},
        {"type": "control", "command": "snapshot"},
    ]
    out = list(weather.process_events(events))
    assert out[0] == {"type": "reset", "asOf": 2}
    assert out[1] == {
        "type": "snapshot",
        "asOf": 3,
        "stations": {"A": {"high": 30.0, "low": 30.0}}
    }
    assert len(out) == 2

def test_unknown_message_type():
    events = [{"type": "foo"}]
    with pytest.raises(Exception) as e:
        list(weather.process_events(events))
    assert "Please verify input." in str(e.value)

def test_unknown_control_command():
    events = [
        {"type": "sample", "stationName": "A", "timestamp": 1, "temperature": 10.0},
        {"type": "control", "command": "foo"},
    ]
    with pytest.raises(Exception) as e:
        list(weather.process_events(events))
    assert "Please verify input." in str(e.value)
