const BROKER_URL = "ws://localhost:8765";
const SIGNAL_TOPIC = "IntersectionSignal";
const MAX_MESSAGES = 50;

const statusElement = document.getElementById("status");
const messagesElement = document.getElementById("messages");

function showMessage(data) {
    const item = document.createElement("li");
    item.textContent = JSON.stringify(data);
    messagesElement.prepend(item);
    while (messagesElement.children.length > MAX_MESSAGES) {
        messagesElement.lastChild.remove();
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
            showMessage(message.data);
        }
    });

    socket.addEventListener("close", () => {
        statusElement.textContent = "disconnected";
    });
}

connect();
