# Factory capture → semantic 3D → browser digital twin → OpenUSD: research report

Date: 2026-10-10. Scope: a small web/Python/AI team, iPhone LiDAR + 360 photos + video + tape measurements of a furniture factory. Note: the web-search budget ran out near the end, so a handful of items (marked **[unverified]**) rest on one secondary source or on prior knowledge; everything else has a URL.

---

## 0. Executive recommendation (read this first)

1. **Do not try to auto-segment a factory point cloud into clean machine objects.** The open-source 3D instance-segmentation stack (Mask3D / OpenMask3D / PTv3) is trained on ScanNet/S3DIS-style rooms (chairs, tables, cabinets). Nothing in the 2025–26 literature I found targets industrial plant scans, and iPhone LiDAR in a 200 m² space already drifts 10–50 cm. Use the scan for **floor plane + wall footprint + machine footprints/heights**, not for object meshes.
2. **Build the twin as a 2.5D parametric model**: floor polygon + zones as JSON/SVG, machines as L×W×H boxes (optionally with a photo-textured front face or a generated low-poly stand-in), conveyors/racks/pallets as parametric primitives, paths as polylines. This is what FlexSim/AnyLogic twins effectively are under the hood, and it is what your simulation needs anyway (stations, positions, path graph).
3. **Add realism with a Gaussian splat backdrop** captured by Scaniverse (exports `.spz` directly), aligned once in SuperSplat, rendered with **Spark** (three.js, MIT) or the native three.js r186 splat renderer. Keep the splat as a non-interactive, toggleable layer.
4. **Viewer: three.js via React Three Fiber v9 + drei + Zustand**, instanced entities, a floor `DataTexture` heatmap, `Line2`/`LineSegments` spaghetti paths, HTML labels. Keep the sim log replay engine as plain TypeScript outside React.
5. **Sim ↔ viewer contract: a JSONL event log with absolute positions** (not just station IDs), replayed with a binary-search cursor and linear interpolation. Emit it from SimPy/salabim; don't try to use salabim's own 3D.
6. **OpenUSD**: author the stage with `usd-core 26.8` from Python as a thin composition (one `.usda` with references to per-asset `.usdc`), convert GLB assets with `guc` (Apache-2.0, KHR_materials_variants supported) or Blender. Omniverse ingests USD natively and can also import GLB itself via `omni.kit.asset_converter`. Omniverse itself appears to have become free for production in 2026 **[one secondary source + forum contradiction; verify]**.

---

## 1. Scan → semantic model pipeline

### 1.1 Realistic quality expectations for iPhone LiDAR in a factory

- Room-scale study (iPhone 13 Pro, ~200 m², two rooms): local RMSE **10 cm for Polycam**, 14 cm SiteScape, 17 cm 3D Scanner App, **56 cm Scaniverse**; drift accumulated and loop closure often failed. https://www.mdpi.com/2673-7418/3/4/30 (same paper on ResearchGate: https://www.researchgate.net/publication/376427651)
- Apple LiDAR vs TLS indoor: dynamic scanning ~16 cm RMS; ±1–2 cm for features ≤4 m, degrading to ±30 cm for features >4 m; static capture ~2.8 cm. https://www.tandfonline.com/doi/full/10.1080/16874048.2024.2408839
- 2026 Springer paper on free iPhone LiDAR apps: cumulative loop-closure drift is the dominant failure in corridors. https://link.springer.com/article/10.1007/s41651-026-00288-x
- Large-scale consumer-device scanning empirical study: https://arxiv.org/pdf/2506.14771

**Implication:** a furniture factory (long sightlines, 30–80 m spans, repetitive racking) will not produce a single consistent cloud from one phone walk. Practical mitigations: scan in overlapping chunks per bay, register each chunk to **tape-measured control points** (column grid, wall corners) in CloudCompare, and treat the cloud as a *reference image* you trace over, not as ground truth. Expect ±5–15 cm after registration to control points; good enough for layout and clearances, not for CAD.

### 1.2 Cleanup and registration (open-source, with versions)

- **CloudCompare** 2.13.x stable; **2.14 beta** (16 Aug 2026) is current on the downloads page. Use for: SOR/noise filter, subsampling, ICP/point-pair registration to control points, cross-sections, RANSAC shape detection plugin (qRANSAC_SD) for planes. https://www.cloudcompare.org/release/ · changelog https://github.com/CloudCompare/CloudCompare/blob/master/CHANGELOG.md
- **Open3D v0.19** (latest GitHub release; Python 3.11 support): `pcd.segment_plane(distance_threshold, ransac_n=3, num_iterations)` for floor; `remove_statistical_outlier`; `voxel_down_sample`; DBSCAN `cluster_dbscan` for separating blobs after removing floor/walls. https://github.com/isl-org/Open3D/releases. (A scan-to-BIM interface for Open3D is only a feature request: https://github.com/isl-org/Open3D/issues/7477.)
- **PDAL** for large-cloud ETL (filters.smrf for ground, filters.outlier, filters.voxeldownsize, LAS/LAZ/COPC I/O). I could not confirm the current release number in this session **[unverified]**; https://pdal.io.
- **MeshLab / PyMeshLab 2025.07** (released 9 Sep 2025) for mesh decimation, hole filling, Poisson reconstruction if you need a mesh at all. https://www.meshlab.net/

