from . import weather

# def test_no_events():
#     assert [{}] == list(weather.process_events([{}]))

def test_sample_events():

    # Test 1: single weather event
    events = [
        {"type": "sample", "stationName": "Ohio Street", \
         "timestamp": 1672531000000, "temperature": 55.0},
        {"type": "control", "command": "snapshot"}
    ]
    output = list(weather.process_events(events))
    assert output == [
        {
            "type": "snapshot",
            "asOf": 1672531000000,
            "stations": {
                "Ohio Street": {"high": 55.0, "low": 55.0}
            }
        }
    ], f"Test 1 failed with output: {output}"

    # Test 2: multiple weather events, one station
    events = [
        {"type": "sample", "stationName": "Ohio Street", \
         "timestamp": 1672531000000, "temperature": 15.0},
        {"type": "sample", "stationName": "Ohio Street", \
         "timestamp": 1672535000000, "temperature": 20.0},
        {"type": "sample", "stationName": "Ohio Street", \
         "timestamp": 1672539000000, "temperature": 10.0},
        {"type": "control", "command": "snapshot"}
    ]
    output = list(weather.process_events(events))
    assert output == [
        {
            "type": "snapshot",
            "asOf": 1672539000000,
            "stations": {
                "Ohio Street": {"high": 20.0, "low": 10.0}
            }
        }
    ], f"Test 2 failed with output: {output}"

    # Test 3: multiple weather events, multiple stations
    events = [
        {"type": "sample", "stationName": "Ohio Street", \
         "timestamp": 1672531000000, "temperature": 15.0},
        {"type": "sample", "stationName": "Calumet", \
         "timestamp": 1672535000000, "temperature": 5.0},
        {"type": "sample", "stationName": "Ohio Street", \
         "timestamp": 1672539000000, "temperature": 25.0},
        {"type": "control", "command": "snapshot"}
    ]
    output = list(weather.process_events(events))
    assert output == [
        {
            "type": "snapshot",
            "asOf": 1672539000000,
            "stations": {
                "Ohio Street": {"high": 25.0, "low": 15.0},
                "Calumet": {"high": 5.0, "low": 5.0}
            }
        }
    ], f"Test 3 failed with output: {output}"

    # Test 4: reset
    events = [
        {"type": "sample", "stationName": "Ohio Street", \
         "timestamp": 1672531000000, "temperature": 15.0},
        {"type": "control", "command": "reset"},
        {"type": "sample", "stationName": "Ohio Street", \
         "timestamp": 1672539000000, "temperature": 25.0},
        {"type": "control", "command": "snapshot"}
    ]
    output = list(weather.process_events(events))
    assert output == [
        {
            "type": "reset",
            "asOf": 1672531000000
        },
        {
            "type": "snapshot",
            "asOf": 1672539000000,
            "stations": {
                "Ohio Street": {"high": 25.0, "low": 25.0}
            }
        }
    ], f"Test 4 failed with output: {output}"

    # Test 5: snapshot with no data
    events = [
        {"type": "control", "command": "snapshot"},
        {"type": "sample", "stationName": "Ohio Street", \
         "timestamp": 1672531000000, "temperature": 15.0},
        {"type": "control", "command": "snapshot"}
    ]
    output = list(weather.process_events(events))
    assert output == [
        {
            "type": "snapshot",
            "asOf": 1672531000000,
            "stations": {
                "Ohio Street": {"high": 15.0, "low": 15.0}
            }
        }
    ], f"Test 4 failed with output: {output}"

    # Test 6: reset with no data
    events = [
        {"type": "control", "command": "reset"},
        {"type": "sample", "stationName": "Ohio Street", \
         "timestamp": 1672531200000, "temperature": 15.0},
        {"type": "control", "command": "snapshot"}
    ]
    output = list(weather.process_events(events))
    assert output == [
        {
            "type": "snapshot",
            "asOf": 1672531200000,
            "stations": {
                "Ohio Street": {"high": 15.0, "low": 15.0}
            }
        }
    ], f"Test 4 failed with output: {output}"

    # Test 7: invalid input
    events = [
        {"type": "unknown", "stationName": "Ohio Street", \
         "timestamp": 1672531200000, "temperature": 15.0},
    ]
    try:
        output = list(weather.process_events(events))
        assert False, "Test 7 failed: Exception not raised."
    except ValueError as e:
        assert "Please verify input." in str(e), f"Test 7 failed: {str(e)}"

    # Test 8: unknown command
    events = [{"type": "control", "command": "unknown"}]
    try:
        output = list(weather.process_events(events))
        assert False, "Test 8 failed: Exception not raised."
    except ValueError as e:
        assert "Please verify input." in str(e), f"Test 8 failed: {str(e)}"
        