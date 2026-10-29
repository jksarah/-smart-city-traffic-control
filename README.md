# Smart City Traffic Control

A smart traffic signal simulator using a custom pub-sub topic broker.
See smart_city_traffic_control_documentation.md for the project plan.

## Setup

```
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

Start each in its own terminal (environment active), in this order:

```
python broker/broker.py
python controller/controller.py
python simulator/simulator.py
```

Then open `web/index.html` in a browser. Click an intersection to force it green;
click again to cancel. The page reconnects by itself if the broker restarts.

Settings (intersections, timings) are in `config/config.json`.

## Test

```
python -m pytest tests
```
