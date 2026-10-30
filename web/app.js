const BROKER_URL = "ws://localhost:8765";
const SIGNAL_TOPIC = "IntersectionSignal";
const OVERRIDE_TOPIC = "IntersectionOverride";
const COUNTDOWN_MS = 1000;
const MAX_LOG_ENTRIES = 100;
const RECONNECT_MS = 2000;

const statusElement = document.getElementById("status");
const mapElement = document.getElementById("map");
const logElement = document.getElementById("log");

// Latest state and seconds left for each intersection id.
const intersections = new Map();
let socket = null;

function logEvent(text) {
    const item = document.createElement("li");
    item.textContent = `${new Date().toLocaleTimeString()}  ${text}`;
    logElement.prepend(item);
    while (logElement.children.length > MAX_LOG_ENTRIES) {
        logElement.lastChild.remove();
    }
}

function setStatus(text) {
    // Failed reconnect attempts would otherwise log "disconnected" every time.
    if (statusElement.textContent === text) {
        return;
    }
    statusElement.textContent = text;
    statusElement.className = text;
    logEvent(`Broker ${text}`);
}

function sendOverride(intersectionId, direction, action) {
    if (socket?.readyState !== WebSocket.OPEN) {
        return;
    }
    const command = { intersection_id: intersectionId, direction, action, source: "web-ui" };
    socket.send(JSON.stringify({ type: "publish", topic: OVERRIDE_TOPIC, data: command }));
}

function sortedIntersections() {
    return [...intersections.entries()].sort((a, b) => a[0] - b[0]).map(([, value]) => value);
}

function render() {
    drawMap(mapElement, sortedIntersections());
}

// Clicking an arm forces that road green; clicking an overridden intersection cancels it.
mapElement.addEventListener("click", (event) => {
    const bounds = mapElement.getBoundingClientRect();
    const column = Math.floor((event.clientX - bounds.left) / CELL_SIZE);
    const row = Math.floor((event.clientY - bounds.top) / CELL_SIZE);
    const clicked = sortedIntersections()[row * COLUMNS + column];
    if (column < COLUMNS && clicked) {
        const { intersection_id: id, override } = clicked.state;
        const dx = event.clientX - bounds.left - column * CELL_SIZE - CELL_SIZE / 2;
        const dy = event.clientY - bounds.top - row * CELL_SIZE - CELL_SIZE / 2;
        sendOverride(id, armAt(dx, dy), override ? "cancel" : "free");
    }
});

function logChanges(state, previous) {
    const name = `Intersection ${state.intersection_id}`;
    if (state.override !== (previous?.state.override ?? false)) {
        logEvent(`${name}: override ${state.override ? "started" : "ended"}`);
    }
    for (const [direction, light] of Object.entries(state.lights)) {
        if (light !== previous?.state.lights[direction]) {
            logEvent(`${name} ${direction}: ${light}`);
        }
    }
}

function updateIntersection(state) {
    logChanges(state, intersections.get(state.intersection_id));
    intersections.set(state.intersection_id, { state, remaining: state.remaining });
    render();
}

// The controller only publishes on change, so the browser counts down itself.
function countDown() {
    for (const intersection of intersections.values()) {
        intersection.remaining = Math.max(0, intersection.remaining - 1);
    }
    render();
}

function connect() {
    socket = new WebSocket(BROKER_URL);

    socket.addEventListener("open", () => {
        setStatus("connected");
        socket.send(JSON.stringify({ type: "subscribe", topic: SIGNAL_TOPIC }));
    });

    socket.addEventListener("message", (event) => {
        const message = JSON.parse(event.data);
        if (message.topic === SIGNAL_TOPIC) {
            updateIntersection(message.data);
        }
    });

    socket.addEventListener("close", () => {
        setStatus("disconnected");
        setTimeout(connect, RECONNECT_MS);
    });
}

setInterval(countDown, COUNTDOWN_MS);
connect();
