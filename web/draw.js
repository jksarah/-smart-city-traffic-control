const COLUMNS = 3;
const CELL_SIZE = 220;
const ROAD_WIDTH = 40;
const CAR_WIDTH = 16;
const CAR_LENGTH = 22;
const CAR_GAP = 4;
const MAX_DRAWN_CARS = 3;
const LIGHT_COLORS = { red: "#e53935", green: "#43a047", yellow: "#fdd835" };
const OVERRIDE_COLOR = "#ffb300";

// Intersections fill the grid row by row.
function cellOf(index) {
    return { column: index % COLUMNS, row: Math.floor(index / COLUMNS) };
}

function mapSize(count) {
    const columns = Math.min(COLUMNS, count);
    const rows = Math.ceil(count / COLUMNS);
    return { width: columns * CELL_SIZE, height: rows * CELL_SIZE };
}

// Each cell draws its four road arms to the cell edges, so neighbours join up.
function drawRoads(context, x, y) {
    const middle = CELL_SIZE / 2;
    context.fillStyle = "#444";
    context.fillRect(x + middle - ROAD_WIDTH / 2, y, ROAD_WIDTH, CELL_SIZE);
    context.fillRect(x, y + middle - ROAD_WIDTH / 2, CELL_SIZE, ROAD_WIDTH);
    context.fillStyle = "#888";
    for (let offset = 0; offset < CELL_SIZE; offset += 20) {
        context.fillRect(x + offset, y + middle - 1, 10, 2);
        context.fillRect(x + middle - 1, y + offset, 2, 10);
    }
    context.fillStyle = "#444";
    context.fillRect(x + middle - ROAD_WIDTH / 2, y + middle - ROAD_WIDTH / 2, ROAD_WIDTH, ROAD_WIDTH);
    context.fillStyle = "#fff";
    context.fillRect(x + middle - ROAD_WIDTH / 2, y + middle - ROAD_WIDTH / 2 - 2, ROAD_WIDTH, 2);
}

function drawLight(context, x, y, light) {
    const middle = CELL_SIZE / 2;
    context.fillStyle = LIGHT_COLORS[light];
    context.beginPath();
    context.arc(x + middle + ROAD_WIDTH / 2 + 12, y + middle - ROAD_WIDTH / 2 - 8, 8, 0, Math.PI * 2);
    context.fill();
}

// Cars wait on the road above the intersection, heading down.
function drawCars(context, x, y, queue) {
    const middle = CELL_SIZE / 2;
    const stopLine = y + middle - ROAD_WIDTH / 2 - 2;
    context.fillStyle = "#4fc3f7";
    const drawn = Math.min(queue, MAX_DRAWN_CARS);
    for (let i = 0; i < drawn; i++) {
        const top = stopLine - CAR_GAP - CAR_LENGTH - i * (CAR_LENGTH + CAR_GAP);
        context.fillRect(x + middle - CAR_WIDTH / 2, top, CAR_WIDTH, CAR_LENGTH);
    }
    if (queue > MAX_DRAWN_CARS) {
        context.fillStyle = "#e6e6e6";
        context.font = "12px sans-serif";
        context.fillText(`+${queue - MAX_DRAWN_CARS}`, x + middle + CAR_WIDTH, y + 14);
    }
}

function drawLabels(context, x, y, intersection) {
    const left = x + 6;
    const middle = y + CELL_SIZE / 2;
    context.fillStyle = "#e6e6e6";
    context.font = "bold 11px sans-serif";
    context.fillText(`Intersection ${intersection.state.intersection_id}`, left, y + 14);
    context.font = "12px sans-serif";
    context.fillText(`Queue: ${intersection.state.queue}`, left, middle + ROAD_WIDTH / 2 + 16);
    context.fillText(`Time left: ${intersection.remaining}s`, left, middle + ROAD_WIDTH / 2 + 32);
    if (intersection.state.override) {
        context.fillStyle = OVERRIDE_COLOR;
        context.fillText("OVERRIDE", left, middle + ROAD_WIDTH / 2 + 48);
        context.strokeStyle = OVERRIDE_COLOR;
        context.lineWidth = 2;
        context.strokeRect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2);
    }
}

// `intersections` is sorted by id; each has `state` and `remaining`.
function drawMap(canvas, intersections) {
    const size = mapSize(intersections.length);
    canvas.width = size.width;
    canvas.height = size.height;
    const context = canvas.getContext("2d");
    context.fillStyle = "#2a303c";
    context.fillRect(0, 0, size.width, size.height);
    intersections.forEach((intersection, index) => {
        const { column, row } = cellOf(index);
        const x = column * CELL_SIZE;
        const y = row * CELL_SIZE;
        drawRoads(context, x, y);
        drawLight(context, x, y, intersection.state.light);
        drawCars(context, x, y, intersection.state.queue);
        drawLabels(context, x, y, intersection);
    });
}
