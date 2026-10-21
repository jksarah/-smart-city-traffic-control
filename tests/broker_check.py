import asyncio
import json

import websockets

URL = "ws://localhost:8765"
TOPIC = "IntersectionSensor"


async def main():
    async with websockets.connect(URL) as subscriber, websockets.connect(URL) as publisher:
        await subscriber.send(json.dumps({"type": "subscribe", "topic": TOPIC}))
        await asyncio.sleep(0.2)

        data = {"intersection_id": 1, "type": "arrive"}
        await publisher.send(json.dumps({"type": "publish", "topic": TOPIC, "data": data}))

        reply = await asyncio.wait_for(subscriber.recv(), timeout=2)
        print("Subscriber received:", reply)


if __name__ == "__main__":
    asyncio.run(main())
