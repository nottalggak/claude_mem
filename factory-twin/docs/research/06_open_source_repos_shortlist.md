# Open-source building blocks for a factory digital twin (3D web viewer + DES + data pipeline + scan processing)

**Method and caveats.** All star counts, push dates, licenses and languages below are the values returned by the GitHub Search API on 2026-10-10 (authenticated GitHub MCP `search_repositories`, plus unauthenticated `api.github.com/search/repositories` via WebFetch until it rate-limited at ~10 req/min). README content comes from `raw.githubusercontent.com` or the repo landing page. Where the API returned `license: null` or `NOASSERTION` I say so rather than guess. SimPy itself lives on GitLab (gitlab.com/team-simpy/simpy), so it has no GitHub star count; and `ifzhang/ByteTrack` is no longer reachable through the API ("resources do not exist or you do not have permission"), so I treat it as gone and point to the maintained re-implementations. The session's WebSearch budget was exhausted by other agents, so this report is built from the GitHub API and READMEs only; I did not run extended web searches. Searches run: all 30 queries from the brief, plus "simpy discrete event simulation", "digital twin platform open source iot", "potree point cloud viewer three.js", "IFC viewer web three.js", "assembly line balancing", "opentwins", "casymda", "ciw queueing", "manpy".

**Headline finding.** Several of the brief's queries return essentially nothing usable: "shop floor tracking yolo" (1 hit, 0 stars, retail), "people tracking factory" (21 hits, all spam/market-report repos), "forklift path tracking" (one 3-star C++ repo from 2018), "spatial-temporal heatmap indoor" (0 hits), "spaghetti diagram" (nothing above 2 stars that is factory-related), "MES open source" (nothing above 8 stars), and "facility layout problem" / "plant layout optimization" (nothing above 9 stars). Those four capabilities (people/vehicle tracking into floor-plane heatmaps, spaghetti diagrams, MES/OEE, layout optimisation) will have to be composed from general-purpose libraries (YOLO + BoxMOT, deck.gl, OR-Tools) rather than cloned. The good news is that the three hard parts, a browser 3D/splat viewer, a DES engine, and point-cloud processing, each have mature, permissively licensed options, and there is one recent repo (WareTwin/RFTwin) that already wires an R3F frontend to a Python tick-based simulation over WebSocket in exactly the shape you want.

---

## (A) Simulation engines

**salabim/salabim** — https://github.com/salabim/salabim — 405 stars, pushed 2026-05-29, license: API returns `null` (the README states MIT), Python.
Object-oriented DES with built-in 2D and 3D animation and video export; components, queues, resources, stores, states, monitors, tracing. Processes are written without `yield` (a deliberate difference from SimPy). Runs on Windows/macOS/Linux and even Pythonista. The 3D animation is OpenGL-based (there is an `install_opengl` helper in the repo) and renders primitives and simple models in a desktop window, not in a browser.
*Use:* the fastest way to get a validated DES model with a visual sanity check during development. For the product you would not use salabim's own 3D; you would emit a state/event stream from the model and render it in three.js. Its monitors give you queue-length/utilisation KPIs for free. Pick salabim if you want the animation during model-building; pick SimPy if you want the smallest dependency.

**SimPy (team-simpy, GitLab; not on GitHub)** — the de facto Python DES kernel that FactorySimPy, casymda, simulatte, ProdSim and DRL-SimPy-JobShop all build on. MIT. *Use:* the kernel under whichever component library you choose; pip-installable, no GitHub stats available via the API.

**FactorySimPy/FactorySimPy** — https://github.com/FactorySimPy/FactorySimPy — 15 stars, pushed 2025-09-29, MIT, Python.
A component library on SimPy ≥4.1.1 that models a plant as a graph: nodes (Source, Machine, Sink, Splitter, Combiner) and edges (Buffer, slotted and continuous Conveyor, Fleet of AGVs/robots). Has performance-metrics reporting, accelerated and *real-time* simulation modes, and the README explicitly targets digital twins. Limitation: discrete items only, fixed topology.
*Use:* this is the closest thing to a ready-made "factory DES vocabulary" for Python. Clone it, map your layout's stations/buffers/conveyors to its nodes and edges, and run it in real-time mode as the live twin or in accelerated mode for what-if. Small and young (15 stars), so budget for reading the source, but it saves writing the conveyor/fleet abstractions yourself.

