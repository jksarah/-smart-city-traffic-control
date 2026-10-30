import asyncio
import os
import sys

# The client folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "client"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "config"))

from client import BrokerClient
from settings import load_config

SENSOR_TOPIC = "IntersectionSensor"
SIGNAL_TOPIC = "IntersectionSignal"
OVERRIDE_TOPIC = "IntersectionOverride"
CONFIG = load_config()
TICK_SECONDS = 1
BASE_DURATIONS = CONFIG["durations"]
EXTRA_QUEUE_THRESHOLD = CONFIG["extra_queue_threshold"]
MAX_GREEN_SECONDS = CONFIG["max_green_seconds"]
DEFAULT_OVERRIDE_SECONDS = CONFIG["default_override_seconds"]
DIRECTIONS = CONFIG["directions"]
# Opposite directions share a green; the two axes never are green together.
AXES = {"NS": ("N", "S"), "EW": ("E", "W")}
AXIS_OF = {d: axis for axis, dirs in AXES.items() for d in dirs}
OTHER_AXIS = {"NS": "EW", "EW": "NS"}

queues = {i: {d: 0 for d in DIRECTIONS} for i in CONFIG["intersections"]}
axes = {i: "NS" for i in queues}          # axis that is green or yellow
phases = {i: "green" for i in queues}     # "green" or "yellow" for that axis
remaining = {i: BASE_DURATIONS["green"] for i in queues}
overridden = set()
last_published = {}


def axis_queue(intersection_id, axis):
    return sum(queues[intersection_id][d] for d in AXES[axis])


def phase_duration(phase, queue_length):
    duration = BASE_DURATIONS[phase]
    if phase == "green":
        extra = max(0, queue_length - EXTRA_QUEUE_THRESHOLD)
        duration = min(duration + extra, MAX_GREEN_SECONDS)
    return duration


def lights_of(intersection_id):
    """Light colour for every direction."""
    axis, phase = axes[intersection_id], phases[intersection_id]
    return {d: (phase if AXIS_OF[d] == axis else "red") for d in DIRECTIONS}


def advance(intersection_id):
    """Count down one tick; green -> yellow, then give the turn to the next axis."""
    remaining[intersection_id] -= TICK_SECONDS
    if remaining[intersection_id] > 0:
        return
    overridden.discard(intersection_id)
    axis = axes[intersection_id]
    if phases[intersection_id] == "green":
        phases[intersection_id] = "yellow"
        remaining[intersection_id] = BASE_DURATIONS["yellow"]
        return
    # Yellow ended: switch axis unless only the current one has waiting cars.
    other = OTHER_AXIS[axis]
    if axis_queue(intersection_id, other) > 0 or axis_queue(intersection_id, axis) == 0:
        axes[intersection_id] = axis = other
    phases[intersection_id] = "green"
    remaining[intersection_id] = phase_duration("green", axis_queue(intersection_id, axis))


def apply_override(command):
    intersection_id = command.get("intersection_id")
    direction = command.get("direction")
    if intersection_id not in queues or direction not in AXIS_OF:
        return
    if command.get("action") == "free":
        axes[intersection_id] = AXIS_OF[direction]
        phases[intersection_id] = "green"
        remaining[intersection_id] = command.get("duration", DEFAULT_OVERRIDE_SECONDS)
        overridden.add(intersection_id)
    elif command.get("action") == "cancel" and intersection_id in overridden:
        # Green always ends in yellow, so the override never jumps straight to red.
        phases[intersection_id] = "yellow"
        remaining[intersection_id] = BASE_DURATIONS["yellow"]
        overridden.discard(intersection_id)


def current_state(intersection_id):
    return {
        "intersection_id": intersection_id,
        "lights": lights_of(intersection_id),
        "queues": dict(queues[intersection_id]),
        "override": intersection_id in overridden,
    }


async def publish_state(client, intersection_id):
    """Publish only when a light, queue or override flag changed."""
    state = current_state(intersection_id)
    if last_published.get(intersection_id) == state:
        return
    last_published[intersection_id] = state
    # Remaining is sent but not compared, so a countdown tick alone never publishes.
    await client.publish(SIGNAL_TOPIC, {**state, "remaining": remaining[intersection_id]})


def apply_sensor_event(event):
    intersection_id = event.get("intersection_id")
    direction = event.get("direction")
    if intersection_id not in queues or direction not in AXIS_OF:
        return
    if event.get("type") == "arrive":
        queues[intersection_id][direction] += 1
    elif event.get("type") == "depart":
        queues[intersection_id][direction] = max(0, queues[intersection_id][direction] - 1)


async def handle_messages(client):
    await client.subscribe(SENSOR_TOPIC)
    await client.subscribe(OVERRIDE_TOPIC)
    async for topic, data in client.messages():
        if topic == OVERRIDE_TOPIC:
            apply_override(data)
            intersection_id = data.get("intersection_id")
        else:
            apply_sensor_event(data)
            intersection_id = data.get("intersection_id")
        if intersection_id in queues:
            await publish_state(client, intersection_id)


async def run_signals(client):
    while True:
        await asyncio.sleep(TICK_SECONDS)
        for intersection_id in queues:
            advance(intersection_id)
            await publish_state(client, intersection_id)


async def main():
    async with BrokerClient() as client:
        await asyncio.gather(handle_messages(client), run_signals(client))


if __name__ == "__main__":
    asyncio.run(main())
