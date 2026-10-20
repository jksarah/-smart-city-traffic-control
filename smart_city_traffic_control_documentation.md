# 🚦 Smart City Traffic Control Simulation: Project Plan

A plan for a smart traffic signal simulator in which all components communicate through **DDS-style publish-subscribe topics** served by **our own custom topic broker**, written from scratch instead of using an existing DDS library such as Eclipse Cyclone DDS. This document is planning only and contains no code.

> **Note:** the custom broker copies the DDS *concepts* (topics, keyed instances, QoS policies, history, durability). It is not wire-compatible with the standard DDS protocol (RTPS), so off-the-shelf DDS tools and vendors cannot connect to it.

---

## 1. Goals

- Simulate one or more traffic intersections with smart signals that adapt to traffic.
- Build a custom DDS-style topic broker and use it as the only way components communicate, so every component is decoupled and replaceable.
- Let a user interact with the simulation, for example by forcing a signal to give a free or extended green.
- Show the simulation state in real time in a visual interface.
- Keep the design extensible: more intersections, vehicle types and sensors should not need architectural changes.

### Non-Goals (for now)
- Real-world traffic data integration.
- Hardware signal controller integration.
- Machine-learning-based signal optimization (listed as a future phase).

---

## 2. Key Features

| Feature | Description |
| :--- | :--- |
| Decoupled pub-sub architecture | Cars, sensors, controllers and UI are separate clients that only share topics on the broker. |
| Custom topic broker | Our own broker handles topics, subscriptions, keyed instances, history and QoS. |
| Adaptive green timing | The controller extends green time when queues grow and shortens it when they are short. |
| Manual override | The user can force a signal to a free or extended green state. |
| Multi-intersection support | Each intersection is a separate instance of the same topics, identified by a key. |
| Live visualization | A UI shows signal states, queue lengths, events and metrics. |
| Event logging | System events (overrides, state changes) are recorded and shown to the user. |

---

## 3. High-Level Architecture

The system is made of independent clients that all connect to one **custom Topic Broker**. Real DDS is brokerless, but here the broker is a central process that receives every published message and routes it to the matching subscribers. Clients never talk to each other directly.

| Component | Role | Publishes | Subscribes |
| :--- | :--- | :--- | :--- |
| **Topic Broker (custom)** | Accepts client connections, manages topics and subscriptions, stores history, applies QoS and routes messages | Nothing of its own (it may publish broker status) | Everything it routes |
| Vehicle Simulator | Generates cars arriving at intersections | Vehicle sensor events | Signal state (to decide whether cars stop or go) |
| Signal Controller | Decides each light's state using queue data | Signal state | Sensor events, override commands |
| Visualizer (web UI) | Draws roads, signals, queues and the log | Override commands | Signal state, metrics |
| Metrics / Logger (optional) | Collects statistics and an event history | Metrics | Every topic |

Data flow in short:
1. The Vehicle Simulator reports car arrivals and departures on the sensor topic.
2. The Signal Controller reads those events, keeps queue counts, and publishes signal states.
3. The browser UI subscribes to signal states and publishes user overrides, both through the broker.

Because the broker accepts WebSocket connections, the browser can connect to it directly, so no separate UI gateway is needed. Python components and the browser use the same protocol.

---

## 4. Technology Choices

| Area | Proposed choice | Reason |
| :--- | :--- | :--- |
| Backend language | Python | Fast to develop, with strong asyncio and WebSocket support. |
| Topic broker | Custom Python broker using asyncio | Built from scratch for full control and learning. No external DDS library is used. |
| Wire protocol | JSON messages over WebSocket | Easy to debug and works in both Python and the browser. A binary format could be considered later. |
| Python client library | Small custom library (connect, publish, subscribe) | Gives every component the same simple API to the broker. |
| Frontend | Single-page HTML/JavaScript with Canvas | Simple, no build step; the existing prototype can be reused. |
| Configuration | A config file (JSON or YAML) | Defines the intersections and timing parameters without code changes. |
| Testing | pytest | Standard Python test framework. |


### 4.1 Languages Used per Part of the Project

