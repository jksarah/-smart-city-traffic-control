import os
import sys

# The controller folder is not a package, so add it to the import path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "controller"))

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
