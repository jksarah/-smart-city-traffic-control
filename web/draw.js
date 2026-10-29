const CANVAS_WIDTH = 160;
const CANVAS_HEIGHT = 200;
const ROAD_WIDTH = 40;
const CAR_WIDTH = 16;
const CAR_LENGTH = 22;
const CAR_GAP = 4;
const MAX_DRAWN_CARS = 4;
const CENTER_X = CANVAS_WIDTH / 2;
const CENTER_Y = 80;
const STOP_LINE_Y = CENTER_Y + ROAD_WIDTH / 2;
const LIGHT_COLORS = { red: "#e53935", green: "#43a047", yellow: "#fdd835" };

function drawRoads(context) {
    context.fillStyle = "#444";
    context.fillRect(CENTER_X - ROAD_WIDTH / 2, 0, ROAD_WIDTH, CANVAS_HEIGHT);
    context.fillRect(0, CENTER_Y - ROAD_WIDTH / 2, CANVAS_WIDTH, ROAD_WIDTH);
    context.fillStyle = "#fff";
    context.fillRect(CENTER_X - ROAD_WIDTH / 2, STOP_LINE_Y, ROAD_WIDTH, 2);
}

function drawLight(context, light) {
    context.fillStyle = LIGHT_COLORS[light];
    context.beginPath();
    context.arc(CENTER_X + ROAD_WIDTH / 2 + 12, STOP_LINE_Y - 8, 8, 0, Math.PI * 2);
    context.fill();
}

function drawCars(context, queue) {
    context.fillStyle = "#4fc3f7";
    const drawn = Math.min(queue, MAX_DRAWN_CARS);
    for (let i = 0; i < drawn; i++) {
        const y = STOP_LINE_Y + CAR_GAP + i * (CAR_LENGTH + CAR_GAP);
        context.fillRect(CENTER_X - CAR_WIDTH / 2, y, CAR_WIDTH, CAR_LENGTH);
    }
    if (queue > MAX_DRAWN_CARS) {
        context.fillStyle = "#e6e6e6";
        context.font = "12px sans-serif";
        context.fillText(`+${queue - MAX_DRAWN_CARS}`, CENTER_X + CAR_WIDTH, CANVAS_HEIGHT - 6);
    }
}

function drawIntersection(canvas, state) {
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    drawRoads(context);
    drawLight(context, state.light);
    drawCars(context, state.queue);
}