Suggested minimal Python flow (Open3D):
```python
import open3d as o3d, numpy as np
pcd = o3d.io.read_point_cloud("bay1.ply").voxel_down_sample(0.02)
pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
plane, inl = pcd.segment_plane(0.03, 3, 2000)          # floor
floor = pcd.select_by_index(inl); rest = pcd.select_by_index(inl, invert=True)
# rotate so floor normal = +Z, then slice z in [1.2,1.6] m for walls/machines footprint
labels = np.array(rest.cluster_dbscan(eps=0.15, min_points=50))   # blobs → machine candidates
```
Each DBSCAN blob gives an oriented bounding box (`get_oriented_bounding_box()`) = L×W×H + yaw; that is exactly the parametric machine box the twin needs. Expect to hand-fix merges/splits.

### 1.3 Floor plane, walls, floor plan

- **Cloud2BIM** (Python, open source, CTU Prague): zoning, slab + wall segmentation on a horizontal slice at 90–100 % of storey height, opening detection, non-orthogonal walls, IFC export, "no RANSAC", claimed up to 7× faster than competitors. Repo: https://github.com/VaclavNezerka/Cloud2BIM (144 stars, updated Oct 2026). Paper: https://arxiv.org/abs/2503.11498 (Automation in Construction). Best free scan-to-BIM starting point.
- **pystruct3d / BIMStruct3D** (RANSAC-variant wall extraction + DBSCAN): https://arxiv.org/html/2604.24311
- **FloorSG** iterative-RANSAC floor-plan vectorization: paper https://www.sciencedirect.com/science/article/abs/pii/S2352710224008064, code github.com/wangxuzhecode/FloorSG **[URL from the paper; not opened]**.
- Commercial reference point (not free): ODA Scan-to-BIM SDK https://www.opendesign.com/products/scan-to-bim.

**Apple RoomPlan**: single-room only; Apple engineers recommend <10 min scans and rooms under ~30 × 30 ft (10 × 10 m); `exceedSceneSizeLimit` errors are common; 2026 forum reports of jittery/inaccurate results. Not suitable for a factory hall. https://developer.apple.com/forums/thread/744976 · https://developer.apple.com/forums/thread/707863

**Polycam floor plans**: exports layered **DXF** (walls/openings/fixtures/labels on layers), SVG, PDF/PNG, but floor-plan export requires a paid tier (Business/Enterprise ~$400/user/yr per their blog). https://learn.poly.cam/hc/en-us/articles/27756102599572-What-File-Types-Can-Polycam-Export · https://poly.cam/floor-plans. Also RoomPlan-based, so the same single-room assumptions apply; for a hall, use it per bay and stitch in CAD, or skip it and trace your own polygon in a web editor over a top-down raster of the cloud.

### 1.4 Instance segmentation of large objects

3D-native options (all MIT unless noted, all ScanNet-centric):
- **Mask3D** (MIT; Python 3.10, CUDA 11.3, torch 1.12, MinkowskiEngine pinned commit, Detectron2) — brittle environment, 2022-era deps. https://github.com/JonasSchult/Mask3D
- **OpenMask3D** (MIT; needs point cloud + RGB-D frames + poses + intrinsics; Mask3D-style mask module + SAM ViT-H + CLIP; open-vocabulary labelling, e.g. "CNC router", "pallet"). ScanNet200 AP ≈ 15. https://github.com/OpenMask3D/openmask3d · https://arxiv.org/pdf/2306.13631
- **Open3DIS** (AP 23.7) https://arxiv.org/html/2312.10671v1 and **Any3DIS** (AP 25.8, SAM2 mask tracking) https://arxiv.org/html/2411.16183v1 — stronger, same domain limits.
- **Pointcept / Point Transformer V3** (MIT): PTv3 (CVPR'24), **Sonata** (CVPR'25, self-supervised PTv3, weights on HF `facebook/sonata`), **Concerto** (NeurIPS'25), **Utonia** (ICML'26, cross-domain encoder). Instance seg only via PointGroup configs. https://github.com/Pointcept/Pointcept · https://github.com/facebookresearch/sonata · https://github.com/Pointcept/Utonia. Fine-tuning Sonata/Utonia on ~20–50 hand-labelled factory scans is the most credible route *if* you later want automatic semantics; not for a first version.
- Survey of 3D foundation models: https://arxiv.org/pdf/2501.18594

2D-first route (recommended if you want any automation): run **SAM 2** on perspective crops of the 360 images (or on video frames), label masks with a VLM, then lift to 3D via depth or by ray-casting onto the registered cloud/mesh. For 360 imagery specifically: **Depth Any Panoramas** foundation model https://arxiv.org/pdf/2512.16913 and **PanoSAMic** (SAM encoder adapted to equirectangular, 2026) https://arxiv.org/pdf/2601.07447. The NeurIPS'24 recipe of cube-mapping the 360 into perspective patches and running Depth Anything per patch is a safe fallback: https://proceedings.neurips.cc/paper_files/paper/2024/file/e6c2e85db1f1039177c4495ccd399ac4-Paper-Conference.pdf

