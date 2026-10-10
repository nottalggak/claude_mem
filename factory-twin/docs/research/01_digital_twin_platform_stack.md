# Software stack research: full digital twin of a mid-size Korean furniture factory (2–4 person web/Python/AI team, low budget)

Date of research: 2026-10-10. Method: ~60 web searches + GitHub API queries for live star/activity counts. Limits: direct page fetches (WebFetch/curl) were blocked by the sandbox proxy, so facts come from search-result snippets of primary pages plus secondary coverage; anything I could not confirm against a primary source is explicitly marked **(unverified)**. Search budget ran out before I could check ~15 secondary items (listed at the end).

---

## 0. Executive summary (TL;DR)

- **NVIDIA Omniverse is no longer a licensing problem, but it is still a hardware and engineering-effort problem.** Multiple sources report NVIDIA's licensing docs now say "As of May 2026, Omniverse is freely available for both development and production use" with no NVIDIA AI Enterprise subscription needed (community support only). The Omniverse Launcher was retired 2025-10-01; USD Composer/Explorer are now *templates* inside `kit-app-template` rather than downloadable apps. Mega (factory/robot-fleet blueprint) is still "preview". Minimum GPU is an RTX 2070-class 8 GB; realistic is 16 GB+. For a 2–4 person web team on a few-weeks deadline, Omniverse should be an **optional "photoreal/robotics" layer on top of OpenUSD data, not the core**.
- **Commercial DES/layout tools (Plant Simulation, FlexSim, AnyLogic, Simio, Visual Components) are quote-priced at roughly USD 6k–19k per seat per year**; free tiers are non-commercial or size-capped (Plant Simulation student: 80 objects; Arena academic: 150 entities; AnyLogic PLE: non-commercial). They are excellent at bottleneck analysis but will not give you a hackable web twin.
- **Recommended core stack: Python DES (salabim first, SimPy/FactorySimPy as fallback) + OpenUSD/glTF scene authored in Blender + Three.js/React-Three-Fiber web viewer + MQTT (Mosquitto) / Node-RED / asyncua + TimescaleDB-or-InfluxDB 3 + Grafana, modeled loosely on ISO 23247 and optionally exposed as AAS via Eclipse BaSyx.** Keep the scene in USD so an Omniverse/Isaac Sim path remains open later.

---

## 1. NVIDIA Omniverse / OpenUSD / Isaac Sim / Blueprints (as of Oct 2026)

### 1.1 What changed in 2025–2026
| Item | Status | Source |
|---|---|---|
| Omniverse Launcher | **Deprecated 2025-10-01.** NVIDIA's legacy page: "Start with Omniverse Kit templates available on GitHub or access Omniverse libraries directly on NGC." | https://developer.nvidia.com/omniverse/legacy-tools |
| USD Composer / USD Explorer / USDView | Moved to **templates** in `NVIDIA-Omniverse/kit-app-template` (1,110 stars, pushed 2026-10-09). NVIDIA staff on the forum: "USD Composer has always been a template… moving our templates to GitHub and off Launcher." Older Launcher builds "no longer supported." | https://forums.developer.nvidia.com/t/omniverse-usd-composer-being-discontinued/307277 ; https://github.com/NVIDIA-Omniverse/kit-app-template |
| Kit SDK | 108.0 Aug 2025 (RTX Real-Time 2.0 default renderer, USD 25.02, Python 3.12, **breaking changes**), 108.1 Oct 2025 (S3/Azure in content browser, OpenTelemetry), then 109.x, and 110.x (Isaac Sim 6.0 is on Kit 110). kit-app-template tracks a *feature branch*; NGC hosts the *production branch*. | https://docs.omniverse.nvidia.com/dev-guide/latest/release-notes/108_0.html ; https://docs.omniverse.nvidia.com/dev-guide/latest/release-notes/108_1_highlights.html |
| Isaac Sim | 5.0 open-sourced (Apache 2.0 for Isaac-specific extensions; Kit itself remains closed) at SIGGRAPH 2025; **6.0 GA** (Kit 110, Newton physics authoring, web streaming client, native Windows ROS 2). `isaac-sim/IsaacSim` has 4,240 stars, pushed 2026-10-10. | https://developer.nvidia.com/blog/announcing-general-availability-for-nvidia-isaac-sim-5-0-and-nvidia-isaac-lab-2-2 ; https://forums.developer.nvidia.com/t/isaac-sim-6-0-general-availability/372621 ; https://github.com/isaac-sim/IsaacSim |
| OpenUSD Exchange SDK | Apache-2.0 since 1.1; 2.0 (SIGGRAPH 2025) adds UsdPhysics authoring; on GitHub + PyPI (`usd-exchange`, 89 stars). Good for programmatic USD authoring from Python. | https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk/latest/ ; https://github.com/NVIDIA-Omniverse/usd-exchange |
| Mega Omniverse Blueprint | Reference workflow for multi-robot fleets in facility twins; **"available in preview on build.nvidia.com"** — I found no GA announcement. Siemens is "first to develop digital twin software supporting Mega", in beta within Xcelerator. GTC 2026 recap still describes Mega as the factory reference architecture. | https://blogs.nvidia.com/blog/mega-omniverse-blueprint-industrial-digital-twins/ ; https://build.nvidia.com/nvidia/mega-multi-robot-fleets-for-industrial-automation/blueprintcard ; https://blogs.nvidia.com/blog/gtc-2026-virtual-worlds-physical-ai/ |
| DSX Blueprint | Separate blueprint for *AI data-center* factories (GTC 2026), open on GitHub (134 stars, TypeScript). Useful as a code reference for a Kit-streamed web front end, not for furniture. | https://github.com/NVIDIA-Omniverse-blueprints/omniverse-dsx-blueprint-for-ai-factories |

