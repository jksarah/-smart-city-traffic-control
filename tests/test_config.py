import os
import sys

# The config folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "config"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "controller"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "simulator"))

from settings import load_config


def test_config_has_required_settings():
    config = load_config()
    assert config["intersections"]
    assert set(config["durations"]) == {"red", "green", "yellow"}
    assert len(config["arrival_delay_seconds"]) == 2


def test_controller_and_simulator_use_config_intersections():
    import controller
    import simulator
    ids = load_config()["intersections"]
    assert list(controller.queues) == ids
    assert list(simulator.waiting) == ids
