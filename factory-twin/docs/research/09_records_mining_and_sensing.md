# Data recovery for a small Korean furniture-factory digital twin: records + 2-week minimal sensing

Scope note: ~60 web searches plus direct GitHub source reads were done; the search budget then ran out, so a few Korean vendor details (exact ERP menu paths, Korean nesting products "큐빅/컷마스터/우드옵티", exact 2026 KEPCO ₩/kWh figures) could not be confirmed and are marked **[unverified]** or **[estimate]**. Code snippets in §1 and §3 were executed against pm4py 2.7.23.9 / pandas 3.0.6 in a scratch venv and run as shown.

---

## 1. Process mining with PM4Py (2025–2026)

**Version and licence.** PyPI's current release is **pm4py 2.7.23.9 (2026-10-09)**, requires Python ≥3.11 ([pypi JSON](https://pypi.org/pypi/pm4py/json)); the repo changelog for 2.7.22 (2026-03) lists Pandas 3.x / NumPy 2.4 support, Polars DFG/stats, and a fix for "incorrectly calculating cycle time and waiting time" ([CHANGELOG](https://github.com/process-intelligence-solutions/pm4py/blob/release/CHANGELOG.md)). Important: on import the package prints *"License: AGPL v3 — Commercial use requires open-sourcing your application"*; a commercial licence is sold at https://processintelligence.solutions/pm4py#licensing. For an internal analysis notebook this is fine; if the twin is a product, budget for the licence or use the DFG/variant logic in plain pandas.

