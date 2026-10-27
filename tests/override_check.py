import asyncio
import os
import sys

# The client folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "client"))

from client import BrokerClient

OVERRIDE_TOPIC = "IntersectionOverride"


async def main():
    async with BrokerClient() as client:
        command = {"intersection_id": 2, "action": "free", "duration": 10, "source": "check"}
        await client.publish(OVERRIDE_TOPIC, command)
        print("Sent override:", command)


if __name__ == "__main__":
    asyncio.run(main())