**jaamsim/jaamsim** — https://github.com/jaamsim/jaamsim — 237 stars, pushed 2026-10-07, Apache-2.0, Java.
A complete desktop DES environment with drag-and-drop model building, interactive 3D graphics (JOGL), queueing/resource palettes, fluid systems, and an input editor. New objects are written in plain Java. Actively maintained since 2002.
*Use:* an excellent reference for what a factory DES tool's object palette and 3D animation should look like, and a good tool for an analyst to build a validated model quickly. It is not embeddable in a browser and has no documented external API, so I would not make it the engine behind a web twin unless the team is Java-first.

**fladdimir/casymda** — https://github.com/fladdimir/casymda — 52 stars, pushed 2024-12-14, MIT, Python.
Builds SimPy models from BPMN diagrams drawn in Camunda Modeler; browser animation via Flask + PixiJS, plus tkinter; supports tilemap (grid) movement of entities with shortest paths. Tested on Python 3.8.
*Use:* worth borrowing two ideas: BPMN as the process-definition format non-programmers can edit, and the tilemap movement model for people/AGV walking paths. Not actively developed; treat as a pattern source rather than a dependency.

**CiwPython/Ciw** — https://github.com/CiwPython/Ciw — 175 stars, pushed 2025-12-05, MIT, Python.
Open queueing-network simulation with many service disciplines and good statistics. *Use:* only if you want an analytical queueing view of the line (station capacity, blocking) rather than a spatial simulation; otherwise FactorySimPy/salabim cover it.

**Nexedi/dream (ManPy)** — https://github.com/Nexedi/dream — 79 stars, pushed 2022-01-12, LGPL-3.0, Python. Mirror of lab.nexedi.com. ManPy was the most complete manufacturing-object library in Python (machines, queues, assemblies, operators, shifts) but it is Python-2 era and dormant. *Use:* mine it for object semantics (failures, shifts, operator pools); do not depend on it.

**proto-lab-ro/jobshoplab** — https://github.com/proto-lab-ro/jobshoplab — 56 stars, pushed 2026-04-28, CC-BY-4.0, Python 3.12+.
Gymnasium environment with a state-machine production simulation: machines with setup times, breakdowns, stochastic processing, pre/post buffers, transport units moving jobs, multi-objective scoring (makespan, energy, utilisation, lead time), YAML-configured instances, pytest suite, IEEE CASE 2025 paper. *Use:* if you want RL-based dispatching experiments on top of the twin. Note the CC-BY licence (unusual for code) and that it has no dashboard.

**dmezzogori/simulatte** — https://github.com/dmezzogori/simulatte — 5 stars, pushed 2026-10-10, MIT, Python. SimPy framework for job shops plus warehouses/AGVs/material flow with release policies and multi-seed experiment tooling; v0.12, API unstable. *Use:* the AGV/intralogistics side if FactorySimPy's Fleet edge is too thin.

Also seen: **AndreasKuhnle/SimRLFab** (134 stars, MIT, pushed 2022-06-22; sim+RL for job shops), **FuchsTom/ProdSim** (40 stars, no license stated; JSON-configured SimPy production sim with CSV output), **heal-research/SimSharp** (162 stars, .NET port of SimPy), **uia4j/uia-sim** (27 stars, Java SimPy port), **markus-senger/discrete-event-simulation-salabim-unity** (8 stars, GPL-3.0; salabim DES driving a Unity conveyor layout), and **manoj-nawale/lernfabrik-simulation** (2 stars, MIT; SimPy learning-factory twin with Dash dashboard).

---

## (B) 3D / web viewers and Gaussian splats

**mrdoob/three.js** — https://github.com/mrdoob/three.js — 116,193 stars, pushed 2026-10-10, MIT. The base renderer; WebGPU backend is now mature. *Use:* foundation of the viewer.

**pmndrs/react-three-fiber** — https://github.com/pmndrs/react-three-fiber — 32,831 stars, pushed 2026-10-10, MIT. **pmndrs/drei** — https://github.com/pmndrs/drei — 9,915 stars, pushed 2026-10-05, MIT. *Use:* R3F + drei (OrbitControls, Html labels, Instances, GLTF loading, Stats) is what WareTwin/RFTwin use and is the quickest path to a React dashboard that embeds the 3D scene.