| Part of the project | Language | Notes |
| :--- | :--- | :--- |
| Topic Broker (routing, subscriptions, history, QoS) | Python | Custom asyncio server accepting WebSocket connections. |
| Python client library (connect, publish, subscribe) | Python | Shared by all Python components. |
| Signal Controller (adaptive timing, override handling) | Python | Uses the custom client library. |
| Vehicle Simulator (car arrivals, scenarios) | Python | Publishes to the sensor topic on the broker. |
| Message definitions (topic data types) | Python and JavaScript | JSON message formats documented in one place and validated in the broker. |
| Metrics / Logger (optional) | Python | Subscribes to all topics. |
| Web UI structure (page layout) | HTML | Single page with canvas and dashboard. |
| Web UI styling (theme, layout) | CSS | Dark theme, dashboard cards, log panel. |
| Web UI behavior (drawing, clicks, WebSocket client) | JavaScript | Subscribes to topics on the broker and publishes override requests. |
| Configuration (intersections, timing parameters) | JSON or YAML | Data only, not code. |
| Tests | Python (pytest) | Unit and integration tests. |
| Setup and run scripts | Shell / PowerShell | Starting the participants (Docker files if containers are added). |
| Documentation | Markdown | This file. |

Summary: the broker and all backend components are **Python**, the frontend is **HTML, CSS and JavaScript**, and configuration is **JSON or YAML**.

---

## 5. Topic and Broker Design

### 5.1 Topics

There is one topic per message type. The intersection ID is the **key field**, which gives each intersection its own instance on the same topic, as in DDS.

| Topic | Message type | Publisher | Subscriber | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `IntersectionSensor` | Sensor event | Vehicle Simulator, Signal Controller | Signal Controller | Car arrivals and departures that drive queue counts. |
| `IntersectionSignal` | Signal state | Signal Controller | Vehicle Simulator, Web UI, Logger | Current light state and queue length. |
| `IntersectionOverride` | Override command | Web UI | Signal Controller | User request to force a free or extended green. |
| `SystemMetrics` (optional) | Metrics | Logger / Controller | Web UI | Throughput, average wait time and so on. |

### 5.2 Message Fields (conceptual)

- **Sensor event:** intersection ID (key), approach direction, event type (arrive or depart), timestamp.
- **Signal state:** intersection ID (key), light state (red, green, yellow, override), queue length, remaining time, timestamp.
- **Override command:** intersection ID (key), action (free or cancel), duration, source.
- **Metrics (optional):** intersection ID (key), cars served, average wait time, current congestion level.

### 5.3 Quality of Service (QoS) Plan

The broker has to implement these policies itself. The table lists the policies we plan to support, which are a small subset of full DDS.

| Topic | Reliability | Durability | History | Reason |
| :--- | :--- | :--- | :--- | :--- |
| `IntersectionSensor` | Reliable | Volatile | Keep last N | Missed events would corrupt queue counts. |
| `IntersectionSignal` | Reliable | Transient local | Keep last 1 per key | New clients (such as the UI) receive the latest state immediately. |
| `IntersectionOverride` | Reliable | Volatile | Keep last 1 | A command must be delivered, but old commands should not be replayed. |
| `SystemMetrics` | Best effort | Volatile | Keep last 1 | Losing a sample is harmless. |

### 5.4 Broker Responsibilities

| Responsibility | Description |
| :--- | :--- |
| Connection management | Accept client connections, give each client an ID, and detect disconnects with heartbeats. |
| Topic registry | Create topics on first use or from configuration, and check that messages match the topic's defined fields. |
| Subscriptions | Let clients subscribe and unsubscribe to a topic, and optionally filter by key (for example only intersection 2). |
| Routing | Deliver each published message to every matching subscriber. |
| Keyed instances | Track the latest value for each key, so each intersection has its own state on a topic. |
| History | Keep the last N messages per key, depending on the topic's QoS. |
| Durability | Send the latest stored value to a client that subscribes late, for topics that use transient-local behavior. |
| Reliability | For reliable topics, use message sequence numbers, acknowledgements and resend of missed messages. |
| Backpressure | Handle slow subscribers by dropping best-effort messages or limiting queue sizes. |
| Observability | Count messages per topic, record connected clients, and allow a monitor client to watch all traffic. |