### 1.2 Licensing & cost
- **Historical list price**: Omniverse Enterprise USD 4,500/GPU/year (EDU/Inception 1,125), 5-yr 18,000, perpetual+5yr support 22,500, or USD 1/GPU-hour consumption. NVIDIA's own Enterprise page still shows the $4,500 figure. https://docs.nvidia.com/ai-enterprise/planning-resource/licensing-guide/latest/pricing.html ; https://www.nvidia.com/en-sg/omniverse/enterprise/
- **2026 change**: StorageReview, WindowsForum, zxcollabs and an NVIDIA developer-forum thread titled "NVIDIA Omniverse Licensing Change" (dated 2026-07-01) report the docs now read "As of May 2026, Omniverse is freely available for both development and production use"; software built with Omniverse may be redistributed under the same terms; enterprise support SLAs still require NVIDIA AI Enterprise via reseller/cloud marketplace. **I could not open the NVIDIA license page itself — treat as very likely but verify** at https://docs.omniverse.nvidia.com/dev-overview/latest/common/NVIDIA_Omniverse_License_Agreement.html. Sources: https://www.storagereview.com/news/nvidia-quietly-makes-omniverse-free-for-production-use ; https://forums.developer.nvidia.com/t/nvidia-omniverse-licensing-change/375138 ; https://roughcut.dev/writing/the-omniverse-license-change-you-might-have-missed/
- Practical reading: a small team can ship a Kit-based or Isaac-based twin to a customer at **zero license cost**, with community support only.

### 1.3 Hardware
- USD Composer official requirements: **min GeForce RTX 2070 8 GB**, "Good" RTX A5000 24 GB, "Ideal" 2x RTX A6000. Digital-Twins install guide: min RTX 2070 8 GB, good RTX 3080 10 GB. https://docs.omniverse.nvidia.com/composer/latest/requirements.html ; https://docs.omniverse.nvidia.com/digital-twins/latest/installation-guide.html
- Isaac Sim (forum guidance, applies to 5.x/6.x): min RTX 3070 8 GB, recommended RTX 4080 16 GB, ideal RTX 6000 Ada 48 GB; **GPUs without RT cores (A100/H100) are not supported**; Windows 10 unsupported for 6.0; container is Linux-only. https://forums.developer.nvidia.com/t/gpu-requirement/305727/2 ; https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html
- Realistic team workstation: one RTX 4070 Ti Super/4080/5080-class 16 GB machine is enough for a 20–60 worker factory scene; a 12 GB RTX 4070 works but will hit limits on large scanned scenes.

