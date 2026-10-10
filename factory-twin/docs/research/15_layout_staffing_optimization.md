# Improvement-study methods for a small furniture factory digital twin (layout, equipment, staffing, sequencing)

Scope note: ~55 web searches and ~20 fetch attempts were run; the proxy blocked most full-text fetches (arXiv, ResearchGate, publisher sites, HOMAG, Simio), so numbers below come from search-result abstracts/snippets plus standard references. Items marked **[est.]** are my engineering estimates; **[knowledge]** means standard textbook content not re-verified online today. Searches stopped at the per-turn budget; a follow-up turn could fill the gaps flagged at the end.

---

## 1. Facility layout optimisation for job shops / small plants

### 1.1 Problem class: QAP vs unequal-area FLP
- **QAP (discrete locations, equal cells)**: n machines → n candidate slots, cost = Σ f_ij · d_{π(i)π(j)} (+ relocation cost). Right choice when the twin already defines a grid of feasible "footprints" (bays between columns, duct drops, pits). The Slovenian furniture study below explicitly reduced to a QAP after simplifications. Exact QAP: instances ≥ ~30 are research-grade (nug30 needed massive compute) **[knowledge]**; for 10–20 machines with 15–25 candidate slots, CP-SAT/MIP with a linearised objective solves or gives small gaps in minutes **[est.]**.
- **Unequal-area FLP (continuous x,y,w,h)**: MIP with disjunctive non-overlap (Sherali–Fraticelli–Meller 2003, *Operations Research* 51(4), polyhedral outer-approximation of area constraints, symmetry breaking; solved three Meller-1999 instances that had 10–40 % gaps after 24 CPU h) — https://pubsonline.informs.org/doi/10.1287/opre.51.4.629.16096. Exact MIP remains limited to roughly 10–12 departments **[est.; review states "only a limited number of departments" solvable]** — review: https://rcs.cic.ipn.mx/2021_150_3/The%20Unequal-Area%20Facility%20Layout%20Problem_%20A%20Review.pdf. Continuous multi-row MILP handles ≈13 departments (https://rc.cplp.org/Record/rcaap_a56fbfb466d2d6c950b359c412c95559). State-of-the-art survey: Anjos & Vieira, GERAD G-2016-05 / EJOR 2017, and their 2021 Springer book *Facility Layout* (https://www.gerad.ca/fr/papers/G-2016-05, https://link.springer.com/978-3-030-70989-1).
- **Flexible-bay (FBS)** and **slicing-tree** encodings restrict the space to make metaheuristics efficient: Konak/Kulturel-Konak/Norman/Smith FBS MIP (https://eng.auburn.edu/~aesmith/files/Anewmixed%20integer%20programming%20formulation%20for%20facility%20layout%20design%20using%20flexible%20bays.pdf); STaTS slicing tree + tabu; graph-pair representation that imposes no bay/cut structure (https://www.sciencedirect.com/science/article/abs/pii/S0377221711010058). Surveys: https://www.researchgate.net/publication/327592010_Heuristics_and_metaheuristics_approaches_for_facility_layout_problems_a_survey ; multi-objective GA survey for UA-FLP: https://www.academia.edu/90492718/.

### 1.2 Practical constraints and how to encode them
| Constraint | Encoding |
|---|---|
| Fixed departments (dust booth, pits, ducts) | fix x,y (QAP: fix π(i)); or treat as obstacles = fixed rectangles in no-overlap set |
| Aisles / forklift lanes | reserve rectangles as obstacles; or model distances on an aisle graph (rectilinear via aisle nodes) rather than Euclidean centroid distance |
| I/O points | distance between I/O points, not centroids: d_ij = |x_i+io_i − x_j − io_j| + … |
| Clearances / working envelopes | inflate each machine's rectangle by its envelope before no-overlap |
| Utilities (dust, 3-phase, air) | adjacency bonus / penalty with duct drop locations; or hard "must be within r of drop k" |
| Relocation classes A/B/C | fixed cost c_i·[π(i) ≠ π0(i)] (DFLP "rearrangement cost") |
| Forklift–pedestrian separation, noise/dust X-relationships | penalty term for pairs closer than s_ij (safety-violation penalty models: VNS bi-objective https://www.iieta.org/download/file/fid/188788 ; NSGA-II/AMOSA multi-row with safe distances https://iieta.org/journals/jesa/paper/10.18280/jesa.581019) and Muther SLP closeness ratings (A…X) as a linear term |

Multi-objective form used in the DFLP literature: min {material-handling cost, rearrangement cost, −closeness rating, area utilisation} (https://redi.cedia.edu.ec/document/4307 ; RAIRO 2016 https://www.rairo-ro.org/10.1051/ro/2016057 ; 2014 unequal-area workshop NSGA variant https://www.springerprofessional.de/en/multi-objective-dynamic-layout-problems-for-unequal-area-worksho/4153180). 2026 human-centric reconfigurable layout (GA + digital human modelling, objectives: well-being, walking distance, area use; validated in an industrial testbed): Lind et al., *Engineering Optimization*, DOI 10.1080/0305215X.2026.2718913 (https://research.chalmers.se/en/publication/553781).

### 1.3 OR-Tools CP-SAT model sketch (unequal-area, fixed obstacles, I/O points, relocation cost)
API verified from the OR-Tools scheduling doc (`new_interval_var`, `new_optional_interval_var`: https://raw.githubusercontent.com/google/or-tools/stable/ortools/sat/docs/scheduling.md); `add_no_overlap_2d`, `add_abs_equality`, `add_multiplication_equality` are standard CP-SAT methods **[knowledge]**.

```python
from ortools.sat.python import cp_model
m = cp_model.CpModel(); G = 10  # grid: 10 cm units; floor W x H
x, y, xi, yi = {}, {}, {}, {}
for i in M:                      # machines incl. envelope w[i], h[i]
    x[i] = m.new_int_var(0, W - w[i], f"x{i}"); y[i] = m.new_int_var(0, H - h[i], f"y{i}")
    xi[i] = m.new_interval_var(x[i], w[i], x[i] + w[i], f"xi{i}")
    yi[i] = m.new_interval_var(y[i], h[i], y[i] + h[i], f"yi{i}")
for o in OBST:                   # pits, ducts, booths, aisles: fixed intervals
    xi[o] = m.new_fixed_interval... (use new_interval_var with constants)
m.add_no_overlap_2d(list(xi.values()), list(yi.values()))
# optional rotation: two optional interval pairs with presence literals r_i, ¬r_i
# fixed machines: m.add(x[i] == x0[i]); m.add(y[i] == y0[i])
# distances between I/O points (rectilinear)
D = {}
for (i, j), f in FLOW.items():
    dx = m.new_int_var(0, W, ""); dy = m.new_int_var(0, H, "")
    m.add_abs_equality(dx, (x[i] + out_i) - (x[j] + in_j))
    m.add_abs_equality(dy, (y[i] + outy_i) - (y[j] + iny_j))
    D[i, j] = dx + dy
# relocation cost: moved_i = 1 unless at original cell
moved = {i: m.new_bool_var(f"mv{i}") for i in M}
for i in M:
    m.add(x[i] == x0[i]).only_enforce_if(moved[i].Not()); m.add(y[i] == y0[i]).only_enforce_if(moved[i].Not())
# separation/safety: for X-pairs enforce |dx|>=s or |dy|>=s via two bools
# objective (weights scaled to money): flow cost per unit distance × annual flow + relocation
m.minimize(sum(f * c_handling * D[i, j] for (i, j), f in FLOW.items())
           + sum(c_reloc[i] * moved[i] for i in M))
s = cp_model.CpSolver(); s.parameters.num_workers = 8; s.parameters.max_time_in_seconds = 600
```
Tips: coarse grid (10–25 cm) keeps domains small; add symmetry breaking (fix one free machine's x ≤ W/2); seed with the current layout via `add_hint`. Gibson & Dhakal (arXiv 2512.18034, Dec 2025/Jan 2026) compare CDCL, CP-SAT and MILP on grid layouts with adjacency/separation/unavailable-cell constraints: CDCL dominates feasibility, CP-SAT scales roughly polynomially vs. exponential for MILP on their instances, and a CDCL-warm-start→CP-SAT hybrid is proposed (https://arxiv.org/abs/2512.18034). For a pure QAP with ≤20 machines and precomputed aisle-graph distances, a MIP in HiGHS/Gurobi with the Kaufman–Broeckx or Adams–Johnson linearisation is also workable **[knowledge]**.

### 1.4 Metaheuristics and construction heuristics
- pymoo: encode layout as a permutation (QAP) or (permutation + bay-break vector) for FBS; `NSGA2(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)`, `ElementwiseProblem` with objectives [flow-distance, relocation cost, safety penalty]. (pymoo docs blocked by proxy; API from knowledge.)
- CRAFT (pairwise-exchange improvement, needs an initial layout, weak with very unequal areas), CORELAP (closeness-rating construction), BLOCPLAN (bands + REL chart). The searches found no published optimality-gap benchmarks for them; sources only say CRAFT is "close to optimum in most real applications" (https://www.scribd.com/document/935097399/06-Basic-algorithms-for-the-layout-problem ; Garside 2010 comparison CRAFT/MULTIPLE/BLOCPLAN https://ejournal.umm.ac.id/index.php/industri/article/view/52). **[est.]** On ≤15-department instances CRAFT-type local search typically lands within ~5–15 % of best-known flow cost but is sensitive to the start layout; use it only to seed CP-SAT/GA.

### 1.5 What relayouts actually deliver (benchmarks)
- **Kanduč & Rodič 2015, "Optimization of a furniture factory layout", Croatian Operational Research Review** (Slovenian furniture plant, AnyLogic DES auto-generated from XML template, one month of real order data, force-directed-graph heuristic on a QAP): total product travel distance −≈25 % (preliminary figure; one later summary says ">30 %"), **but "rearranging machine positions does not have a significant effect on total manufacturing times; speeding up … would require additional machines … to remove existing bottlenecks."** (https://hrcak.srce.hr/en/138602 ; https://www.proquest.com/docview/1683082581 ; follow-up "Manufacturing processes optimisation in a furniture factory" https://www.researchgate.net/publication/303425362). This is the key defensible message for the owner: layout cuts handling/walking, not throughput, unless the bottleneck is handling itself.
- Other DES layout cases report handling-cost cuts of ~55 % with modest output gains when a bottleneck was simultaneously relieved (https://www.academia.edu/39899872/) and a manual-assembly case where output rose 195→213/month only after a packaging bottleneck was added, not from logistics reduction (http://www.ijsimm.com/Full_Papers/Fulltext2019/text18-2_366-377.pdf). SME job-shop Arena case (IEOM 2016): cycle-time reduction attributed to better material handling (http://ieomsociety.org/ieom_2016/pdfs/354.pdf).
- **[est.]** Typical furniture job-shop relayout: 15–35 % less transport distance, 5–15 % less non-value-added operator time, throughput change within ±3 % unless the forklift/cart loop or a handling-bound station was the constraint. Design the twin experiments to test exactly that.

---

## 2. Simulation–optimisation loop with the SimPy twin

### 2.1 Architecture
1. **Pre-screen analytically** (queueing, §3) and with cheap layout solvers (§1) → shortlist 20–200 candidates.
2. **Twin as evaluator**: candidate = {layout π, machine set, staffing/skill matrix, rule set}. Each evaluation = k replications × horizon (e.g., 3 months) × demand regime.
3. **Search driver**: (a) OptQuest-style scatter search + tabu (Glover/Laguna/Kelly, the engine in Simio/Arena/AnyLogic) **[knowledge]**; (b) NSGA-II in pymoo for Pareto fronts; (c) Bayesian optimisation (GP surrogate + EI/KG; Osnabrück evaluation of BO on DES https://opus.hs-osnabrueck.de/frontdoor/index/index/year/2020/docId/1564 ; Gunn et al. 2022 "Improving high value manufacturing with simulation-based Bayesian Optimisation", IEEE SysCon https://dro.deakin.edu.au/articles/conference_contribution/Improving_high_value_manufacturing_with_simulation-based_Bayesian_Optimisation/20589981); (d) surrogate-assisted NSGA-II with ANN trained on DES output (2025, *Int. J. Computer Integrated Manufacturing* https://www.tandfonline.com/doi/full/10.1080/0951192X.2025.2455631); (e) GPR + fuzzy-TOPSIS layout ranking under uncertainty (ASME 2025/26 https://doi.org/10.1115/1.4071314). Automated model generation + design-space exploration: arXiv 2312.00526 (poultry lines; cites Kanduč & Rodič as the automation precedent) https://arxiv.org/pdf/2312.00526.

### 2.2 Budgets **[est.]**
A SimPy twin of 20–50 workers/10–20 machines simulating 3 months typically runs in 2–30 s per replication on one core. With 8–16 cores: ~5,000–20,000 replications overnight. Rule of thumb: BO for ≤10 continuous/ordinal decision variables converges in 50–150 evaluations; NSGA-II for discrete layout+staffing needs 2,000–10,000 evaluations; so use 5 replications in search and 30–50 for final confirmation of the top 5–10.

### 2.3 Noise handling
- **Common random numbers**: seed each stochastic stream (order arrivals, process times, breakdowns) per replication index and reuse across candidates — paired comparisons cut variance drastically. CRN-aware R&S: Chick & Inoue 2001 (https://stars.library.ucf.edu/scopus2010/5547), sequential Bayesian R&S with CRN (arXiv 1410.6782), KG-CRN with GP metamodel (WSC 2019 https://www.informs-sim.org/wsc19papers/377.pdf), GA + indifference-zone selection with CRN (Nazzal et al., https://stars.library.ucf.edu/facultybib2010/3076).
- **Ranking & selection**: KN (Kim–Nelson) fully sequential procedure for the final shortlist; Simio's Subset Selection needs ≥2 and recommends ≥10 replications per scenario, "Select Best Scenario" implements KN (https://simio.com/resources/release-notes/notes/sprint-41-standard%20library-enhancement-additional-engine-level-capabilities.php). Subset-selection theory: Eckman, Plumlee & Nelson WSC 2020 (https://informs-sim.org/wsc20papers/302.pdf).
- **Warm-up**: Welch's method on WIP; or initialise from the twin's validated snapshot state.

### 2.4 Multi-objective and robustness
- Objectives: throughput (or on-time %) ↑, capex ↓, walking/handling distance ↓, worker load balance. Report the Pareto front and then the owner's trade-off, not a weighted sum. Examples: NSGA-II with simulation inside fitness for RMS (https://arxiv.org/pdf/2212.00581); Chalmers DES+NSGA-II (https://odr.chalmers.se/items/91bdc6d5-e7e4-41aa-9997-138c4c469199); meta-model Pareto via DoE (https://dspace.lib.cranfield.ac.uk/items/f4f00c72-3e72-4aae-b88e-17f21b8adcb4/full); Pareto-front selection for a real battery-assembly layout (https://www.mdpi.com/2076-3417/14/22/10736).
- **Robust across regimes**: evaluate each candidate under R demand regimes (peak season, off-peak, mix shift) from order history; score = E[Δ] − λ·σ(Δ) or min over regimes; "robust layout" vs "adaptive layout" literature (Pillai et al. 2011 CAIE; Kumar & Singh 2017 https://ideas.repec.org/a/ids/ijmcph/v10y2017i2p147-164.html; Kulturel-Konak 2007 review https://sites.psu.edu/kulturel/files/2021/01/JIM-2007.pdf). Require P(Δ>0) ≥ 0.9 in every regime (see §7).

---

## 3. Equipment investment decisions

### 3.1 Queueing pre-screen (Kingman / VUT) **[knowledge, Hopp & Spearman *Factory Physics*]**
CT_q ≈ ((c_a² + c_e²)/2) · (u/(1−u)) · t_e for a single server; multi-server: u^{√(2(m+1))−1}/(m(1−u)). Departure variability c_d² = u² c_e² + (1−u²) c_a² chains stations. Effective process time with failures: t_e = t_0/A, c_e² = c_0² + (1+c_r²)·A(1−A)·m_r/t_0 (A = availability, m_r = MTTR). Setup batching: t_e = t_0 + t_s/k, c_e² = (σ_0² + σ_s²/k + ((k−1)/k²)t_s²)/t_e². Moving 80→90 % utilisation ≈ doubles queue time; 90→95 % doubles again (https://metricgate.com/docs/hopp-spearman-factory-physics/ ; https://www.fabrico.io/blog/kingman-formula-queue/). Use: compute u and CT_q per machine for each demand regime; any machine with u ≥ 0.85 at peak is a capex candidate; estimate post-investment u' = u·t_e'/t_e and recompute to see which station becomes the next constraint.

### 3.2 Bottleneck shift
Use Roser–Nakano–Tanaka active-period (shifting bottleneck) detection on the twin's state logs (sole vs shifting bottleneck, magnitudes) — WSC 2002 https://www.informs-sim.org/wsc02papers/145.pdf, sensitivity paper https://www.allaboutlean.com/publications/2002_wsc-throughput-sensitivityanalysis-preprint/ (valid only while the bottleneck does not move → re-run after each capacity change), practitioner summary https://www.allaboutlean.com/shifting-bottlenecks/. Rule: a machine purchase is justified only if the bottleneck's active-period share > ~60 % and the next bottleneck's capacity gap absorbs at least the planned demand growth **[est.]**.

### 3.3 ROI with uncertainty
Simulation-based NPV: draw demand paths (bootstrap from order history by season; or GBM), run the twin → throughput, overtime, scrap → cash flow; report NPV p10/p50/p90, payback distribution, P(NPV>0). Real-option/staged valuation: Amico et al. WSC 2003 (Monte Carlo NPV of expansion + binomial option) https://www.informs-sim.org/wsc03papers/043.pdf ; staged entry under demand uncertainty (Fleten, Kozlova, Lawryshyn 2020) https://www.realoptions.org/openconf2020/data/papers/477.pdf ; option-to-wait for AMT (Leite Filho) https://web.bndes.gov.br/bib/jspui/handle/1408/2588 ; double-Monte-Carlo real-option (Pawlak 2025) https://research.wu.ac.at/ws/files/38077863/document.pdf. Used vs new: used single-sided edgebanders listed at €17–37 k (Exapro https://www.exapro.com/wood-machines-edgebanders-c128/?page=1) vs small new banders ≈ $21 k (SCMI K130 forum) and larger new lines far higher; forum consensus: used banders are often sold because of problems, require inspection (https://woodweb.com/knowledge_base/Buying_an_Edgebander_New_Versus_Used.html). In the twin, model used machines with lower availability A (e.g. 0.85 vs 0.95) and higher c_e² **[est.]**; lease = convert capex to monthly cost in NPV, keeps option value.

### 3.4 Furniture machine economics (vendor numbers, treat as upper bounds)
- Edgebander return conveyor: enables one-operator operation (HOMAG LOOPTEQ O-200/300/400; HOMAG says O-200 "pays off from 9 hours working time per week") https://www.homag.com/fileadmin/product/automation/brochures/loopteq-o-200/return-conveyor-LOOPTEQ-O-200-en.pdf ; https://stilesmachinery.com/series/homag-loopteq-o-300-return-conveyors/. Biesse Winner W4 return+stacking: "25 % increase in production and decrease in labour cost" (vendor) https://www.surfaceandpanel.com/biesses-stream-a-winner-w4-a-perfect-combination-of-industry-40-efficiency/. HOMAG Australian case: "previously 6 joiners, now 2 for the same work" after return conveyor https://www.homag.com/en/news-events/case-studies/detail/a-machine-that-can-run-all-day. UK case: old double-sided bander productive only ~4 h of an 8 h shift (https://homag.com/en/news-events/case-studies/detail/sven-christiansen-invests-in-new-edge-banding-and-cnc-solutions). **[est.]** For a 1-operator-plus-helper bander, a return conveyor frees 0.5–1 FTE and raises bander utilisation 10–25 %; parts/shift gain is bounded by feed speed and part size.
- Nesting vs beam saw + point-to-point: nesting yield typically 5–15 % better, but savings only materialise when a whole sheet is saved (https://cutplan.ai/en/blog/cnc-nesting-vs-manual-cut-list.html); nesting cycle ~6–7 min/sheet full machining (forum) vs saw 15 min/sheet with 2 operators (vendor claim) vs "60–80 sheets/day nested; a saw cuts that in an hour" for stacked straight cuts; nesting tooling+energy ≥50 % higher per part; nesting = 1 operator vs saw+drill = 2; no side boring on nested routers (https://woodweb.com/knowledge_base/NestedBased_Routers_Versus.html ; https://www.woodworkingnetwork.com/magazine/fdmc-magazine/pros-and-cons-nested-based-manufacturing ; https://woodweb.com/cgi-bin/forums/cnc.pl?read=778938).
- Batch-size-1 drilling/cutting: HOMAG SAWTEQ robot mode "up to 850 parts per shift" (https://www.homag.com/en/company/news/case-studies/detail/the-robotic-saw-manager); DRILLTEQ L-500 through-feed for batch 1, DRILLTEQ C-500 suited to batches >250, up to 38 parts/min in two-machine groups (https://wtp.hoechsmann.com/en/lexikon/pdf/hom_drillteq_c_h_l_2022_en.pdf ; https://homag.com/en/product-detail/machines/cnc-automatic-drilling-and-fitting-machines/throughfeed-processing-center-drillteq-l-500). No independent parts/shift comparison was found; measure cycle times for your own part mix.

---

## 4. Staffing, cross-training and allocation

### 4.1 Literature results
- **Chaining** (Jordan & Graves 1995, *Mgmt Sci* 41(4):577–594): a closed 2-skill chain over n workers/stations captures "well above 90 %" of full-flexibility benefit; later analyses ~96–97 % as n grows (https://ideas.repec.org/a/inm/ormnsc/v41y1995i4p577-594.html ; https://experts.umn.edu/en/publications/machine-sharing-in-manufacturing-systems-total-flexibility-versus/). Agile workforce framework (Hopp & Van Oyen): performance degrades with less cross-training, fewer workers, higher processing-time variability and higher machine utilisation (https://vanoyen.engin.umich.edu/wp-content/uploads/sites/150/2014/07/AWE-IIE-Hopp-VanOyen.pdf).
- **DRC job-shop simulations**: the first increment of labour flexibility gives the largest gain, then diminishing returns (JOM 1989 https://www.iaorifors.com/paper/3737); additional labour beats cross-training alone, combination best (IJPR 1993 https://iaorifors.com/paper/10880); labour-assignment ("when/where") rules can matter more than dispatching (Fryer 1973 https://ideas.repec.org/a/inm/ormnsc/v19y1973i9p1001-1012.html); review of 16 DRC simulation studies (Hottenstein & Bowman https://www.sciencedirect.com/science/article/pii/S1047831098900025); heterogeneous-worker efficiency loss in DRC lines, eight training matrices compared (Costa, Thürer, Portioli-Staudacher 2023, *Ops Mgmt Research* https://link.springer.com/article/10.1007/s12063-023-00371-2); learning/forgetting losses quantified by DES (https://emerald.com/insight/content/doi/10.1108/ijopm-06-2012-0197/full/html). Most benefit at "moderate" cross-training (https://www.sciencedirect.com/science/article/abs/pii/S0360835208003197).
- **ILUO skills matrix** (I = trained, L = can do with support, U = independent, O = can teach): https://www.ag5.com/templates/iluo-skills-matrix-template/ ; coverage rule "≥2 people at proficiency ≥U per critical asset per shift" is practitioner guidance, not a standard (https://www.fabrico.io/blog/maintenance-cross-training-curriculum/).
- SALBP / ALWABP (worker-dependent times, infeasible pairs = ∞): heuristics and exact methods https://arxiv.org/pdf/1003.3676 ; https://arxiv.org/pdf/1308.0299 ; hierarchical worker skills (ALBHW) https://arxiv.org/pdf/2004.13396.

### 4.2 CP-SAT sketch: worker–station assignment with skills, takt, coverage ≥ 2 on critical machines
```python
m = cp_model.CpModel()
a = {(w,s): m.new_bool_var(f"a{w}{s}") for w in W for s in S if skill[w][s] >= 'L'}   # ILUO level
for w in W: m.add_at_most_one(a[w,s] for s in S if (w,s) in a)          # one station per shift
for s in S:                                                               # station load must be covered
    m.add(sum(a[w,s] for w in W if (w,s) in a) >= need[s])
    # takt: sum of station task time / assigned workers <= takt  →  linearised:
    m.add(sum(eff[w][s] * a[w,s] for w in W if (w,s) in a) * takt >= load[s])   # eff = rate factor (U=1.0, L=0.7)
# coverage: for each critical machine, at least 2 workers on the roster hold level >= U (training decision t)
t = {(w,s): m.new_bool_var(f"t{w}{s}") for w in W for s in CRIT}        # train w on s this quarter
for s in CRIT:
    m.add(sum((skill[w][s] >= 'U') + t[w,s] for w in W) >= 2)
# chaining structure: each worker has >= 2 'U' skills, each station >= 2 'U' workers (soft via penalties)
# ethics/labour: max hours, rest, no skill downgrade, voluntary-training list V: t[w,s] <= 1 if w in V else 0
m.minimize(sum(c_train[w,s] * t[w,s] for (w,s) in t)
           + sum(c_wage[w] * a[w,s] for (w,s) in a)
           + lam * imbalance_var)   # imbalance = max_station_load - min_station_load
```
Precedence/takt per task (true SALBP): task→station bools with `x[t,k] <= sum_{k'<=k} x[p,k']` for p ≺ t and load_k ≤ takt. Feed the resulting roster + matrix to the twin, where worker movement, learning curves (efficiency 0.7→1.0 over ~N repetitions **[est.]**) and absenteeism are stochastic.
Ethics/labour constraints: encode as hard constraints (max hours, breaks, ergonomic-load caps from the Lind et al. DHM approach), make training voluntary/consented, never optimise "reallocation" that implies redundancies without presenting the no-headcount-loss alternative on the Pareto front.

---

## 5. Batching and sequencing in panel furniture

- **Evidence base**: Gawroński 2012, *Annals of OR* 201:169–182, made-to-order furniture dynamic job shop: hierarchical rule "similar setup → EDD → SPT" cut setup time per operation by 58 % vs EDD+shortest-setup+SPT and >70 % vs SPT alone; setup matrices impractical (>10,000 part types) so setups computed from attribute similarity (https://link.springer.com/article/10.1007/s10479-012-1233-z). Stochastic job shop with sequence-dependent setups (9 rules, u = 90 %): SIMSET best for flow time / tardy count, JMEDD best for tardiness measures (https://journal.hep.com.cn/fme/EN/10.1007/s11465-014-0315-9). Real job shop: ATC with batch 150 → 4.23 % tardy (https://www.tandfonline.com/doi/full/10.1080/08839510600779738). ATCS (Lee & Pinedo 1997 **[knowledge]**) priority I_j = (w_j/p_j)·exp(−max(d_j−p_j−t,0)/(k1·p̄))·exp(−s_{lj}/(k2·s̄)) outperforms EDD/WSPT on total weighted tardiness; EDD second (https://cse.tongji.edu.cn/_upload/article/files/57/2b/a419b6c140d3b3798e72b2ef601c/29eecbb6-fe5f-4635-a38c-b86c7aab5e66.pdf). Family batching: non-exhaustive family rules best; gains largest when setup/run ratio is low or load is high (https://www.growingscience.com/ijiec/Vol7/IJIEC_2016_3.pdf ; flow-line family setups https://dl.acm.org/doi/abs/10.1016/0272-6963(91)90009-M). Colour-change sequencing analogues (coating/powder booths) https://arxiv.org/pdf/2608.14122.
- **Batch-one / order-based flow**: vendor claims only (HOMAG "batch size 1" case studies, SORTEQ sorting "e.g. for assembly, tour order or colour", buffers decoupling saw peaks from bander; Rudolf and Goldbach Kirchner cases https://www.homag.com/en/company/news/case-studies/detail/batch-size-1-takes-center-stage ; https://www.homag.com/fileadmin/product/automation/brochures/buffering-sorting/buffering-sorting-collating-systems-en.pdf). No independent academic validation found; model it in the twin instead.
- **Optimal batch size under sequence-dependent setups (edge-tape colour)**: k* balances setup share vs queueing: via Factory Physics t_e(k) = t_0 + t_s/k, CT = CT_q(k) + k·t_0 (wait-to-batch) → convex in k; evaluate 1..k_max in the twin. Colour campaigning rule: sequence the bander queue by (colour family, then EDD within family), with a "max wait per order" cap to protect due dates (Gawroński-type hierarchical rule).
- **Nesting effects**: yield +5–15 % (whole-sheet granularity), 1 operator; but parts are locked until the sheet is done and mixed-colour nests create downstream colour-sorting work → model the sorting buffer explicitly.

### Experiments to run on the twin
1. Dispatch rule grid at the bander and CNC: FIFO, EDD, SPT, CR, ATCS(k1∈{1,2,3}, k2∈{0.5,1}), colour-campaign+EDD. KPIs: on-time %, mean/max tardiness, setups/shift, WIP.
2. Batch size k ∈ {1,2,4,8,16} × colour grouping on/off × release policy (CONWIP cap ∈ {N/2…N}).
3. Nesting on/off (yield, sheet cycle, sorting buffer size).
4. Factorial over demand regimes; replicate 10–30 with CRN; check interaction with staffing.

---

## 6. Presenting to a small-factory owner (short)
- One page per option: capex, annual benefit (p10/p50/p90), payback distribution, **P(NPV > 0)**, "what has to be true". Monte-Carlo output as p10–p90 bands rather than point estimates (https://docs.flowx.ai/5.9/observatory/roi/sensitivity-analysis); tornado chart of the 3–5 drivers (demand, cycle-time gain, availability, labour rate, scrap) https://www.e-education.psu.edu/eme460/node/724 ; probabilistic tornado that shows proportion above zero = probability of improvement (SMDM https://smdm.confex.com/smdm/16BEC/webprogram/Paper9928.html).
- "Confident / not confident" split: confident = things the twin validated against history (walking distance, machine utilisation, setups); not confident = demand growth, vendor cycle-time claims (label them "vendor claim, discounted ×0.6–0.8 **[est.]**"), learning curves.
- Before/After KPI set consultancies use **[knowledge]**: throughput/shift, OTD %, lead time (p50/p90), WIP €, handling distance m/order, labour hours per order, bottleneck utilisation, setups/shift, overtime h, floor-area freed.
- Staged investment = option value: show "return conveyor now, nesting line only if demand > X" with the decision trigger quantified (Fleten et al.; Amico et al.).

---

## 7. Improvement-study protocol using the twin

**Data prerequisites from capture** (must exist before step 1): validated from–to flow matrix (per order type, seasonal), machine envelopes + fixed obstacles + aisle graph, relocation classes A/B/C with € and downtime days, process-time and setup distributions per machine×family (incl. colour-change), MTBF/MTTR, order history ≥12 months (for regimes), skills matrix (ILUO) + wage + consent to train, cart/forklift speeds and capacities, shift calendar, cost data (€/h labour, €/m handling, scrap €/sheet, hurdle rate).

**Step 0 – Baseline & regimes.** Define ≥3 demand regimes (peak, off-peak, mix-shift) from order history; 30 CRN replications each; record KPI baseline with 95 % CIs; run active-period bottleneck detection.
**Step 1 – Identify (TOC).** Bottleneck = max active-period share; confirm with Kingman u and CT_q. Analytic what-ifs for ±10 % capacity.
**Step 2 – Exploit.** Rules only (no capex): dispatching, batching/colour campaigning, CONWIP release, protecting the bottleneck with a time buffer, staffing the bottleneck through breaks. Budget: ~200 scenarios × 10 reps.
**Step 3 – Subordinate.** Staffing/cross-training via CP-SAT roster → twin; test chaining vs 2-skill vs full; absenteeism scenarios. Budget: ~100 rosters × 10 reps.
**Step 4 – Elevate.** Equipment options (new/used/lease, return conveyor, nesting+drilling line): Kingman pre-screen → twin → simulation NPV with demand paths. Re-run bottleneck detection after each to show the shift.
**Step 5 – Layout.** CP-SAT/QAP shortlist (5–20 layouts on Pareto of flow-distance vs relocation vs safety) → twin with the new rules/roster/machines; expect handling/walking gains, verify throughput neutrality or gain.
**Step 6 – Combine & rank.** Pareto over {ΔNPV, capex, P(improvement), disruption days}; KN selection for the top set with 30–50 reps.
**Step 7 – Repeat** (TOC step 5): new bottleneck → iterate.

**Acceptance criteria for a recommendation** **[est., choose with the owner]**: P(ΔKPI_primary > 0) ≥ 0.9 in every demand regime and ≥ 0.95 pooled (paired CRN test); p10 payback ≤ 36 months for capex items; no regime where OTD drops >2 pts; safety/labour constraints feasible; sensitivity (tornado) shows no single unvalidated input flips the sign; disruption plan (relocation days) within an agreed window; result reproducible with a fresh seed set.

---

### Gaps a follow-up turn could close (search budget hit)
Full text of Kanduč & Rodič (exact machine count, final % figure), Gibson & Dhakal runtime tables, Costa et al. 2023 numeric results, an independent parts/shift study for nesting+drilling cells, BoTorch noisy-BO guidance for DES, and a published consultancy Before/After template.