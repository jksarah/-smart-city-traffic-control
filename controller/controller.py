import asyncio
import os
import sys

# The client folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "client"))

from client import BrokerClient

SENSOR_TOPIC = "IntersectionSensor"
SIGNAL_TOPIC = "IntersectionSignal"
GREEN_QUEUE_LENGTH = 3
RELEASE_SECONDS = 1

queues = {}
lights = {}


def update_light(intersection_id):
    queue = queues[intersection_id]
    light = lights.get(intersection_id, "red")
    if light == "red" and queue >= GREEN_QUEUE_LENGTH:
        lights[intersection_id] = "green"
    elif light == "green" and queue == 0:
        lights[intersection_id] = "red"


async def publish_state(client, intersection_id):
    state = {
        "intersection_id": intersection_id,
        "light": lights.get(intersection_id, "red"),
        "queue": queues[intersection_id],
    }
    await client.publish(SIGNAL_TOPIC, state)


async def handle_arrivals(client):
    await client.subscribe(SENSOR_TOPIC)
    async for _, event in client.messages():
        if event["type"] != "arrive":
            continue
        intersection_id = event["intersection_id"]
        queues[intersection_id] = queues.get(intersection_id, 0) + 1
        update_light(intersection_id)
        await publish_state(client, intersection_id)


async def release_cars(client):
    while True:
        await asyncio.sleep(RELEASE_SECONDS)
        for intersection_id in list(queues):
            if lights.get(intersection_id) == "green":
                queues[intersection_id] -= 1
                update_light(intersection_id)
                await publish_state(client, intersection_id)


async def main():
    async with BrokerClient() as client:
        await asyncio.gather(handle_arrivals(client), release_cars(client))


if __name__ == "__main__":
    asyncio.run(main())
