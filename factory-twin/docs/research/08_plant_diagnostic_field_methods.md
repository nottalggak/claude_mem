# One-Day Plant Diagnostic for a Korean Furniture Factory: Field Methods, Instruments, and Protocol

**Research note.** WebSearch results (~55 queries, EN + KR) were usable; WebFetch failed on DNS for every page, and the search budget ran out before the last ~8 planned queries (forklift queueing, dust-collection CFM, DES input-data checklists, Woodweb layout threads, Strategos tool detail). Items marked **[memory]** are reproduced from standard references (ILO *Introduction to Work Study*; Muther *SLP*; Tompkins et al. *Facilities Planning*; Rother & Shook *Learning to See*; Goodson, *HBR* May 2002) and should be spot-checked against the cited page before being printed on field forms. Korean legal text marked **[verified]** was confirmed via law.go.kr / lbox extracts; **[memory]** means verify at law.go.kr.

---

## 1. Classic IE data-collection instruments (fields to capture)

### 1.1 Flow process chart (ASME 5 symbols)
Symbols: ○ Operation, ⇨ Transport, □ Inspection, D Delay, ▽ Storage (ASME 1947 set from Gilbreth) — [Wikipedia](https://en.wikipedia.org/wiki/Flow_process_chart), [EMU lecture notes](https://staff.emu.edu.tr/orhankorhan/Documents/courses/ieng301-mane301/Lecture-Notes/spring2019-2020/CH7.pdf). Three types: material-type, man-type, equipment-type.

ILO form header/fields **[memory]**:
```
FLOW PROCESS CHART   Chart No.__ Sheet No.__ of __   Type: Material / Worker / Equipment
Activity: ____  Method: Present / Proposed   Location: ____  Operative(s): ____ Clock No.__
Charted by: ____ Date: ____   Approved by: ____
SUMMARY: Activity | Present | Proposed | Saving   (rows: ○ ⇨ □ D ▽, Distance (m), Time (man-min), Cost: labour/material, TOTAL)
BODY columns: No. | Description | Qty | Distance (m) | Time (min) | ○ ⇨ □ D ▽ (tick/line) | Remarks
```
Add for a digital-twin purpose: *container/unit load*, *who moves it (role)*, *handling device*, *batch size at step*, *queue position (FIFO/LIFO/random)*.

### 1.2 From-to chart / flow matrix
Rows = From, columns = To, cells = loads (or trips) per period; listing elements in general flow order makes entries **below the diagonal = backtracking** — [Binus](https://base.binus.ac.id/business-engineering/2025/12/05/from-to-chart-to-measure-flow-efficiency/), [Woodworking Network Ch.3 (Art Raymond)](https://www.woodworkingnetwork.com/management/chapter-3-rationalizing-your-plant-layout). Raymond's furniture version: convert component volumes to *cart or pallet loads* using process-sequence charts, build one matrix per product, sum for the representative mix. Companion distance matrix (rectilinear, measured along aisles, not Euclidean) gives **flow intensity = Σ loads × distance** (load-metres/day) — [FE study guide](https://open-exam-prep.com/study-guides/fe-industrial/facilities-planning-material-handling/layout-design-from-to-slp), [Total Flow Volume lecture](https://resourcer.yolasite.com/resources/E212-S06-Total%20Flow%20Volume%20.pdf).

### 1.3 Activity relationship (REL) chart — Muther
Closeness: A absolutely necessary / E especially important / I important / O ordinary / U unimportant / X undesirable; line convention 4-3-2-1 lines, zig-zag for X; guideline: A and X ≤ ~5% each, U ≈ 50% — [Wikipedia](https://en.wikipedia.org/wiki/Activity_relationship_chart), [Muther RMA procedure](https://richardmuther.com/wp-content/uploads/2014/06/RMA%201111%20Procedure%20for%20Making%20Relationship%20Diagram.pdf). Reason codes (sources vary; common SLP set, [textile slides](https://www.slideshare.net/slideshow/analytical-tools-for-textile-plant-layoutpptx/261183817), [ExcelDemy](https://www.exceldemy.com/activity-relationship-chart-excel/)):
```
1 Flow of material   2 Ease of supervision   3 Common personnel   4 Contact necessary
5 Convenience        6 Same equipment/tools  7 Share records/paperwork
8 Noise / dust / vibration / fire-safety (usually the X reasons)   9 Service frequency
```
Field form: pair list (activity i, activity j) × rating × reason code × "who said so" (owner/foreman/observed).

### 1.4 Systematic Layout Planning — PQRST key and procedure
Input key: **P**roduct (what), **Q**uantity (how much), **R**outing (process sequence), **S**upporting services, **T**ime (when/how long) — [open-exam-prep SLP](https://open-exam-prep.com/study-guides/pe-industrial/facility-layout-material-handling/systematic-layout-planning). Four phases: Location → General overall layout → Detailed layout → Installation. SLP pattern of procedures **[memory]**: 1 PQRST input → 2 Flow of materials (from-to) → 3 Activity relationships (REL) → 4 Relationship diagram → 5 Space required → 6 Space available → 7 Space-relationship diagram → 8 Modifying considerations → 9 Practical limitations → 10 Layout alternatives X/Y/Z → 11 Evaluation (weighted factors) → selected plan. Muther's "Four ways to analyze flow" ([RMA training PDF](https://richardmuther.com/wp-content/uploads/2021/06/SLP-On-line-Training-8-Four-Ways-to-Analyze-Flow-of-Materials.pdf)): operation process chart (few products), multi-product process chart (several), from-to chart (many products, none dominant), and sampling of representative parts. Intensity is ranked and calibrated to vowel letters (A = top ~10% of flow intensity, then E, I, O) **[memory]**.

### 1.5 String / spaghetti diagram
Scale plan + pins + thread (string diagram) or pen trace (spaghetti) of one person/one product for a defined period; measure thread length → distance — [NPTEL](https://archive.nptel.ac.in/content/storage2/courses/112107142/part1/lecture3.htm). Fields: operator/part ID, start–end time, colour per entity, each leg: from, to, purpose (fetch part/tool/info/ask), distance (m), time-stamp, carried load. For a twin, also record *walking speed* (m/s) and *aisle used*.

### 1.6 Multiple activity (man-machine) chart
Columns per worker/machine on a common time scale; shows idle time to re-sequence — [Scribd work-study notes](https://www.scribd.com/presentation/426156306/Work-study). Fields: entity, element description, start/end (s), state code (working / loading / waiting / idle / walking), cycle length, machine auto-run time vs. attended time. Essential for CNC + edgebander cells where one operator tends 2 machines.

### 1.7 Travel chart
Same matrix as from-to but for **people** (trips between stations, by role) — [SlideShare recording techniques](https://www.slideshare.net/slideshow/recording-techniques-used-in-method-study-ppt/30608193).

### 1.8 Work sampling observation sheet
Random instantaneous observations; % in state ≈ share of observations — [NPTEL lecture 10](https://archive.nptel.ac.in/content/storage2/courses/112107142/part1/lecture10.htm), [Scribd form](https://www.scribd.com/document/406902255/Work-Sampling-Data-Forms). Sheet fields: company/area, date, analyst, random time list (Excel RAND), per observation: subject (operator/machine ID), activity code, location, remark. Suggested code set for furniture: VA-processing, setup, load/unload, walk-fetch, wait-material, wait-crane/forklift, rework, inspect, clean/dust, talk/instruction, absent, machine auto-run (no operator). Sample size n = Z²p(1−p)/e² (e.g., p=0.5, ±5%, 95% → 384 obs).

### 1.9 Time study observation sheet
Standard time = Observed × Rating × (1 + allowance) — [KSU direct time study](https://fac.ksu.edu.sa/sites/default/files/5-b_direct_time_study_-_p1_ams_mar27_17.pdf), [EMU CH22](https://staff.emu.edu.tr/orhankorhan/Documents/courses/ieng301-mane301/Lecture-Notes/spring2019-2020/CH22.pdf). Fields **[memory, ILO form]**: study no., operation, part/drawing, machine & settings (feed m/min, tool), operator & experience, conditions, element list with breakpoints, per-cycle watch readings (R) and element times, rating (BS 0–100 or Westinghouse), basic time, allowances (personal 5%, basic fatigue 4%, variable fatigue, contingency — typical totals 10–20%), standard time, units/cycle, foreign elements, start/finish/elapsed check.

### 1.10 SMED setup observation sheet
Internal vs external (Shingo) — [Minitab QCO form](https://support.minitab.com/en-us/workspace/help-and-how-to/forms/form-tools/lean-improvement/quick-changeover-qco-smed), [SafetyCulture](https://safetyculture.com/checklists/smed/), [Enna setup combination sheet](https://enna.com/learning-center/using-the-setup-combination-work-sheet). Fields: machine, from-product → to-product, date, crew; per element: seq, description, start/end, duration, I/E classification, category (adjust / find-fetch / clean / trial-run / walk / wait), distance walked, tools used, could-be-external (Y/N), first-good-piece time, number of trial pieces scrapped.

### 1.11 OEE six-big-losses data form
Availability (breakdowns, setups/changeover), Performance (minor stops, slow cycles), Quality (startup rejects, production rejects) — [Tennessee MEP OEE guide](https://tmep.cis.tennessee.edu/oee-implementation-guide), [PlantRun](https://plantrun.co.uk/oee-overall-equipment-effectiveness.html). One-day form per key machine: planned production time, ideal cycle time (nameplate feed), units out, good units, downtime log (start, end, reason code, who fixed), minor stops tally (<5–10 min), speed actually run vs. rated. Benchmarks: median ~60%, top quartile ~75%, "world class" 85% — [TeepTrak](https://teeptrak.com/en/wp-json/wp/v2/posts/94795).

### 1.12 VSM data box and current-state procedure
Data box: C/T (s, machine vs operator separately), C/O (min), uptime %, EPEI / batch size, # operators, shifts & available time (minus breaks), scrap/rework %, pack/lot size, product variants — [Reliable Plant](https://www.reliableplant.com/Articles/Print/11238?id=11238), [EMS](https://emsstrategies.com/dd120103article1.html), [Enna data box](https://enna.com/learning-center/using-the-vsm-data-box-form). Procedure: start at customer (demand/takt) → walk from shipping upstream with stopwatch → process boxes + data boxes → inventory triangles (count pieces, convert to days) → push/pull arrows → information flow (who schedules each step, how often) → timeline (PT vs lead time) — [Rework](https://resources.rework.com/vi/libraries/process-management/value-stream-mapping).

### 1.13 Gemba walk checklist and 5S audit
Gemba: ask "what/why", not "why don't you"; theme-based (7 wastes, 5S, 4M, safety) — [Oxmaint](https://oxmaint.com/checklist-center/gemba-walk-checklist), [ease.io template](https://ease.io/blog/gemba-walk-checklist-template). 5S audit: 25 items (5 per S), 0–4 scale is common but not standard — [Scribd 5S checklist](https://www.scribd.com/document/54165915/5s-Checklist), [Mettler-Toledo 5S audit](https://www.mt.com/dam/P5/labtec/11_Campaigns/2018/Lean-Lab/5S/GU_Lean_5S_Audit_EN.pdf); Korean 현장용 5S 평가 체크리스트 (통로·구획선 백색선 표시, 설비 주변 불요품, 바닥 오염 문항) — [예스폼](https://www.yesform.com/z_n/forms/view_iso/iso_404352.html).

---

## 2. Rapid diagnostics used by consultants

### 2.1 Goodson, "Read a Plant—Fast" (HBR May 2002) — Rapid Plant Assessment
Rating sheet: **11 categories**, each scored 1 poor / 3 below avg / 5 avg / 7 above avg / 9 excellent / 11 best-in-class; total 11–121 — [SafetyCulture RPA sheet](https://public-library.safetyculture.io/products/rpa-rating-2wvg30lh2mxnm4py), [maaw summary](https://maaw.info/ArticleSummaries/ArtSumGoodson2002.htm), [Tauber Institute "Rate Lean: Fast"](https://tauber.umich.edu/rate-lean-fast-0). Team of 4–5, no note-taking during the ~30-min tour, debrief immediately.

Categories: 1 Customer satisfaction · 2 Safety, environment, cleanliness, order · 3 Visual management system · 4 Scheduling system · 5 Use of space, movement of materials, product-line flow · 6 Levels of inventory and WIP · 7 Teamwork and motivation · 8 Condition and maintenance of equipment and tools · 9 Management of complexity and variability · 10 Supply-chain integration · 11 Commitment to quality.

**20 yes/no questions** (Q1–3 and Q20 confirmed via [The Auditor](https://www.theauditoronline.com/lean-rapid-plant-assessment-as-a-tool-for-more-effective-audits/) and [RPA tool PDF](http://immestudytour.weebly.com/uploads/1/0/2/9/102992016/rapid_plant_assessment_tool.pdf); remainder **[memory]**, wording may differ slightly from the HBR original):
1. Are visitors welcomed and given information about plant layout, workforce, customers and products?
2. Are ratings for customer satisfaction and product quality displayed?
3. Is the facility safe, clean, orderly and well lit? Is the air quality good and are noise levels low?
4. Does a visual labeling system identify and locate inventory, tools, processes and flow?
5. Does everything have its own place, and is everything stored in its place?
6. Are up-to-date operational goals and performance measures for those goals prominently posted?
7. Are production materials brought to and stored at line side rather than in separate storage areas?
8. Are work instructions and product quality specifications visible at all work areas?
9. Are updated charts on productivity, quality, safety and problem solving visible for all teams?
10. Can the current state of the operation be viewed from a central control room, status board or display?
11. Are production lines scheduled off a single pacing process, with appropriate inventory levels at each stage?
12. Is material moved only once, as short a distance as possible, and in appropriate containers?
13. Is the plant laid out in continuous product-flow lines rather than in "shops"?
14. Are work teams trained, empowered and involved in problem solving and ongoing improvement?
15. Do employees appear committed to continuous improvement?
16. Is a timetable posted for equipment preventive maintenance and continuous improvement of tools and processes?
17. Is there an effective project-management process, with cost and timing goals, for new-product start-ups?
18. Is a supplier certification process—with measures for quality, delivery and cost—displayed?
19. Have key product characteristics been identified, and are fail-safe (poka-yoke) methods used to prevent propagation of defects?
20. Would you buy the products this operation produces?

### 2.2 Lean waste walk — 8 wastes with observation prompts
DOWNTIME: Defects, Overproduction, Waiting, Non-utilized talent, Transportation, Inventory, Motion, Extra-processing — [LearnLeanSigma TIMWOODS template](https://www.learnleansigma.com/template/8-wastes-timwoods/) ("observe, document, categorize; don't fix during the walk"). Furniture-specific prompts: *Defects* — chipped edges, glue lines, re-sanding piles, "보류" tags; *Overproduction* — cut parts for orders not yet scheduled, over-nested sheets; *Waiting* — operator watching CNC run, assembly waiting for hardware/edgebanded parts; *Talent* — skilled bander operator stacking panels; *Transport* — pallets moved to "temporary" floor spots; *Inventory* — board stock, veneer, hardware, WIP between cut/band/bore; *Motion* — reaching across saw table, flipping panels, walking to get hardware; *Extra-processing* — hand sanding after CNC, double inspection.

### 2.3 Toyota TSSC-style diagnosis
TSSC works on-floor to build a *model line*; principles: customer first, people most valuable, kaizen, focus on the workplace — [LEI 2013 TSSC plenary](https://www.lean.org/wp-content/uploads/2022/04/2013_LTS_tssc_plenary.pdf). Practical TSSC first-visit lens **[memory]**: takt vs. actual cycle at the pacemaker; is there standardized work (sequence, takt, standard WIP) posted and followed; production analysis board (hourly plan vs actual with reasons); andon/abnormality visibility; 4M status; where WIP accumulates and why.

### 2.4 McKinsey/BCG-style operations diagnostic (one-day site visit)
No public checklist was found; the practice visible in sources: plant walk-throughs + interviews with each production-unit lead, gap vs best practice and improvement levers — [McKinsey blog](https://www.mckinsey.com/careers/life-at-mckinsey/our-culture-and-communities/mckinsey-women-blog/seeing-the-effects-of-a-basic-materials-engagement); OEE waterfall / loss tree from planned time down to OEE — [Oxmaint](https://oxmaint.com/industries/steel-plant/oee-loss-tree-analysis-for-manufacturing); DILO (Day-in-the-Life-Of) shadowing of supervisor/planner with 8-step guide — [SlideShare DILO guide](https://www.slideshare.net/slideshow/dilo-how-to-do-it-practical-guide/139545146); 48-hour OEE proof-of-concept at kickoff, diagnostic deck by week 2–3 — [TeepTrak (ex-BCG)](https://teeptrak.com/en/?p=89451). Typical one-day structure **[memory]**: 08:00 management interview + KPI pack request → 09:00 RPA-style tour → 10:00–12:00 bottleneck OEE snapshot + DILO → 13:00 data room (orders, routings, downtime logs, overtime) → 15:00 value-driver tree hypotheses (volume, OEE, labour productivity, material yield, lead time) → 16:30 read-out.

### 2.5 Shingo / AME plant tour lens
Shingo examiners observe *behaviour* (frequency, duration, intensity, scope of principle-based behaviour) rather than tools — [Shingo "Go and Observe"](https://shingo.org/?p=543), [Shingo awards](https://shingo.org/awards/). AllAboutLean's visit checklist: count workers doing value-adding work at an instant, machine utilization, inventory reach, order & cleanliness — [allaboutlean](https://www.allaboutlean.com/shop-floor-visit-checklist/).

### 2.6 Capturing tacit decision rules (scheduling, dispatching, nesting)
- Tacit knowledge is hard to verbalize; unstructured interviews bias toward rule-friendly parts — [ACM expert-systems abstract](https://www.springermedizin.de/doi/pdf/10.1145/63266.63288); eliciting *schedule repair* heuristics is especially valuable — [Toselli et al. 2016](https://bdu.siu.edu.ar/bdu/Record/I49-R155-61717); shop-floor heuristics/rules-of-thumb capture — [TU Delft](https://research.tudelft.nl/files/152458562/3544549.3585755.pdf).
- **Critical Decision Method** (Klein): semi-structured recall of a non-routine incident with sweeps and probes for cues, goals, options, basis of judgment, experience — [Otago DP 97-04](https://isgb.otago.ac.nz/infosci/nigel.stanger/Discussion_Papers/raw/master/Papers/1997/97-04/dp1997-04.pdf).
- Field technique for one day: (a) **"Show me yesterday's plan"** — take the actual whiteboard/Excel, ask why each job sits where it sits; (b) **think-aloud** while the planner builds tomorrow's cut list / nesting; (c) **critical incident**: "last time a rush order came in / the edgebander broke / veneer ran out — what did you do?"; (d) **paired comparison**: two real jobs, "which first, why?"
- Document as **IF–THEN–ELSE rules with priority and exception**: `R07 IF order.dueDate − today ≤ 2d AND panels not yet cut THEN cut on nesting CNC before any batch-optimised nesting; ELSE batch same-material sheets (priority 3; owner: 생산반장; observed/stated: stated; confidence: M)`. Capture also: trigger data source (Kakao message, ERP screen, phone), decision frequency, and who may override.

---

## 3. Flow analysis for layout decisions

**Building a from-to chart from one day:** (1) take last 4–12 weeks' orders/routings (ERP or job sheets) to get Q per product family; (2) take today's observed routings (flow process charts) to validate sequence and unit load; (3) convert quantities into *loads* (cart/pallet) per period; (4) sum per (from,to) pair; (5) distance matrix along real aisles; (6) intensity = loads × distance; rank pairs; (7) calibrate to A/E/I/O; (8) merge with non-flow reasons in the REL chart (supervision, noise/dust X, shared tools). Flow data is unreliable for highly dynamic job shops; pair with qualitative observation — [Binus](https://base.binus.ac.id/business-engineering/2025/12/05/from-to-chart-to-measure-flow-efficiency/). Total handling cost = Σ F_ij × C_ij — [Pressbooks OM](https://ecampusontario.pressbooks.pub/opsmgmt/?p=1689).

**Constraint register the layout study must record** (one row per constraint, with location on the plan, movability, cost):
- Column grid (bay x,y), clear height, floor slab thickness / point-load rating, floor level changes, pits.
- Dust extraction: main duct route, branch diameters, drops per machine, collector location, available CFM headroom (cannot verify CFM/velocity figures this session — search budget exhausted).
- Compressed air: compressor, receiver, ring main route, drop locations, pressure.
- Electrical: panel locations, 3-phase drops, busbar.
- Doors/docks: dock height, door widths, overhead-door clear height, which door is used for board inbound vs finished goods outbound.
- Fire egress routes, extinguisher/hydrant positions, spray booth zoning (hazardous area), paint storage.
- Crane rails, hoists, forklift and pedestrian aisles.
- Korean regulation items **(산업안전보건기준에 관한 규칙)**: 제22조(통로의 설치) ①안전한 통로 설치·유지 ②통로 표시 ③통로면으로부터 높이 2m 이내 장애물 금지 (예외 시 안전조치) **[verified]** — [law.go.kr 해석](https://www.law.go.kr/LSW/cgmExpcInfoP.do?cgmExpcDatSeq=23260&mode=2&ofiClsCd=350101), [lbox 제22조](https://lbox.kr/v2/statute/%EC%82%B0%EC%97%85%EC%95%88%EC%A0%84%EB%B3%B4%EA%B1%B4%EA%B8%B0%EC%A4%80%EC%97%90%EA%B4%80%ED%95%9C%EA%B7%9C%EC%B9%99/%EB%B3%B8%EB%AC%B8%20%3E%20%EC%A0%9C1%ED%8E%B8%20%3E%20%EC%A0%9C3%EC%9E%A5%20%3E%20%EC%A0%9C22%EC%A1%B0); 제28조 계단참(높이 3m 이내마다 너비 1.2m 이상), 제29조 천장 높이 2m **[verified]**; 제98조 차량계 하역운반기계 제한속도 지정 의무 (사내 10 km/h 관행) **[verified]** — [lbox 제98조](https://lbox.kr/statute/%EC%82%B0%EC%97%85%EC%95%88%EC%A0%84%EB%B3%B4%EA%B1%B4%EB%B2%95%EC%8B%9C%ED%96%89%EA%B7%9C%EC%B9%99/%EB%B3%B8%EB%AC%B8%20%3E%20%EC%A0%9C6%EC%9E%A5%20%3E%20%EC%A0%9C1%EC%A0%88%20%3E%20%EC%A0%9C98%EC%A1%B0), [korea.kr 브리핑](https://www.korea.kr/briefing/policyBriefingView.do?newsId=148887852); 제21조 통로의 조명(75럭스), 제26조 계단 강도(500 kg/m²), 제27조 계단 폭(1m 이상), 제3조 전도방지, 제17조 비상구 **[memory — verify]**. Note: the rule sets no numeric width for a general shop-floor aisle; the "통로 폭 80 cm" figure often quoted is not in 제22조.
- Forklift aisle width rule of thumb: **load length + right-angle stacking aisle + ~300 mm (12 in)** — [Damotech/Toyota](https://www.damotech.com/blog/why-aisle-width-matters-when-it-comes-to-pallet-rack-safety), [Raymond West](https://raymondwest.com/learn/blog/2021/sep/forklift-aisle-minimums); planning widths counterbalance 3.6–4.3 m, reach 2.4–3.0 m, VNA 1.5–1.8 m — [BigRentz](https://www.bigrentz.com/blog/forklift-aisle-width-requirements-osha-standards-and-planning-guide). KOSHA material: 지게차 전용통로 확보, 보행자 동선 분리, 10 km/h — [KOSHA 지게차 자료](https://oshri.kosha.or.kr/kosha/intro/northernGyeonggiBranch_A.do?mode=download&articleNo=449134&attachNo=254107).

**Fixed vs movable equipment sheet:** machine ID, footprint (incl. infeed/outfeed envelope — a beam saw/CNC needs sheet length on both sides), anchoring (bolted/grouted/free), services (dust Ø mm, air, 3-phase kW, water), relocation class (A free-standing <1 day; B needs rigging + service re-drop; C foundation/pit/booth, effectively fixed), and relocation cost = equipment + labour + rigging/transport rental, ABC-ranked — [MSPE 2025 relocation cost model](https://reference-global.com/2/v2/download/pdf/10.2478/mspe-2025-0045); utilities review first, 15–20% open floor for reconfiguration — [Robertson](https://robertsonsite.ca/blog/planning-process-for-plant-relocations), [Oxmaint layout guide](https://mail.oxmaint.com/industries/manufacturing-plant/manufacturing-plant-layout-design-best-practices-guide).

---

## 4. Material handling analysis

- **Material handling equation:** Material (what) + Move (where, when) = Method (how, who); analyse materials and moves before choosing equipment — [open-exam-prep MH](https://open-exam-prep.com/study-guides/pe-industrial/facility-layout-material-handling/material-handling-equipment), [UCF expert system](https://stars.library.ucf.edu/rtd/4112). Apple (1972/77) attributed up to 80% of production activity and 50–90% of cost to handling — [Wiley excerpt](https://catalogimages.wiley.com/images/db/pdf/9780470170700.excerpt.pdf). MHI 10 principles (planning, standardization, work, ergonomic, unit load, space utilization, system, automation, environmental, life-cycle cost) **[memory]** — [MHI](https://og.mhi.org/about).
- **Unit load definition sheet:** container type (pallet 1,100×1,100 KR standard / panel cart / A-frame / bundle), dims, tare, pieces per load, stack height, stability (strapped?), who builds it, where it is broken down.
- **Handling frequency & cost per move:** cost = Σ moves × cost/move; forklift ~US$15–25/h operating, labour 60–70% of MH cost, typical move 4–12 min, empty (deadhead) travel 35–50% of travel time (vendor figures) — [FleetRabbit](https://fleetrabbit.com/industry/manufacturing-fleet/forklift-fleet-cost-per-pallet-move-analysis). Field capture: per trip — origin, destination, loaded/empty, load type, start/end time, distance, waits (door, blocked aisle, other truck).
- **Forklift queueing:** treat forklift as server(s), move requests as arrivals; collect inter-request times and service (trip) times; use M/M/c or simulation (search on this was cut off — Dukic et al. fleet-sizing paper [here](https://simlab.mas.bg.ac.rs/_media/istrazivanje/fme/vol46/3/7_g_dukic_et_al.pdf)).
- **Gate/door traffic study:** station an observer (or camera) at each door/aisle junction; tally in 15–30 min bins: vehicle type, direction, loaded/empty, load type, pedestrian crossings; run whole shift to catch shift-start/lunch peaks. Flow Planner-style structure (quantity FROM/TO via METHOD and CONTAINER) — [PMC Flow Planner](https://pmcorp.com/wp-content/uploads/2020/05/Flow_Planner_PDF_7744A91B6C829.pdf).

---

## 5. People / workforce analysis

- **Skills matrix (ILUO):** I = in training, L = performs to standard, U = autonomous, O = can train others; built from standardized operations, not HR titles; target ≥2 qualified per task per shift — [merca.team](https://merca.team/en/lean-competency-matrix/), [AG5 ILUO template](https://www.ag5.com/templates/iluo-skills-matrix-template/). Fields: operator × operation, level, certified date, last performed, safety licence (지게차 운전기능사, 프레스/목재가공기계 특별교육).
- **Yamazumi:** stacked bar per operator/station (VA / NVA-necessary / waste) vs takt line — [fabrico](https://www.fabrico.io/blog/yamazumi-chart/), [fabriq](https://fabriq.tech/en/2025/10/07/yamazumi-chart-lean-manufacturing-line-balancing/).
- **Takt / line balancing:** takt = available time / demand; N_min = ⌈Σt_i / C⌉; balance delay = (n·C − Σt)/(n·C); smoothness index = √Σ(t_max − t_j)²; inputs: task times, precedence, available time, demand — [open-exam-prep](https://open-exam-prep.com/study-guides/fe-industrial/manufacturing-production-systems/line-balancing-throughput-takt-time).
- **Absenteeism/overtime:** last 3 months by person/day, overtime hours by week, temp/day-labour (일용직) use, foreign-worker share and language, shift pattern, break times.
- **Ergonomics quick screens (data fields):** REBA — Group A neck/trunk/legs + load, Group B upper arm/lower arm/wrist + coupling, + activity → 1–15, action levels 1 negligible / 2–3 low / 4–7 medium / 8–10 high / 11+ very high — [ErgoPlus REBA](https://ergo-plus.com/wp-content/uploads/REBA.pdf); OWAS — back(4)/arms(3)/legs(7)/load(<10,10–20,>20 kg) codes → action category 1–4 — [OWAS slides](https://www.scribd.com/presentation/617736274/OWAS); NIOSH RWL = 23 kg × HM×VM×DM×AM×FM×CM, LI = load/RWL — [CDC NIOSH](https://stacks.cdc.gov/view/cdc/197620/cdc_197620_DS1.pdf). Furniture hot spots: panel flipping at bander outfeed, sheet loading on CNC, finished cabinet lift to pallet.

---

## 6. Furniture / woodworking-specific guides and numbers

- **Woodworking Network (Art Raymond, FDMC) 3-part layout series:** Ch1 product/process data, Ch2 tools, Ch3 from-to chart in cart/pallet loads with backtracking below the diagonal — [Ch.3](https://www.woodworkingnetwork.com/management/chapter-3-rationalizing-your-plant-layout), [series overview](https://www.woodworkingnetwork.com/management/fdmc-300/rationalizing-your-plant-layout).
- **FIRA (UK):** Facility Space Planning Template (13-page PDF + Excel: SPUs, material-flow and non-flow affinity matrices, space, constraints; £40 non-members) — [FIRA](https://fira.co.uk/technical-information/information/facility-space-planning-template); Lean Manufacturing Training Toolkit (5C, 7 wastes, visual management, standardised work, QCD measures) — [FIRA info](https://www.fira.co.uk/technical-information/information/p2).
- **Lean assessment in furniture (Strategos tool, 9 areas):** quality and suppliers weakest; automotive lean needs modification for furniture — [UTHM study](https://periodical.uthm.edu.my/index.php/rmtb/article/view/523). Simulation case: operator utilisation 29% → 54% — [Inderscience](https://www.inderscience.com/offer.php?id=107812).
- **Benchmark numbers (treat vendor figures as upper bounds):** edgebander feed 6–7 m/min entry, ~12 m/min mid, 18–25 m/min industrial — [Exapro listings](https://www.exapro.com/homag-kal-3106a3s2-p231026074); compact bander 20–50 panels/h, 150–200 panels per 8-h shift with one operator — [Würth](https://www.wurthmachinery.com/blog/?p=5042); 1,400–2,700 edges/h rated, halve for real conditions — [Fabertec](https://fabertec.co.uk/?p=4465); CNC 4×8 sheet 4–8 min; 16 cabinets cut/dado/band in 5.5 labour-h (~21 min/cabinet) — [WoodWeb](https://woodweb.com/knowledge_base/Panel_Processing_Time_with_and_without_CNC.html); sales/employee US$80–125k, ~1,000 ft² (≈93 m²) per employee — [Woodworking Network](https://www.woodworkingnetwork.com/magazine/fdmc-magazine/how-do-you-measure), [WoodWeb](https://woodweb.com/knowledge_base/Output_Volume_Per_Employee.html). No independent edgebander OEE study was found; furniture OEE pages are vendor marketing — [fabrico](https://www.fabrico.io/ro/blog/best-integrated-oee-cmms-furniture-manufacturing/).
- **Korean furniture reference:** 현대리바트 스마트워크센터 (MES 전 공정) — [MT](https://www.mt.co.kr/future/2019/02/20/2019021417583317558).

---

## 7. Korean sources

- **스마트공장 수준확인 (중기부/스마트제조혁신추진단, 확인기관 KPC·KSA·KMR 등):** 4 영역 / 10 범주 / 44–46 항목 / 1,000점; 범주: 리더십과 전략, 제품개발, 생산계획, 공정관리, 품질관리, 설비관리, 물류운영, 정보시스템, 설비자동화, 성과. 예시 세부항목·배점: 설비관리 60 (설비가동, 설비보전, 보전자재, 금형/지그/공구; 설비 보유현황, 설비종합효율, MTBF/MTTR), 물류운영 60 (구매·외주, 자재, 출하·배송; 자재소요계획, SCM, 적정재고, 이송장비 현황), 정보시스템 220 (ERP, SCM, MES, PLM, FEMS, 보안), 설비자동화 180 (생산·물류·검사설비, 설비정보 네트워크, 에너지/안전/환경), 성과 120 (생산성, 품질, 원가, 납기, 안전, 환경). 등급: Level 3 중간1 750–850, Level 4 중간2 850–950, Level 5 고도화 ≥950. 절차: 사전진단(자가진단표.xlsx) → 현장진단(면담·자료조사·현장실사, 1일). 2026년 지표 개편: 중간1부터 AI 기능 평가, 안전·에너지 지표 추가 — [중소벤처기업인증원](https://www.kosre.or.kr/site/html/smart/factory.htm), [대한상의 SBMI](https://sbmi.korcham.net/Service/SmartFactory/appl/Outline.asp), [KPC 스마트제조](https://www.kpc.or.kr/PTWCT016_smtProd_index.do), [한국형 수준진단 모형 논문](https://ki-it.com/xml/39848/39848.pdf), [업종별 평가영역 논문](https://jkiie.org/xml/30765/30765.pdf), [cosmorning 2026 개편](https://www.cosmorning.com/mobile/article.html?no=52334), [중기부 공고](https://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=310&bcIdx=1055678&parentSeq=1055678).
- **한국생산성본부(KPC):** 10개 진단영역 종합리포트·모듈별 결과·개선이슈 제공; 제조현장 4M 관리실무 교육 — [KPC](https://www.kpc.or.kr/PTWED003_dtil_view.do?ecno=43051). No public KPC 현장진단 체크리스트 or 공장 레이아웃 진단 양식 surfaced in search.
- **중소벤처기업진흥원:** no public 생산현장 진단표 found; 4M (Man/Machine/Material/Method) framing is the common Korean field structure — [koreascience 4M](https://koreascience.kr/article/CFKO201618459285875.pdf).
- **안전 규정 체크리스트:** 산업안전보건기준 규칙 전체 체크리스트 — [safechem](https://www.safechem.co.kr/2026/08/blog-post_25.html); 작업장 통로 KOSHA GUIDE 체크리스트 — [koshaguide](https://www.koshaguide.co.kr/2026/02/kosha-guide.html); 현행 규칙 (고용노동부령 제450호, 시행 2026.03.02) — [nepla](https://www.nepla.ai/law/%EC%82%B0%EC%97%85%EC%95%88%EC%A0%84%EB%B3%B4%EA%B1%B4%EA%B8%B0%EC%A4%80%EC%97%90%20%EA%B4%80%ED%95%9C%20%EA%B7%9C%EC%B9%99/20250629).

---

## 8. Consolidated one-day plant diagnostic protocol (20–50 person furniture plant)

**Team:** 4 people — Lead/interviewer, Flow observer, Time/OEE observer, Layout/utilities surveyor. Kit: 360° camera or LiDAR phone scan, laser distance meter, 2 stopwatches/phone apps, clipboards with the forms below, coloured markers + A1 plan printouts, power/clamp meter (optional), pedometers or phone step-trackers for 2–3 operators (with consent).

**Pre-visit (1 week before) — request:** CAD/plan of building with column grid; machine list; last 12 weeks' orders/routings/BOM; shift calendar; downtime & maintenance log; scrap/rework log; overtime/attendance; electricity bills (12 months) and monthly 생산량; existing MES/ERP exports; last 스마트공장 자가진단표 if any.

| Time | Activity | Instruments | Key fields |
|---|---|---|---|
| 07:40–08:00 | Shift start observation (before the tour) | Gemba notes | Start-up sequence, who gets the plan, how, first-hour abnormalities |
| 08:00–08:40 | Management interview (대표/공장장/생산반장) | PQRST sheet; KPI list | Product families, demand mix, seasonality, lead-time promise, bottleneck per owner, pain points, planned investments |
| 08:40–09:20 | RPA tour (no notes) + 10-min debrief | RPA 11 categories / 20 Q | Scores, three biggest visual signals |
| 09:20–12:00 | Parallel tracks: **(A)** Layout/utilities survey — scan plant, measure bays, doors, aisles, each machine envelope, dust/air/electrical drops, floor marking; constraint register; fixed/movable sheet. **(B)** Flow — walk 2–3 representative products end-to-end: flow process chart + spaghetti; count WIP at every buffer; photograph every container type; door traffic tally (15-min bins). **(C)** Time/OEE — pacemaker (usually edgebander or CNC nesting): time study of 10+ cycles, SMED observation of one changeover, downtime log; work sampling across all operators (one sweep every 10 min) | Forms 1.1, 1.5, 1.8, 1.9, 1.10, 1.11, §3 constraint register, §4 unit-load sheet | See fields in §1, §3, §4 |
| 12:00–13:00 | Lunch with operators (informal elicitation) | Critical-incident prompts | "Last breakdown / rush order / material shortage — what happened?" |
| 13:00–14:00 | Planner DILO: "show me yesterday's plan", think-aloud building tomorrow's cut list & nesting | §2.6 IF-THEN rule sheet | Decision triggers, priorities, exceptions, data sources, overrides |
| 14:00–15:00 | VSM current-state draft on the wall with foreman; from-to chart from records + observations | 1.12, 1.2, 1.3 REL | C/T, C/O, uptime, batch, operators, WIP days, information flow; REL ratings with reasons |
| 15:00–15:45 | Workforce: skills matrix fill-in with 반장; yamazumi for assembly; REBA/OWAS/NIOSH on 3 worst tasks; absenteeism/overtime data check | §5 forms | Levels, licences, posture codes, load weights |
| 15:45–16:30 | Energy/utilities: nameplate kW of all motors ≥3.7 kW, dust collector and compressor run hours, air leaks (listen at break), bill reconciliation | §3 constraint register + energy register | kW, hours, load factor estimate, compressed-air pressure, leak points |
| 16:30–17:15 | End-of-shift: second traffic peak, WIP count repeat (gives daily throughput by difference), 5S audit, housekeeping/cleaning time | 1.13, WIP sheet | WIP delta, cleaning minutes, where parts sleep overnight |
| 17:15–18:00 | Team debrief: fill gaps list, photograph forms, read-out of top 5 observations to management | — | Open items; follow-up data requests |

**Deliverables for the twin:** scan + CAD overlay with grid; machine table (envelope, services, movability class, relocation cost); routing table per product family with step types, C/T distributions (min/mode/max), C/O, batch, container; from-to & distance matrices; WIP snapshots (AM/PM); operator table (skills, walking speed, roles, breaks); MH resource table (forklift/cart counts, speeds, trip log); decision-rule table (IF-THEN, priority, owner); downtime reason codes with MTBF/MTTR estimates; energy per machine; constraint register; calendar (shifts, breaks, overtime pattern).

---

## 9. The 25 most-missed data items in such diagnostics

1. Machine **working envelope** (infeed/outfeed sheet length, door swing, operator stand position), not just footprint.
2. **Dust-duct routing and drop diameters** — the real reason machines "cannot move".
3. Compressed-air ring main and pressure at the farthest drop.
4. **Column grid and clear height** under ducts/lights/cranes (제22조 2 m rule).
5. Floor point-load rating and pits/foundations (CNC, booth).
6. **Container/unit-load definitions** and how many pieces per cart — flows are counted in loads, not pieces.
7. Empty-travel share of forklift/cart trips.
8. Door/dock **usage direction** and peak traffic bins (shift start, pre-lunch, end of shift).
9. Operator vs machine time split in C/T (auto-run time while operator does something else).
10. **Changeover time by product-pair** (colour/thickness of edge tape, sheet material), not an average.
11. Minor stops (<5 min) on the bander/CNC — invisible in downtime logs.
12. First-good-piece time and trial-piece scrap after setup.
13. **WIP location and residence time** (what sleeps overnight where).
14. Rework loops (re-sanding, re-banding) as explicit routing branches.
15. Information flow: how the plan reaches each station (paper, Kakao, verbal) and its latency.
16. The **sequencing/dispatch rules actually used** (and who overrides them).
17. Nesting/batching rules (material-based batching vs order-based) and resulting over-cut inventory.
18. Lot-size reasons (glue pot warm-up, tape reel change, booth batch).
19. Cleaning/sweeping time and dust-bin emptying as a scheduled activity.
20. Break/lunch synchronization and shift-start ramp losses.
21. Skills/licence coverage per machine (who can run the CNC when the one operator is absent).
22. Overtime and 일용직/외국인 labour pattern — determines real capacity.
23. Walking speed, aisle used, and pedestrian–forklift conflicts (needed for a people-movement twin).
24. Energy base load (compressor, dust collector) vs production load, and run hours.
25. Fire/egress/booth zoning and 안전보건규칙 compliance of aisles (통로표시, 2 m clearance, 제한속도) that constrain any relayout.

---

### Sources (non-exhaustive, used above)
RPA: [maaw](https://maaw.info/ArticleSummaries/ArtSumGoodson2002.htm) · [wisys](https://wisys.com/blog/how-to-do-a-rapid-plant-assessment) · [Tauber](https://tauber.umich.edu/rate-lean-fast-0) · [The Auditor](https://www.theauditoronline.com/lean-rapid-plant-assessment-as-a-tool-for-more-effective-audits/) · [SafetyCulture RPA](https://public-library.safetyculture.io/products/rpa-rating-2wvg30lh2mxnm4py). IE charts: [Wikipedia FPC](https://en.wikipedia.org/wiki/Flow_process_chart) · [Wikipedia ARC](https://en.wikipedia.org/wiki/Activity_relationship_chart) · [RMA flow analysis](https://richardmuther.com/wp-content/uploads/2021/06/SLP-On-line-Training-8-Four-Ways-to-Analyze-Flow-of-Materials.pdf) · [SLP guide](https://open-exam-prep.com/study-guides/pe-industrial/facility-layout-material-handling/systematic-layout-planning) · [NPTEL work sampling](https://archive.nptel.ac.in/content/storage2/courses/112107142/part1/lecture10.htm) · [KSU time study](https://fac.ksu.edu.sa/sites/default/files/5-b_direct_time_study_-_p1_ams_mar27_17.pdf) · [Minitab SMED](https://support.minitab.com/en-us/workspace/help-and-how-to/forms/form-tools/lean-improvement/quick-changeover-qco-smed) · [TN MEP OEE](https://tmep.cis.tennessee.edu/oee-implementation-guide) · [Reliable Plant VSM](https://www.reliableplant.com/Articles/Print/11238?id=11238) · [Enna VSM data box](https://enna.com/learning-center/using-the-vsm-data-box-form) · [LearnLeanSigma 8 wastes](https://www.learnleansigma.com/template/8-wastes-timwoods/) · [allaboutlean checklist](https://www.allaboutlean.com/shop-floor-visit-checklist/) · [Shingo](https://shingo.org/?p=543) · [TSSC plenary](https://www.lean.org/wp-content/uploads/2022/04/2013_LTS_tssc_plenary.pdf) · [DILO guide](https://www.slideshare.net/slideshow/dilo-how-to-do-it-practical-guide/139545146) · [CDM paper](https://isgb.otago.ac.nz/infosci/nigel.stanger/Discussion_Papers/raw/master/Papers/1997/97-04/dp1997-04.pdf). Layout/MH: [Woodworking Network Ch.3](https://www.woodworkingnetwork.com/management/chapter-3-rationalizing-your-plant-layout) · [Binus from-to](https://base.binus.ac.id/business-engineering/2025/12/05/from-to-chart-to-measure-flow-efficiency/) · [Damotech aisle](https://www.damotech.com/blog/why-aisle-width-matters-when-it-comes-to-pallet-rack-safety) · [BigRentz](https://www.bigrentz.com/blog/forklift-aisle-width-requirements-osha-standards-and-planning-guide) · [MSPE relocation cost](https://reference-global.com/2/v2/download/pdf/10.2478/mspe-2025-0045) · [MH equation](https://open-exam-prep.com/study-guides/pe-industrial/facility-layout-material-handling/material-handling-equipment) · [FleetRabbit](https://fleetrabbit.com/industry/manufacturing-fleet/forklift-fleet-cost-per-pallet-move-analysis). People: [ILUO](https://www.ag5.com/templates/iluo-skills-matrix-template/) · [yamazumi](https://www.fabrico.io/blog/yamazumi-chart/) · [line balancing](https://open-exam-prep.com/study-guides/fe-industrial/manufacturing-production-systems/line-balancing-throughput-takt-time) · [REBA](https://ergo-plus.com/wp-content/uploads/REBA.pdf) · [NIOSH](https://stacks.cdc.gov/view/cdc/197620/cdc_197620_DS1.pdf). Furniture: [FIRA template](https://fira.co.uk/technical-information/information/facility-space-planning-template) · [UTHM lean assessment](https://periodical.uthm.edu.my/index.php/rmtb/article/view/523) · [Würth](https://www.wurthmachinery.com/blog/?p=5042) · [Fabertec](https://fabertec.co.uk/?p=4465) · [WoodWeb panel time](https://woodweb.com/knowledge_base/Panel_Processing_Time_with_and_without_CNC.html). Korean: [law.go.kr 제22조 해석](https://www.law.go.kr/LSW/cgmExpcInfoP.do?cgmExpcDatSeq=23260&mode=2&ofiClsCd=350101) · [lbox 제22조](https://lbox.kr/v2/statute/%EC%82%B0%EC%97%85%EC%95%88%EC%A0%84%EB%B3%B4%EA%B1%B4%EA%B8%B0%EC%A4%80%EC%97%90%EA%B4%80%ED%95%9C%EA%B7%9C%EC%B9%99/%EB%B3%B8%EB%AC%B8%20%3E%20%EC%A0%9C1%ED%8E%B8%20%3E%20%EC%A0%9C3%EC%9E%A5%20%3E%20%EC%A0%9C22%EC%A1%B0) · [기계설비신문 통로 해설](http://www.kmecnews.co.kr/news/articleView.html?idxno=44553) · [KOSHA 지게차](https://oshri.kosha.or.kr/kosha/intro/northernGyeonggiBranch_A.do?mode=download&articleNo=449134&attachNo=254107) · [수준확인 개요 (중소벤처기업인증원)](https://www.kosre.or.kr/site/html/smart/factory.htm) · [SBMI 수준확인](https://sbmi.korcham.net/Service/SmartFactory/appl/Outline.asp) · [KPC 스마트제조](https://www.kpc.or.kr/PTWCT016_smtProd_index.do) · [중기부 수준확인 공고](https://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=310&bcIdx=1055678&parentSeq=1055678) · [예스폼 5S](https://www.yesform.com/z_n/forms/view_iso/iso_404352.html).

**Gaps to close in a follow-up (search budget exhausted):** exact 2026 수준확인 44/46-item list from 자가진단표.xlsx; KOSHA numeric forklift aisle guidance; dust-collection CFM/velocity design figures per machine; forklift queueing (M/M/c) worked method; Strategos lean-assessment item list; Woodweb "Optimizing Factory Layout" thread; verification of 제21/26/27조 numeric values at law.go.kr.