**BabylonJS/Babylon.js** — https://github.com/BabylonJS/Babylon.js — 26,150 stars, pushed 2026-10-09, Apache-2.0. Full engine with built-in splat support and an inspector. *Use:* viable alternative to three.js if you prefer batteries-included; the splat ecosystem below is three.js-centric, which is why I lean three.js.

**sparkjsdev/spark** — https://github.com/sparkjsdev/spark — 3,715 stars, pushed 2026-10-07, MIT, TypeScript. World Labs' splat renderer that hooks into the three.js pipeline so splats and meshes sort correctly in one scene; loads PLY/compressed PLY/SPZ/SPLAT/KSPLAT/SOG; multiple splat objects, multiple viewpoints, per-splat transforms and GPU shader-graph editing; targets 98%+ WebGL2 coverage and mobile. Includes a PLY-to-SPZ compressor.
*Use:* the primary choice for showing the scanned factory as a splat *and* overlaying simulated machines/AGVs as meshes. The mesh/splat fusion is exactly the digital-twin need.

**reall3d-com/Reall3dViewer** — https://github.com/reall3d-com/Reall3dViewer — 513 stars, pushed 2026-09-11, MIT, TypeScript. Three.js splat viewer with preset LOD streaming for 100M+ points, distance/area measurement, labelling, SH 1–3, GIS basemap, quality levels, and a `gsbox` CLI to convert PLY to SPX/SOG. Usable as a drop-in viewer or as a `SplatMesh` you add to your own scene; `npm i @reall3d/reall3dviewer`.
*Use:* if the scanned plant is large (multi-building) its LOD/streaming and measurement tools are ahead of Spark's. Evaluate both on your scan; they are complementary.

**mkkellogg/GaussianSplats3D** — https://github.com/mkkellogg/GaussianSplats3D — 2,907 stars, pushed 2025-10-19, MIT. The original three.js splat viewer (.ply/.splat/.ksplat, WebXR, WASM SIMD sort). README now states it is *no longer in active development*; splat caps ~8–16M, CPU sort artifacts, weak on mobile. *Use:* no; use Spark or Reall3dViewer.

**playcanvas/supersplat** — https://github.com/playcanvas/supersplat — 10,322 stars, pushed 2026-10-05, MIT, TS. Browser splat editor. *Use:* the cleanup tool: crop the scan to the building, delete floaters, export compressed PLY/SOG before loading into Spark. Not a runtime component.

**nerfstudio-project/nerfstudio** — https://github.com/nerfstudio-project/nerfstudio — 12,057 stars, pushed 2025-07-29, Apache-2.0. **nerfstudio-project/gsplat** — https://github.com/nerfstudio-project/gsplat — 5,767 stars, pushed 2026-09-19, Apache-2.0. *Use:* training splats from your own photo/video capture (`ns-train splatfacto`); gsplat is the CUDA rasteriser underneath. nerfstudio's last push is over a year old, gsplat is active.

**PixarAnimationStudios/OpenUSD** — https://github.com/PixarAnimationStudios/OpenUSD — 7,522 stars, pushed 2026-10-08, license NOASSERTION (Pixar's Apache-derived "Tomorrow Open Source Technology" licence), C++ with `usd-core` on PyPI. *Use:* only if you need Omniverse/Isaac interoperability or a layered scene-graph for layout variants. For a small team shipping to the browser, glTF/GLB is the practical interchange format (realvirtual-WEB, Meteor3D and R3F all consume GLB directly). Keep USD as an export target, not the core.

**game4automation/realvirtual-WEB** — https://github.com/game4automation/realvirtual-WEB — 152 stars, pushed 2026-10-03, **AGPL-3.0**, TypeScript. Browser 3D-HMI for industrial twins: three.js (WebGPU beta, WebXR), React 19 + MUI 7, ECharts 6, Vite. Loads GLB models carrying `rv_extras` metadata that bind drives/sensors/signals; 60 Hz transport simulation, LogicStep sequencing, document attachment, plugin system. Connects via their CONNECT gateway (S7, TwinCAT ADS, OPC UA, EtherNet/IP, Modbus, MQTT, ctrlX) or directly via WebSocket/MQTT-over-WS/REST. Layout planner and multiuser are beta; CAD import, asset editor and DES are commercial add-ons.
*Use:* the best reference implementation of an industrial web HMI on three.js, and the GLB-with-signal-metadata convention is worth copying. The AGPL terms are broad (they claim it covers plugins, config and delivered GLB models, and branding must stay), so either keep it as a reference or accept AGPL for your deployment.

