import asyncio
import os
import sys

# The client folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "client"))

from client import BrokerClient

SENSOR_TOPIC = "IntersectionSensor"
SIGNAL_TOPIC = "IntersectionSignal"
OVERRIDE_TOPIC = "IntersectionOverride"
INTERSECTION_COUNT = 5
TICK_SECONDS = 1
PHASE_ORDER = ["red", "green", "yellow"]
BASE_DURATIONS = {"red": 8, "green": 6, "yellow": 2}
EXTRA_QUEUE_THRESHOLD = 3
MAX_GREEN_SECONDS = 15
DEFAULT_OVERRIDE_SECONDS = 10

queues = {i: 0 for i in range(1, INTERSECTION_COUNT + 1)}
phases = {i: "red" for i in queues}
remaining = {i: BASE_DURATIONS["red"] for i in queues}
overridden = set()


def next_phase(phase):
    index = PHASE_ORDER.index(phase)
    return PHASE_ORDER[(index + 1) % len(PHASE_ORDER)]


def phase_duration(phase, queue_length):
    duration = BASE_DURATIONS[phase]
    if phase == "green":
        extra = max(0, queue_length - EXTRA_QUEUE_THRESHOLD)
        duration = min(duration + extra, MAX_GREEN_SECONDS)
    return duration


def advance(intersection_id):
    """Count down one tick; move to the next phase when time runs out."""
    remaining[intersection_id] -= TICK_SECONDS
    if remaining[intersection_id] <= 0:
        phase = next_phase(phases[intersection_id])
        phases[intersection_id] = phase
        overridden.discard(intersection_id)
        remaining[intersection_id] = phase_duration(phase, queues[intersection_id])


def apply_override(command):
    intersection_id = command.get("intersection_id")
    if intersection_id not in queues:
        return
    if command.get("action") == "free":
        phases[intersection_id] = "green"
        remaining[intersection_id] = command.get("duration", DEFAULT_OVERRIDE_SECONDS)
        overridden.add(intersection_id)
    elif command.get("action") == "cancel" and intersection_id in overridden:
        # Green always ends in yellow, so the override never jumps straight to red.
        phases[intersection_id] = "yellow"
        remaining[intersection_id] = BASE_DURATIONS["yellow"]
        overridden.discard(intersection_id)


async def publish_state(client, intersection_id):
    state = {
        "intersection_id": intersection_id,
        "light": phases[intersection_id],
        "queue": queues[intersection_id],
        "remaining": remaining[intersection_id],
        "override": intersection_id in overridden,
    }
    await client.publish(SIGNAL_TOPIC, state)


async def handle_messages(client):
    await client.subscribe(SENSOR_TOPIC)
    await client.subscribe(OVERRIDE_TOPIC)
    async for topic, data in client.messages():
        if topic == OVERRIDE_TOPIC:
            apply_override(data)
            intersection_id = data.get("intersection_id")
        elif data["type"] == "arrive":
            intersection_id = data["intersection_id"]
            queues[intersection_id] += 1
        else:
            continue
        if intersection_id in queues:
            await publish_state(client, intersection_id)


async def run_signals(client):
    while True:
        await asyncio.sleep(TICK_SECONDS)
        for intersection_id in queues:
            if phases[intersection_id] == "green" and queues[intersection_id] > 0:
                queues[intersection_id] -= 1
            advance(intersection_id)
            await publish_state(client, intersection_id)


async def main():
    async with BrokerClient() as client:
        await asyncio.gather(handle_messages(client), run_signals(client))


if __name__ == "__main__":
    asyncio.run(main())
