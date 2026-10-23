import asyncio
import os
import random
import sys

# The client folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "client"))

from client import BrokerClient

TOPIC = "IntersectionSensor"
INTERSECTION_COUNT = 5
MIN_DELAY_SECONDS = 0.5
MAX_DELAY_SECONDS = 2


async def main():
    async with BrokerClient() as client:
        while True:
            event = {"intersection_id": random.randint(1, INTERSECTION_COUNT), "type": "arrive"}
            await client.publish(TOPIC, event)
            print("Sent:", event)
            await asyncio.sleep(random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS))


if __name__ == "__main__":
    asyncio.run(main())
