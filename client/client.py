import json

import websockets

DEFAULT_URL = "ws://localhost:8765"


class BrokerClient:
    """Small wrapper around a WebSocket connection to the broker."""

    def __init__(self, url=DEFAULT_URL):
        self.url = url
        self._ws = None

    async def connect(self):
        self._ws = await websockets.connect(self.url)

    async def subscribe(self, topic):
        await self._send({"type": "subscribe", "topic": topic})

    async def publish(self, topic, data):
        await self._send({"type": "publish", "topic": topic, "data": data})

    async def messages(self):
        """Yield (topic, data) for each message received."""
        async for raw in self._ws:
            message = json.loads(raw)
            # Error replies have no topic, so they are not delivered as messages.
            if "error" in message:
                continue
            yield message["topic"], message["data"]

    async def close(self):
        if self._ws is not None:
            await self._ws.close()

    async def _send(self, message):
        await self._ws.send(json.dumps(message))

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *exc_info):
        await self.close()