### 1.4 Can a 2–4 person web team realistically use it?
- Yes for **viewing/streaming** a USD factory scene (kit-app-template "USD Viewer" + `web-viewer-sample`, 149 stars, TypeScript, pushed 2026-06-09: streams a Kit app to a browser and passes messages both ways — https://github.com/NVIDIA-Omniverse/web-viewer-sample).
- Yes for **live data overlays**: `NVIDIA-Omniverse/iot-samples` (85 stars, MIT, last push 2024-09-05 — stale but still the canonical pattern for pushing sensor data into a USD stage) https://github.com/NVIDIA-Omniverse/iot-samples.
- **No** as the primary DES engine: Omniverse has no discrete-event material-flow simulator. Factory throughput/bottleneck logic must come from a DES tool (Plant Simulation/FlexSim/AnyLogic via their Omniverse connectors, or your own Python DES driving USD transforms).
- Costs that are *not* zero: a dedicated RTX box per developer, Linux/driver fiddling, Kit API churn (108 had breaking changes), and server GPU cost if you stream to the factory's tablets.

### 1.5 Siemens–NVIDIA outputs
- **Teamcenter Digital Reality Viewer** (announced 2025-01-07): Omniverse RTX rendering inside Teamcenter. https://news.siemens.com/en-us/siemens-teamcenter-digital-reality-viewer/
- **Digital Twin Composer** (CES 2026-01): combines 2D/3D data, built on Omniverse; "early access with select customers", scheduled for Siemens Xcelerator Marketplace **mid-2026** (whether it shipped is **unverified**). https://news.siemens.com/en-us/digital-twin-composer-ces-2026/ ; https://press.siemens.com/global/en/pressrelease/siemens-unveils-technologies-accelerate-industrial-ai-revolution-ces-2026
- **Tecnomatix Connector for NVIDIA Omniverse**: commercial add-on; Process Simulate / Plant Simulation can run synchronized with an Omniverse scene for photoreal visualization; presented at the 2025 Plant Simulation User Conference (which also announced **Python integration** in Plant Simulation). https://plm.sw.siemens.com/en-US/tecnomatix/products/tecnomatix-connector-nvidia-omniverse ; https://blogs.sw.siemens.com/tecnomatix/plant-simulation-user-conference-2025-recap-python-integration-ai-industrial-metaverse-and-more
- Industrial AI Operating System + 9 copilots (CES 2026); customers: PepsiCo, KION/GXO forklifts (Mega), Toyota Georgetown (idealworks iw.sim). https://www.siemens.com/en-us/company/artificial-intelligence/siemens-nvidia-partnership/ ; https://blogs.nvidia.com/blog/how-digital-twins-scale-industrial-ai/

---

## 2. Commercial factory simulation / layout tools

All list prices below are **third-party/reseller figures unless stated**; vendors quote-price.

| Tool | Free/student/trial | Indicative commercial price | Bottleneck / layout strengths | Sources |
|---|---|---|---|---|
| **Siemens Tecnomatix Plant Simulation** | Free Student Edition (Windows only, **max 80 objects**, non-commercial). Academic site licenses discounted. | Quote only. (Industry chatter: high five figures USD/seat; **unverified**.) | Gold standard for DES: automatic bottleneck analyzer, Sankey material-flow, experiment manager, GA optimizer; 2025: Python integration, Omniverse connector. Used in a published Slovak furniture-plant study (Bambura 2020). | https://resources.sw.siemens.com/hu-HU/download-tecnomatix-plant-simulation-student-software ; https://bioresources.cnr.ncsu.edu/wp-content/uploads/2020/07/BioRes_15_3_6752_Bambura_SC_Utilization_Computer_Simulation_Furniture_Production_17528.pdf |
| **FlexSim (Autodesk since 2023/24)** | **Express** = default unlicensed state (model-size-limited), 30-day full trial. No individual student SKU found. | ~USD 6,000/yr standalone (reseller estimate), support +195/595 per user. | Built-in 3D, conveyors, AGVs, "Experimenter"/optimizer (OptQuest), dashboards. Very fast to learn; export to 3D limited. | https://forums.autodesk.com/t5/flexsim-knowledge-base/flexsim-feature-limitations-by-license-type/tac-p/13814419 ; https://www.rfp.wiki/supply-chain-logistics-transportation/supply-chain-planning-solutions/supply-chain-simulation-software/enterprise-dynamics/flexsim |
| **AnyLogic** | **PLE** free, size-limited, **no commercial use**. | Professional ~USD 12,390–18,990/yr; University Researcher ~3,550–4,250/yr (third-party). | Multi-method (DES + agent + SD), Java extensible, Material Handling Library (conveyors, AGVs, workers), Omniverse export exists (anylogic.help/advanced/omniverse). Used in a Vietnamese furniture-plant optimisation paper. | https://www.ki-syndikat.de/tools/anylogic/ ; https://anylogic.help/advanced/omniverse/prerequisites.html ; https://jst.bdu.edu.vn/index.php/jst/article/view/338 |
| **Simio** | Personal Edition free (size-limited); USD 25 student copy; academic grants free for a year; 30-day trial. **Acquired by Aegis Software Jan 2026 (single source, unverified)**. | Quote (Design/Team/Enterprise/RPS). | Object-oriented 3D, built-in scheduling (RPS). | https://simio.com/academics/student-resources.htm ; https://www.rfp.wiki/supply-chain-logistics-transportation/supply-chain-planning-solutions/supply-chain-simulation-software/simul8/simio |
| **Visual Components** | Trial only via paid Essentials training (EUR 950/company) or by request; academic program exists. | Essentials for SolidWorks 12-mo: CAD$ 7,280 (one reseller). Premium is "full factory virtualization". | Best-in-class 3D layout + robot OLP + huge eCatalog of machines/conveyors; statistics are decent but weaker than Plant Simulation for pure DES. | https://www.visualcomponents.com/services/essentials-training/ ; https://shop.cadmicro.com/products/visual-components-for-solidworks-12-month-term |
| **Dassault DELMIA (3DEXPERIENCE Factory Flow Simulation)** | No free tier found. | Role-based subscription, quote. | Workers/machines/material flow on 2D/3D/point-cloud layouts; enterprise-oriented. | https://www.solidworks.com/customer-story/behlen-streamlines-factory-flow-3dexperience-works/ ; https://www.gartner.com/reviews/product/3dexperience-delmia |
| **Rockwell Arena** | Demo/Academic: full functionality, no time limit, **~150 entity cap**. | Quote (Standard/Professional, unlimited model size). | Classic flowchart DES, 2D animation; weak 3D. | https://rockwellautomation.com/en-au/products/software/arena-simulation/buying-options.html |
| **Simul8** | Student free only via school license. | ~USD 6,049/user/yr (Capterra). | 2D-first, cloud option, OptQuest. | https://capterra.com/p/114609/SIMUL8-Professional/ |
| **Autodesk Factory Design Utilities** | Only in Product Design & Manufacturing Collection (staging page: USD 3,375/yr; **verify**), or Flex tokens for 24 h. | — | Layout (AutoCAD/Inventor/Navisworks) with asset library; no DES. **Prodsmart → Fusion Operations** (MES): USD 173–600/month depending on source. | https://www.autodesk.com/products/factory-design-utilities/overview ; https://www.costbench.com/software/manufacturing-erp/prodsmart/ |

**Verdict for this team:** the only ones worth buying later are Plant Simulation (if a Siemens-literate consultant joins) or FlexSim (fastest ROI). For a few-week build, use free tiers to *validate* your Python DES results, not as the delivery platform (their free tiers forbid commercial use).

---

## 3. Open-source / cheap tools a web+Python team can actually use

Ratings: (a) 3D layout viz, (b) DES material flow, (c) worker/forklift animation, (d) live data. Scale: ●●● strong, ●● usable, ● weak/needs glue, ○ none.

| Tool | a | b | c | d | Notes & evidence |
|---|---|---|---|---|---|
| **SimPy** (BSD/MIT, GitLab) | ○ | ●●● | ○ | ● | The reference Python DES. No animation. Use with **FactorySimPy** (15★, MIT, created 2025-04, pushed 2026-10-09: machines/conveyors components) or **ProdSim** (40★, synthetic production data generator, paper in Procedia CIRP). https://github.com/FactorySimPy/FactorySimPy ; https://github.com/FuchsTom/ProdSim |
| **salabim** (405★, pushed 2026-05-29; PyPI very active) | ●● | ●●● | ●● | ● | Pure-Python DES with **built-in 2D and 3D animation** (primitives + OBJ models, video export), no `yield` boilerplate, monitors/queues/stores. WSC 2018 paper. 3D factory example: `ghackenberg/salabim-grid-plant-3D` (gantry FMS configurator). Best "sim + animation in one file" option. https://github.com/salabim/salabim ; https://www.informs-sim.org/wsc18papers/includes/files/416.pdf ; https://github.com/ghackenberg/salabim-grid-plant-3D |
| **JaamSim** (237★, Java, Apache 2.0, pushed 2026-10-07; releases 2025-07, 2025-08, 2026-01) | ●● | ●●● | ●● | ● | Drag-and-drop DES with interactive OpenGL 3D; Fraunhofer comparison found it a "real alternative to commercial DES tools." Java, not Python; scripting via input files. Commercial JaamSim Pro adds vehicles/terminals. https://github.com/jaamsim/jaamsim ; https://jaamsim.com/docs/JaamSim%20Release%20Notes%202025-08.pdf ; https://publica.fraunhofer.de/handle/publica/267879 |
| **OpenModelica** | ○ | ● | ○ | ● | Continuous/equation-based; wrong paradigm for job-shop flow. Skip. |
| **Gazebo (Harmonic/Ionic)** | ● | ○ | ●● | ●● (ROS 2) | Robotics physics/sensor sim; no DES. Only if you later need AMR/forklift autonomy testing. (No 2025 source found on factory DES use.) |
| **Blender + bpy** (GPL tool, outputs free) | ●●● | ○ | ●● | ● | Author/clean the plant model, import LiDAR/Polycam scans, export **glTF** (web) and **USD** (Omniverse). Known pitfall: unit scale mismatch vs Omniverse. https://docs.omniverse.nvidia.com/connect/latest/blender/manual.html ; https://forums.developer.nvidia.com/t/export-to-usd-scale-units-from-blender-to-omniverse/201112 |
| **Three.js / React-Three-Fiber** (R3F 32,831★, pushed 2026-10-10) | ●●● | ○ | ●●● | ●●● | Your team's natural home: glTF loading, instancing for pallets/panels, drei helpers, WebSocket/MQTT-over-WS. Industrial reference: **realvirtual-WEB** (152★, created 2026-03, "Browser-based 3D-HMI for industrial automation — Three.js/TypeScript viewer for realvirtual digital twins", pushed 2026-10-07). Chinese low-code twin frameworks: **three-vue-tres** (2,439★), **Meteor3DEditor** (71★). https://github.com/pmndrs/react-three-fiber ; https://github.com/game4automation/realvirtual-WEB ; https://github.com/hawk86104/three-vue-tres |
| **Babylon.js 8** (2025-03-27; WGSL/WebGPU native, IBL shadows, Gaussian splat support) | ●●● | ○ | ●●● | ●●● | Equivalent to Three.js with a built-in inspector/GUI and splat rendering (nice for scanned factories). https://radiancefields.com/babylon-js-v8-0-released |
| **PlayCanvas** | ●● | ○ | ●● | ●● | Engine MIT; hosted editor free tier / USD 15 mo Personal / USD 50 seat Org (aggregator figures). Editor lock-in; fine for quick demos. https://playcanvas.com/products/editor |
| **Unity 6** | ●●● | ● | ●●● | ●●● | Personal free below USD 200k revenue/funding; Pro ~USD 2,040–2,310/seat/yr (5% rise 2026-01-12); Runtime Fee cancelled 2024-09-12; **Unity Industry** required for non-game firms >USD 1M. OPC UA refs: OPC Foundation **UA-CloudMetaverse** (13★), **rparak/Unity3D_Robotics_Overview** (52★), **BeltTwinUnity** (TwinCAT→OPC UA→Node-RED→MQTT→Unity). Heavy WebGL builds; C# not Python. https://unity.com/products/pricing-updates ; https://unity.com/blog/unity-is-canceling-the-runtime-fee ; https://github.com/OPCFoundation/UA-CloudMetaverse |
| **Unreal Engine 5** | ●●● | ● | ●●● | ●● | Free under USD 1M revenue; USD 1,850/seat/yr for non-game firms above that; from 2026-05-27 Twinmotion/RealityScan no longer bundled. Pixel Streaming works but needs GPU servers; steepest learning curve. https://www.unrealengine.com/en-US/blog/we-are-updating-unreal-engine-twinmotion-and-realitycapture-pricing-in-late-april |
| **Godot 4** (MIT) | ●● | ● | ●● | ●● | `godot-mqtt` addon (56★); a 2025 IEEE paper fed open62541 OPC UA data into Godot via GDExtension. Web export is weaker than Three.js. https://github.com/goatchurchprime/godot-mqtt |
| **CesiumJS / deck.gl** | ● (indoor) | ○ | ● | ●● | Geospatial; 3D Tiles good for point clouds, but indoor coordinate handling and factory-scale interaction are awkward. Only if the client wants a site/campus map. https://talks.osgeo.org/foss4g-2025/talk/N3KH8B/ |

---

## 4. Industrial IoT / data layer

| Component | Status (verified) | Role in a small factory |
|---|---|---|
| **Eclipse BaSyx (AAS)** | Python SDK 1.0.0 implements **AAS Part 1 metamodel v3.0** + AASX; **Part 2 API "not implemented yet"**. Java server SDK (85★) + AAS Web UI (34★) are the runnable server/UI. python-sdk 103★, all pushed Oct 2026. | Standard "asset passport" per machine (panel saw, edgebander, CNC, press). Optional; useful for grants/certification narratives (Industry 4.0 / 스마트공장). https://pypi.org/project/basyx-python-sdk/1.0.0 ; https://github.com/eclipse-basyx/basyx-python-sdk |
| **Eclipse Ditto** | 935★, pushed 2026-10-08; Docker Compose deploy; needs MongoDB; HTTP/WebSocket + MQTT/AMQP/Kafka connectors; RQL search. | Twin state store ("thing" per machine with features). Simpler than FIWARE for device mirroring. https://github.com/eclipse-ditto/ditto ; https://eclipse.dev/ditto/intro-overview.html |
| **FIWARE (Orion-LD / NGSI-LD)** | Semantic JSON-LD property graphs. | Better for cross-org/semantic city/energy twins; overkill here. https://arxiv.org/pdf/2309.12358 |
| **Node-RED** | Modbus + OPC UA + MQTT contrib nodes; runs on Raspberry Pi 4/5 (4 GB recommended) as OT→IT gateway. (A dev.to piece claims Node-RED 5 shipped in 2026 — **unverified**.) | The glue: poll Modbus/OPC UA, normalize to a unified-namespace topic tree, publish MQTT. https://flowfuse.com/blog/2024/08/opc-ua-to-mqtt-with-node-red/ ; https://zbotic.in/raspberry-pi-for-industrial-iot-modbus-mqtt-and-node-red/ |
| **MQTT broker** | **Mosquitto** 2.0.22 (Jul 2025), EPL/EDL, <1 MB single-threaded. **EMQX** moved to **BSL 1.1 from v5.9** (Apache 2.0 ≤5.8). | Mosquitto for one site; EMQX only if you need clustering/dashboard and accept BSL. https://cedalo.com/blog/mosquitto-vs-emqx-an-honest-comparison-for-iot-teams/ |
| **OPC UA** | **open62541** 3,238★, MPL-2.0, 1.4.x through 2025, 1.5.x in 2026 (spec 1.05.07). **asyncua** 1,495★, 1.1.8 Sep 2025, **2.0 June 2026**. | asyncua client in your Python collector for any machine with an OPC UA server (newer HOMAG/Biesse/SCM lines usually do; verify per machine). https://github.com/open62541/open62541 ; https://github.com/FreeOpcUa/opcua-asyncio |
| **Modbus** | pymodbus / Node-RED modbus nodes. | Energy meters, VFDs, dust-collector PLCs. |
| **Time-series DB** | **InfluxDB 3 Core** GA 2025-04-15, MIT/Apache-2 (early 72-h query cap later lifted). **TimescaleDB**: Postgres extension, Apache core + "Timescale License" community features (**license detail not re-verified this session**). | Pick TimescaleDB if you already run Postgres for the twin's master data; InfluxDB 3 Core if you want a pure sensor store. https://www.influxdata.com/blog/influxdata-announces-influxdb-3-OSS-GA |
| **Grafana** | Standard IIoT dashboarding. | OEE / downtime / queue-length boards next to the 3D twin. https://grafana.com/blog/industrial-iot-visualization-how-grafana-powers-industrial-automation-and-iiot/ |
| **United Manufacturing Hub** | 396★, Go, pushed 2026-10-09; Helm chart bundling MQTT+Kafka+Node-RED+TimescaleDB+Grafana + OEE "factoryinsight". License listing conflicting (Apache vs AGPL) — check repo. | Opinionated all-in-one if you are comfortable with Kubernetes (k3s). Otherwise copy its Unified Namespace topic conventions and run Docker Compose. https://github.com/united-manufacturing-hub/united-manufacturing-hub ; https://umh.docs.umh.app/ |
| **ISO 23247 (2021, Parts 1–4)** | Part 1 principles; Part 2 reference architecture (built on ISO/IEC 30141 IoT RA: Observable Manufacturing Elements → Data Collection & Device Control entity → Digital Twin entity → User entity); Part 3 OME attribute lists (personnel, equipment, materials, process, facility, environment, product, documents); Part 4 information exchange across user/service/access/proximity networks. Protocol-agnostic. | Use its four-layer vocabulary to structure the repo and the pitch deck; no need to buy the PDFs for a prototype. https://iteh.es/catalog/standards/iso/7a6c23aa-d7d0-4df1-a5d5-52155aa78f36/iso-23247-2-2021 |

### Minimal viable "live data" architecture for a mostly non-networked Korean furniture plant
Retrofit guidance (non-invasive, do not touch machine wiring/certification): clamp-on **CT current sensors** on each machine's supply (run/idle/off state + rough cycle counting), **vibration/accelerometer** on edgebander/CNC spindles, **photo-eye or IR beam counters** on panel saw out-feed and edgebander in-feed, **BLE/UWB tags or simple QR scans** for carts/forklift position, and a **tablet "andon" form** for operators to log job start/stop/reason codes (this gives you MES-grade data in week one). Edge: ESP32 nodes → Wi-Fi/LoRa → one Raspberry Pi 5 (4 GB) running Mosquitto + Node-RED + TimescaleDB/InfluxDB + Grafana via Docker Compose; the Python twin server subscribes via MQTT-over-WebSocket and pushes state to the browser. Sources: https://www.kern-it.be/en/definitions/iot-retrofit/ ; https://www.bisinfotech.com/brownfield-retrofitting-upgrading-legacy-factories-without-replacing-core-control-systems/ ; https://learn.umh.app/blog/connectivity-retrofitting-the-shopfloor-with-plug-play-sensors. Vendor estimate: retrofit ≈ 5–15 % of the price of equivalent natively-connected equipment.

Topic convention (UMH-style unified namespace): `kr/<site>/<area>/<line>/<machine>/<tag>` e.g. `kr/paju/panel/line1/edgebander1/state`.

---

## 5. Notable open-source repos & papers (stars/activity from GitHub API, 2026-10-10)

**Simulation (Python/Java)**
- `salabim/salabim` — 405★, pushed 2026-05-29, Python DES with 2D/3D animation. https://github.com/salabim/salabim
- `jaamsim/jaamsim` — 237★, Apache-2.0, pushed 2026-10-07. https://github.com/jaamsim/jaamsim
- `OpenFactoryTwin/ofact` — 58★, Python, created 2024-09, pushed 2026-10-06, "Simulation-based Digital Twin for Production and Logistics Material Flows" (agent-based, ML hooks). Closest open-source thing to a *factory digital twin framework*. https://github.com/OpenFactoryTwin/ofact
- `FuchsTom/ProdSim` — 40★, SimPy production DES + synthetic data; paper https://www.sciencedirect.com/science/article/pii/S2212827122004395
- `FactorySimPy/FactorySimPy` — 15★, MIT, SimPy component library, actively developed 2025–26. https://factorysimpy.github.io/FactorySimPy/
- `ghackenberg/salabim-grid-plant-3D` — gantry FMS configurator with salabim 3D (stars not retrievable). https://github.com/ghackenberg/salabim-grid-plant-3D
- `markus-senger/discrete-event-simulation-salabim-unity` — 8★, salabim sim + Unity 2D layout planner (conveyor/carriers). https://github.com/markus-senger/discrete-event-simulation-salabim-unity
- `Nerozud/FTS_simpel` — 21★, Plant Simulation as RL environment via Python. https://github.com/Nerozud/FTS_simpel
- `juanhorgan/guitar_factory` — 29★ (cached), SimPy furniture-like job shop tutorial. https://github.com/juanhorgan/guitar_factory

**Browser 3D twins**
- `game4automation/realvirtual-WEB` — 152★, TS/Three.js industrial 3D-HMI, created 2026-03, very active. https://github.com/game4automation/realvirtual-WEB
- `hawk86104/three-vue-tres` — 2,439★, Apache-2.0, Chinese low-code digital-twin framework (Three.js/tres.js, WebGPU). https://github.com/hawk86104/three-vue-tres
- `nikonikoCW/Meteor3DEditor` — 71★, Three.js+Vue3 IoT twin editor. https://github.com/nikonikoCW/Meteor3DEditor
- `adizanni/floor3d-card` — 611★, Home-Assistant 3D twin (pattern for binding live state to meshes). https://github.com/adizanni/floor3d-card
- `tolgayanasik/3d-factory-in-three.js` — 0★, created 2026-09-25 (Claude-generated branch name), Excel-driven factory flow demo; small but on-topic. https://github.com/tolgayanasik/3d-factory-in-three.js
- `jyax/3d-factory-digital-twin` — MSU capstone, WebGPU/Orillusion, "far from complete". https://github.com/jyax/3d-factory-digital-twin

**Unity/OPC UA**
- `OPCFoundation/UA-CloudMetaverse` — 13★; `OPCFoundation/UA-CloudDashboard` — 22★; `digitaltwinconsortium/UA-CloudTwin` — 32★ (DTDL adapter). https://github.com/OPCFoundation/UA-CloudDashboard
- `rparak/Unity3D_Robotics_Overview` — 52★ (B&R PLC ↔ Unity via OPC UA). https://github.com/rparak/Unity3D_Robotics_Overview
- `Xudarker/DigitalTwinFactory` — 33★, Unity 卫星车间 twin (Chinese). https://github.com/Xudarker/DigitalTwinFactory
- `rohithrvarun-vr/BeltTwinUnity` — 1★, 2026-09, TwinCAT→OPC UA→Node-RED→MQTT→Unity pipeline. https://github.com/rohithrvarun-vr/BeltTwinUnity

**Omniverse / OpenUSD**
- `NVIDIA-Omniverse/kit-app-template` 1,110★; `web-viewer-sample` 149★; `iot-samples` 85★ (2024); `usd-exchange` 89★; `usd-exchange-samples` 31★; `aif-pipeline-samples` 46★ (CAD→SimReady USD ingestion, MIT, pushed 2026-09-08); `kit-cae` 64★; `ovrtx` 228★ (sensor sim lib). https://github.com/orgs/NVIDIA-Omniverse/repositories
- `NVIDIA-Omniverse-blueprints/omniverse-dsx-blueprint-for-ai-factories` 134★. No official NVIDIA "furniture/warehouse USD sample scene" repo exists; warehouse assets come via SimReady packs inside Isaac Sim.
- `isaac-sim/IsaacSim` 4,240★.

**Papers (furniture DES)**
- Kanduč & Rodič 2015, Slovenian furniture factory layout optimisation with automated DES model building (10k products, 30k subprocesses). https://hrcak.srce.hr/clanak/204318
- Bambura et al. 2020, BioResources — Tecnomatix Plant Simulation of a furniture plant (material flow, productivity, workload). (link above)
- Pham et al., AnyLogic furniture plant optimisation. (link above)
- WSC 2000 furniture rough-mill modelling. https://informs-sim.org/wsc00papers/183.PDF

---

## 6. Recommended stack and phased plan

### 6.1 Core recommendation
**"Python-DES + Blender-authored USD/glTF + React-Three-Fiber web twin + MQTT/Node-RED edge", with Omniverse as an optional photoreal/robotics export.**

Reasoning:
1. The team's strengths are web/Python/AI. Three.js/R3F and salabim/SimPy are zero-cost, hackable, and deployable to the factory's tablets without GPUs.
2. Commercial DES tools cost USD 6k–19k/seat/yr and their free tiers forbid commercial use; Omniverse is now free but demands RTX hardware and Kit expertise and still has no DES.
3. Authoring the scene in **OpenUSD** (via Blender USD export or `usd-exchange` Python) keeps the door open to Omniverse/Isaac Sim (AMR forklifts, photoreal sales renders) and to Siemens/AnyLogic connectors, while **glTF** serves the browser.
4. A furniture plant (panel saw → edgebander → CNC drilling → sanding/finishing → assembly → packing; solid-wood branch: kiln → planer/moulder → CNC → sanding → finishing) is a classic job-shop DES. Its bottleneck questions (edgebander utilisation, WIP between saw and CNC, finishing-line batching, forklift contention) are answered well by salabim/SimPy with ~500 lines of code.

Concrete components:
- **Capture**: iPhone/iPad LiDAR + Polycam (free tier / Pro ~USD 12/mo) or Matterport for the hall; tape-measure + photos for machine footprints; export OBJ/glTF → Blender. https://aecmag.com/technology/polycam-for-aec/
- **Scene**: Blender 4.x: clean mesh, place machine blocks (low-poly placeholders first), name prims per ISO 23247 OMEs, export `.usd` + `.glb`. Keep a `layout.json` (machine id, position, footprint, process params) as the single source of truth that generates both the USD stage and the sim model.
- **Simulation**: salabim (first choice — animation for free, Python-native) or SimPy + FactorySimPy. Run headless on FastAPI; stream event log (entity id, machine, t_in, t_out, position) over WebSocket.
- **Web twin**: React + R3F + drei; glTF scene; instanced meshes for panels/pallets; worker/forklift paths as splines driven by sim events or live tags; Grafana panels embedded for KPIs; Zustand store fed by MQTT-over-WebSocket.
- **Data**: Mosquitto → Node-RED (Modbus/OPC UA/asyncua) → TimescaleDB (or InfluxDB 3 Core) → Grafana; Python collector with `asyncua` for OPC UA machines; ESP32 CT/vibration nodes for legacy machines; operator tablet form for job events.
- **Twin model layer** (optional): Eclipse Ditto for current state, or BaSyx AAS submodels per machine if the client cares about standards/grants.

### 6.2 Phased plan
**Week 1 — Capture (현장 캡처).** Walk the plant: LiDAR scan, machine list with cycle times, changeover times, batch sizes, shift pattern, routing per product family (panel vs solid wood), buffer locations, forklift routes; pull 3 months of ERP/production data. Deliverable: `layout.json`, routing table, a cleaned Blender scene, and a Grafana board of historical output.

**Weeks 2–3 — Static twin (정적 트윈).** R3F viewer loading the glTF hall with clickable machines (info cards from `layout.json`), USD export of the same scene, basic path drawings for forklifts/workers. Validate scale with a few measured distances. Deliverable: shareable URL the plant manager can open on a tablet.

**Weeks 4–6 — Simulation (시뮬레이션).** salabim model of current state; calibrate against the 3-month data (throughput ±10 %); animate in the web twin; run scenarios: add second edgebander, re-sequence CNC batches, move buffer, add forklift; bottleneck report (utilisation, queue lengths, WIP, lead time). Optionally cross-check one scenario in FlexSim Express / Plant Simulation Student (non-commercial, validation only).

**Later — Live IoT (실시간 연동).** Pi 5 edge box + Mosquitto + Node-RED; 3–5 ESP32 CT clamps on bottleneck machines; operator andon tablet; map tags to twin state (Ditto or in-house); run the DES "in the loop" to forecast end-of-shift output. Then, if a customer wants photoreal or AMR testing: import the USD into Omniverse USD Composer template / Isaac Sim on one RTX 16 GB box.

### 6.3 Fallbacks
- If salabim's 3D animation is too limiting → keep salabim for logic, render in R3F only (already planned) or JaamSim for a desktop 3D viewer.
- If the web viewer needs heavy scanned geometry → Babylon.js 8 with Gaussian splats or a Pixel-Streamed Unity/UE5 build (free under USD 1M revenue) — accept GPU server cost.
- If the client demands a brand-name simulator → FlexSim (fastest, ~USD 6k/yr) or Plant Simulation (if Siemens ecosystem/grant requires); drive them from your `layout.json`.
- If the client demands "NVIDIA Omniverse" by name → kit-app-template USD Viewer + web-viewer-sample streaming your USD stage, with iot-samples pattern for live tags; budget one RTX 4080/5080-class workstation and 2–3 weeks of Kit learning.
- Korean funding angle: 2026 스마트공장 지원 (e.g., 경기도형: 최대 5천만 원, 총사업비 70 % 이내) deadlines have passed; prepare for 2027 공고 via 스마트공장 사업관리시스템 and local 테크노파크. https://www.dailian.co.kr/news/view/1611213/

---

## 7. Things I could not verify (search budget exhausted)
NVIDIA's own license-page text for the May 2026 change; Isaac Sim 6.0's exact VRAM table; whether Siemens Digital Twin Composer shipped on Xcelerator Marketplace; Simio/Aegis acquisition; TimescaleDB 2025 license wording; Node-RED 5 release; HOMAG tapio / Biesse SOPHIA / SCM Maestro Connect API availability for edgebander/CNC data; current Unity Industry price; Blender 4.5/5.0 USD improvements; FlexSim Express exact limits; AnyLogic/Visual Components Omniverse connector details. Star counts marked "cached" (guitar_factory) come from search snippets, not the API.