### 5.5 Wire Protocol (conceptual)

Every message between a client and the broker is a small JSON object with a type field. The planned message types are:

| Message type | Direction | Purpose |
| :--- | :--- | :--- |
| `hello` | Client to broker | Introduce the client and its name. |
| `subscribe` / `unsubscribe` | Client to broker | Start or stop receiving a topic, with an optional key filter. |
| `publish` | Client to broker | Send data to a topic, including the key and a timestamp. |
| `data` | Broker to client | Deliver a message to a subscriber, with a sequence number. |
| `ack` | Client to broker | Confirm receipt for reliable topics. |
| `heartbeat` | Both ways | Detect dead connections. |
| `error` | Broker to client | Report an invalid message or unknown topic. |

---

## 6. Component Details

### 6.0 Topic Broker
- Runs as one standalone process that listens on a single network port.
- Holds all topic, subscription and history state in memory (persistence to disk is optional later).
- Processes messages in order per topic so subscribers see a consistent sequence.
- Reads topic definitions and QoS settings from the configuration file.


### 6.1 Signal Controller
- Keeps per-intersection state: current light, timer, queue length and override status.
- Cycles through red, green and yellow.
- Adapts green duration to the queue length: longer for heavy queues, shorter for light ones.
- Handles override commands: pauses the normal cycle, holds a free state for a set time, then returns to automatic mode.
- Publishes a signal state only when something changes.
- Works on a fixed tick, so the simulation speed is controllable.

### 6.2 Vehicle Simulator
- Generates car arrivals at random intervals, with a configurable arrival rate per intersection.
- Publishes arrival events to the sensor topic.
- Optionally listens to signal state so that cars stop on red and move on green.
- Supports traffic scenarios such as light traffic, rush hour and a sudden burst.

### 6.3 Visualizer (Web UI)
- Connects to the broker directly over WebSocket.
- Subscribes to signal state and metrics, and receives the latest state when it connects.
- Draws roads, intersections, signal lights, queued cars and queue counts.
- Highlights the override state.
- Shows a dashboard with per-intersection status, an event counter and a scrolling event log.
- Click or tap on a signal to request an override.

### 6.4 Metrics / Logger (optional)
- Subscribes to all topics and records an event history.
- Computes throughput and average wait times.

---

## 7. Behavior Rules

| Rule | Description |
| :--- | :--- |
| Normal cycle | Red, then green, then yellow, then red, with configurable base durations. |
| Congestion extension | If the queue reaches a threshold, the green phase is extended up to a maximum. |
| Override | A user override puts the signal into a free state for a set duration, then returns to automatic mode. |
| Safety | Two conflicting approaches must never both be green at the same time. |
| Fallback | If the controller sees no sensor data for a while, it uses a fixed-time cycle. |

---

## 8. Proposed Project Structure (conceptual)

- **Broker:** the custom topic broker, with its topic registry, routing, history and QoS handling.
- **Client library:** the shared Python library for connecting, publishing and subscribing.
- **Backend components:** shared message definitions, the signal controller, the vehicle simulator and an optional logger.
- **Frontend:** a single page with the canvas, the dashboard and the log.
- **Config:** intersection definitions and timing parameters.
- **Tests:** unit tests for controller logic and integration tests through the broker.
- **Docs:** this plan, plus setup and usage instructions as the project matures.

---

## 9. Implementation Phases

