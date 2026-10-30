Traffic signal controller. Subscribes to `IntersectionSensor` and `IntersectionOverride`, publishes `IntersectionSignal`.
Each intersection has four signals (N, E, S, W) and a queue per direction. N+S share a green, then E+W; the other axis is red.
Green is longer when the queue is long; an axis with no cars is skipped.

Sensor message: `{intersection_id, direction, type: arrive|depart}`.
Signal message: `{intersection_id, lights: {N,E,S,W}, queues: {N,E,S,W}, override, remaining}`.
Override message: `{intersection_id, direction, action: free|cancel}`.

Run: `python controller/controller.py` (broker must be running).