**Meta SAM 3D Objects** (Nov 2025; "SAM License", not MIT): single image → posed 3D object(s) with layout, output is Gaussian splats via `output["gs"].save_ply()`; multi-object scene demo exists. Useful for quick machine stand-ins from one photo, but output is splats not meshes. https://github.com/facebookresearch/sam-3d-objects · https://arxiv.org/pdf/2511.16624 · https://about.fb.com/news/2025/11/new-sam-models-detect-objects-create-3d-reconstructions/

**Bottom line for §1:** cloud → floor/walls/blob OBBs semi-automatically; object identity, IDs and attributes come from a human-in-the-loop table (machine_id, name, L×W×H, yaw, photos), not from a segmentation network.

---

## 2. Fast "good-enough" 2.5D twin + Gaussian-splat backdrop

### 2.1 Parametric layout schema (suggested)
```json
{ "units":"m", "origin":"SW column A1",
  "floor":{"polygon":[[0,0],[62,0],[62,28],[0,28]], "zones":[{"id":"Z-cut","name":"Cutting","polygon":[...],"color":"#..."}]},
  "walls":[{"id":"W1","line":[[0,0],[62,0]],"height":7.5,"thickness":0.3}],
  "machines":[{"id":"M-012","type":"panel_saw","name":"Holzma HPP 300","pos":[12.4,6.1,0],"yaw_deg":90,"size":[5.2,4.1,1.9],
               "model":"assets/panel_saw.glb","texture":"photos/M-012_front.jpg","ports":{"in":[0,-2.1],"out":[0,2.1]},"nameplate":{"kW":18.5,"V":400}}],
  "conveyors":[{"id":"C3","path":[[...]],"width":0.8,"height":0.9,"speed_mps":0.3}],
  "racks":[{"id":"R7","pos":[...],"size":[2.7,1.1,5.0],"bays":3,"levels":4}],
  "paths":{"nodes":[...],"edges":[...]} }
```
Box + yaw + photo-on-front-face reads surprisingly well in a twin and is what the DES needs. Generate GLB boxes in code (three.js `BoxGeometry`, or Blender `bpy` for the USD side).

### 2.2 Splat capture → file → browser

Capture/export:
- **Scaniverse** (Niantic): on-device splat training; exports **.ply and .spz** directly. https://dev.scaniverse.com/news/creating-splats-which-app-to-choose · https://www.3dgsviewers.com/learn/guide/scaniverse
- **Polycam**: exports `.ply`/`.splat` (sources conflict on free-tier limits; no SPZ mentioned). https://swyvl.io/blog/how-to-create-gaussian-splats/
- **Luma AI**: one 2026 source says Luma suspended splat processing and the mobile app no longer does 3DGS **[single source; verify]**. https://www.polyvia3d.com/guides/gaussian-splatting-tools-comparison
- Desktop alternative for higher quality from your 360/video: Postshot (Windows), or open-source gsplat/nerfstudio training from video frames (not researched further here).

Edit/align: **SuperSplat** (PlayCanvas, MIT; latest release v3.5.2, 5 Oct 2026). Has crop/selection, transform, **Orient tool (three-point grid alignment, snaps within 3° to an axis; v2.32)**, SPZ export (v2.29+), SOG/streamed SOG export via `splat-transform` CLI (v3.6.x), LOD required when publishing >40 M splats. https://github.com/playcanvas/supersplat/releases · https://developer.playcanvas.com/user-manual/supersplat/editor/ · https://radiancefields.com/playcanvas-adds-a-three-point-grid-alignment-tool-to-supersplat-2.32

Formats & sizes: `.ply` is the raw 3DGS format (~250 bytes/splat); **`.spz` is ~1/10 the size of `.ply`** (SuperSplat and three.js sources agree); `.ksplat` is mkkellogg's streaming format; `.sog` is PlayCanvas' self-organising-Gaussians image-bundle format with streamed LOD for very large scenes. Rule of thumb: a factory bay at 1–3 M splats ≈ 250–750 MB ply ≈ 25–75 MB spz. Keep the backdrop ≤ ~2 M splats for laptops.