| Phase | Goal | Deliverables |
| :--- | :--- | :--- |
| 1. Foundations | Set up the environment and define the data model | Python environment, project structure, topic and message definitions agreed, wire protocol drafted. |
| 2. Broker core and first loop | A single intersection working end to end | Minimal broker (connect, subscribe, publish, route) and client library, with vehicle simulator and signal controller exchanging sensor and signal topics. |
| 3. Adaptive logic | Smart timing | Congestion-based green extension, configurable thresholds, unit tests. |
| 4. Override and QoS | Interactive control | Override topic, broker QoS (reliable delivery, history, durable latest state, heartbeats), return to automatic mode. |
| 5. UI | Visualization | Web canvas connected directly to the broker, dashboard and log. |
| 6. Multi-intersection | Scale out | Several intersections from config, with the key field separating them. |
| 7. Metrics and polish | Observability | Metrics topic, logger, scenario presets, documentation. |
| 8. Future (optional) | Advanced features | Coordinated signals ("green wave"), emergency vehicle priority, learning-based timing. |

---

## 10. Testing Strategy

- **Unit tests:** controller state transitions, green-time extension, override expiry, queue counting.
- **Integration tests:** run several participants together and check that signal changes follow sensor events and overrides.
- **QoS tests:** confirm that a late-joining UI receives the latest signal state, and that override commands are delivered.
- **Scenario tests:** run light traffic, heavy traffic and bursts, and compare queue length and wait time against a fixed-time baseline.
- **Manual UI checks:** click overrides, browser reconnects and multi-browser behavior.

---

## 11. Success Criteria

- All inter-component communication goes through topics on the custom broker.
- Adaptive timing measurably lowers average queue length or wait time compared with a fixed-time cycle.
- An override takes effect within about one second and expires on schedule.
- The UI shows the correct state within a short delay, including after a reconnect.
- Adding a new intersection requires only a configuration change.

---

## 12. Risks and Mitigations

| Risk | Mitigation |
| :--- | :--- |
| Building a broker is a large task and could grow beyond what the simulator needs | Support only the planned QoS subset and build it in small steps with tests. |
| The broker is a single point of failure | Accept this for the simulator; consider a restartable broker with stored state later. |
| The custom broker is not compatible with real DDS | State this clearly, and keep the message and topic design generic so a real DDS library could be swapped in later. |
| Broker bugs in ordering or delivery | Write protocol tests early and add sequence numbers. |
| Race conditions between sensor events and timing | Use a single controller loop that handles all inputs in order. |
| Lost or duplicated events change queue counts | Use reliable delivery in the broker and, if needed, periodic queue resynchronization. |
| Simulation drift from the real clock | Use a fixed tick and include timestamps in messages. |

---

## 13. Feature Ideas

Ideas beyond the core scope. Each one is also meant to show off a pub-sub strength. They are ordered roughly by how much value they add compared to the effort.

### 13.1 Traffic Intelligence

| Idea | Description | Broker angle |
| :--- | :--- | :--- |
| Emergency vehicle priority | An ambulance, fire truck or police car publishes a priority request, and the signals along its route turn green ahead of it. | New topic with a priority field; the broker delivers priority messages first. |
| Green wave coordination | Neighboring signals share timing so that a platoon of cars hits consecutive greens. | Controllers subscribe to each other's signal topic. |
| Pedestrian crossing requests | Pedestrians press a button, which adds a walk phase and holds cars on red. | A new publisher type with a command topic. |
| Public transport priority | Buses and trams get a short green extension when running late. | Priority sensor topic. |
| Predictive timing | Use recent arrival rates to forecast demand and adjust the cycle before queues build up. | The controller subscribes to the metrics topic. |
| Learning-based control | A reinforcement learning agent chooses green durations and is compared against fixed-time and rule-based baselines. | The agent is a separate broker client that can be swapped in without touching other components. |

### 13.2 Simulation Realism

| Idea | Description |
| :--- | :--- |
| Individual vehicle agents | Cars have positions, speeds, destinations and routes instead of just queue counts. |
| Multiple vehicle types | Cars, trucks, buses, motorbikes and bicycles with different sizes and acceleration. |
| Turn lanes and protected turns | Left and right turn queues with their own phases. |
| Road network from a map | Load a real road layout (for example from OpenStreetMap) and place intersections automatically. |
| Weather and time of day | Rain slows cars down, and a day/night cycle changes traffic volume (rush hours, quiet nights). |
| Incidents and road closures | A random accident or a blocked lane that traffic has to cope with. |
| Scenario presets | One-click scenarios: rush hour, stadium event ending, burst of arrivals, accident. |

