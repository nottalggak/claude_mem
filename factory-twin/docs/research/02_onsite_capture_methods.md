# Factory Digital-Twin Field Capture: Research Report
*Prepared 2026-10-10 for a one-day visit (next Tuesday) to a Korean furniture factory, 1,000–5,000 m², low budget (smartphones + at most one consumer device).*

> Research caveat: the shared web-search budget was exhausted before every item was verified, and direct fetches to poly.cam, scaniverse.com, KEPCO and docs.ultralytics.com were blocked by the sandbox proxy. Items marked **(est.)** are approximate Korean prices from general knowledge, not verified listings. Verify on 쿠팡/다나와 before purchase.

---

## 0. Executive recommendation (read this first)

| Need | Cheapest reliable approach for 1 day | If you buy ONE device |
|---|---|---|
| 3D geometry / layout | **Scaniverse (free, on-device) on an iPhone Pro / iPad Pro with LiDAR**, scanned in 15–25 segments of ≤150 m² each; plus a Bosch/Leica Bluetooth laser meter for control dimensions; plus the building's 건축물현황도 from 세움터 as the master floor plan | **Insta360 X5 (~₩759,000 official KR store, ~₩645,000 on sale)** – gives 8K 360° walk-through video for Gaussian splat training (Scaniverse/Postshot/Nerfstudio), Kuula/Matterport tours, and later photo reference for every machine |
| Machine specs | Nameplate photos (명판) + HMI screen photos + maintenance log | – |
| Power | Nameplates + a ₩40–60k clamp meter spot-reading each machine running vs. idle + KEPCO 파워플래너 15-min data from the owner | Shelly Pro 3EM (~₩200–250k est.) on the main incoming feeder for a 1–2 week log |
| Movement | 2–4 fixed smartphones/action cams on tripods (10–20 min clips, with written worker consent) → YOLO + ByteTrack + homography offline; plus manual spaghetti diagrams | – |
| Process times | Stopwatch app + video of 5–10 cycles per station + foreman interview + request ERP/order sheets | – |

Total new spend can be kept under ₩1.0–1.3M (laser meter ~₩150–250k, clamp meter ~₩50k, 360 cam ~₩650–760k, tripods/clamps/power banks ~₩100k).

---

## 1. 3D capture of the factory interior with consumer gear

### 1.1 Reality check on phone LiDAR
- iPhone/iPad LiDAR has a practical range of ~5 m and drifts over long walks; a 1:300 mockup study measured Polycam Pro at 42.6% and Scaniverse at 10.4% average error on small objects, while Polycam's own marketing claims "within 0.5 in" on standard interiors and admits phone LiDAR is not survey-grade ([ScienceDirect study](https://www.sciencedirect.com/science/article/pii/S1877050925026742), [Polycam](https://poly.cam/blog/the-best-3d-scanners-for-apartment-as-builts-2026-guide)). An arXiv evaluation of a six-floor building found the Matterport Pro3 produced ~1.88M points vs. ~0.51M for an iPhone and cites Pro3 accuracy of ±20 mm at 10 m ([arXiv 2506.14771](https://arxiv.org/html/2506.14771v1)).
- **Conclusion:** for a 1,000–5,000 m² hall, phone LiDAR is fine for *shape, placement and machine envelopes* (±2–5 cm per segment, worse across the whole hall), but you must anchor it to a laser-measured control network and the building drawing. Do not expect one continuous 3,000 m² scan to close without drift.

