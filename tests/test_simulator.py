import os
import sys

# The simulator folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "simulator"))

import simulator


def test_only_green_roads_with_waiting_cars_release():
    for key in simulator.waiting:
        simulator.waiting[key] = 0
        simulator.lights[key] = "red"
    simulator.waiting.update({(1, "N"): 2, (1, "E"): 2, (1, "S"): 0})
    simulator.lights.update({(1, "N"): "green", (1, "E"): "red", (1, "S"): "green"})
    assert simulator.roads_to_release() == [(1, "N")]
