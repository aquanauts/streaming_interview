import json
import sys
from . import weather

def generate_input():
    for line in sys.stdin:
        yield json.loads(line)

for output in weather.process_events(generate_input()):
    print(json.dumps(output))
