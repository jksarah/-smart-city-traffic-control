import os
import sys

# The simulator folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "simulator"))

import simulator


def test_only_green_with_waiting_cars_release():
    simulator.waiting.update({1: 2, 2: 2, 3: 0})
    simulator.lights.update({1: "green", 2: "red", 3: "green"})
    assert simulator.intersections_to_release() == [1]
