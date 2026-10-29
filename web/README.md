Web UI. Open `web/index.html` in a browser (broker must be running).

`index.html` is the page and `style.css` styles it. `app.js` connects to the broker and shows a card for each intersection with its light, queue and time left. `draw.js` draws the road, light and queued cars on each card's canvas.

Click an intersection card to force it green for a few seconds. Click it again to cancel.
