Python client library for the broker.

```python
from client import BrokerClient

async with BrokerClient() as c:
    await c.subscribe("IntersectionSensor")
    await c.publish("IntersectionSensor", {"intersection_id": 1})
    async for topic, data in c.messages():
        print(topic, data)
```

Test (broker must be running): `python tests/client_check.py`
