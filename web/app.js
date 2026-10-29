const BROKER_URL = "ws://localhost:8765";
const SIGNAL_TOPIC = "IntersectionSignal";
const COUNTDOWN_MS = 1000;

const statusElement = document.getElementById("status");
const intersectionsElement = document.getElementById("intersections");

// Latest state and card elements for each intersection id.
const cards = new Map();

function createCard(intersectionId) {
    const element = document.createElement("div");
    element.className = "card";
    element.innerHTML = `
        <h3>Intersection ${intersectionId}</h3>
        <div class="light"></div>
        <div class="queue"></div>
        <div class="time"></div>
        <div class="override"></div>`;
    const card = { element, remaining: 0 };
    cards.set(intersectionId, card);
    intersectionsElement.append(element);
    sortCards();
    return card;
}

function sortCards() {
    const ids = [...cards.keys()].sort((a, b) => a - b);
    for (const id of ids) {
        intersectionsElement.append(cards.get(id).element);
    }
}

function showTime(card) {
    card.element.querySelector(".time").textContent = `Time left: ${card.remaining}s`;
}

function updateCard(state) {
    const card = cards.get(state.intersection_id) ?? createCard(state.intersection_id);
    card.remaining = state.remaining;
    card.element.querySelector(".light").className = `light ${state.light}`;
    card.element.querySelector(".queue").textContent = `Queue: ${state.queue}`;
    card.element.querySelector(".override").textContent = state.override ? "OVERRIDE" : "";
    showTime(card);
}

// The controller only publishes on change, so the browser counts down itself.
function countDown() {
    for (const card of cards.values()) {
        card.remaining = Math.max(0, card.remaining - 1);
        showTime(card);
    }
}

function connect() {
    const socket = new WebSocket(BROKER_URL);

    socket.addEventListener("open", () => {
        statusElement.textContent = "connected";
        socket.send(JSON.stringify({ type: "subscribe", topic: SIGNAL_TOPIC }));
    });

    socket.addEventListener("message", (event) => {
        const message = JSON.parse(event.data);
        if (message.topic === SIGNAL_TOPIC) {
            updateCard(message.data);
        }
    });

    socket.addEventListener("close", () => {
        statusElement.textContent = "disconnected";
    });
}

setInterval(countDown, COUNTDOWN_MS);
connect();