**nikonikoCW/Meteor3DEditor** — https://github.com/nikonikoCW/Meteor3DEditor — 71 stars, pushed 2026-09-21, MIT, JavaScript. Vue 3 + three.js low-code scene editor for "digital twin big-screen" dashboards: drag-drop placement, GLTF asset manager with LOD/Draco, WGS84 conversion, ECharts widgets; Node/Express/MongoDB backend; docs in Chinese; no IoT binding yet. *Use:* a source for the layout-editor UX (placing machines on a floor plan) if you need non-developers to edit the scene.

**tentone/potree-core** — https://github.com/tentone/potree-core — 256 stars, updated 2026-09-29, JS. Potree octree point-cloud rendering as a three.js library. *Use:* if you want to show the raw LiDAR point cloud (rather than a splat) at scale in the same scene.

**ThatOpen/engine_components** — https://github.com/ThatOpen/engine_components — 711 stars, updated 2026-10-09, TypeScript. IFC/BIM in three.js (web-ifc). *Use:* if the building shell exists as IFC from the architect, load it alongside the scan.

**visgl/deck.gl** — https://github.com/visgl/deck.gl — 14,641 stars, pushed 2026-10-10, MIT. **keplergl/kepler.gl** — 12,040 stars, pushed 2026-10-10, MIT. *Use:* deck.gl's HeatmapLayer, TripsLayer and PathLayer on a non-geo orthographic view are the right tools for the spatio-temporal heatmap and spaghetti diagram over the floor plan; kepler.gl is the no-code version for analysts. This is how you cover the two queries that returned no purpose-built repos.

**apache/echarts** — https://github.com/apache/echarts — 67,466 stars, pushed 2026-10-04, Apache-2.0. *Use:* KPI/OEE charts in the React UI (realvirtual-WEB uses it too). **grafana/grafana** — 77,219 stars, pushed 2026-10-10, AGPL-3.0. *Use:* ops dashboards over the time-series store; fine as a separate deployed service, AGPL is irrelevant unless you modify and redistribute it.

---

## (C) Scan and vision processing

**isl-org/Open3D** — https://github.com/isl-org/Open3D — 14,060 stars, pushed 2026-09-30, license NOASSERTION in API (MIT in LICENSE), C++/Python. Point-cloud IO (PLY/PCD/LAS via plugins), voxel downsampling, plane segmentation (RANSAC), DBSCAN clustering, ICP registration, TSDF reconstruction, ML module. *Use:* the workhorse for scan cleanup, floor/wall plane extraction, aligning multiple scans, and converting to a mesh for collision/footprint extraction.

**CloudCompare/CloudCompare** — https://github.com/CloudCompare/CloudCompare — 4,789 stars, pushed 2026-10-09, NOASSERTION (GPL-2.0), C++. *Use:* interactive GUI for manual registration, cropping, cloud-to-cloud distance (as-built vs model). Desktop tool, not a library you embed.

**humantecheu/pystruct3d** — https://github.com/humantecheu/pystruct3d — 37 stars, pushed 2026-06-25, MIT, Python 3.10–3.12. Fits bounding boxes to segmented point-cloud instances, computes volumetric IoU, reads LAS/LAZ/E57/PCD/PLY/XYZ/PTS; built on NumPy/SciPy/Open3D. *Use:* after you have instance labels for machines/racks, this turns them into oriented boxes, which is precisely what the DES layout and the collision footprints need. Small but directly on target.

**LTTM/Scan-to-BIM** — https://github.com/LTTM/Scan-to-BIM — 131 stars, pushed 2025-03-03, API license null (README: CC BY-SA 4.0), Python. BIM-Net++ semantic segmentation of building point clouds, trained on HePIC/S3DIS; mIoU 43.7 on HePIC. *Use:* a research baseline for walls/floors/columns, not machines; share-alike licence; retrain needed for industrial content. Also in this family: **weiliansong/A-Scan2BIM** (74 stars), **mac999/scan_to_bim_pipeline** (56 stars), **Parikshit00/Deep3D-FloorPlan-Net** (42 stars, RandLA-Net → DXF floor plan), **Silentbarber/FloorSAM** (32 stars, SAM on LiDAR density maps for floor plans).

