import asyncio
import os
import sys

# The client folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "client"))

from client import BrokerClient

TOPIC = "IntersectionSensor"


async def main():
    async with BrokerClient() as subscriber, BrokerClient() as publisher:
        await subscriber.subscribe(TOPIC)
        # Give the broker time to register the subscription before publishing.
        await asyncio.sleep(0.2)

        await publisher.publish(TOPIC, {"intersection_id": 1, "type": "arrive"})

        messages = subscriber.messages()
        topic, data = await asyncio.wait_for(anext(messages), timeout=2)
        print("Subscriber received:", topic, data)


if __name__ == "__main__":
    asyncio.run(main())