### 13.3 Resilience and Fault Handling

| Idea | Description | Broker angle |
| :--- | :--- | :--- |
| Sensor failure simulation | Sensors can drop out or send bad data, and the controller falls back to fixed timing. | The broker uses heartbeats to detect silent publishers and publishes a status message. |
| Controller failover | A standby controller takes over automatically when the primary stops. | The broker accepts messages only from the highest-priority live publisher for that key. |
| Network fault injection | Add delay, message loss or a network partition to test behavior. | Compare reliable and best-effort QoS under stress. |
| Safety monitor | An independent participant watches all signal topics and raises an alarm if two conflicting greens are ever seen. | Subscribes to all signal states. |
| Stale data detection | Mark data as old if no update arrives within its deadline. | Broker-side deadline check that flags a topic key with no update in time. |

### 13.4 Visualization and User Experience

| Idea | Description |
| :--- | :--- |
| Animated cars | Cars drive through the intersection, stop at red and queue up visibly. |
| Heat map | Color roads by congestion level. |
| Live charts | Queue length, throughput and average wait time over time. |
| Topic inspector | A panel that shows messages as they flow, which helps explain pub-sub to learners. |
| Time controls | Pause, step, slow motion, fast forward, and replay a recorded run. |
| Control panel | Sliders for arrival rate and timing parameters, applied while the simulation runs. |
| Mode comparison | Run fixed-time and adaptive control side by side on identical traffic and show the difference. |
| Dark and light themes, mobile-friendly layout | Basic usability polish. |

### 13.5 Data, Analytics and Operations

| Idea | Description |
| :--- | :--- |
| Recording and replay | Record every message to a file, then replay it later for debugging or demos. |
| Metrics dashboard | Throughput, average and maximum wait time, stops per vehicle, and estimated emissions or fuel use. |
| Report export | Export a run summary as CSV or a report. |
| Alerts | Notify the user when queues pass a threshold or an intersection stays in override for too long. |
| Event history search | Filter the event log by intersection, type and time. |

### 13.6 Security and Multi-User

| Idea | Description | Broker angle |
| :--- | :--- | :--- |
| Role-based override | Only authorized operators can force a signal state, while viewers have read-only access. | Broker authentication and per-topic permissions (who may publish or subscribe). |
| Audit trail | Record who issued every override and when. | Override commands carry a source field. |
| Multi-user mode | Several operators watch and control the same simulation, with conflicts handled sensibly (for example a lock or last-writer-wins). | One broker reachable over the network. |
| Encrypted traffic | Secure WebSocket (TLS) between clients and the broker. | TLS on the broker port. |

### 13.7 Integration and Deployment

| Idea | Description |
| :--- | :--- |
| Docker setup | One command starts all participants as containers. |
| Distributed demo | Run the controller, simulator and UI on different machines to show that clients only need the broker's address. |
| External APIs | A REST or MQTT endpoint so other tools can read signal state. |
| Digital twin link | Feed real sensor data into the same topics and use the simulator as a digital twin. |
| Hardware demo | Drive LEDs on a small model intersection from the signal topic (Raspberry Pi or Arduino). |
| Real DDS bridge | A bridge client that copies selected topics between our broker and a real DDS system. |

### 13.8 Suggested Priority

| Priority | Features |
| :--- | :--- |
| Must try early | Animated cars, scenario presets, mode comparison (fixed-time versus adaptive), live charts. |
| Strong pub-sub showcases | Emergency vehicle priority, topic inspector, heartbeat and deadline checks, controller failover, recording and replay. |
| Later | Green wave coordination, learning-based control, real map import, broker authentication and TLS, hardware demo. |

---

## 14. Open Questions

1. How many intersections are needed initially, and should they be connected in a grid or stay independent?
2. Should vehicles be individual agents with positions, or just queue counts as in the prototype?
3. Should the broker be a single process, or later support clustering or failover?
4. Is a web UI enough, or is a desktop interface also wanted?
5. Should the system need to run across several machines?
6. Are metrics and logging in scope for the first release?
