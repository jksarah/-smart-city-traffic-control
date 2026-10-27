import asyncio
import os
import sys

# The controller folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "controller"))

import controller
from controller import next_phase, phase_duration


def test_cycle_order():
    assert next_phase("red") == "green"
    assert next_phase("green") == "yellow"
    assert next_phase("yellow") == "red"


def test_green_is_base_for_short_queue():
    assert phase_duration("green", 2) == 6


def test_green_extends_with_queue():
    assert phase_duration("green", 8) == 11


def test_green_has_maximum():
    assert phase_duration("green", 100) == 15


def test_red_ignores_queue():
    assert phase_duration("red", 50) == 8


def reset(intersection_id):
    controller.phases[intersection_id] = "red"
    controller.remaining[intersection_id] = 8
    controller.overridden.discard(intersection_id)


def test_free_override_forces_green():
    reset(2)
    controller.apply_override({"intersection_id": 2, "action": "free", "duration": 10})
    assert controller.phases[2] == "green"
    assert controller.remaining[2] == 10
    assert 2 in controller.overridden


def test_override_expires_into_yellow():
    reset(2)
    controller.apply_override({"intersection_id": 2, "action": "free", "duration": 1})
    controller.advance(2)
    assert controller.phases[2] == "yellow"
    assert 2 not in controller.overridden


def test_cancel_ends_override_with_yellow():
    reset(2)
    controller.apply_override({"intersection_id": 2, "action": "free", "duration": 10})
    controller.apply_override({"intersection_id": 2, "action": "cancel"})
    assert controller.phases[2] == "yellow"
    assert 2 not in controller.overridden


def test_unknown_intersection_is_ignored():
    controller.apply_override({"intersection_id": 99, "action": "free", "duration": 5})
    assert 99 not in controller.overridden


class FakeClient:
    def __init__(self):
        self.published = []

    async def publish(self, topic, data):
        self.published.append(data)


def test_publish_only_when_state_changes():
    reset(3)
    controller.last_published.pop(3, None)
    controller.queues[3] = 0
    client = FakeClient()

    async def run():
        await controller.publish_state(client, 3)
        controller.remaining[3] -= 1
        await controller.publish_state(client, 3)
        controller.queues[3] += 1
        await controller.publish_state(client, 3)

    asyncio.run(run())
    assert len(client.published) == 2
    assert client.published[1]["queue"] == 1
