import asyncio
import os
import sys

# The controller folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "controller"))

import controller
from controller import phase_duration


def test_green_is_base_for_short_queue():
    assert phase_duration("green", 2) == 6


def test_green_extends_with_queue():
    assert phase_duration("green", 8) == 11


def test_green_has_maximum():
    assert phase_duration("green", 100) == 15


def test_red_ignores_queue():
    assert phase_duration("red", 50) == 8


def reset(intersection_id):
    controller.axes[intersection_id] = "NS"
    controller.phases[intersection_id] = "green"
    controller.remaining[intersection_id] = 6
    controller.overridden.discard(intersection_id)
    for d in controller.queues[intersection_id]:
        controller.queues[intersection_id][d] = 0


def test_only_one_axis_is_lit():
    reset(1)
    assert controller.lights_of(1) == {"N": "green", "E": "red", "S": "green", "W": "red"}
    controller.phases[1] = "yellow"
    assert controller.lights_of(1) == {"N": "yellow", "E": "red", "S": "yellow", "W": "red"}


def test_green_then_yellow_then_other_axis():
    reset(1)
    controller.queues[1]["E"] = 1
    controller.remaining[1] = 1
    controller.advance(1)
    assert controller.phases[1] == "yellow"
    controller.remaining[1] = 1
    controller.advance(1)
    assert controller.axes[1] == "EW"
    assert controller.phases[1] == "green"


def test_axis_with_cars_keeps_turn_when_other_is_empty():
    reset(1)
    controller.queues[1]["N"] = 2
    controller.phases[1] = "yellow"
    controller.remaining[1] = 1
    controller.advance(1)
    assert controller.axes[1] == "NS"
    assert controller.phases[1] == "green"


def test_free_override_forces_green_on_that_axis():
    reset(2)
    controller.apply_override({"intersection_id": 2, "direction": "E", "action": "free", "duration": 10})
    assert controller.axes[2] == "EW"
    assert controller.phases[2] == "green"
    assert controller.remaining[2] == 10
    assert 2 in controller.overridden


def test_override_expires_into_yellow():
    reset(2)
    controller.apply_override({"intersection_id": 2, "direction": "N", "action": "free", "duration": 1})
    controller.advance(2)
    assert controller.phases[2] == "yellow"
    assert 2 not in controller.overridden


def test_cancel_ends_override_with_yellow():
    reset(2)
    controller.apply_override({"intersection_id": 2, "direction": "N", "action": "free", "duration": 10})
    controller.apply_override({"intersection_id": 2, "direction": "N", "action": "cancel"})
    assert controller.phases[2] == "yellow"
    assert 2 not in controller.overridden


def test_unknown_intersection_is_ignored():
    controller.apply_override({"intersection_id": 99, "direction": "N", "action": "free", "duration": 5})
    assert 99 not in controller.overridden


class FakeClient:
    def __init__(self):
        self.published = []

    async def publish(self, topic, data):
        self.published.append(data)


def test_publish_only_when_state_changes():
    reset(3)
    controller.last_published.pop(3, None)
    client = FakeClient()

    async def run():
        await controller.publish_state(client, 3)
        controller.remaining[3] -= 1
        await controller.publish_state(client, 3)
        controller.queues[3]["W"] += 1
        await controller.publish_state(client, 3)

    asyncio.run(run())
    assert len(client.published) == 2
    assert client.published[1]["queues"]["W"] == 1


def test_arrive_and_depart_change_direction_queue():
    reset(3)
    controller.apply_sensor_event({"intersection_id": 3, "direction": "S", "type": "arrive"})
    assert controller.queues[3]["S"] == 1
    controller.apply_sensor_event({"intersection_id": 3, "direction": "S", "type": "depart"})
    controller.apply_sensor_event({"intersection_id": 3, "direction": "S", "type": "depart"})
    assert controller.queues[3]["S"] == 0
