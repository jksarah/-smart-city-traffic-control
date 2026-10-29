Web UI. Open `web/index.html` in a browser (broker must be running).

`index.html` is the page and `style.css` styles it. `app.js` connects to the broker and draws one map of connected roads with each intersection's light, queue and time left. `draw.js` draws the roads, lights and queued cars on the map canvas.

Intersections are laid out in a grid (3 per row). Each one has four road arms that join its neighbours' arms into a connected road network.

Click an intersection to force it green for a few seconds. Click it again to cancel.

The event log lists light changes, overrides and connection changes, newest first.
