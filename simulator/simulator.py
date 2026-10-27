import asyncio
import os
import random
import sys

# The client folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "client"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "config"))

from client import BrokerClient
from settings import load_config

SENSOR_TOPIC = "IntersectionSensor"
SIGNAL_TOPIC = "IntersectionSignal"
CONFIG = load_config()
MIN_DELAY_SECONDS, MAX_DELAY_SECONDS = CONFIG["arrival_delay_seconds"]
DEPART_SECONDS = 1

waiting = {i: 0 for i in CONFIG["intersections"]}
lights = {i: "red" for i in waiting}


def intersections_to_release():
    """Intersections with a green light and at least one waiting car."""
    return [i for i in waiting if lights[i] == "green" and waiting[i] > 0]


async def send_event(client, intersection_id, event_type):
    event = {"intersection_id": intersection_id, "type": event_type}
    await client.publish(SENSOR_TOPIC, event)
    print("Sent:", event)


async def read_signals(client):
    await client.subscribe(SIGNAL_TOPIC)
    async for _, state in client.messages():
        if state["intersection_id"] in lights:
            lights[state["intersection_id"]] = state["light"]


async def generate_arrivals(client):
    while True:
        intersection_id = random.choice(CONFIG["intersections"])
        waiting[intersection_id] += 1
        await send_event(client, intersection_id, "arrive")
        await asyncio.sleep(random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS))


async def release_cars(client):
    while True:
        await asyncio.sleep(DEPART_SECONDS)
        for intersection_id in intersections_to_release():
            waiting[intersection_id] -= 1
            await send_event(client, intersection_id, "depart")


async def main():
    async with BrokerClient() as client:
        await asyncio.gather(
            read_signals(client), generate_arrivals(client), release_cars(client)
        )


if __name__ == "__main__":
    asyncio.run(main())
