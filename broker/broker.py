import asyncio
import json

import websockets

HOST = "localhost"
PORT = 8765

subscribers = {}


async def handle_client(websocket):
    try:
        async for raw_message in websocket:
            await handle_message(websocket, raw_message)
    finally:
        remove_client(websocket)


async def handle_message(websocket, raw_message):
    try:
        message = json.loads(raw_message)
        message_type = message["type"]
        topic = message["topic"]
    except (json.JSONDecodeError, KeyError, TypeError):
        await websocket.send(json.dumps({"error": "invalid message"}))
        return

    if message_type == "subscribe":
        subscribers.setdefault(topic, set()).add(websocket)
    elif message_type == "publish":
        publish(topic, message.get("data"))
    else:
        await websocket.send(json.dumps({"error": "unknown message type"}))


def publish(topic, data):
    payload = json.dumps({"topic": topic, "data": data})
    websockets.broadcast(subscribers.get(topic, ()), payload)


def remove_client(websocket):
    for clients in subscribers.values():
        clients.discard(websocket)


async def main():
    async with websockets.serve(handle_client, HOST, PORT):
        print(f"Broker listening on ws://{HOST}:{PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
