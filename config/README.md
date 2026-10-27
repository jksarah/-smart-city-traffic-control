Configuration files.

`config.json` holds the settings used by the controller and simulator.
Edit it and restart the components to apply changes. `settings.py` loads it.

| Setting | Meaning |
| :--- | :--- |
| `intersections` | Intersection ids. Add an id to add an intersection. |
| `durations` | Seconds for each light: `red`, `green`, `yellow`. |
| `extra_queue_threshold` | Green is extended by 1 second per car above this queue length. |
| `max_green_seconds` | Longest green the extension can reach. |
| `default_override_seconds` | Override length when the command gives no duration. |
| `arrival_delay_seconds` | Min and max seconds between car arrivals in the simulator. |
