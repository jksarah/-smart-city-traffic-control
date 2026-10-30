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

DIRECTIONS = CONFIG["directions"]

waiting = {(i, d): 0 for i in CONFIG["intersections"] for d in DIRECTIONS}
lights = {key: "red" for key in waiting}


def roads_to_release():
    """(intersection, direction) roads with a green light and a waiting car."""
    return [key for key in waiting if lights[key] == "green" and waiting[key] > 0]


async def send_event(client, intersection_id, direction, event_type):
    event = {"intersection_id": intersection_id, "direction": direction, "type": event_type}
    await client.publish(SENSOR_TOPIC, event)
    print("Sent:", event)


async def read_signals(client):
    await client.subscribe(SIGNAL_TOPIC)
    async for _, state in client.messages():
        for direction, light in state["lights"].items():
            if (state["intersection_id"], direction) in lights:
                lights[(state["intersection_id"], direction)] = light


async def generate_arrivals(client):
    while True:
        intersection_id = random.choice(CONFIG["intersections"])
        direction = random.choice(DIRECTIONS)
        waiting[(intersection_id, direction)] += 1
        await send_event(client, intersection_id, direction, "arrive")
        await asyncio.sleep(random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS))


async def release_cars(client):
    while True:
        await asyncio.sleep(DEPART_SECONDS)
        for intersection_id, direction in roads_to_release():
            waiting[(intersection_id, direction)] -= 1
            await send_event(client, intersection_id, direction, "depart")


async def main():
    async with BrokerClient() as client:
        await asyncio.gather(
            read_signals(client), generate_arrivals(client), release_cars(client)
        )


if __name__ == "__main__":
    asyncio.run(main())
