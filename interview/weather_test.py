import pytest
from . import weather

def test_basic_snapshot():
    events = [
        {
            "type": "sample",
            "stationName": "Montrose Harbor",
            "timestamp": 1001,
            "temperature": 42.3
        },
        {
            "type": "sample",
            "stationName": "Montrose Harbor",
            "timestamp": 1002,
            "temperature": 38.7
        },
        {
            "type": "sample",
            "stationName": "63rd Street Beach",
            "timestamp": 1003,
            "temperature": 55.0
        },
        {
            "type": "sample",
            "stationName": "63rd Street Beach",
            "timestamp": 1004,
            "temperature": 53.2
        },
        {"type": "control", "command": "snapshot"},
    ]
    out = list(weather.process_events(events))
    assert out == [{
        "type": "snapshot",
        "asOf": 1004,
        "stations": {
            "Montrose Harbor": {"high": 42.3, "low": 38.7},
            "63rd Street Beach": {"high": 55.0, "low": 53.2}
        }
    }]

def test_reset_and_ignore_control_before_sample():
    events = [
        {"type": "control", "command": "snapshot"},  # ignored
        {
            "type": "sample",
            "stationName": "Oakwood Beach",
            "timestamp": 2001,
            "temperature": 60.0
        },
        {
            "type": "sample",
            "stationName": "Oakwood Beach",
            "timestamp": 2002,
            "temperature": 58.5
        },
        {"type": "control", "command": "reset"},
        {"type": "control", "command": "snapshot"},  # ignored after reset
        {
            "type": "sample",
            "stationName": "Rainbow Beach",
            "timestamp": 2003,
            "temperature": 47.1
        },
        {"type": "control", "command": "snapshot"},
    ]
    out = list(weather.process_events(events))
    assert out[0] == {"type": "reset", "asOf": 2002}
    assert out[1] == {
        "type": "snapshot",
        "asOf": 2003,
        "stations": {"Rainbow Beach": {"high": 47.1, "low": 47.1}}
    }
    assert len(out) == 2

def test_unknown_message_type():
    events = [{"type": "unexpected_type"}]
    with pytest.raises(Exception) as e:
        list(weather.process_events(events))
    assert "Please verify input." in str(e.value)

def test_unknown_control_command():
    events = [
        {
            "type": "sample",
            "stationName": "12th Street Beach",
            "timestamp": 3001,
            "temperature": 65.2
        },
        {"type": "control", "command": "unknown_command"},
    ]
    with pytest.raises(Exception) as e:
        list(weather.process_events(events))
    assert "Please verify input." in str(e.value)