**JonasSchult/Mask3D** — https://github.com/JonasSchult/Mask3D — 748 stars, pushed 2023-10-29, MIT. **OpenMask3D/openmask3d** — 271 stars, pushed 2023-12-15, MIT. 3D instance segmentation (closed-vocab) and open-vocabulary instance segmentation of indoor scans. *Use:* OpenMask3D lets you query "CNC machine", "pallet", "rack" against the scan without training, which is the pragmatic path for machine extraction; both are unmaintained since 2023 and need a CUDA/MinkowskiEngine environment. Budget for environment pain.

**facebookresearch/sam2** — https://github.com/facebookresearch/sam2 — 19,978 stars, pushed 2026-05-30, Apache-2.0. *Use:* video object segmentation to mask machines/people in camera frames; feeds OpenMask3D-style lifting to 3D and improves tracking masks.

**DepthAnything/Depth-Anything-V2** — https://github.com/DepthAnything/Depth-Anything-V2 — 8,925 stars, pushed 2026-03-24, Apache-2.0 at repo level (check per-model weights; the larger checkpoints have historically carried a non-commercial licence). *Use:* monocular depth from fixed CCTV to lift 2D tracks to the floor plane when a homography is not enough.

**pyvista/pyvista** — 3,841 stars, pushed 2026-10-10, MIT; **mikedh/trimesh** — 3,694 stars, pushed 2026-10-02, MIT. *Use:* trimesh for mesh IO, boolean/convex hulls, footprint polygons and GLB export of extracted machines; pyvista for quick offline 3D inspection and VTK filters.

---

## (D) Tracking people and vehicles

**ultralytics/ultralytics** — https://github.com/ultralytics/ultralytics — 62,352 stars, pushed 2026-10-09, **AGPL-3.0**. YOLO detection/segmentation/pose with built-in ByteTrack and BoT-SORT trackers (`model.track(...)`). *Use:* person/forklift/AGV detection on shop-floor cameras. The AGPL licence applies to your service if you ship it; Ultralytics sells an enterprise licence. If that is a problem, use an Apache-2.0 detector (e.g. RT-DETR/YOLOX weights) with BoxMOT.

**mikel-brostrom/boxmot** — https://github.com/mikel-brostrom/boxmot — 8,310 stars, pushed 2026-09-18, **AGPL-3.0**, Python/C++. Pluggable SOTA trackers (ByteTrack, BoT-SORT, OC-SORT, DeepOC-SORT, StrongSORT, BoostTrack), axis-aligned and oriented boxes, TensorRT. *Use:* the tracker layer; its ByteTrack is the maintained implementation now that the original repo is unreachable. Same AGPL caveat.

**ifzhang/ByteTrack** — the GitHub API now reports the repository as non-existent/inaccessible (query `repo:ifzhang/ByteTrack` fails validation). Do not plan on cloning it; use BoxMOT's or Ultralytics' ByteTrack.

**taherfattahi/vda5050-robot-simulator** — https://github.com/taherfattahi/vda5050-robot-simulator — 22 stars. Simulates multiple AGVs speaking VDA 5050 over MQTT and visualises them. *Use:* a stand-in AGV fleet for the twin before real AMRs are connected, and a reference for consuming VDA 5050 state messages. **wh200720041/warehouse_simulation_toolkit** (313 stars, ROS/Gazebo) is the heavier ROS alternative; **botprof/agv-examples** (81 stars) has kinematic models.

*Gap:* nothing on GitHub packages "camera → floor-plane heatmap/spaghetti" for factories. The composition is: YOLO+BoxMOT tracks → per-camera homography to floor coordinates (OpenCV) → store (x, y, t, id) → deck.gl HeatmapLayer/TripsLayer. That is roughly a week of work, not a clone.

---

## (E) IoT / data layer

**eclipse-ditto/ditto** — https://github.com/eclipse-ditto/ditto — 935 stars, pushed 2026-10-08, EPL-2.0, Java. Twin state store with Things/Features JSON model, WebSocket/SSE change streams, policies, connectivity to MQTT/Kafka/AMQP. *Use:* if you want a standards-shaped "last known state" service that the browser subscribes to. Heavy (MongoDB + several JVM services). For a small team a FastAPI + Redis/Timescale state service like WareTwin's is lighter.