Renderers:
- **Spark** (World Labs, MIT): `npm install @sparkjsdev/spark`; three.js ≥ r180 (the README's import map uses `three@0.180.0`); reads PLY/compressed PLY/SPZ/SPLAT/KSPLAT/SOG; `SplatMesh extends THREE.Object3D` so you position/rotate/scale it like any mesh and fuse it with mesh geometry with correct depth; 2.0 added LOD with a splat budget (~500 k on phones, ~2.5 M desktop) and `extSplats: true` float32 centres for large coordinates; parent the `SparkRenderer` to the camera for large scenes to avoid float16 quantisation. Current npm version reported as 2.3.1 (1 Oct 2026) **[from search summary; npm page returned 403]**. https://github.com/sparkjsdev/spark · https://sparkjs.dev/docs/system-design/ · https://sparkjs.dev/docs/new-features-2.0/
- **three.js r186 native** (released 24 Sep 2026): `GaussianSplat` mesh, `GaussianSplatPLYLoader`, `SPZLoader` (v4), `GLTFGaussianSplatLoaderExtension` (KHR_gaussian_splatting), TSL-based, WebGPU with WebGL fallback, GPU counting sort, frustum culling, raycasting. Targets object/room scale. https://github.com/mrdoob/three.js/releases/tag/r186 · https://ben3d.ca/blog/how-to-use-threejs-native-gaussian-splats
- **@mkkellogg/gaussian-splats-3d** (MIT): author states it is **no longer in active development and recommends Spark**; CPU sort, sub-optimal on mobile, needs COOP/COEP for SharedArrayBuffer. https://github.com/mkkellogg/GaussianSplats3D
- **Babylon.js** (v8/v9): unified loader for `.splat/.ply/.spz/.sog`, streamed SOG bundles, shadows on splats in v9. https://doc.babylonjs.com/features/featuresDeepDive/mesh/gaussianSplatting · https://radiancefields.com/babylon.js-v9.0-3dgs-gets-shadows-sogs-and-triangle-splatting-support-announced
- **PlayCanvas engine**: first-class splats + SOG; gsplat.js is older and not recommended now. Viewer comparison: https://swyvl.io/blog/best-gaussian-splat-viewers/

Aligning splat with simulation coordinates (practical recipe):
1. In SuperSplat: Orient (floor → grid), crop to the hall, export `.spz`.
2. Pick 3+ landmarks visible in both splat and layout (column bases). Compute a similarity transform (Umeyama / Kabsch with scale) in Python; store `{position, quaternion, scale}` in the layout JSON.
3. Apply to `SplatMesh` in three.js (`splat.position.set(...)`, `quaternion`, `scale`). Keep the layout JSON (not the splat) as the authoritative metric frame.
4. Render the splat with `depthWrite` on so machine boxes occlude correctly; give it a toggle and an opacity slider.

---

## 3. Free assets and generated stand-ins

Free CC0/CC-BY libraries:
- **Kenney City Kit (Industrial)** — 40 CC0 assets, factory/warehouse-themed, GLB/OBJ/FBX. https://kenney.nl/assets/city-kit-industrial
- **Quaternius** — CC0 GLB/FBX packs (mostly characters/environments; useful for low-poly workers). https://gamefromscratch.com/quaternius-free-3d-assets/
- **Poly Haven** — CC0 HDRIs (use for lighting), textures (concrete floor, plywood, MDF), some models. https://polyhaven.com
- **Sketchfab** — filter *Downloadable + CC license*; >600 k CC models, >2 000 CC0. Search terms that work: "forklift", "pallet", "industrial shelving", "conveyor", "CNC router", "table saw"; dedicated panel saws/edge banders are rare, expect to box-model those. https://sketchfab.com/blogs/community/600000-free-3d-models-on-sketchfab. Note CC0/NC/ND models stay on Sketchfab and do not migrate to Fab.
- **BlenderKit** — ~48 k free assets, commercial use allowed; many free industrial props. https://www.cgchannel.com/tag/8k-free
- **Unity Asset Store free** — no specific factory pack verified in this session; search "industrial" with Free filter. Quixel's free warehouse pack (85 FBX assets) https://cgtricks.com/free-3d-model-warehouse-quixel/.
- **NVIDIA Omniverse packs** (USD): SimReady Warehouse Asset Pack (racks, step stands, shelving, ramps) https://developer.nvidia.com/omniverse/simready-assets; "Industrial" downloadable pack with 72 OpenUSD assets, ~1.8 GB, "free to use in your own work" https://docs.omniverse.nvidia.com/usd/latest/usd_content_samples/downloadable_packs.html; PhysicalAI-SimReady-Materials (open source MaterialX USD materials) https://github.com/NVIDIA-Omniverse/PhysicalAI-SimReady-Materials. These are USD-only; for the web convert via Blender (USD import → glTF export) **[the docs host was unreachable from this sandbox; pack details come from search snippets]**.
- Curated index of CC0 sources with loader: https://github.com/hakyong-tae/game-asset-library · https://app.cinevva.com/guides/free-3d-model-sites

Image-to-3D for machine stand-ins (photo → textured mesh):
- **TRELLIS / TRELLIS.2** (Microsoft, MIT; TRELLIS.2 Dec 2025, 4 B params, GLB/OBJ/PLY with PBR). Best open license; chosen over Hunyuan/TripoSG by DeepJEB++ for that reason. https://app.cinevva.com/guides/ai-3d-model-generators · https://arxiv.org/pdf/2606.12994
- **Hunyuan3D 2.1** (June 2025, open weights, community license excluding EU/UK/South Korea). Hunyuan3D **3.0** was announced Sept 2025 with open source "planned"; I found **no confirmed open-weights 3.0 release** as of Oct 2026 (2026 "Hunyuan 3.0" news is the LLM). https://www.meshy.ai/compare/meshy-vs-hunyuan3d · https://www.notebookcheck.net/Tencent-s-new-Hunyuan-3D-3-0-brings-realistic-AI-model-generation-to-developers-and-creators.1116964.0.html
- **SAM 3D Objects** (see §1.4) — splats not meshes.
- Hosted: **Tripo** (free 200–300 credits/mo, non-commercial; Pro ≈ $19.9/mo, 3 000 credits), **Meshy** (free 100 credits/mo, CC-BY output; Pro $20/mo, 1 000 credits; ~20–30 credits per image-to-3D), **Rodin**. https://picoberry.ai/ai-3d-generator-pricing-comparison · https://www.neural4d.com/features/neural4d-vs-tripo-vs-meshy-vs-rodin
- Caveat from papers: generators are weak on lettering/fine machinery detail; use them for silhouette + colour, then scale the result to the measured L×W×H (non-uniform scale is fine for a stand-in). https://arxiv.org/pdf/2605.26137

Post-process every GLB with **gltf-transform** (`npx @gltf-transform/cli optimize in.glb out.glb --texture-compress webp`, `dedup`, `instance`, `draco`/`meshopt`).

---

## 4. Browser twin architecture

### 4.1 Engine choice

| Need | three.js / R3F | Babylon.js | PlayCanvas |
|---|---|---|---|
| GLB | GLTFLoader + Draco/Meshopt/KTX2 | excellent | excellent |
| Splats | Spark or native r186 | native (.spz/.sog, shadows) | native, SOG/LOD, SuperSplat |
| Instancing | InstancedMesh / BatchedMesh / drei `<Instances>` | thin instances | hardware instancing |
| React integration | R3F v9 (React 19) + drei; "no overhead" claim from docs | manual | manual / editor-centric |
| Ecosystem for dashboards (charts, UI) | best (React) | good | editor-first |

**Recommendation: three.js through React Three Fiber v9 (React 19) + @react-three/drei + Zustand**, three.js ≥ r180 (for Spark) or r186 (native splats). Reasoning: largest ecosystem, splat support now both native and via Spark, trivial to combine with React dashboards (Recharts/ECharts), and almost every open-source warehouse-twin example is R3F. Babylon.js is the credible alternative if you prefer a batteries-included engine and shadows on splats; PlayCanvas if you want a visual editor. R3F migration guide: https://r3f.docs.pmnd.rs/tutorials/v9-migration-guide. Keep the replay loop and entity state in a flat typed-array store updated in `useFrame`, not in React state.

### 4.2 Techniques
- **Entities (workers, carts, panels)**: one `InstancedMesh` per entity type (single geometry) or `BatchedMesh` for many geometries; InstancedMesh2 adds per-instance visibility/culling/LOD. Thousands of moving instances in one draw call is routine (8 k entities → 1 draw call, ~0.5 ms render CPU in one benchmark). https://discourse.threejs.org/t/how-to-choose-between-instancedmesh-and-batchedmesh/81221 · https://discourse.threejs.org/t/significant-performance-drop-and-high-cpu-usage-with-batchedmesh/67324 (BatchedMesh regressions exist; profile).
- **Static machines from GLB with EXT_mesh_gpu_instancing**: `gltf-transform dedup && instance` on export; three.js GLTFLoader creates `InstancedMesh` automatically (caveat: multi-geometry instances had a bug thread). https://gltf-transform.dev/modules/extensions/classes/EXTMeshGPUInstancing · https://discourse.threejs.org/t/load-gltf-models-as-instanced-mesh/57183
- **KHR_materials_variants** (e.g. machine "idle/busy/blocked" colour variants baked in the GLB): guc supports it fully for USD; three.js has an official variants example with a helper to select variants **[from prior knowledge; not re-verified this session]**.
- **Heatmap overlay**: a floor-sized `PlaneGeometry` with a `DataTexture` (Float32 or RGBA8 grid, e.g. 0.25 m cells) updated from an occupancy/dwell accumulator; colour ramp in a small shader or a canvas-texture. Alternative 2D: deck.gl `OrthographicView` + `HeatmapLayer`/`PathLayer` in metres as a synced top-down panel (OrthographicView is explicitly for non-geo XY data; HeatmapLayer in ortho **[not verified]**). https://deck.gl/docs/api-reference/core/orthographic-view
- **Spaghetti paths**: `LineSegments` with per-vertex colours, or `Line2`/`LineMaterial` for width; one geometry per entity class, rebuilt when the time window changes.
- **Labels/HUD**: drei `<Html>` for a few labels, `<Text>` (SDF) or sprite atlas for many; React overlay for KPIs.
- **Camera presets**: store `{position,target}` per preset; animate with `camera-controls` (drei `<CameraControls>`), support orthographic top view.
- **Laptop performance budget**: ≤ 300 draw calls, ≤ 2 M splats, ≤ 1.5 M triangles, textures KTX2/WebP, `renderer.setPixelRatio(min(dpr,1.5))`.

### 4.3 Open-source examples
- **WareTwin** (MIT, 2026): R3F + FastAPI, deterministic 100 ms tick engine shared bit-for-bit in Python and TS, WebSocket `FULL` + per-tick `PATCH` diffs (~12 kB/s), map/traffic/heatmap modes, SQLite audit log with JSON/CSV export, what-if diffing. Closest reference architecture. https://github.com/WayneChou-bot/WareTwin
- **warehouse-twin** (R3F mock, camera presets, URL state): https://github.com/johanvessen/warehouse-twin
- **austin410203/warehouse** (Next.js 15, pause/1×/4×/8× time controls, store-driven scene): https://github.com/austin410203/warehouse
- **Rajkishore08/warehouse-digital-twin** (R3F + Zustand, 8 camera presets): https://github.com/Rajkishore08/warehouse-digital-twin
- **degital-twin-3d** (R3F smart-warehouse, Chinese): https://github.com/anyone-yuren/degital-twin-3d
- **Twin-Fabric/TwinForge** (3D infra twin): https://github.com/hussain-humaidan/Twin-Fabric
- I did not find Siemens/Bosch official twin demos on GitHub in this session **[gap]**.

---

## 5. Simulation ↔ viewer contract

### 5.1 Event log format (recommended)
JSON Lines, one event per line, **absolute metres in the layout frame**, plus a static header:
```jsonl
{"type":"meta","units":"m","t0":"2026-10-10T06:00:00Z","layout":"layout_v3.json","seed":42}
{"t":0.0,"e":"worker:7","ev":"spawn","at":[3.2,4.0],"state":"idle"}
{"t":12.5,"e":"cart:2","ev":"move","from":[12.4,8.2],"to":[30.1,8.2],"dur":18.0,"path":[[12.4,8.2],[20,8.2],[30.1,8.2]],"carry":["panel:881"]}
{"t":30.5,"e":"panel:881","ev":"enter","station":"M-012","state":"queued"}
{"t":41.0,"e":"panel:881","ev":"state","station":"M-012","state":"processing","until":95.0}
{"t":41.0,"e":"M-012","ev":"state","state":"busy","util":0.71}
{"t":95.0,"e":"panel:881","ev":"exit","station":"M-012"}
```
Rules: `move` carries `dur` and optional `path` so the viewer interpolates without knowing the sim; `state` events for stations drive colour; `until` lets the viewer draw progress bars; sort by `t`; keep IDs stable (`type:n`). Derived data (dwell heatmap, utilisation per station, queue-length time series, bottleneck ranking = max of queue × wait) can be computed once in Python and shipped as a second file, or computed in a web worker from the log.

Replay engine: parse into typed arrays per entity (`t[]`, `x[]`, `y[]`, `state[]`); a cursor with binary search on `t`; `simTime += dt * speed` in `useFrame`; position = lerp between the bracketing `move` keyframes (or along `path` by arc-length); scrubbing = set `simTime`, re-seek all cursors. For 100 k+ events, chunk the file (one JSONL per 10 min) and lazy-load. WareTwin's `FULL`+`PATCH` WebSocket is the live-mode equivalent.

### 5.2 Emitting from Python
- **SimPy 4**: wrap `env.process` steps in a small `log(ev, **kw)` helper writing JSONL; positions come from your layout JSON + path graph (NetworkX shortest path). Prior art: **SimPlay** (SimPy → JSON EventQueue → `simplay-web` Jupyter viewer; good reference for the schema) https://pypi.org/project/simplay/1.0.0/ · https://github.com/team-simplay/SimPlay/blob/main/docs/source/quickstart.rst; HSMA Plotly-based `simpy_visualisation` https://github.com/hsma-programme/simpy_visualisation; OST thesis that prototyped SimPy animation in three.js/D3/Pixi https://eprints.ost.ch/id/eprint/995/.
- **salabim 26.0.8** (MIT, PyPI 24 Jun 2026): built-in 2D/3D animation (PyOpenGL; `.obj` models via pywavefront + pyglet, version-sensitive) and video recording via OpenCV. **No export of the 3D scene or an event trace for another engine** that I could find; its `trace=True` prints a text trace. Use salabim for modelling if you like its API, but write your own JSONL emitter from component methods. https://pypi.org/project/salabim/ · https://salabim.org/manual/Overview.html · https://github.com/salabim/salabim
- **JaamSim** (Java, Apache-2.0): best open-source built-in 3D (JOGL), drag-and-drop objects, but model logic lives in its own config language; trace/export formats not confirmed here **[gap]**. https://jaamsim.com/ · https://github.com/jaamsim/jaamsim
- **AnyLogic**: 3D presentation is bound per agent (shapes with Z-height; Collada `.dae` import); its **Omniverse connector** streams agent/shape state changes at runtime to a USD scene and can emit a base USD layout "by no means a finished solution". This confirms the pattern: the sim streams state deltas; the renderer owns assets. https://anylogic.help/anylogic/3d/omniverse.html · https://anylogic.help/9/anylogic/presentation/index-3d.html
- **FlexSim**: 3D is the core; the same scene is editor, model and animation; objects are 3D nodes with runtime-editable properties (WSC 2011 paper) https://www.informs-sim.org/wsc11papers/251.pdf. The classic "convert simulation results into animation events" framing: https://koreascience.kr/article/JAKO200420828926124.pdf

---

## 6. OpenUSD authoring from Python and the Omniverse path

- **`pip install usd-core`** → `usd-core 26.8` (released 20 Jul 2026; Python 3.9–3.14; macOS universal2, Linux glibc ≥ 2.27 x86-64, Windows x64; core libs without imaging/usdview). Check: `python -c "from pxr import Usd; print(Usd.GetVersion())"`. https://pypi.org/project/usd-core/ · https://docs.nvidia.com/learn-openusd/latest/usdview-install-instructions.html

Composition sketch (factory stage referencing per-asset files; metres, Z-up to match Omniverse/Isaac defaults):
```python
from pxr import Usd, UsdGeom, Sdf, Gf
stage = Usd.Stage.CreateNew("factory.usda")
UsdGeom.SetStageMetersPerUnit(stage, 1.0); UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
world = UsdGeom.Xform.Define(stage, "/World"); stage.SetDefaultPrim(world.GetPrim())
UsdGeom.Xform.Define(stage, "/World/Floor").GetPrim().GetReferences().AddReference("assets/floor.usdc")
for m in layout["machines"]:
    x = UsdGeom.Xform.Define(stage, f"/World/Machines/{m['id']}")
    x.GetPrim().GetPayloads().AddPayload(f"assets/{m['type']}.usdc")     # payload = lazy-load
    api = UsdGeom.XformCommonAPI(x)
    api.SetTranslate(Gf.Vec3d(*m["pos"])); api.SetRotate(Gf.Vec3f(0,0,m["yaw_deg"]))
    x.GetPrim().CreateAttribute("factory:machineId", Sdf.ValueTypeNames.String).Set(m["id"])
    x.GetPrim().CreateAttribute("factory:powerKW", Sdf.ValueTypeNames.Float).Set(m["nameplate"]["kW"])
stage.GetRootLayer().Save()
```
Tutorials: https://openusd.org/release/tut_referencing_layers.html · https://docs.nvidia.com/learn-openusd/latest/composition-basics/references.html · https://docs.nvidia.com/learn-openusd/latest/creating-composition-arcs/references-payloads/working-with-payloads.html · Xform blueprint https://docs.nvidia.com/learn-openusd/latest/scene-description-blueprints/xform.html. Put per-station IDs/attributes in a custom namespace (`factory:`) or write a tiny codeless schema later; keep zones as `UsdGeom.BasisCurves`/`Mesh` with `primvars`. Time-sampled transforms (`xformOp:translate.timeSamples`) can carry a replay directly into usdview/Omniverse.

- **GLB → USD**: **guc 0.5** (Apache-2.0; glTF/GLB → usda/usdc/usdz with MaterialX; all glTF features except animation/skinning; KHR_materials_variants and KHR_texture_transform complete; KHR_gaussian_splatting in progress; requires USD ≥ 24.08 with MaterialX, tested v25.08/25.11; build with CMake). https://github.com/pablode/guc. Google `usd_from_gltf` is archived (Jun 2024) https://github.com/google/usd_from_gltf; Apple `usdzconvert` (usdpython) is macOS-only and effectively unmaintained **[prior knowledge]**; Adobe USD-Fileformat-plugins (Apache-2.0) load glTF as a USD file format plugin https://forum.aousd.org/t/usdz-gltf-usdz-pipeline/1352. Khronos interoperability survey: https://members.khronos.org/document/dl/33075
- **Blender 5.x** imports/exports USD natively (Blender 5.2 LTS manual https://docs.blender.org/manual/en/latest/files/import_export/index.html). Known pitfall: `metersPerUnit` handling — assets can land 100× too small in Omniverse; set scene units and check `metersPerUnit` on export. https://projects.blender.org/blender/blender/issues/100448 · https://forums.developer.nvidia.com/t/export-to-usd-scale-units-from-blender-to-omniverse/201112
- **Omniverse ingestion**: USD is native. Non-USD assets go through `omni.kit.asset_converter` (ASSIMP backend: OBJ/FBX/glTF; Python `create_converter_task(..., AssetConverterContext)`; does not create instanceable prims). https://docs.omniverse.nvidia.com/extensions/latest/ext_asset-importer.html · https://docs.omniverse.nvidia.com/extensions/latest/ext_asset-converter.html · https://isaac-sim.github.io/IsaacLab/main/source/how-to/import_new_asset.html. Omniverse licensing: StorageReview reports the docs now state "As of May 2026, Omniverse is freely available for both development and production use" (previously NVIDIA AI Enterprise, $4,500/GPU/yr); an NVIDIA forum reply disputes awareness of the change and SaaS cases remain unclear. **Verify against the current license text before relying on it.** https://www.storagereview.com/news/nvidia-quietly-makes-omniverse-free-for-production-use · https://forums.developer.nvidia.com/t/can-we-use-nvidia-omniverse-sdk-kit-and-nucleus-server-as-saas-in-cloud-for-our-commercial-project/374101
- glTF extensions to standardise on in your web assets: `KHR_materials_*` (clearcoat/transmission rarely needed; `KHR_materials_emissive_strength` for status lights), `KHR_texture_transform`, `KHR_texture_basisu` (KTX2), `EXT_meshopt_compression` or `KHR_draco_mesh_compression`, `EXT_mesh_gpu_instancing`, `KHR_materials_variants`. guc covers all but gpu_instancing (not listed) — flatten instancing before USD conversion or write instances as USD `instanceable` references yourself.

---

## 7. Generative / agentic shortcuts

- **Nameplate extraction**: photograph each nameplate straight-on; run a VLM with a strict JSON schema (`manufacturer, model, serial, year, kW, V, A, Hz, phase, air_bar`) and ask for per-field confidence + a "verbatim" transcription. Use **PaddleOCR 3.0** (Apache-2.0: PP-OCRv5 recognition, PP-StructureV3, PP-ChatOCRv4 key-information extraction) or **PaddleOCR-VL** (0.9 B VLM, runs on modest GPUs; a vendor benchmark shows it ahead of GPT-4o/Gemini 2.5 Pro on document parsing) as a second opinion and reconcile disagreements by human review. None of these are validated on embossed/glared metal plates, so build a 30-plate test set first. https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/index.md · https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/PaddleOCR-VL.html · https://www.researchgate.net/publication/393511573_PaddleOCR_30_Technical_Report · Tesseract remains fine for clean printed plates but is weak on glare/perspective.
- **Counting** (pallets, panels on a cart, rack levels): VLMs are acceptable for small counts (<20) and unreliable beyond; prefer SAM 2 masks + simple heuristics, or a detector fine-tuned on 100 labelled frames.
- **Dimensions from photos**: VLM metre estimates are **not measurements** — on MSMU-Bench GPT-4o scored 32 % and Gemini 35 % vs a specialised model's 56 %; Q-Spatial Bench shows reference objects help but scoring is "within 2×"; "Ill-Posed by Design" concludes VLM size estimates mix priors with weak visual evidence. Treat VLM sizes as a sanity check only. https://www.alphaxiv.org/abs/2509.17664 · https://arxiv.org/pdf/2409.09788 · https://arxiv.org/pdf/2606.24335 · Metric-Bench (ECCV 2026, in-image reference objects) https://arxiv.org/html/2609.25841
- **Depth-from-photo**: Depth Anything V2 Small is Apache-2.0; Base/Large are **CC-BY-NC-4.0** (not for a commercial product); metric variants indoor (Hypersim) / outdoor (vKITTI) https://github.com/DepthAnything/Depth-Anything-V2 · https://huggingface.co/depth-anything/Depth-Anything-V2-Metric-Outdoor-Large-hf. Indoor robotics evaluation: 89 % of errors within ±0.5 m under 2 m, 71 % within 6 m — too coarse for machine dimensions https://www.researchgate.net/publication/397955860. Better single-image metric options: **Metric3D v2** (beats Depth Pro on several zero-shot sets) https://arxiv.org/html/2404.15506v2, **Depth Pro** (Apple, sharp, ~0.65 s/image) https://arxiv.org/pdf/2410.02073, **MoGe-2** (explicit scale head; reported best absolute error) https://www.emergentmind.com/topics/moge-2. **The reliable recipe is the simple one:** place a known-size reference (a 1 m folding rule, an A4 sheet, a Euro pallet 1200×800 mm) in the plane of the face you measure, detect it with SAM 2, compute a homography, and measure in that plane; or use the iPhone's own ARKit/LiDAR measurement at capture time. For rough L×W×H to populate the layout, a two-photo approach (front + side with a pallet in frame) with homography gives ±3–5 %, far better than any monocular depth net.
- **Agentic glue**: a script that walks the photo folder, asks the VLM "which machine ID is this? (list)" against your table, extracts the nameplate JSON, proposes L×W×H from reference-object homography, and writes a review spreadsheet is a realistic one-week deliverable; keep humans approving every row before it reaches `layout.json`.

---

## 8. Phased plan (suggested)

1. **Week 1–2**: tape-measure column grid + walls; scan bay-by-bay (Scaniverse splat + Polycam LiDAR mesh/cloud); register in CloudCompare to control points; export top-down raster.
2. **Week 2–3**: trace `layout.json` (floor, zones, walls, machine OBBs from Open3D DBSCAN + manual fixes); VLM/OCR nameplate pass; photo-textured box assets; a few generated GLB stand-ins (TRELLIS/Tripo) scaled to measured sizes.
3. **Week 3–5**: R3F viewer: layout renderer, instanced entities, JSONL replay with scrub/speed, heatmap plane, spaghetti lines, labels, camera presets; splat backdrop via Spark aligned in SuperSplat.
4. **Week 4–6**: SimPy model emitting the JSONL contract; bottleneck analytics; what-if scenario diff (seeded runs, WareTwin pattern).
5. **Later**: `usd-core` exporter from `layout.json` (+ time-sampled transforms from a replay), guc for assets, validate in usdview, then Omniverse/Isaac Sim.

## Key uncertainties to verify yourself
- Omniverse's 2026 "free for production" status (single secondary source; forum contradiction).
- Luma AI splat export status (single 2026 blog claim).
- Hunyuan3D 3.0 open weights (not found; only "planned").
- Spark's exact npm version (search said 2.3.1, npm page blocked).
- deck.gl HeatmapLayer under OrthographicView; three.js KHR_materials_variants helper (prior knowledge).
- Omniverse Industrial/Warehouse pack contents (docs host unreachable from this sandbox; from search snippets).
- PDAL current version; JaamSim trace export; salabim scene export (none found — treat as absent).