**Event log contract (what the factory export must become).** One row per (order/batch/part, station) step with at least `case:concept:name`, `concept:name`, `time:timestamp`; optionally `start_timestamp` and `org:resource`. `pm4py.format_dataframe(df, case_id=..., activity_key=..., timestamp_key=..., start_timestamp_key=..., timest_format=...)` renames and sorts (signature read from [pm4py/utils.py](https://raw.githubusercontent.com/process-intelligence-solutions/pm4py/release/pm4py/utils.py)). Choice of case id for furniture: **작업지시번호 (work order)** for routing/variant analysis; **작업지시+품목(part)** when the cut list tracks parts per panel; a batch id (재단 batch / sheet) as a *trace attribute*, not case id, so batch behaviour can be found by `discover_batches`.

**What to compute (verified calls, pm4py 2.7.23.9):**

```python
import pandas as pd, pm4py
df = pd.read_excel("작업실적.xlsx")               # 작업지시번호, 공정, 설비/작업자, 시작, 종료, 수량, 불량
log = pm4py.format_dataframe(df, case_id="작업지시번호", activity_key="공정",
                             timestamp_key="종료", start_timestamp_key="시작")
variants = pm4py.get_variants_as_tuples(log)                   # routing variants & counts
rework   = pm4py.get_rework_cases_per_activity(log)            # activities repeated in a case (e.g. 엣지 twice)
serv     = pm4py.get_service_time(log, start_timestamp_key="start_timestamp", aggregation_measure="median")
perf, sa, ea = pm4py.discover_performance_dfg(log, perf_aggregation_key="median")
# with an interval log the DFG edge time runs from source COMPLETE to target START -> this is WAITING
arrival  = pm4py.get_case_arrival_average(log)                 # mean inter-arrival of orders (s)
batches  = pm4py.discover_batches(log, merge_distance=30*60, min_batch_size=2, resource_key="org:resource")
std = pm4py.filter_variants(log, [("재단","엣지","보링","조립","포장")])   # the "standard routing"
net, im, fm = pm4py.discover_petri_net_inductive(std, noise_threshold=0.0)
print(pm4py.fitness_alignments(log, net, im, fm))             # % traces fitting the standard route
diag = pm4py.conformance_diagnostics_alignments(log, net, im, fm, return_diagnostics_dataframe=True)
```
On a synthetic 40-order log this produced e.g. `rework: {'엣지': 5}`, median waiting per edge in seconds, and `fitness vs standard routing: percFitTraces 87.5`. `discover_batches` implements Martin et al. 2015 and returns *simultaneous / batching-at-start / batching-at-end / sequential / concurrent* batches per (activity, resource) — exactly the "cut 20 sheets then move the cart" behaviour you need for batch rules. `discover_performance_dfg` also supports `business_hours=True` with weekly slots (e.g. Mon 07:00–17:00) so waiting excludes nights/weekends.

**Logs with only one timestamp per step (the normal case for 작업일보).** Options, in order of preference: (a) if the sheet has 완료 time only, treat the previous step's completion as the earliest possible start and estimate service time from a *separate* short time study or from the machine current trace (§3), then set `start = complete − service_est`; (b) if the sheet has both 시작/종료 for only some rows, fit a per-(station, qty) regression `service = a + b·qty` and impute the rest, tagging imputed rows (`imputed=True`); (c) if 작업자 logs are "lifecycle" style (one row "시작", one row "완료"), use `pm4py.objects.log.util.interval_lifecycle.to_interval(log)` which merges `lifecycle:transition` start/complete pairs into `start_timestamp`/`time:timestamp` (source: [interval_lifecycle.py](https://raw.githubusercontent.com/process-intelligence-solutions/pm4py/release/pm4py/objects/log/util/interval_lifecycle.py)). Never run `get_service_time` on a single-timestamp log — it will silently return 0.

**Paper 작업일보 / 작업지시서 → table.**
- OCR: PaddleOCR 3.x PP-StructureV3 converts page images to JSON/Markdown and saves tables with `res.save_to_xlsx()` / `save_to_html()`; a **`korean_PP-OCRv5_mobile_rec`** model exists ("Supports Korean, English and numeric text") ([PP-StructureV3 docs](https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/PP-StructureV3.html), [text recognition models](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/module_usage/text_recognition.en.md)). The PP-OCRv5 report claims gains on handwriting but publishes no handwritten-table benchmark ([arXiv 2507.05595](https://arxiv.org/abs/2507.05595)); expect it to be good on printed 작업지시서 and weak on pencil 작업일보.
```python
from paddleocr import PPStructureV3
pipe = PPStructureV3(lang="korean", use_doc_orientation_classify=True, use_doc_unwarping=True)
for res in pipe.predict("daily_report_2026-09-03.jpg"):
    res.save_to_xlsx(save_path="out/"); res.save_to_json(save_path="out/")
```
- VLM extraction: for handwritten 작업일보 the practical route is a vision LLM with a fixed JSON schema (`{date, line, rows:[{공정, 품목, 수량, 불량, 시작, 종료, 작업자}]}`) and a *second pass* that re-reads the image and verifies each cell (self-consistency) — then a human spot-checks 10 %. Treat extracted values as confidence "C" until reconciled (§6).
- Manual entry effort **[estimate]**: vendor benchmarks put a keyer at ~8,000–15,000 keystrokes/h with ~1–4 % error single-keyed and 0.005–0.05 % double-keyed ([docuclipper](https://www.docuclipper.com/blog/data-entry-statistics/), [lido](https://lido.app/blog/data-entry-error-rates)). A 작업일보 row (~8 fields, ~40 keystrokes with lookups) → **≈1,000 rows ≈ 4–6 person-hours single entry, 8–12 h double-keyed**; two weeks of a 30-person plant is typically 1,500–4,000 rows. Budget 2–3 person-days plus a 10 % re-check.

**Korean SME ERP exports — fields you can expect and how to ask.**
- **더존 (iCUBE / Smart A 생산재고)**: the iCUBE 생산관리 manual documents `작업실적등록(공정별)` with 실적일, 구분, 실적수량, 검사여부, 실적담당자, 생산설비, 작업팀, 작업조, 창고, 장소; defects are in `작업실적검사` (합격/불합격, 불량코드, 불량수량) ([iCUBE 작업관리_공정별 manual PDF](https://www.douzoneon.com/s1/down/manual/icube_production_06.pdf)). Most 더존 grids export via right-click → 엑셀변환 (documented for 판매일(월)보 in a Smart A guide; same UI pattern) **[unverified for 생산]**. Ask the accountant/ERP operator for: `작업지시등록`, `작업실적등록(공정별)`, `작업실적검사`, `생산일보` for the period, as .xlsx with codes *and* names. Smart A proper is the tax/accounting product; many small furniture shops only have 생산입고 (quantity in/out), with no 시작/종료 times — plan for completion-date-only logs.
- **이카운트 (ecount)**: production flow is 작업지시서 → 생산불출 → 생산입고(실적) (ecount inventory training PDF, https://download.ecounterp.com/doc_Ecount_Inventory.pdf); all 입력자료 can be downloaded to Excel by period and uploaded via 엑셀자료올리기 ([ecount migration page](https://www.ecount.com/us/ecount/product/erp_migration)). Typical columns: 일자, 전표번호, 작업지시번호, 품목코드/품목명, 규격, 수량, 창고, 담당자, 프로젝트, 적요 — **no per-process timestamps unless the shop bought 공정/MES add-ons [estimate]**.
- **아이퀘스트 얼마에요**: the 다공정관리 module records per-process 작업시간, 생산실적 and 검수내역 ([iquest blog](https://blog.iquest.co.kr/entry/%EC%A0%9C%EC%A1%B0%EC%83%9D%EC%82%B0-%EC%96%BC%EB%A7%88%EC%97%90%EC%9A%94-ERP%EB%A1%9C-%EA%B0%81-%EA%B3%B5%EC%A0%95%EB%B3%84-%EC%9E%91%EC%97%85-%EC%8B%9C%EA%B0%84-%EC%83%9D%EC%82%B0-%EC%8B%A4%EC%A0%81-%EA%B2%80%EC%88%98-%EB%82%B4%EC%97%AD-%EA%B4%80%EB%A6%AC%ED%95%98%EB%8A%94-%EB%B0%A9%EB%B2%95-%EB%8B%A4%EA%B3%B5%EC%A0%95%EA%B4%80%EB%A6%AC%EB%A1%9C-%EC%89%BD%EA%B3%A0-%ED%8E%B8%ED%95%98%EA%B2%8C)) — the best of the four for process mining if present.
- **영림원 K-System**: a custom-built ERP (구축형, 수억원대; MES link is not standardised per analyst reports) — exports depend on the implementation; request `생산실적등록` grid with 설비/작업자/시작/종료/양품/불량 **[estimate]**.
- Request template (Korean): "2026-01-01~2026-09-30 기간의 작업지시등록·작업실적등록(공정별)·작업실적검사·생산일보를 코드와 명칭이 모두 포함된 엑셀(xlsx)로 내려 주세요. 가능하면 '등록일시(입력시간)' 컬럼도 포함해 주세요." The *record creation timestamp* is often the only real timestamp in these systems and is usable as a proxy for completion.

**Korean case material.** 퍼즐데이터 (ProDiscovery) is the domestic process-mining vendor (3× Gartner representative vendor; [byline.network](https://byline.network/2020/11/26-114/), [venturesquare](https://www.venturesquare.net/940004/)). A Korean thesis explicitly studies process mining on **domestic SME ERP** (cosmetics manufacturer), finding SME ERPs "do not properly record event data per work step" and proposing logging/pre-processing fixes ([RISS](https://www.riss.kr/search/detail/ssoSkipDetailView.do?p_mat_type=be54d9b8bc7cdb09&control_no=f9f28a96f0c01eb8ffe0bdc3ef48d419)) — this matches what you should expect. No 푸른기술 or Korean Apromore manufacturing case was found; Apromore's manufacturing references are large firms ([casestudies.com](https://www.casestudies.com/company/apromore)). The IFIP survey of process mining in manufacturing is a good checklist for event-data sources ([IFIP AICT 591](https://dl.ifip.org/IFIP-AICT-591/hal-03630900)).

---

## 2. Nesting / cut-list software as a data source

- **HOMAG/HOLZMA Cut Rite**: imports parts/board lists from CSV/XLSX; exports *summaries* (parts, boards, material, cutting-pattern) to **XLS(X) and PDF**, report data to **Access**, patterns to **DXF**; "configurable reports & summaries" ([Cut Rite 2018 sheet](https://www.hoechsmann.com/fr/lexikon/pdf/hom_cut-rite_2018_en.pdf), [v9 2014](https://www.hoechsmann.com/pl/lexikon/pdf/holzma_cut_rite_version_9_2014_en.pdf)). The *Parts summary* gives part code, L×W, qty, material; the *Board summary* gives sheets used, yield (%), offcuts; the *Pattern/Run* report gives cut sequence and estimated saw time per pattern.
- **HOMAG intelliDivide (tapio cloud)**: parts list in by manual entry, text/Excel, productionManager, cloud API or File Agent; optimisation goals waste / shortest production time / simplest handling; file- and API-based import/export ([HOMAG product page](https://www.homag.com/en/product-detail/software/work-preparation/intellidivide-cutting), [brochure](https://homag.com/fileadmin/software/brochures/intellidivide/homag-digital-factory-intellidivide-brochure-en.pdf)). Its "production time" objective means the tool already contains a saw-time model — ask the shop to export the plan PDF/XLSX per job; the estimated time is a useful prior for the saw's cycle time.
- **OptiCut (Wood Designer) / PolyBoard**: semicolon CSV with reference, length, width, qty, material, grain, per-edge flags + thickness + edge material (thickness shared by opposite edges) ([PolyBoard→OptiCut export](https://wooddesigner.org/help-centre/polyboard-cutting-list-export/), [CSV setup](https://wooddesigner.org/opticut-cutting-list-set-up-spreadsheet-import/)); labels printable with barcodes per field ([label printing](https://wooddesigner.org/opticut-label-printing/)).
- **Korean products**: 다임소프트 sells a 합판 재단 프로그램 for 가구/싱크 makers with Excel import and 손실률 output ([daimsoft](http://www.daimsoft.co.kr/), [panels.kr](http://panels.kr/hpad.php)); 한스코시스템즈 distributes PYTHA, which generates 재단목록 + CNC programs from the 3D design ([newswire](https://www.newswire.co.kr/newsRead.php?no=909579)). "큐빅", "컷마스터", "우드옵티" could not be verified in this run **[unverified]** — in practice many Korean sink shops run OptiCut, Cut Rite (bundled with HOLZMA saws), MaxCut, or a free web tool (CutList Optimizer / cutlistevo) and keep the PDF/Excel in the order folder; ask for "재단도/재단 리스트 파일" per order.

**Deriving twin inputs from the cut list** (all deterministic, high confidence once the file is in hand):
- *Panels per order* = Σ qty in the parts list; *sheets per order* = board summary; *re-nesting rate* = jobs re-optimised (file versions).
- *Edge-band metres* = Σ over parts of (L·[edge_front+edge_back] + W·[edge_left+edge_right])·qty, from the per-edge flags (OptiCut/PolyBoard export them; Cut Rite parts summary usually has an "edging" column). This is the edge-bander's service-time driver (m/min × metres + per-part handling).
- *Hole count / boring time*: not in the nesting file; comes from the CAD/CNC program (PYTHA, Cabinet Vision, intelliDivide Nesting). If absent, use part-type rules (측판: 32 mm system holes 2 rows; 선반: 4 pins; 도어: 2 hinge cups + plate holes) **[estimate]** and calibrate against observed boring time in week 1.
- *Cut sequence / saw time*: Cut Rite "run" report or intelliDivide "production time"; otherwise count cuts per pattern (strips + crosscuts) → saw cycle = cuts × t_cut + sheets × t_load.

---

## 3. Non-intrusive machine-state sensing for 2 weeks

**Per-machine CT vs single-feeder NILM.** Industrial NILM papers are encouraging but not plug-and-play: the thermoform/milling case study reached ≥85 % accuracy using only aggregate V/I with event features ([arXiv 1912.01500](https://arxiv.org/html/1912.01500)); an operating-state + grey-wolf method reports ≥90 % per load ([Applied Energy](https://www.sciencedirect.com/science/article/abs/pii/S0306261923012989)); ANN disaggregation was validated on a compressed-air system ([Energy and AI 2024](https://www.sciencedirect.com/science/article/pii/S2666546824000739)); an active-learning study got 23–90 % depending on labelling budget ([Energy Informatics 2025](https://link.springer.com/article/10.1186/s42162-025-00517-5)); and a 2026 textile paper disaggregates *identical* induction motors with event detection ([arXiv 2601.01616](https://arxiv.org/pdf/2601.01616)). For 5–10 woodworking machines where the dust collector (often the largest load) and the panel saw/edge bander/CNC all have similar inductive signatures, single-feeder NILM is a research project, not a 2-week measurement. **Recommendation: one CT per machine (or per machine feeder), plus one 3-phase meter on the main feeder** so the sum can be reconciled with the KEPCO 15-min data.

**Hardware options.**
- *Shelly Pro 3EM-120A* (DIN rail, 3×120 A clamps, Wi-Fi/LAN/BT, MQTT, Modbus-TCP, ~1 % accuracy, 60 days of 1-min on-device history; ~€120–150 / £125–150 in 2026) ([Pi Hut](https://thepihut.com/products/shelly-pro-3em-120a), [netxl](https://www.netxl.com/energy-management/shelly-pro-3em-120-amp-3-phase-energy-meter.md)). Use one on the main feeder; its three channels can alternatively be used as three single-phase machine monitors.
- *ESP32 + SCT-013 with ESPHome `ct_clamp`*: the sensor reads an ADC source; `sample_duration` raises accuracy; calibrate with `calibrate_linear` against a clamp meter ([ESPHome docs](https://esphome.io/components/sensor/ct_clamp/)). Use the 1 V-output SCT-013-030/050 variants (internal burden) with a 1.65 V bias; set ADC `attenuation: 12db`. For 3-phase motors clamp **one phase only** — state detection does not need power, only current.
```yaml
sensor:
  - platform: adc
    pin: GPIO34
    id: adc_m1
    attenuation: 12db
  - platform: ct_clamp
    sensor: adc_m1
    name: "edgebander_current"
    sample_duration: 200ms
    update_interval: 1s
    filters:
      - calibrate_linear:
          - 0.0 -> 0.0
          - 0.0128 -> 9.3   # raw -> amps measured with a clamp meter
mqtt:
  broker: 192.168.0.10
```
- *Emporia Vue 2 (16 CT)* with the open-source `emporia-vue-local` ESPHome firmware gives fully local data every 5 s ([repo](https://github.com/emporia-vue-local/esphome)); **Vue 3 is cloud-only (1-min averages) with no supported local firmware** ([HA forum](https://community.home-assistant.io/t/emporia-vue-3/915845)) — buy Vue 2 or avoid.
- *Vibration*: an ADXL345/MPU6050 on the machine frame + ESP32 (RMS over 1 s) works for machines whose spindle runs continuously only when cutting; BLE tags/commercial units (IoTFlows SenseAi etc.) exist but are not needed. Vendor guidance quotes CT at $50–200/machine with 90–95 % run/stop accuracy vs accelerometers at $100–500 ([fabrico](https://www.fabrico.io/blog/oee-software-iot-sensors-legacy-equipment/)).
- *Optical cycle counter*: a retro-reflective photoelectric sensor (e.g. Omron E3JK-R4M1, ~₩25–40k **[estimate]**) at the edge-bander infeed into ESPHome `binary_sensor` + `pulse_counter` → parts/min; the edge bander's current trace alone cannot count parts.
- *Sound*: an I2S MEMS mic + Edge Impulse keyword-style classifier (running/idle/off) is viable on ESP32 but needs ~30 min of labelled audio per machine; use it only where clamping is impossible (e.g. hand tools).

**Current → off/idle/busy/cycle count** (threshold + hysteresis + minimum duration; tested on a synthetic trace: 5 cycles recovered, busy/idle/off seconds summed):
```python
def states_from_current(ts, amps, off_on=0.3, busy_on=4.0, busy_off=3.0, min_dur_s=3):
    st, states = "off", []
    for a in amps:
        if st == "off" and a > off_on: st = "idle"
        elif st != "off" and a <= off_on*0.8: st = "off"
        if st == "idle" and a >= busy_on: st = "busy"
        elif st == "busy" and a <= busy_off: st = "idle"
        states.append(st)
    seg = pd.DataFrame({"t": ts, "s": states})
    seg["k"] = (seg.s != seg.s.shift()).cumsum()
    seg = seg.groupby("k").agg(s=("s","first"), t0=("t","first"), t1=("t","last"))
    seg["dur"] = (seg.t1 - seg.t0).dt.total_seconds()
    seg.loc[seg.dur < min_dur_s, "s"] = seg.s.shift()          # absorb glitches
    seg["k2"] = (seg.s != seg.s.shift()).cumsum()
    return seg.groupby("k2").agg(s=("s","first"), t0=("t0","first"), t1=("t1","last"))
# cycles = number of 'busy' segments; service time = busy duration; idle = waiting for work/operator
```
Tuning rules from practice: sample ≥10 Hz RMS at the sensor (ESPHome does this inside `sample_duration`), log at 1 Hz, set `busy_on` at idle_RMS + 30–50 % of (busy−idle), hysteresis ≈ 10–20 % of the band, min duration ≥ 2–3 s; an SCADA retrofit guide gives the same advice (≥10 Hz sampling, 200–500 ms running RMS, threshold with margin above idle) ([industrialmonitordirect](https://industrialmonitordirect.com/blogs/knowledgebase/detecting-machine-run-state-in-scada-when-no-idle-signal-exists)). Learn thresholds per machine from the first day's histogram (bimodal → k-means with k=3). Related open code: OpenEnergyMonitor emonTx/emonPi firmware (CT RMS, multi-channel), ESPHome `ct_clamp`, NILMTK for event detection.

**Recommended 2-week kit (≤ ₩500k, prices are 2026 Korean retail estimates):**
| Item | Qty | ₩ (est.) | Purpose |
|---|---|---|---|
| Shelly Pro 3EM-120A | 1 | 200,000 | main feeder kW/kWh at 1-min, reconciles with KEPCO |
| ESP32 DevKit + SCT-013-030 (1 V) + bias board | 8 | 8×15,000 = 120,000 | one phase per machine, 1 Hz current |
| Photoelectric retro-reflective sensor + reflector | 2 | 60,000 | edge-bander / packing cycle counts |
| MPU6050/ADXL345 modules | 2 | 10,000 | hand-sanding bench / press (no clamp point) |
| Raspberry Pi 4 (or old laptop) + 1 TB SSD | 1 | 90,000 (SSD) | Mosquitto + SQLite/CSV logger + NTP server |
| Wi-Fi AP/extender, DIN boxes, cable | — | 20,000 | |
| **Total** | | **≈ ₩500,000** | |

**Install plan.** Day 0: licensed electrician (전기공사업 면허) opens the 분전반, fits the 3EM on the incoming 3-phase and clamps one phase per machine breaker, labels breakers → machine map; everything else is non-contact. Day 1: walk each machine through off/idle/one cycle while a person logs wall-clock times (this is the labelling set). Days 1–14: log at 1 Hz to MQTT → a Python subscriber writing `readings(machine, ts_utc, amps)` to SQLite (WAL mode) and a daily CSV; 10 machines × 1 Hz × 2 weeks ≈ 12 M rows ≈ 400 MB in SQLite. **Clocks:** run `chrony` on the Pi as NTP server, point ESPHome (`time: platform: sntp`) and all cameras at it; ESP32 RTC drift is tens of ms/day with SNTP, cameras can drift seconds — log a once-daily "sync event" (switch a machine on while a camera watches) and correct offsets afterwards.

---

## 4. Video-derived data from 3 fixed cameras

**Beyond people tracking.**
- *Gate crossings (carts, forklifts, pallets)*: `sv.LineZone(start, end)`; `crossed_in, crossed_out = line.trigger(detections)` requires `tracker_id`; since **supervision 0.31.0 `sv.ByteTrack` was removed — use `ByteTrackTracker` from the `trackers` package** ([count-in-zone how-to](https://supervision.roboflow.com/latest/how_to/count_in_zone/)). Detector: YOLO11/RF-DETR fine-tuned on 200–400 frames of *your* carts (COCO has no "cart" class).
- *Queue length*: `sv.PolygonZone(polygon)` per buffer area; `zone.trigger(detections)` returns the in-zone mask, `zone.current_count` the count; draw polygons with the PolygonZone web tool ([blog](https://blog.roboflow.com/how-to-count-objects-in-a-zone)). Log `(ts, zone, count)` every second → WIP time series per buffer, the single most valuable video output for the twin.
- *Machine busy/idle from ROI motion*: frame-difference or MOG2 background subtraction inside an ROI on the moving part (saw carriage, bander belt), mean foreground ratio > τ for ≥3 s → busy; use the same hysteresis code as §3.
- *Stack/andon light colour*: crop the lamp ROI, HSV threshold (green/amber/red), majority vote over 1 s; a 2020 paper does exactly this with detection + colour classification ([arXiv 2004.11187](https://arxiv.org/abs/2004.11187)). Colour-to-state maps are machine-specific — confirm with the operator.

```python
import supervision as sv, numpy as np
from trackers import ByteTrackTracker
line = sv.LineZone(start=sv.Point(100, 600), end=sv.Point(1800, 600))
buffer = sv.PolygonZone(polygon=np.array([[300,200],[900,200],[900,700],[300,700]]))
tracker = ByteTrackTracker()
for frame_idx, frame in enumerate(sv.get_video_frames_generator("cam2.mp4")):
    det = sv.Detections.from_ultralytics(model(frame)[0]); det = tracker.update(det, frame)
    det = det[det.tracker_id != -1]
    crossed_in, crossed_out = line.trigger(det)
    inside = buffer.trigger(det)
    log.append((frame_idx/FPS, line.in_count, line.out_count, int(inside.sum())))
```

**Privacy-preserving processing.** Run detection on-device (Frigate NVR or a Python service on the Pi/laptop with a Coral/GPU), store **only** `(ts, cam, class, tracker_id, bbox, zone)` rows and aggregate counts; delete raw video after the 2-week window or keep face-blurred clips only. Ultralytics ships `solutions.ObjectBlurrer(classes=[0], blur_ratio=0.5)` / `yolo solutions blur classes="[0]"` ([object blurring guide](https://docs.ultralytics.com/guides/object-blurring/)); a paper notes solid fill is safer than blur when the output is machine-processed later ([dev.to write-up](https://dev.to/laythayache/real-time-video-anonymization-at-30-fps-on-a-35-computer-2gkl)). Under 개인정보보호법 §25 post the CCTV notice (목적·촬영범위·시간·관리책임자) and collect written consent from workers for the 2-week study; frame it as line/queue measurement, not performance monitoring.

**Storage** **[estimate]**: a static factory scene at 1080p/5 fps H.264 encodes at roughly 0.5–2 Mbit/s (variable bitrate, CRF 23–28). 3 cameras × 14 days × 9 h = 378 camera-hours → **≈85 GB @0.5 Mbit/s, ≈170 GB @1 Mbit/s, ≈340 GB @2 Mbit/s**; H.265 roughly halves this. A 1 TB SSD covers the worst case plus the sensor DB. If only derived tracks are kept, the output is < 1 GB.

---

## 5. KEPCO data and 2026 industrial tariffs

**What you can actually get.**
- *AMI granularity*: 15-min interval data exists for AMI (지능형 전력량계) customers; all 고압 customers have electronic meters with load-profile (LP) data. 파워플래너 (pp.kepco.co.kr / app) is only for AMI customers and shows 시간대별 usage and 예상요금; blogs report Excel download of 사용내역 but the official feature list for 고압 사업자 could not be confirmed **[unverified]** ([brunch guide](https://brunch.co.kr/@60f53b767dfe4bf/58), [App Store listing](https://apps.apple.com/kr/app/id1164394809)). 한전ON (online.kepco.co.kr) covers 청구/납부 and, where AMI exists, 시간대별 사용량 ([dnublog 2026](https://dnublog.co.kr/2026/07/05/%ED%95%9C%EC%A0%84on-%EC%A0%84%EA%B8%B0%EC%9A%94%EA%B8%88-%EC%A1%B0%ED%9A%8C%EC%99%80-%EC%82%AC%EC%9A%A9%EB%9F%89%C2%B7%EC%98%88%EC%83%81%EC%9A%94%EA%B8%88-%ED%99%95%EC%9D%B8-%EB%B0%A9%EB%B2%95/)).
- *Practical route*: have the factory owner (고객번호 holder) (1) log into 한전ON → 사용량 조회 → 시간대별, and (2) ask the 관할 한전 지사 in writing for "15분 단위 LP(부하) 데이터 엑셀" for the last 12 months — 영업소 routinely supply this to 고압 customers for 요금제 선택 consulting **[practice, unverified]**.
- *Open data / API*: the 전력데이터 개방포털 (bigdata.kepco.co.kr) and EN:TER data platform have a 고객용 service (조회/다운로드 only) and a 사업자용 포털 where a third party collects data after 고객 정보제공 동의 ([EDS-Market page](https://edsm.kepco.co.kr/cmsmain.do?scode=S02&pcode=000313&redirect=Y), [EN:TER](https://en-ter.co.kr/ft/biz/engr/engrInfo/info5.do)). For a one-off study the owner's download is simpler than registering as a 사업자.

**2026 tariff reform (산업용(을)).** The 계절·시간대별 전기요금 개편안 took effect **2026-04-16** for 산업용(을) (deferral to 2026-10-01 possible; 514 sites deferred); 일반용·교육용·산업용(갑)II from 2026-06-01. Changes reported: the former daytime 최대부하 block (reported as 11–15 h, some sources 9–15 h) becomes 중간부하, cutting up to **16.9 ₩/kWh**; **18–21 h becomes 최대부하**; night (경부하) **+5.1 ₩/kWh**; 봄·가을 주말·공휴일 낮 **50 % off** the energy charge ([korea.kr policy brief](https://www.korea.kr/news/policyNewsView.do?newsId=148960823), [전기신문](https://www.electimes.com/news/articleView.html?idxno=367002), [enersentry analysis](https://enersentry.com/%EC%82%B0%EC%97%85%EC%9A%A9-%EC%A0%84%EA%B8%B0%EC%9A%94%EA%B8%88-%EA%B0%9C%ED%8E%B8/)). Baseline 기본요금 for 산업용(을) 고압A: 선택I ≈ 7,220, 선택II ≈ 8,320, 선택III ≈ 9,810 ₩/kW (2025 tables; 선택II confirmed in the [KFTC price survey](https://data.cmpi.or.kr/program/board/2025.04.01%20%EC%8B%9C%ED%96%89.pdf)) **[선택I/III from memory — verify]**. Exact post-reform ₩/kWh by season/band could not be retrieved in this run; download the current 전기요금표 from KEPCO Cyber branch (https://cyber.kepco.co.kr/cyber/updata/down/elec_total.pdf) and encode it as a `(season, weekday/weekend, hour) → band → rate` lookup; add 기후환경요금 (~9 ₩/kWh) and 연료비조정요금 (±5 ₩/kWh) **[estimate]**. A 20–50-person furniture plant is usually 산업용(을) 고압A 선택II (or 산업용(갑) low-voltage if < 300 kW contract) — read the bill header.

**Attributing kWh to machines (reconciliation).** Inputs: bill/15-min kWh (truth at feeder level), nameplate kW per machine, measured current traces (§3) and states. Method: (1) per machine, `P_state = V_line·√3·I_rms·pf` with pf from nameplate (0.8 motors) or measured by the 3EM for the aggregate; (2) energy per 15-min slot = Σ_machines Σ_states P_state·t_state; (3) residual = KEPCO slot kWh − Σ machines = lighting/compressor/dust-collector/heating — regress residual on time-of-day and busy-fraction to split it; (4) solve a non-negative least-squares scaling of per-machine load factors so the sum matches the KEPCO 15-min series (two weeks ≈ 1,300 slots, > enough); (5) report per-machine kWh/part and kWh/busy-h with the RMSE of step (4) as the confidence. The 3EM-on-main-feeder plus KEPCO data gives two independent aggregate series — if they disagree by > 3 %, suspect a missed feeder or CT clamp orientation.

---

## 6. Reconciliation, gap-filling and the data-quality scorecard

**One parameter, several witnesses.** Each twin parameter (routing, service time, setup, batch size, arrivals, availability, energy) gets *candidate values* from up to four witnesses — Records (ERP/작업일보), Sensing (current/beam-break), Observation (time study/video), Expert (supervisor). Triangulation rules:
1. **Precedence by physics**: for *service time* trust Sensing > Observation > Records > Expert; for *routing/variants* trust Records (full population) but validate rework loops against Sensing/video; for *waiting* use Records' gaps only after removing non-working hours (`business_hours=True`) and cross-check with queue counts from video; for *batch rules* use `discover_batches` on records and confirm cart counts at the gate.
2. **Agreement test**: two witnesses agree if their medians differ by < 20 % (times) or < 1 unit (counts); agreement upgrades the confidence tag one level.
3. **Population vs sample**: a sensor value from 2 weeks represents the product mix of those weeks; re-weight by the 12-month order mix from the ERP (stratify by 품목군) before freezing distributions.
4. **Gap filling order**: measured → regression on drivers (edge metres, holes, parts, sheets) → analogy to a similar machine → expert estimate; every filled cell carries `source` and `method`.
5. **Mass balance**: Σ panels cut (nesting) = Σ panels edged (beam-break) = Σ panels assembled (작업실적) ± scrap; Σ machine kWh = KEPCO; Σ cart passes ≈ orders × carts/order. Imbalances > 5 % trigger investigation, not averaging.
6. **Uncertainty**: separate *stochastic* (fit a distribution), *parameter* (bootstrap CI from n samples) and *model* uncertainty, as recommended for simulation input modelling ([Biller & Mokashi, WSC 2018](https://www.informs-sim.org/wsc18papers/includes/files/279.pdf)); with scarce data a metamodel-assisted bootstrap still yields usable CIs on throughput and tells you which input to measure more ([Matta et al.](https://re.public.polimi.it/handle/11311/1218180)).

**Confidence tags per parameter** (store next to each value): **A** = measured by ≥2 independent witnesses, n ≥ 30, agree; **B** = one measured witness, n ≥ 30, or two agreeing small samples; **C** = derived/regressed/imputed or OCR-extracted and unverified; **D** = expert estimate only. Twin outputs must carry the lowest tag among their inputs; scenario conclusions relying on C/D inputs are flagged in the report.

**Data-quality scorecard (per source, per field; 0–1 each, report the product and the minimum):**
| Dimension | Metric | Example threshold |
|---|---|---|
| Completeness | share of expected rows/fields present (e.g. 작업실적 rows / 작업지시 × 공정) | ≥ 0.9 |
| Timeliness/resolution | median timestamp resolution (day/shift/minute/second) | minute for routing, second for sensing |
| Accuracy | agreement with a reference (OCR vs manual 10 % re-key; ERP qty vs nesting qty) | ≥ 0.95 |
| Consistency | mass-balance closure across sources | ≤ 5 % gap |
| Coverage | % of product mix / machines / shifts observed | ≥ 80 % of 12-month mix |
| Clock integrity | max offset between sources after correction | ≤ 2 s sensors, ≤ 1 min records |
| Traceability | % of parameter values with `source`, `method`, `n`, `tag` filled | 100 % |

**Deliverable for the twin**: a single `parameters.csv` (`parameter, machine/product, value, unit, distribution, n, ci_low, ci_high, source, method, tag, last_updated`) plus `scorecard.csv`; the twin reads only from these, and every re-run of the §1 script, the §3 state extraction and the §5 reconciliation regenerates them.

---

### Open items (search budget exhausted — can continue on request)
1. Exact post-2026-04-16 ₩/kWh table for 산업용(을) 고압A 선택I/II/III and the official band hours (download KEPCO elec_total.pdf).
2. Official statement of what 한전ON/파워플래너 lets a 고압 사업자 download (15-min Excel).
3. Korean nesting products "큐빅/컷마스터/우드옵티" — only 다임소프트 and PYTHA(한스코) were confirmed.
4. Exact ecount production-screen field list (training PDF URL found but not fetchable from this sandbox).

Local validation artefacts: `/tmp/claude-0/-home-user-claude-mem/508c8abb-4a55-5c43-94f1-9a63dde73d06/scratchpad/code/pm_demo.py` (pm4py end-to-end on a synthetic furniture log) and `.../code/state_demo.py` (current → state/cycle algorithm).