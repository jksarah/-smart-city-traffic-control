const COLUMNS = 3;
const CELL_SIZE = 220;
const ROAD_WIDTH = 40;
const CAR_WIDTH = 16;
const CAR_LENGTH = 22;
const CAR_GAP = 4;
const MAX_DRAWN_CARS = 3;
const LIGHT_COLORS = { red: "#e53935", green: "#43a047", yellow: "#fdd835" };
const MAP_MARGIN = 20;
const MIN_SCALE = 0.5;
const OVERRIDE_COLOR = "#ffb300";

// Intersections fill the grid row by row.
function cellOf(index) {
    return { column: index % COLUMNS, row: Math.floor(index / COLUMNS) };
}

// Everything is drawn in CELL_SIZE units, then scaled up to fill the window.
let mapScale = 1;

function mapSize(count) {
    const columns = Math.min(COLUMNS, count);
    const rows = Math.ceil(count / COLUMNS);
    return { width: columns * CELL_SIZE, height: rows * CELL_SIZE };
}

function fitScale(canvas, size) {
    const top = canvas.getBoundingClientRect().top + window.scrollY;
    const availableWidth = window.innerWidth - 2 * MAP_MARGIN;
    const availableHeight = window.innerHeight - top - MAP_MARGIN;
    return Math.max(MIN_SCALE, Math.min(availableWidth / size.width, availableHeight / size.height));
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

// For each direction: unit vector pointing from the centre out along that arm.
const ARMS = { N: [0, -1], S: [0, 1], E: [1, 0], W: [-1, 0] };

// Which arm of a cell a click at (dx, dy) from its centre is closest to.
function armAt(dx, dy) {
    if (Math.abs(dx) > Math.abs(dy)) {
        return dx > 0 ? "E" : "W";
    }
    return dy > 0 ? "S" : "N";
}

// A light sits beside each arm, just outside the intersection box.
function drawLight(context, x, y, direction, light) {
    const [ax, ay] = ARMS[direction];
    const middle = CELL_SIZE / 2;
    const distance = ROAD_WIDTH / 2 + 10;
    const side = ROAD_WIDTH / 2 + 12;
    context.fillStyle = LIGHT_COLORS[light];
    context.beginPath();
    context.arc(
        x + middle + ax * distance - ay * side,
        y + middle + ay * distance + ax * side,
        7, 0, Math.PI * 2
    );
    context.fill();
}

// Cars wait on their own arm, lined up from the stop line outward.
function drawCars(context, x, y, direction, queue) {
    const [ax, ay] = ARMS[direction];
    const middle = CELL_SIZE / 2;
    const width = ax === 0 ? CAR_WIDTH : CAR_LENGTH;
    const height = ax === 0 ? CAR_LENGTH : CAR_WIDTH;
    context.fillStyle = "#4fc3f7";
    const drawn = Math.min(queue, MAX_DRAWN_CARS);
    for (let i = 0; i < drawn; i++) {
        const gap = ROAD_WIDTH / 2 + CAR_GAP + i * (CAR_LENGTH + CAR_GAP);
        const centreX = x + middle + ax * (gap + CAR_LENGTH / 2);
        const centreY = y + middle + ay * (gap + CAR_LENGTH / 2);
        context.fillRect(centreX - width / 2, centreY - height / 2, width, height);
    }
    if (queue > MAX_DRAWN_CARS) {
        const gap = ROAD_WIDTH / 2 + CAR_GAP + MAX_DRAWN_CARS * (CAR_LENGTH + CAR_GAP);
        context.fillStyle = "#e6e6e6";
        context.font = "12px sans-serif";
        context.fillText(`+${queue - MAX_DRAWN_CARS}`, x + middle + ax * gap - 8 + 20 * (ax === 0), y + middle + ay * gap + 4);
    }
}

function drawLabels(context, x, y, intersection) {
    const left = x + 6;
    const { state } = intersection;
    const total = Object.values(state.queues).reduce((sum, value) => sum + value, 0);
    context.fillStyle = "#e6e6e6";
    context.font = "bold 11px sans-serif";
    context.fillText(`Intersection ${state.intersection_id}`, left, y + 14);
    context.font = "12px sans-serif";
    context.fillText(`Queue: ${total}`, left, y + CELL_SIZE - 22);
    context.fillText(`Time left: ${intersection.remaining}s`, left, y + CELL_SIZE - 8);
    if (state.override) {
        context.fillStyle = OVERRIDE_COLOR;
        context.fillText("OVERRIDE", left, y + 30);
        context.strokeStyle = OVERRIDE_COLOR;
        context.lineWidth = 2;
        context.strokeRect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2);
    }
}

// `intersections` is sorted by id; each has `state` and `remaining`.
function drawMap(canvas, intersections) {
    const size = mapSize(intersections.length);
    mapScale = fitScale(canvas, size);
    canvas.width = size.width * mapScale;
    canvas.height = size.height * mapScale;
    const context = canvas.getContext("2d");
    context.scale(mapScale, mapScale);
    context.fillStyle = "#2a303c";
    context.fillRect(0, 0, size.width, size.height);
    intersections.forEach((intersection, index) => {
        const { column, row } = cellOf(index);
        const x = column * CELL_SIZE;
        const y = row * CELL_SIZE;
        drawRoads(context, x, y);
        for (const direction of Object.keys(ARMS)) {
            drawLight(context, x, y, direction, intersection.state.lights[direction]);
            drawCars(context, x, y, direction, intersection.state.queues[direction]);
        }
        drawLabels(context, x, y, intersection);
    });
}