### 1.2 App-by-app assessment (iOS LiDAR)
| App | Cost | Exports | Verdict for a factory |
|---|---|---|---|
| **Scaniverse** (Niantic Spatial) | Free "Classic" mode: unlimited on-device mesh + Gaussian splat generation; Plus $20/mo and Pro $50/mo add cloud credits and 360-camera input ([skyebrowse comparison](https://www.skyebrowse.com/news/posts/polycam-vs-scaniverse)) | OBJ, FBX, GLB, USDZ, STL, PLY, LAS (E57 was "planned" per [community thread](https://community.scaniverse.com/t/can-i-generate-a-point-cloud/49)); splats as PLY/SPZ | **Primary tool.** Free, processes on device (no upload wait), LAS/PLY out for CloudCompare registration. Scan in segments. |
| **Polycam** | Free tier exports GLTF only; paid tier unlocks OBJ/FBX/STL/point cloud. Sources disagree on plans (Pro ~$150/yr or ~$27/mo; one source says Pro replaced by Basic $30/mo + Business $400/yr) ([skyebrowse](https://www.skyebrowse.com/news/posts/polycam-vs-scaniverse), [aisotools](https://aisotools.com/blog/polycam-review-2026)) | GLTF, FBX, PLY, USDZ, OBJ, LAS/E57/DXF on paid; auto floor plans; splats | Best UX and floor-plan export, but you pay. Worth one month of a paid plan if you want automatic 2D floor plans and DXF. |
| **3D Scanner App** | Free | OBJ, PLY, GLTF, point cloud, raw depth frames | Good free backup; raw frame export useful for custom pipelines. |
| **SiteScape** | Free tier limited (~500 m² of cloud capture per aggregator listing); Pro $49.99/mo or $449.99/yr: unlimited, RCP/E57/PLY ([SiteScape help](https://help.holobuilder.com/en/articles/8178757-free-sitescape-accounts-sitescape-pro), [techimply](https://www.techimply.com/profile/sitescape)) | E57, PLY, RCP | AEC-oriented point clouds; E57 direct. Consider if you need Revit/Recap workflows. |
| **Canvas (Occipital)** | Scan free; CAD conversion paid per scan | Paid "Scan to CAD" (SketchUp/Revit) | Room-oriented, not ideal for an open hall. |
| **Matterport app (iPhone LiDAR)** | Starter ~$9.99–12/mo; Professional ~$58–69/mo; floor plans, E57, MatterPak cost extra ([thefuture3d pricing guide](https://www.thefuture3d.com/blog/matterport-pricing-guide-2026/), [Matterport](https://matterport.com/en-GB/blog/unveiling-the-perfect-lens-cameras-compatible-with-matterports-spatial-data)) | Tour, schematic floor plan (paid), E57/OBJ (higher tiers) | Old forum limits were 10,000 sq ft / 200 scan points per model; users report 260+ points before crashes ([WGAN forum](https://www.wegetaroundnetwork.com/topic/1342/current-scan-limit/)). Usable for a tour, weak for a measurable point cloud. |
| **Apple RoomPlan API** | Free (your own app) | USDZ parametric walls/doors/objects; MultiRoom API merges rooms (iOS 17+) | Indoor-only taxonomy (walls, doors, windows, furniture); no API to re-align independent scans; long sessions overheat and lose accuracy ([Apple forum reply](https://developer.apple.com/forums/thread/831648), [flutter_roomplan docs](https://pub.dev/documentation/flutter_roomplan/latest/)). Not suited to a 30 m open hall with machines. Skip. |

### 1.3 Android options
- **KIRI Engine** now does Gaussian splatting on Android (previously iOS-only); free tier exists; photogrammetry and video-to-splat modes; splat download from the app has been limited ([80.lv](https://80.lv/articles/kiri-engine-brings-3d-gaussian-splatting-to-phones), [App Store listing](https://apps.apple.com/app/id1577127142)).
- **Luma AI 3D Capture** still lists NeRF/splat export (USDZ, glTF, OBJ) but Luma sunset Genie and Flythroughs on 2026-01-01 and the CEO has said capture is not actively developed; treat as end-of-life ([radiancefields](https://radiancefields.com/luma-ai-alternatives), [App Store](https://apps.apple.com/DE/app/id1615849914)).
- **magicplan removed AR scanning on Android in late 2024** ([illustrarch review](https://illustrarch.com/articles/architectural-technology/73956-magicplan-review.html)).
- Practical Android role: shoot 4K video and photo sets for photogrammetry/splats; do not rely on ARCore depth for measurement.

### 1.4 360 cameras + tour platforms
- **Insta360 X5**: official Korean store ₩759,000 standard bundle, seen at ₩645,000 on sale; 쿠팡 bundle listing ₩875,000 ([Insta360 KR](https://store.insta360.com/kr/product/x5), [쿠팡](https://www.coupang.com/vp/products/9302404965)). Matterport lists it as compatible, but it has no LiDAR so Matterport cannot make measurement-accurate floor plans from it ([Matterport blog](https://matterport.com/en-GB/blog/unveiling-the-perfect-lens-cameras-compatible-with-matterports-spatial-data)). **X4** is $499 US / ~₩600–680k KR (est.); the lighter X4 Air was $339.99 in Feb 2026 ([Slickdeals](https://slickdeals.net/f/19246324-insta360-x4-air-339-99)).
- **Ricoh Theta X**: ~₩900k–1.1M (est.); better still images for tours, weaker video.
- **Kuula**: Pro plan roughly $16–20/mo (est.) for hosted 360 tours with floor-plan hotspots. Free alternative: self-host with Pannellum/Marzipano (open source).
- Scaniverse Plus/Pro now accepts 360-camera input for cloud splat generation ([skyebrowse](https://www.skyebrowse.com/news/posts/polycam-vs-scaniverse)).

### 1.5 Photogrammetry and Gaussian splatting (desktop, free)
- **RealityScan 2.x** (Epic, free for most users): GPU-accelerated alignment, imports LAS/LAZ/E57, exports COLMAP format for Postshot and Nerfstudio ([radiancefields: 2.0](https://radiancefields.com/realityscan-2-0-released), [2.1.1](https://radiancefields.com/realityscan-releases-v2.1.1-with-colmap-updates)). Best free photogrammetry for textured meshes.
- **Meshroom / COLMAP**: fully open source; slower; COLMAP is the standard pose solver feeding splat trainers.
- **Postshot (Jawset)**: free tier is non-commercial, no limits on images/model size, up to 4K; Indie tier adds commercial use and PLY splat export; Studio adds CLI ([Jawset pricing](https://activation.jawset.com/shop/pricing)). Easiest Windows splat trainer; needs an NVIDIA GPU (8 GB+ VRAM recommended, est.).
- **Nerfstudio splatfacto / gsplat**: open source, CUDA; [nerfstudio](https://github.com/nerfstudio-project/nerfstudio), [gsplat](https://github.com/nerfstudio-project/gsplat). AWS publishes a batch pipeline if you lack a GPU ([AWS toolbox](https://github.com/aws-solutions-library-samples/guidance-for-open-source-3d-reconstruction-toolbox-for-gaussian-splats-on-aws)).
- **Why splats matter here**: a splat gives a photoreal "look" of the hall for the web twin in hours, while the LiDAR mesh/LAS gives geometry for measurement. Khronos now has a glTF extension for splats with point-cloud fallback ([Khronos press release](https://www.khronos.org/news/press/gltf-gaussian-splatting-press-release)).

### 1.6 Web viewing
- **Spark** (`@sparkjsdev/spark`, MIT, by World Labs): loads PLY/compressed PLY/SPZ/SPLAT/KSPLAT/SOG; v2.x adds streamable LoD; examples use three@0.180 ([GitHub](https://github.com/sparkjsdev/spark), [radiancefields](https://radiancefields.com/spark-v2.3.0-fixes-on-demand-rendering-for-paged-lod)). Minimal code: `scene.add(new SparkRenderer({renderer})); scene.add(new SplatMesh({url}))`.
- **three.js r186** merged a native splat renderer (SH0 only, no LoD/streaming) ([radiancefields](https://radiancefields.com/three.js-merges-a-native-gaussian-splat-renderer-for-webgpu-in-r186)).
- **@mkkellogg/GaussianSplats3D**: 2.9k stars, still updated Oct 2026 ([GitHub](https://github.com/mkkellogg/GaussianSplats3D)).
- **SuperSplat** editor (PlayCanvas, MIT, 10k stars) for cropping/cleaning splats and exporting compressed PLY/SOG; **supersplat-viewer** for embedding ([editor](https://github.com/playcanvas/supersplat), [viewer](https://github.com/playcanvas/supersplat-viewer)).
- Recommended stack: LiDAR LAS → CloudCompare (register + decimate) → Blender/Meshlab → GLB for the twin's collision/measure layer; splat SOG/SPZ via Spark for the visual layer.

### 1.7 Practical scan protocol (factory, dust, mixed light)
1. **Divide the hall into ≤150 m² segments** (one aisle/bay each). Start and finish each segment at a printed AprilTag/ArUco or taped "+" on the floor so segments can be registered later. Keep a sketch numbering each segment.
2. **Walk slowly (<1 m/s), 1–1.5 m from surfaces, phone at chest height, sweep up/down**; the LiDAR range is ~5 m, so high ceilings and roof trusses will not be captured by LiDAR (use photos/360 for those). Close each loop by returning to the start marker; loop closure and slow walking are the standard advice for handheld scanners ([MultiSet/Leica guidance](https://docs.multiset.ai/basics/third-party-scans/leica-scans)).
3. **Machines**: scan each large machine as its own object scan (walk a full 360° around it twice, high and low). Add 10–20 photos per machine for photogrammetry/splat and the nameplate.
4. **Lighting**: turn on all hall lights; avoid scanning into windows/skylights; shiny laminate panels and glass cause LiDAR holes, so photograph those areas. Dust in the air is fine for LiDAR; dust on the phone lens is not—wipe every segment.
5. **Control measurements**: with the laser meter, measure 15–30 long diagonals and column-to-column distances; write them on the sketch. These are used to scale-check and align every segment.
6. **Battery/heat**: iPhone LiDAR sessions overheat; keep two devices and rotate, carry a 20,000 mAh power bank, pre-clear storage (each segment 0.5–2 GB).
7. **Export immediately** (LAS + GLB + splat) to a laptop over AirDrop/cable at lunch; never leave all data on one phone.
8. **Time budget**: ~2–3 min scanning per 100 m² plus 2–3 min processing on device; a 3,000 m² hall in 20 segments ≈ 2.5–3 hours for one scanner, so run two scanners.

---

## 2. Floor plan and measurement

### 2.1 Laser distance meters (Bluetooth)
| Model | Price | Notes |
|---|---|---|
| **Bosch GLM 50-27 C / CG** | RS Korea lists GLM 50-27 CG at ₩609,026 (grey-import markup); EU ~€185; 쿠팡 typical ₩180–260k (est.) | 50 m, ±1.5 mm, IP65, Bluetooth 4.2 to Bosch MeasureOn and magicplan ([RS KR](https://kr.rs-online.com/web/p/laser-measures/2174391), [skroutz](https://skroutz.mt/s/28452832/Bosch-Laser-Distance-Meter-GLM-50-27-C-with-Range-up-to-50m.html)) |
| **Bosch GLM 50 C** | ~$110–150 US; ~₩150–200k KR (est.) | Older Bluetooth model, still common |
| **Leica DISTO D2** | ~AUD 157 / discontinued in UK; successor **D2-2** (150 m, IMU) ~€220 ([PB Tech](https://www.pbtech.com/product/TOLLEC762200/Leica-DISTO-D2-60m-range), [global-geosystems](https://global-geosystems.com/en/product/leica-disto-d2-2/)) | Bluetooth, magicplan-supported |
| **신콘 SD-60 / cheap Chinese 50 m** | ₩40–70k (est.) | No Bluetooth; fine as a second meter |

Buy one Bluetooth unit (Bosch GLM 50-27 C is the value pick) and one cheap backup.

### 2.2 magicplan
Free up to two projects; Sketch $9.99/mo, Report $29.99/mo; Bluetooth meter integration with Bosch, Leica, Hilti, Stabila, DeWalt, Würth; DXF export ([Capterra](https://www.capterra.co.uk/software/210335/magicplan), [illustrarch](https://illustrarch.com/articles/architectural-technology/73956-magicplan-review.html)). Use it on iPhone to lay out the wall/column grid with laser-meter values during the visit; export DXF as the twin's ground-truth 2D plan.

### 2.3 Building drawings in Korea (건축물대장 + 건축물현황도)
- 정부24 issues only the 건축물대장; **세움터 (cloud.eais.go.kr)** issues the 대장 *and* the 건축물현황도 (배치도/평면도) ([Seoul housing portal](https://news.seoul.go.kr/citybuild/?p=22429), [safehomes guide](https://safehomes.kr/insights/kn-20260521-138-summarizing-how-to-get-building-ledger-via-seumter/)).
- Path: 세움터 → 건축물대장 발급 → address search → check 건축물현황도 → 배치도/평면도. Non-member access works but needs 공동인증서 identity verification.
- **Floor plans contain personal data, so the owner's consent/권한 is needed; the owner (소유자) or their delegate must request them** ([safehomes](https://safehomes.kr/insights/kn-20260521-134-how-to-view-and-look-up-building-ledger/)). Ask the owner before the visit to download the 평면도/배치도 PDF (or their original 준공도면/설계도면 CAD files from the architect) and send them.
- Also ask for: 공장등록증, 전기안전관리 점검 보고서 (has the panel single-line diagram and transformer kVA), 소방 도면 (shows sprinkler layout and column grid), machine layout drawing (설비배치도) if any.

### 2.4 Registering scans to the floor plan
1. Import the 평면도 DXF/PDF into CloudCompare or QGIS as a raster, scale it using one known laser dimension.
2. For each LAS segment: pick 3+ floor-marker / column-corner points, align with CloudCompare "Align (point pairs picking)", then ICP-refine against neighboring segments.
3. Check the long diagonals you measured; if error > 5 cm, re-run with more pairs or split the segment.
4. Export one merged LAS/E57 and a decimated GLB; keep the transform matrices so splats (trained from the same walks) can be aligned using the same markers.

---

## 3. Worker and vehicle movement tracking

### 3.1 Video-based (recommended for both the 1-day visit and the 1–2 week phase)
**Pipeline**
- Detection + tracking: Ultralytics YOLOv8/YOLO11 `track` with ByteTrack or BoT-SORT; Roboflow `supervision` wraps ByteTrack and provides `TraceAnnotator` and `HeatMapAnnotator` (added v0.16) for trajectory and heat-map video output ([Roboflow guide](https://roboflow.com/how-to-track/yolov8), [supervision annotators](https://supervision.roboflow.com/0.26.1/detection/annotators/)). BoxMOT (8.3k stars) offers pluggable trackers (ByteTrack, BoT-SORT, StrongSORT, OC-SORT) ([GitHub](https://github.com/mikel-brostrom/boxmot)).
- Image-to-floor mapping: per camera, click 4–8 floor points visible in the frame whose floor-plan coordinates you know (use the taped markers), compute `cv2.findHomography`, and map each track's bottom-center point to plan coordinates. supervision's `ViewTransformer` does this in one class.
- Multi-camera fusion reference implementation: **alexandergg/multicam-3d-tracking** (YOLO + ByteTrack + homography ground-plane fusion + Rerun bird's-eye view, CPU/Apple-silicon friendly) ([GitHub](https://github.com/alexandergg/multicam-3d-tracking)). No ready-made "spaghetti diagram" repo exists; the diagram is just a `matplotlib`/Plotly polyline per track ID over the plan image, color-coded by role (worker, forklift, cart). Classes: `person`; for forklifts/carts, fine-tune on 200–500 labeled frames (Roboflow free tier) or use `truck`/custom.
- Vehicles vs. people: track forklifts with a custom class; carts without engines are best logged by attaching a colored marker (cheap, high contrast) to the cart and using color/ArUco detection.

**Cameras for the visit**: 2–4 old smartphones or action cams on ₩10–20k tripods/clamp mounts at 2.5–3.5 m height, looking diagonally down aisles. Record 10–20 min clips at each of 3–4 positions during active production, plus 1 continuous 60–90 min clip over the busiest crossroads. For the 1–2 week phase, leave 2–3 Wi-Fi cams (TP-Link Tapo C-series ~₩30–50k est., record to microSD) or ask to use existing factory CCTV exports (NVR export in MP4).

**Privacy/consent in Korea (개인정보보호법)**
- Fixed cameras are 고정형 영상정보처리기기 (제25조). Operators must post an 안내판 with purpose, location, coverage, hours, manager name/contact (시행령 제24조); multiple cameras in one building may use one sign at entrances ([NPS policy page](https://www.nps.or.kr/comm/footer/personal_policy_easy.do), [nepla wiki](https://www.nepla.ai/wiki/it-정보-방송통신/개인정보-위치정보-신용정보/고정형-영상정보처리기기/고정형-영상정보처리기기-설치·운영시의-의무/고정형영상정보처리기기운영자의-안내판-설치-의무-6349gxxm8zx5)).
- Supreme Court 2023.6.29 (2018도1917): installing CCTV in a plant without worker consent and without 노사협의회 협의 was found to carry illegality risk; cameras that effectively monitor workers were treated differently from perimeter cameras ([Shin & Kim newsletter](https://www.shinkim.com/kor/media/newsletter/2201), [Lawtalk](https://www.lawtalk.co.kr/posts/65700)). The 개인정보위/고용노동부 guideline requires hearing workers' opinions before installing CCTV for workplace monitoring ([Byline](https://byline.network/2023/01/0131_02/)).
- Practical protocol: (1) short written 동의서 per worker stating purpose (공정 분석·디지털 트윈 연구), what is recorded, retention (e.g., 90 days), that faces will be blurred, no HR use; (2) brief the 노사협의회/foreman; (3) temporary A4 안내판 at entrances for the day; (4) blur faces in exports (YOLO-face + Gaussian blur) before leaving the raw video with anyone; (5) store raw video encrypted, delete after analysis. Movement analysis adds location data so consent should explicitly cover it.

### 3.2 Tag-based (UWB/BLE/Wi-Fi RTT/phone logging)
- **Qorvo MDEK1001 (12× DWM1001-DEV)**: EOL announced 2025-12-04, last-time-buy 2026-07-15; single DWM1001-DEV ~SGD 44 (~₩45k) from Mouser, not sold to consumers in EU/UK ([Qorvo](https://www.qorvo.com/products/p/MDEK1001), [Mouser](https://www.mouser.sg/c/rf-wireless/rf-wireless-development-tools/multiprotocol-development-tools/?m=Qorvo)). Risky to build on now.
- **Makerfabs ESP32 UWB (DW1000 $39.80; DW3000 variant; MaTouch ESP32-S3 UWB $59.80)**: ~10 cm claimed, ~10 m indoor range reports; 4–6 anchors minimum, humans block UWB so plan more ([Hackster](https://hackster.io/news/makerfabs-arduino-compatible-esp32-usb-module-takes-aim-at-accurate-indoor-positioning-3f4b1a5967a3), [Arduino forum](https://forum.arduino.cc/t/affordable-indoor-positioning-using-esp32-uwb-modules/957727), [cnx](https://cnx-software.com/2026/08/09/matouch-esp32-s3-mauwb-board-integrates-3-95-inch-touchscreen-and-uwb-module-for-indoor-positioning-and-ranging/)). A DIY 6-anchor + 4-tag set ≈ ₩600–800k and a week of firmware work (reference repos: [Hm7762/uwb-indoor-positioning-system](https://github.com/Hm7762/uwb-indoor-positioning-system)). Only worthwhile for the multi-week phase in a ≤1,000 m² zone.
- **Pozyx**: UWB RTLS kit from $4,970 (4 anchors + 6 tags); Creator kits being phased out ([Pozyx store](https://www.pozyx.io/store)). **Sewio**: quote-only ([rfp.wiki](https://www.rfp.wiki/specialty-industries/positioning-industrial-technology/sewio/alternatives-and-competitors)). Both over budget.
- **BLE beacons**: ₩10–15k per beacon, 2–5 m accuracy with phones as receivers; good for *zone* presence (which station a worker is at), not paths.
- **Wi-Fi RTT**: needs 802.11mc APs and Android phones; impractical here.
- **Phone-based path logging**: ARKit/ARCore VIO path apps (e.g., record `ARSession` camera transforms in a tiny custom app, or free "AR Ruler"-type apps) give 1–3% drift over a walk; useful for the *analyst's* own walk logging (spaghetti diagram of a product following a batch), not for workers.

### 3.3 Manual methods
- **Spaghetti diagram**: one analyst follows one worker/one batch for 20–30 min, drawing the path on a printed 평면도 (one color per worker/product); count trips and estimate distance from the plan scale.
- **Time-motion / work sampling**: random-instant observations (e.g., every 3 min for 2 h, each worker: working / walking / waiting / setup / idle) give utilization with ±5–10% at 100–200 observations per worker.
- **REBA/OWAS** posture scores from 5–10 photos per station (free scoring sheets) to flag ergonomic hotspots for the twin's "risk" layer.
- Apps: **Timestudy Stopwatch** (iOS; TMU/decimal-minute, CSV/JSON/PDF), **Time Study Engineer** (free, VA/NVA tagging, CSV), **ProcessTM** (free, time study + activity sampling with web sync), **Lean Tool Kit – Time&Sample** (work sampling to Excel) ([App Store listings](https://apps.apple.com/app/id6757175566), [Time Study Engineer](https://apps.apple.com/app/id6740770124), [ProcessTM](https://apps.apple.com/app/id874921740)). Android: any lap-stopwatch + Google Sheets form.

### 3.4 Recommendation
- **1-day visit**: fixed-camera video (3–4 positions) + manual spaghetti/work sampling. Zero hardware cost, highest information per hour.
- **1–2 week phase**: 2–3 microSD Wi-Fi cameras or the factory's own NVR exports, processed offline with YOLO+ByteTrack+homography; add 10–20 BLE beacons at stations if you need station-level dwell by worker without video. UWB only if a sub-area needs <30 cm paths and someone can spend a week on firmware.

---

## 4. Power / energy data

### 4.1 Nameplates and spot measurements
- Photograph every 명판: rated kW (or HP), rated current A, voltage (220/380 V), phase, Hz, motor count, spindle kW, dust-port diameter, year. For multi-motor machines (edge banders, CNC) note each motor.
- **Clamp meter**: **UNI-T UT210E** (true-RMS, 100 A AC/DC, ~$40–60 abroad, ~₩45–70k KR est.) is sufficient for 1–100 A loads ([eleshop](https://eleshop.eu/uni-t-ut210e.html), [EEVblog](https://eevblog.com/forum/testgear/a-look-at-the-uni-t-ut210e)); **Hioki CM3289** (1000 A, ~¥16,700 / ~€118 / $162, ~₩200–250k KR est.) if you must clamp the incoming feeder ([Hioki EU](https://shop.hioki.eu/CM3289-AC-CLAMP-METER/CM3289), [Test Equipment Depot](https://www.testequipmentdepot.com/hioki-cm3289-true-rms-ac-clamp-meter-with-compact-sensor-600v-acdc-1000a-ac-resistance-continuity.html)). **Safety**: clamping inside a live 380 V panel is work for the factory's 전기안전관리자/electrician; ask them to open panels and clamp while you record. Measure each machine in three states: off, idle (spindle/pump running, no cut), cutting. kW ≈ √3 × V × A × PF / 1000 (PF ≈ 0.85 loaded, ~0.6 unloaded for motors) ([Plant Services audit guide](https://www.plantservices.com/home/blog/11314272/basic-compressed-air-auditing-techniques)).
- Per-machine kWh estimate = nameplate kW × load factor (measured idle/cut ratio, typically 0.3–0.6 for woodworking) × operating hours/day.

### 4.2 Continuous CT loggers (1–2 week phase)
| Device | Price | Fit |
|---|---|---|
| **Shelly Pro 3EM (120 A / 3CT63)** | $151–155 US; €120–143 EU; ~₩200–280k KR via importers (est.) | DIN-rail, 3-phase, ~1% accuracy, stores 60 days at 1-min resolution locally, MQTT/HTTP API, no cloud needed ([smarthomecompared](https://smarthomecompared.com/energy-monitors/emporia-vue-3-3-phase-vs-shelly-pro-3em-3ct63), [Zendure](https://be.zendure.com/en/products/shelly)). 400 A version $329.99 for the main feeder. **Best pick.** |
| **Emporia Vue 3 (3-phase)** | $199–210 | 16 CT channels (good for a sub-panel with many machines) but cloud-tied ([smarthomecompared](https://smarthomecompared.com/energy-monitors/emporia-vue-3-3-phase-vs-shelly-pro-3em-400)) |
| **IoTaWatt** | ~$200 + CTs | 14 channels, local; no 2026 pricing found |
| **Sense** | US split-phase only; skip |
| **DIY ESP32 + SCT-013 + ESPHome `ct_clamp`** | ₩10–15k per channel | Current-only (no PF), ESP32 ADC is non-linear, needs burden resistor/DC bias and calibration; fine for run/idle state, not for billing-grade kWh ([atomic14](https://www.atomic14.com/esp32/sensors/sct-013/), [HA community](https://community.home-assistant.io/t/esp32-and-sct013/694710)) |

Install one Shelly Pro 3EM on the main incomer (or the 380 V sub-panel feeding the production hall) and, budget permitting, one Emporia Vue 3 on the machine sub-panel for 16 per-circuit channels. A licensed electrician must install CTs.

### 4.3 KEPCO data
- The factory is likely 산업용(을) 고압 with AMI; **한전 파워플래너** (web/app) gives AMI customers real-time usage, daily/weekly/monthly usage, active/reactive power and power factor ([App Store](https://apps.apple.com/kr/app/id1164394809), [Newsis](https://www.newsis.com/view/NISX20240628_0002791606)); **i-SMART** historically gave high-voltage customers load-duration curves and load-shift savings analysis ([kidd 2011](https://kidd.co.kr/news/139431)). 15-min interval downloads for high-voltage customers were not confirmed by this research—ask the owner to log into 파워플래너/한전ON with the 고객번호 and export whatever 시간별/15분 data is offered, plus the last 12 monthly bills (shows 계약전력 kW, 최대수요전력, 역률, 시간대별 kWh for TOU tariffs).
- Also photograph the transformer nameplate (kVA), the incoming breaker rating, and the KEPCO meter display (it cycles through kWh, peak demand, PF).

### 4.4 Compressed air and dust collection
- Compressed air can be >40% of a woodworking shop's electricity per an Atlas Copco case study (vendor claim) ([Atlas Copco](https://shopit.atlascopco.com/content/dam/atlas-copco/local-countries/united-states/documents/Modern-Woodcrafts.pdf)); unloaded screw compressors still draw 20–40% of full-load power ([Plant Services](https://www.plantservices.com/equipment/compressed-air-systems/article/11305601/diy-compressed-air-audits-8-things-you-need-to-know)).
- Method: record compressor nameplate kW, tank size, set pressure (load/unload bar); read the controller's **loaded hours vs. running hours** counters now and again a week later to get the duty cycle; clamp amps loaded vs. unloaded; kWh = (kW_loaded × t_loaded + kW_unloaded × t_unloaded) × hours ([Plant Services audit techniques](https://www.plantservices.com/home/blog/11314272/basic-compressed-air-auditing-techniques)). Count air-using machines and note leaks (hissing) during lunch break when the line is quiet.
- Dust collection (집진기): nameplate fan kW (often 15–75 kW, the single largest motor), number of ducted machines, whether blast gates are manual or automatic, whether it runs all shift regardless of load. Clamp amps once; it is usually constant-load so kWh ≈ kW × hours. Note the bag-house location (often outdoors) for the twin.

---

## 5. Machine data

- **Standards**: OPC UA for Woodworking Machines (OPC 40550-1, "Vertical Interface": machine identification, states, messages, KPI inputs, job handling) was developed by VDMA/EUMABOIS with HOMAG, Biesse, SCM, Weinig, IMA Schelling participating; umati covers ~25 companion specs ([OPC Foundation](https://reference.opcfoundation.org/specs/OPC-40550-1/6), [opcconnect](https://opcconnect.opcfoundation.org/2019/06/eumabois-opc-ua-for-plug-work-in-woodworking/)). Machines built after ~2020 from these brands may expose an OPC UA server on the machine PC—ask the service engineer for the endpoint and credentials; read with `asyncua` (Python).
- **HOMAG tapio / MachineBoard**: cloud IoT platform; data owner controls which apps see the data; no public API docs found—contact tapio for partner API access ([tapio](https://tapio.one/en/MachineBoard), [HOMAG](https://homag.com/en/machines/tapio-ready)). **Biesse SOPHIA**: machine-to-cloud only, HTTPS with dual-token auth; no export API documented ([Biesse](https://www.Biesse.com/in/wood/services/sophia)). Realistically: ask the owner for a CSV/PDF export of the dashboards (uptime, alarm list, pieces produced).
- **PLCs in Korea**: LS Electric (XGT/XGB/XGK), Mitsubishi (FX/Q/iQ-R), Siemens S7 on European machines, plus Delta/Omron. Tools: LS XGT native protocol via `PyXGT` (TCP 2004) or Modbus TCP module XBL-EMTA ([PyPI PyXGT](https://pypi.org/project/PyXGT), [AutomationDirect cut sheet](https://cdn.automationdirect.com/static/specs/cutsheet/XBL-EMTA_cutsheet.pdf)); Mitsubishi via `pymcprotocol` (MC protocol, MIT) ([GitHub](https://github.com/senrust/pymcprotocol)); Siemens via `python-snap7`; generic via `pymodbus` ([docs](https://pymodbus.readthedocs.io/en/stable/)). On the visit, only **photograph** the PLC/HMI model labels, the Ethernet switch, and any IP labels; do not connect to the machine network without the owner's and the machine vendor's written OK.
- **Reading from the HMI**: photograph every HMI page (counters, alarm history, program list, spindle hours, cycle counts, speeds/feeds). Most Korean-made saws/edge banders (양지, 대성, 우성, 삼성 etc.) have simple counters on the HMI or a mechanical piece counter.
- **Cheap non-intrusive state sensing (1–2 week phase)**: one CT clamp per machine supply (SCT-013 + ESP32/ESPHome, or Shelly EM channels) with threshold + hysteresis + minimum-duration logic gives off/idle/cutting and cycle counts; vibration sensors (ADXL345 on ESP32, or a ₩20k BLE vibration tag) work when the machine has no accessible cable. No ready-made repo does the cycle-count logic; it is ~50 lines on top of RMS current ([ESPHome ct_clamp thread](https://community.home-assistant.io/t/ct-clamp-for-esp/183812/12)).

---

## 6. Process data capture

### 6.1 Per process step (record for each station: 재단 → 엣지밴딩 → 보링/CNC → 샌딩/도장 → 조립 → 포장)
- Cycle time (per panel/part and per unit), setup/changeover time and what triggers it (material, thickness, edge tape), batch size, operators per station, machine count, WIP before/after (count panels on carts/racks now), scrap/rework rate and causes, availability losses (breakdowns, material waiting), takt/target, shift pattern, buffer locations and capacities, material handling means (forklift, hand cart, vacuum lifter), typical lot routing variants.
- Sampling plan: 5–10 cycles per station with a stopwatch app (more for short cycles), timestamp-synced with video so you can re-time later; one continuous 60–90 min video at the bottleneck; a 2-hour work-sampling round for utilization.
- Video for later study: fixed camera per station, wide angle, 1080p/30, include a clock or synchronize phones to NTP; name files `station_cam_HHMM.mp4`.

### 6.2 Interview questions (owner / foreman) — 사장님·반장 인터뷰
1. 주력 제품군과 월 생산량(개/세트), 주문 방식(수주생산/재고생산), 평균 리드타임은?
2. 공정 순서와 각 공정의 병목은 어디인가? 왜?
3. 기계별 하루 가동 시간, 교대 수, 월 가동일수, 점심/휴식 시간?
4. 가장 자주 바뀌는 세팅(두께, 엣지 종류, 색상)과 교체 시간은?
5. 자재 입고 → 재단 → 조립 → 출하까지 자재가 어디에 쌓이나(WIP 위치)? 랙/대차 수량?
6. 지게차/대차 대수, 운전자, 주요 경로와 하루 이동 횟수?
7. 불량/재작업 비율과 주요 원인; 폐기 자재 처리?
8. 집진기·컴프레서 가동 패턴(항상 켜두는지), 월 전기요금과 계약전력?
9. ERP/MES/엑셀 등 생산 기록이 있는가? 어떤 형식으로 받을 수 있나?
10. 안전 구역, 출입 통제 구역, 촬영 금지 구역?
11. 향후 변경 계획(기계 추가, 레이아웃 변경)은?
12. 작업자 수, 숙련도 구분, 작업자별 담당 공정?

### 6.3 Documents to request
**Before the visit**: 건축물현황도/준공도면(CAD), 설비배치도, 설비 목록(기계명·제조사·모델·연식·kW), 전기 단선결선도/수변전 설비 도면, 최근 12개월 전기요금 고지서 + 파워플래너 데이터, 조직도/교대표, 제품 카탈로그.
**During/after**: 생산일보·작업일보 3개월, 주문서/작업지시서 샘플, BOM(제품별 부품표), 재단 최적화(네스팅) 출력물, 품질/불량 기록, 설비 점검·고장 이력, 컴프레서 컨트롤러 시간 카운터 값, 집진기 사양서, ERP/MES export (CSV), CCTV 녹화 export(동의 후), 안전보건 작업계획서.

---

## 7. One-day visit plan

### 7.1 Team roles (3–4 people)
- **A. Scan lead** (iPhone Pro #1): LiDAR segments + machine object scans; owns the segment map.
- **B. 360/photo + measurement** (Insta360 + laser meter + magicplan): 360 walk-through video of every aisle, control dimensions, column grid, nameplate photos.
- **C. Process/energy analyst**: interviews, stopwatch cycles, work sampling, clamp readings with the electrician, HMI/PLC photos, compressor/dust collector.
- **D. (optional) Camera/consent**: sets fixed cameras, handles 동의서/안내판, spaghetti diagrams, forklift route counts. With 3 people, A also sets cameras first thing and D's tasks split between B and C.

### 7.2 Hour-by-hour (production day, assume 08:30 start)
| Time | Activity |
|---|---|
| 07:45–08:30 | Arrive before shift. Safety briefing, 동의서 signatures, temporary 안내판 at doors. Walk the hall once with the foreman; draw segment map and camera positions. Place floor markers (tape "+", numbered). Sync all phone clocks. Set 3–4 fixed cameras rolling. |
| 08:30–10:30 | A: LiDAR segments 1–10 (quiet corners first, aisles while clear). B: Insta360 walk (two full laps: one at 2 m/s for tour, one slow), then control dimensions + column grid in magicplan. C: Owner interview (45 min), then compressor/dust collector nameplates and counters with the electrician; clamp readings on the 5 largest machines. |
| 10:30–10:45 | Break: offload data (AirDrop/cable to laptop), swap batteries, check segment overlaps on screen. |
| 10:45–12:00 | A: segments 11–20 + object scans of 5 largest machines. B: nameplate + HMI photo sweep of every machine (one folder per machine, start with a photo of a numbered card), photogrammetry photo sets. C: stopwatch cycles at stations 1–3, WIP counts, spaghetti diagram of one batch. D: forklift route counting at the main crossroads. |
| 12:00–13:00 | Lunch (hall quiet): scan areas blocked earlier, listen for air leaks, photograph panels/single-line diagram with electrician, re-shoot 360 of busy aisles now empty. Backup everything. |
| 13:00–15:00 | A: re-scans of failed segments, roof/mezzanine/outdoor dust collector, loading dock. B: remaining machine object scans; cart/rack/pallet dimensions (they become reusable twin assets). C: cycles at stations 4–6, changeover observation, work-sampling round (every 3 min). D: second spaghetti diagram (different worker/product), move cameras to new positions. |
| 15:00–15:15 | Break, backup, checklist review against Section 7.4. |
| 15:15–16:30 | Gap filling from the checklist; foreman follow-up questions; request documents; collect cameras; read compressor counters again; photograph KEPCO meter again (gives a daytime kWh delta). |
| 16:30–17:00 | Debrief with owner: agree on the 1–2 week logging phase (Shelly install by their electrician, camera positions, data export), take the 동의서 originals. |
| Evening | Verify every segment opens; export LAS/GLB/splats; start CloudCompare registration and a Postshot/Scaniverse splat of the main aisle as a sanity check. |

### 7.3 Equipment packing list (approximate Korean prices)
| Item | Qty | Price (₩, approx.) | Note |
|---|---|---|---|
| iPhone 15/16/17 Pro or iPad Pro (LiDAR) | 2 | owned | Scaniverse + 3D Scanner App installed, 100 GB free each |
| Insta360 X5 (or X4) | 1 | 645,000–759,000 (X5, official store) / ~600,000 X4 est. | + invisible selfie stick, 2 batteries, 256 GB microSD |
| Bosch GLM 50-27 C (Bluetooth) | 1 | 180,000–260,000 est. (RS KR lists CG at 609,026) | magicplan/MeasureOn |
| Cheap 50 m laser meter (신콘 등) | 1 | 40,000–70,000 est. | backup |
| UNI-T UT210E clamp meter | 1 | 45,000–70,000 est. | Hioki CM3289 ~200–250k if >100 A needed |
| Old smartphones / action cams for fixed video | 3–4 | owned | + 128 GB cards |
| Tripods / clamp mounts / magnetic mounts | 4 | 10,000–25,000 each | 3 m reach preferred |
| Power banks 20,000 mAh | 3 | 25,000–40,000 each | |
| Laptop with ≥1 TB free, USB-C cables, card reader | 1 | owned | CloudCompare, RealityScan, Postshot installed |
| Printed 평면도 (A3) ×10, segment map, numbered cards 1–60, tape, markers, AprilTag sheets | – | 10,000 | |
| Printed 동의서, 안내판 A4 ×6, document request list | – | – | |
| PPE: safety shoes, glasses, dust masks, hi-vis vests | per person | 20,000–40,000 each | factory may require |
| Optional: Shelly Pro 3EM for the logging phase | 1 | 200,000–280,000 est. (import) | electrician install |
| Optional: BLE beacons ×10 | 10 | ~120,000 | zone dwell |

### 7.4 Data checklist (must-have / nice-to-have)

**Must-have (필수)**
- [ ] 전체 홀 LiDAR 세그먼트 (LAS + GLB), 세그먼트 맵, 겹침 확인
- [ ] 레이저 제어 치수 15개 이상 (대각선, 기둥 간격, 천장고, 문 폭)
- [ ] 건축물현황도 또는 준공 평면도 (DXF/PDF)
- [ ] 기계별 폴더: 명판 사진, 전체/측면 사진, HMI 화면, 설치 위치(세그먼트 번호), 외형 치수
- [ ] 집진기·컴프레서 명판, 세팅 압력, 가동 시간 카운터, 덕트/배관 경로 사진
- [ ] 분전반/수변전 사진, 변압기 kVA, 계약전력, 최근 전기요금 고지서
- [ ] 기계별 클램프 전류(정지/공회전/가공) 상위 10대
- [ ] 공정 순서도 + 공정별 사이클타임 5회 이상, 작업자 수, WIP 위치/수량
- [ ] 고정 카메라 영상 3개소 이상 × 15분 (동의서 완료)
- [ ] 지게차/대차 주요 경로와 왕복 횟수, 자재 입출고 위치
- [ ] 인터뷰 기록 (6.2), 요청 서류 목록 합의
- [ ] 360 영상 전체 통로 1회 이상

**Nice-to-have (권장)**
- [ ] 기계별 오브젝트 스캔(360° 근접) 및 포토그래메트리 사진 세트
- [ ] Gaussian splat용 느린 360 워크 (2회)
- [ ] 파워플래너 15분/시간별 데이터 export, i-SMART 부하지속곡선
- [ ] 작업 샘플링 2시간, 스파게티 다이어그램 2개, REBA 사진
- [ ] PLC/네트워크 스위치 모델·IP 라벨 사진, OPC UA/tapio/SOPHIA 접근 가능 여부
- [ ] 랙·대차·팔레트·자재 번들 치수(재사용 에셋)
- [ ] 외부: 건물 외관 360, 하역장, 집진기 외부 설치 위치, 주차/진입 경로
- [ ] 소음/조도 스팟 측정 (폰 앱)으로 환경 레이어
- [ ] 생산일보 3개월 CSV, BOM, 네스팅 출력물

---

## Key sources
- Phone LiDAR accuracy: [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1877050925026742), [arXiv 2506.14771](https://arxiv.org/html/2506.14771v1), [Polycam](https://poly.cam/blog/the-best-3d-scanners-for-apartment-as-builts-2026-guide)
- Scaniverse/Polycam pricing & exports: [skyebrowse](https://www.skyebrowse.com/news/posts/polycam-vs-scaniverse), [Scaniverse community](https://community.scaniverse.com/t/can-i-generate-a-point-cloud/49)
- Matterport pricing/compat: [thefuture3d](https://www.thefuture3d.com/blog/matterport-pricing-guide-2026/), [Matterport](https://matterport.com/en-GB/blog/unveiling-the-perfect-lens-cameras-compatible-with-matterports-spatial-data)
- SiteScape: [help center](https://help.holobuilder.com/en/articles/8178757-free-sitescape-accounts-sitescape-pro)
- RoomPlan limits: [Apple forums](https://developer.apple.com/forums/thread/831648)
- RealityScan 2.x: [radiancefields](https://radiancefields.com/realityscan-2-0-released); Postshot: [Jawset](https://activation.jawset.com/shop/pricing)
- Web splat viewers: [Spark](https://github.com/sparkjsdev/spark), [GaussianSplats3D](https://github.com/mkkellogg/GaussianSplats3D), [SuperSplat](https://github.com/playcanvas/supersplat), [three.js r186](https://radiancefields.com/three.js-merges-a-native-gaussian-splat-renderer-for-webgpu-in-r186)
- Insta360 X5 KR: [official store](https://store.insta360.com/kr/product/x5), [쿠팡](https://www.coupang.com/vp/products/9302404965)
- Laser meters: [RS Korea GLM 50-27 CG](https://kr.rs-online.com/web/p/laser-measures/2174391), [Leica D2-2](https://global-geosystems.com/en/product/leica-disto-d2-2/); magicplan: [Capterra](https://www.capterra.co.uk/software/210335/magicplan)
- 세움터 도면: [서울시 주택포털](https://news.seoul.go.kr/citybuild/?p=22429), [safehomes](https://safehomes.kr/insights/kn-20260521-138-summarizing-how-to-get-building-ledger-via-seumter/)
- Tracking: [Roboflow YOLOv8 tracking](https://roboflow.com/how-to-track/yolov8), [supervision annotators](https://supervision.roboflow.com/0.26.1/detection/annotators/), [BoxMOT](https://github.com/mikel-brostrom/boxmot), [multicam-3d-tracking](https://github.com/alexandergg/multicam-3d-tracking)
- Korean CCTV law: [Shin & Kim](https://www.shinkim.com/kor/media/newsletter/2201), [Lawtalk 대법원 2018도1917](https://www.lawtalk.co.kr/posts/65700), [Byline guideline](https://byline.network/2023/01/0131_02/), [안내판 요건](https://www.nps.or.kr/comm/footer/personal_policy_easy.do)
- UWB: [Qorvo MDEK1001 EOL](https://www.qorvo.com/products/p/MDEK1001), [Makerfabs/Hackster](https://hackster.io/news/makerfabs-arduino-compatible-esp32-usb-module-takes-aim-at-accurate-indoor-positioning-3f4b1a5967a3), [Pozyx store](https://www.pozyx.io/store)
- Energy monitors: [Shelly vs Emporia](https://smarthomecompared.com/energy-monitors/emporia-vue-3-3-phase-vs-shelly-pro-3em-3ct63), [Zendure Shelly](https://be.zendure.com/en/products/shelly); clamp meters: [UT210E](https://eleshop.eu/uni-t-ut210e.html), [Hioki CM3289](https://shop.hioki.eu/CM3289-AC-CLAMP-METER/CM3289); ESP32 CT: [atomic14](https://www.atomic14.com/esp32/sensors/sct-013/)
- KEPCO: [파워플래너 App Store](https://apps.apple.com/kr/app/id1164394809), [i-SMART 2011](https://kidd.co.kr/news/139431)
- Compressed air audit method: [Plant Services](https://www.plantservices.com/home/blog/11314272/basic-compressed-air-auditing-techniques), [Atlas Copco woodworking case](https://shopit.atlascopco.com/content/dam/atlas-copco/local-countries/united-states/documents/Modern-Woodcrafts.pdf)
- Machine data standards: [OPC 40550-1](https://reference.opcfoundation.org/specs/OPC-40550-1/6), [EUMABOIS OPC UA](https://opcconnect.opcfoundation.org/2019/06/eumabois-opc-ua-for-plug-work-in-woodworking/), [tapio](https://tapio.one/en/MachineBoard), [Biesse SOPHIA](https://www.Biesse.com/in/wood/services/sophia), [PyXGT](https://pypi.org/project/PyXGT), [pymcprotocol](https://github.com/senrust/pymcprotocol)
- Time-study apps: [Timestudy Stopwatch](https://apps.apple.com/app/id6757175566), [Time Study Engineer](https://apps.apple.com/app/id6740770124), [ProcessTM](https://apps.apple.com/app/id874921740)

**Unverified / needs a follow-up search if the user wants it**: exact 쿠팡/다나와 prices for laser meters, clamp meters and Shelly; whether 파워플래너 offers 15-min CSV export for 고압 customers; current Polycam plan names; Korean woodworking-machine makers' (양지/대성) PLC brands.