**ertis-research/opentwins** — https://github.com/ertis-research/opentwins — 278 stars, pushed 2026-10-09, Apache-2.0. Composite digital-twin platform (Ditto + Kafka/MQTT + InfluxDB + Grafana + Kubernetes, with a Unity plugin and ML hooks per its papers). README says "under development", not for production, deploy via Helm. *Use:* a full reference architecture to read; too operationally heavy to adopt wholesale. The related **aleka07/openegiz** (4 stars) packages Ditto + MQTT + InfluxDB + Grafana + Unity WebGL into one docker-compose, which is a cheaper way to try that stack.

**Eclipse BaSyx**: **basyx-java-server-sdk** — 85 stars, pushed 2026-10-06, MIT; **basyx-python-sdk** — https://github.com/eclipse-basyx/basyx-python-sdk — 103 stars, pushed 2026-10-08, MIT; **basyx-aas-web-ui** — 34 stars (Vue). *Use:* if customers or partners expect Asset Administration Shell (AAS) submodels for machines, the Python SDK lets you emit AASX files/REST from your own asset model with little overhead. Not needed for an internal twin.

**FIWARE**: **telefonicaid/fiware-orion** — 223 stars, pushed 2026-10-06, AGPL-3.0, C++ (NGSI context broker); **FIWARE/tutorials.Getting-Started** — 49 stars, MIT. *Use:* only if you are in a European smart-industry programme that mandates NGSI-LD. Otherwise skip.

**node-red/node-red** — https://github.com/node-red/node-red — 23,730 stars, pushed 2026-10-08, Apache-2.0. *Use:* the pragmatic ingestion glue: OPC UA/MQTT/Modbus nodes → transform → MQTT/HTTP into your state service; also a quick OEE calculator (see **yaseralie/Node-RED_Animation**, 1 star, for an OEE dashboard flow example).

**FreeOpcUa/opcua-asyncio** — https://github.com/FreeOpcUa/opcua-asyncio — 1,495 stars, updated 2026-10-09, Python ≥3.10. *Use:* read PLC tags directly from Python when Node-RED is not wanted.

**MES/OEE**: **factorysemantics/factorysemantics-mes** — 8 stars, pushed 2026-10-10, Apache-2.0, Python 3.12/3.13, v0.2.0 pre-alpha: OPC UA in, OEE/downtime, ISA-95 data shapes, SPC, finite-capacity scheduling, ERPNext connector, 95 MCP tools + REST, SQLite/Postgres, docker-compose. *Use:* interesting as an ISA-95 schema and OEE-calculation reference, and its MCP surface suits an LLM copilot, but it has never run on a real plant. **dharmesh-data/isa95-oee-dashboard** (2 stars; Kafka + PyFlink + TimescaleDB + Grafana) and Siemens' **industrial-edge/Performance-Insight-OEE-Dashboard** (24 stars, a guide) are the only other hits; there is no mature open-source MES on GitHub by stars.

**OPCFoundation/UA-CloudViewer** — 40 stars, pushed 2025-02-11, MIT, JS. Browses OPC UA information models as "industrial digital twins". *Use:* niche; useful if your machines expose rich companion-spec models.

**INTO-CPS-Association/DTaaS** — https://github.com/INTO-CPS-Association/DTaaS — 185 stars, pushed 2026-10-04, NOASSERTION, TypeScript. "Digital Twin as a Service": web client + library/runner/logger microservices + CLI; twins assembled from reusable assets (FMUs, models) and shared between users. *Use:* a platform for hosting many co-simulation twins; overkill for one factory, but its asset/runner split is a sensible pattern.

---

## (F) Optimisation

**google/or-tools** — https://github.com/google/or-tools — 14,168 stars, pushed 2026-10-09, Apache-2.0. CP-SAT, MIP, routing. *Use:* job-shop/flow-shop scheduling (CP-SAT has canonical examples), AGV routing (routing solver), and facility layout formulated as QAP or unequal-area MIP with no-overlap constraints. The facility-layout search returned only student repos (**dkunitsk/FLP-layout-optimization** 9 stars, **TejaswiniMedi/gym-flp** 2 stars), so write the model yourself on CP-SAT; it is a few hundred lines.

**anyoptimization/pymoo** — https://github.com/anyoptimization/pymoo — 2,972 stars, pushed 2026-07-07, Apache-2.0. NSGA-II/III, MOEA/D, GA, DE, CMA-ES, PSO. *Use:* simulation-based multi-objective optimisation where the objective is a DES run (throughput vs WIP vs travel distance), i.e. the layout/line-balancing what-if loop. Wrap FactorySimPy runs as the evaluation function.

