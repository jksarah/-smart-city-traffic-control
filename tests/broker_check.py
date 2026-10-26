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


async def check_latest_state():
    topic = "IntersectionSignal"
    async with websockets.connect(URL) as publisher:
        data = {"intersection_id": 1, "light": "green"}
        await publisher.send(json.dumps({"type": "publish", "topic": topic, "data": data}))
        await asyncio.sleep(0.2)

        async with websockets.connect(URL) as late_subscriber:
            await late_subscriber.send(json.dumps({"type": "subscribe", "topic": topic}))
            reply = await asyncio.wait_for(late_subscriber.recv(), timeout=2)
            print("Late subscriber received:", reply)


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(check_latest_state())
