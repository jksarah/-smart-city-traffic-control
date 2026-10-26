Traffic signal controller. Subscribes to `IntersectionSensor`, publishes `IntersectionSignal`.
Turns an intersection green when its queue reaches 3 cars, red when empty.

Run: `python controller/controller.py` (broker must be running).