**Line balancing**: **RahulShagri/Interactive-Assembly-Line-Balancer** — 39 stars, updated 2026-09-28, Python GUI for simple ALB; **hihiworld/mixed-assembly-line-balancing-and-sequencing** — 26 stars (docplex); **bulentsiyah/Double-Sided-...-Genetic-Algorithm** — 27 stars, C#, archived. *Use:* read for precedence-graph handling; implement SALBP-1/2 on CP-SAT instead.

**Scheduling/RL**: jobshoplab and SimRLFab (section A) are the reusable environments; **colinlee0924/DRL-SimPy-JobShop** (29 stars) shows DRL + SimPy integration.

---

## (G) Complete reference digital-twin projects

**WayneChou-bot/WareTwin** — https://github.com/WayneChou-bot/WareTwin — 121 stars, pushed 2026-09-11, MIT, TypeScript/Python.
Browser twin of a 100×70 m warehouse with 20 AMRs. React 18 + TS + Vite + React Three Fiber + zustand frontend; FastAPI + Pydantic v2 + asyncio + SQLite backend; shared Twin State schema; 100 ms tick engine with robot state machines, A* pathfinding, battery/charger scheduling and conveyor bottlenecks; WebSocket sends a full state then per-tick diffs; a TypeScript fallback engine with the same PRNG runs in the browser if the backend is down. What-if runs clone the live engine, inject a scenario and compare 12 metrics against a same-seed baseline. Virtual 270° LiDAR per robot, a VLM path over CCTV frames, an "AI Ops Copilot" (rule-based by default). 84 tests, Dockerfile, Render/Fly/Vercel configs. Layout is synthetic.
*Use:* this is the single most reusable repo for your architecture: the state-diff WebSocket protocol, the deterministic engine + what-if cloning, and the R3F scene organisation are exactly what a factory twin needs. Replace its warehouse engine with a FactorySimPy/salabim model and its synthetic layout with your scan-derived layout.

**WayneChou-bot/RFTwin** — https://github.com/WayneChou-bot/RFTwin — 9 stars, pushed 2026-09-12, MIT. Same author and stack applied to a robotic production line: 4 process cells, 12 robot arms, an AMR fleet, stations such as Machine Tending and Inspection, fault injection with blocking/starvation propagation, 100 ms Python engine as the single source of truth, what-if branches with first-divergence reporting. *Use:* the production-line variant of WareTwin; between the two you get both intralogistics and line semantics. Young, single-author, so read the code before trusting the model.

**game4automation/realvirtual-WEB** (see B) — the most industrially complete open web HMI; AGPL.

**NVIDIA-Omniverse-blueprints/omniverse-dsx-blueprint-for-ai-factories** — https://github.com/NVIDIA-Omniverse-blueprints/omniverse-dsx-blueprint-for-ai-factories — 134 stars, pushed 2026-05-07, NOASSERTION, TypeScript; and **NVIDIA-Omniverse/aif-pipeline-samples** — 46 stars, pushed 2026-09-08, MIT, Python (CAD → SimReady USD ingestion scripts). *Use:* the blueprint shows NVIDIA's reference for design/sim/ops twins on OpenUSD but assumes Omniverse/RTX infrastructure; the pipeline samples are useful if you ever need CAD→USD. Not a fit for a browser-first small team.

**Autodesk-Forge/forge-digital-twin** — 182 stars, updated 2026-10-04 (last substantive push 2023-02-01 per API), MIT; successor **autodesk-platform-services/aps-digital-twin** — 21 stars, pushed 2026-10-06, MIT. Manufacturing twin demos on the Autodesk Viewer with sensor overlays. *Use:* good UX reference for sensor-to-3D binding; requires Autodesk Platform Services cloud, so not self-hostable.

**SINTEF-9012/SINDIT** — 56 stars, pushed 2023-11-01, MIT, Python. Knowledge-graph-based factory twin (Neo4j + time series + dashboard). *Use:* reference for an asset knowledge graph; dormant.

**Xudarker/DigitalTwinFactory** — 33 stars, pushed 2021-09-18, no license, Unity workshop twin (Chinese). **rparak/Unity3D_Robotics_UR** — 203 stars, Unity UR3 twin. *Use:* Unity is viable (OpenTwins has a Unity plugin) but WebGL builds are heavy and the splat ecosystem is thinner; I would stay on three.js.

**Khalidabdi1/factory** — 115 stars, top hit for "factory simulation" and "factory three.js", is an isometric city/Starship-launch sim, not a factory; ignore.

---

## Shortlist: the 10 most directly reusable repos

1. **WayneChou-bot/WareTwin** (MIT) — architecture template: R3F front end, FastAPI engine, state-diff WebSocket, what-if cloning.
2. **FactorySimPy/FactorySimPy** (MIT) — factory DES vocabulary on SimPy with real-time mode.
3. **salabim/salabim** (MIT per README) — alternative DES with monitors and desktop 2D/3D animation for model validation.
4. **sparkjsdev/spark** (MIT) — splat + mesh rendering in one three.js scene.
5. **reall3d-com/Reall3dViewer** (MIT) — LOD-streamed splats with measurement; evaluate against Spark on your scan.
6. **isl-org/Open3D** (MIT) — scan cleanup, plane/instance extraction, registration.
7. **humantecheu/pystruct3d** (MIT) — oriented bounding boxes of machines from segmented scans.
8. **mikel-brostrom/boxmot** (AGPL-3.0) with **ultralytics/ultralytics** (AGPL-3.0) — person/forklift tracking; the maintained ByteTrack.
9. **google/or-tools** (Apache-2.0) with **anyoptimization/pymoo** (Apache-2.0) — scheduling, layout and simulation-based multi-objective optimisation.
10. **game4automation/realvirtual-WEB** (AGPL-3.0) — read-only reference for industrial HMI patterns and GLB signal-binding metadata; plus **node-red/node-red** (Apache-2.0) as the ingestion glue.

```bash
mkdir -p vendor && cd vendor
git clone --depth 1 https://github.com/WayneChou-bot/WareTwin.git
git clone --depth 1 https://github.com/WayneChou-bot/RFTwin.git
git clone --depth 1 https://github.com/FactorySimPy/FactorySimPy.git
git clone --depth 1 https://github.com/salabim/salabim.git
git clone --depth 1 https://github.com/sparkjsdev/spark.git
git clone --depth 1 https://github.com/reall3d-com/Reall3dViewer.git
git clone --depth 1 https://github.com/isl-org/Open3D.git
git clone --depth 1 https://github.com/humantecheu/pystruct3d.git
git clone --depth 1 https://github.com/mikel-brostrom/boxmot.git
git clone --depth 1 https://github.com/ultralytics/ultralytics.git
git clone --depth 1 https://github.com/google/or-tools.git
git clone --depth 1 https://github.com/anyoptimization/pymoo.git
git clone --depth 1 https://github.com/game4automation/realvirtual-WEB.git
git clone --depth 1 https://github.com/node-red/node-red.git
# optional references
git clone --depth 1 https://github.com/ertis-research/opentwins.git
git clone --depth 1 https://github.com/proto-lab-ro/jobshoplab.git
git clone --depth 1 https://github.com/OpenMask3D/openmask3d.git
git clone --depth 1 https://github.com/taherfattahi/vda5050-robot-simulator.git
# pip/npm rather than clone:
pip install simpy factorysimpy salabim open3d pystruct3d boxmot ultralytics ortools pymoo trimesh pyvista asyncua usd-core
npm i three @react-three/fiber @react-three/drei @sparkjsdev/spark @reall3d/reall3dviewer deck.gl echarts
```

**Licence summary for the shortlist:** everything except BoxMOT/Ultralytics (AGPL-3.0), realvirtual-WEB (AGPL-3.0, broad interpretation in their README) and Grafana (AGPL-3.0, fine if unmodified) is MIT/Apache. If AGPL is unacceptable for the tracking service, swap the detector to an Apache-licensed model and keep the tracker logic in-house (OC-SORT/ByteTrack are short algorithms).

**Suggested assembly:** scan → SuperSplat cleanup → Spark/Reall3d splat in an R3F scene (WareTwin layout) ← machine GLBs placed from pystruct3d boxes; FactorySimPy engine behind FastAPI streaming state diffs; Node-RED/opcua-asyncio feeding live machine states into the same state service; YOLO+BoxMOT tracks projected to the floor and rendered as deck.gl heatmap/trips over the plan; OR-Tools/pymoo driving what-if layouts and schedules evaluated by the same engine; ECharts for OEE tiles in the UI, Grafana for ops.