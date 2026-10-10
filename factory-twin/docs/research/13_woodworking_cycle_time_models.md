# Cycle-Time Models for Panel-Furniture Machines — Digital-Twin Reference

**Scope and evidence quality.** Sources were gathered via web search snippets (manufacturer pages, Woodweb knowledge base/forums, Woodworking Network, MAGI-CUT help, PLOS ONE/PMC, Chinese vendor data). Direct page fetches were blocked by the sandbox egress policy and the search budget was exhausted, so a few items (Korean 6면드릴/런닝쏘 specs, PU flash-off schedules, OEE benchmarks) could not be sourced and are flagged. Tags used throughout: **[SPEC]** manufacturer datasheet, **[VENDOR]** marketing/dealer claim, **[FORUM]** practitioner anecdote (Woodweb etc.), **[PAPER]** peer-reviewed, **[EST]** my engineering estimate — calibrate on site.

**Notation.** `L` part length (m), `W` width, `t` thickness, `v_f` feed speed (m/min), `G` inter-part gap (m), `N_x` counts, `T` time (s unless noted), `n_b` book/stack count, `p_i` per-event constants.

---

## 1. Beam saw / panel sizing saw (런닝쏘)

### (i) Time model
```
T_book = T_load + N_head·t_head + Σ_rips [t_cut(L_rip) + t_push]
       + N_strips·t_strip_transfer + Σ_cross [t_cut(L_cross) + t_push]
       + N_third·t_third + N_parts·t_label + T_unload_sort
t_cut(L) = t_clamp + L/v_cut + L/v_return + t_release        (per saw stroke)
T_sheet  = T_book / n_b                                      (n_b = sheets per book)
```
Pattern structure drives everything: a HOMAG/Holzma-class saw does one stroke per rip (strip), then re-feeds each strip (or several strips side-by-side up to "max width for cross-cutting multiple strips") for cross cuts. Third-phase (head/recut) cuts add a stroke each and extra handling.

### (ii) Default coefficients
| Term | Default | Range / basis |
|---|---|---|
| `v_cut` saw carriage | 60–80 m/min effective | SPEC max: SAWTEQ S-200 80 (120 opt), S-300 150 (170 opt), HPP 250 120, HPP 230 60, Gabbiani 120 m/min; SCM Sigma Impact 90 only 6–30 m/min; EU/CE limits pusher forward feed to 24–25 m/min on some models ([HOMAG S-300](https://www.homag.com/en/product-detail/panel-dividing-saw-sawteq-b-300), [HPP 230/250 brochure](https://www.exfactory.com/Literature/HOLZMA/HPP250-PDFa.pdf), [Gabbiani brochure](https://www.scmgroup.com/products/docs/sezionatura-gabbiani/gabbiani-p95-pt95/new/Brochure_gabbianippt_EN.pdf), [SCM Sigma Impact](http://smartproduction.scmgroup.com/medias/0B_qaKOU2Kj_zR1B2eGRUUGl5bjQ_sigma%20impact%2090.pdf)) |
| `v_return` | 100–150 m/min | SPEC (carriage return at max speed; MAGI-CUT asks for return speed explicitly) |
| Pusher / program fence | 40–90 m/min | SPEC: HPP 230 40, HPP 250 80, S-300 90, Gabbiani 70 |
| `t_clamp + t_release` (pressure beam) | 2.0 s | [EST] 1.5–3 s |
| `t_push` (fence reposition, accel/decel) | 1.0–1.5 s | [EST] |
| `t_cut` full 2.8 m rip, single sheet | ≈ 7–8 s | [EST] derived: 2 + 2.8/(1.0 m/s) + 2.8/(2 m/s) + 1 |
| `t_cut` cross cut (0.6 m strip) | ≈ 4–5 s | [EST] |
| `t_strip_transfer` (operator turns/re-feeds strip) | 6–10 s | [EST]; 0 with angular/automatic systems |
| `t_label` per part (printer + apply) | 3–6 s | [EST]; label printing is parallel on automated saws |
| Feed derating with book height | ×0.6–0.8 at 60–80 mm book | [EST]; blade projection/motor limited |

**Worked default (single 2440×1220 melamine sheet, 5 strips, 20 cross cuts, 1 head cut):** 8 + 5×9 + 5×8 + 20×6 + load 40 + unload/sort 90 ≈ 5.0–5.5 min → 11–12 sheets/h *machine-paced*. This matches forum data: "5 min per nest ≈ 12 sheets/h", shops planning **7 sheets/h** (3–12 range), a Rover S with auto-outfeed and two feeders at **10–12 sheets/h** ([Woodweb beam saw thread](https://www.woodweb.com/knowledge_base/CNC_Equipment_Beam_Saws_and_Cabinet.html), [Woodweb CNC/beam saw](https://woodweb.com/knowledge_base/Machinery_Dilemma_CNC_or_Beam_Saw.html)). Stack-cutting 3 identical sheets: **8–10 min per 3-sheet book**; mixed sizes 12–25 min per 3-sheet run [FORUM: [Woodweb nested vs beam saw](https://woodweb.com/cgi-bin/forums/cnc.pl?read=778938)]. One shop with a 5-high-capable saw cutting singles reached only 47 sheets/day actual vs 67 theoretical [FORUM].

### (iii) Driving attributes
Number of rips, cross cuts, head/third cuts; strip count (each strip = one re-feed); book count; cut lengths; parts per sheet (labelling); material (thin/sensitive → lower pressure and feed); whether pattern allows multi-strip cross-cutting.

### (iv) Setup/changeover
Pattern change on CNC saws ≈ 0 (program load); KDT markets "30 s–2 min" setup per job vs 2–5 min on a sliding saw [VENDOR: [KDT](https://kdt.com.au/panel-saw-vs-beam-saw-which-cutting-solution-is-right/)]. Blade + scoring blade change 10–20 min, every 1–2 shifts on melamine [EST]. Label roll change 2–3 min [EST].

### (v) Availability losses
[EST] 8–15 % of shift: blade changes, dust extraction/air-table cleaning, label printer, offcut handling, waiting for lifts. Holzma claims its side aligner cuts cycle time "up to 25 %" and HOMAG claims "up to 20 %" S-300 vs predecessor [VENDOR] — treat as the range of *pattern-dependent* overhead you are modelling.

### (vi) Operators / handling
1 operator + 1 helper is typical for 2440×1220; 2 feeders when running at 10–12 sheets/h [FORUM]. Post-cut, the operator has "5–8 min per sheet" to label/sort/edgeband-stage parts [FORUM] — i.e., unload/sort is the bottleneck, not the saw. Load from stack: 30–60 s manual (2 persons) or lift table/vacuum.

### Optimizer time models
HOMAG **Cut Rite** lists "calculation of cutting time" and **intelliDivide** reports "production time", "parts/min", "average stacking height" and offers "shortest production time" as an objective, but neither publishes the formula ([Cut Rite brochure](https://www.homag.com/fileadmin/product/paneldividing/brochures/cutrite/panel-dividing-saw-cut-rite-en.pdf), [intelliDivide](https://www.homag.com/en/product-detail/software/work-preparation/intellidivide-cutting)). **MAGI-CUT**'s saw simulator is the documented analogue: `Pattern time = Average cycle time × number of cycles; Run time = Σ pattern times`, with parameters for rip/cross speeds, return speed, "max width for cross cutting multiple strips", and a variance report comparing actual vs estimated cycle times ([MAGI-CUT saw simulator](https://www.magi-cut.co.uk/files/html/V12webhelp/mct2144.htm), [saw parameters](https://www.magi-cut.co.uk/files/html/V12webhelp/sawparam.htm)). Yield: beam-saw optimization typically 85–92 % on cabinet jobs; a Woodweb contributor claims 30–40 % *better* yield than a slider [FORUM, probably overstated].

---

## 2. Sliding table saw (판넬쏘)

```
T_sheet = T_load + N_cuts·(t_set + L_cut/v_hand + t_handle) + T_stack
```
- `v_hand` manual push 8–15 m/min; `t_set` fence/stop setting 5–15 s (0 for repeat cuts); `t_handle` 8–15 s per cut (turn, restack) [EST].
- Per cut all-in **20–40 s**; 20–30 cuts/sheet → 8–15 min/sheet.
- [FORUM] "10 min per sheet on jobs of 10+ sheets", "about 6 sheets/h", experienced breakdown-only "20–30 sheets in 1–2 h" (≈3–5 min/sheet, strips only), 23 sheets in 1.5 h ([Woodweb slider vs CNC](https://woodweb.com/cgi-bin/forums/cabinetmaking.pl?read=833544), [slider vs cabinet saw](https://woodweb.com/knowledge_base/Sliding_Table_Saw_Versus_Conventional_Cabinet_Saw.html)). Vertical panel saw ≈ 10 min/sheet, 6/h [FORUM].
- 1 operator; sheet lift is the hard part (2nd person or roller/cart for loading). CV high (0.4–0.6) because operator-paced [EST].

---

## 3. CNC nesting router (네스팅 CNC)

### (i) Model
```
T_sheet = t_load + t_vac + t_label_pre + Σ_tools [ L_path,k / v_f,k ] + N_parts·(t_ramp + t_lead)
        + N_holes·t_hole + N_tc·t_tc + t_unload + t_clean(spoilboard/table)
```
`L_path` = Σ part perimeters (nesting does not share edges unless common-line cutting) + onion-skin/second pass if used. Drilling via spindle (ramp plunge) or boring head.

### (ii) Defaults
| Term | Default | Basis |
|---|---|---|
| `v_f` 18 mm PB/MDF, 12 mm compression bit | 15 m/min | DTF Z2+2 12–18 m/min; DTE/DTF 15–20 m/min; DTM "worth it at 20+ m/min" [VENDOR: [Smarter Production feeds](https://smarterproduction.co.uk/blog/feeds-and-speeds-cnc-routing-practical-guide), [nesting bits guide](https://smarterproduction.co.uk/blog/cnc-nesting-router-bits-complete-guide)]; 20–22 m/min at 16k rpm with 15 HP; 11.4 m/min (3/8" bit, light machine); 15.2 m/min (3/4" MDF/melamine) [FORUM: [Woodweb nesting feed](https://woodweb.com/cgi-bin/forums/cnc.pl?read=831094)] |
| `t_ramp + t_lead` per part | 2–4 s | [EST] |
| `t_hole` (spindle drill) / (boring head) | 2.5 s / 0.8 s | [EST] |
| `t_tc` linear ATC | 8 s | 3–8 s, 3–5 s, 8–20 s [VENDOR: [AccTek](https://www.acctekgroup.com/how-to-choose-automatic-tool-changers-for-cnc-routers/)] |
| Machine time, standard cabinet nest | 5 min | 4–7 min; 5–7 min; shelf-only 3–4 min; closet verticals with system holes 20+ min [FORUM: [Woodweb minutes per sheet](https://woodweb.com/knowledge_base/CNC_Routing_Minutes_per_Sheet.html), [sheets per day](https://woodweb.com/cgi-bin/forums/cnc.pl?read=853952)] |
| Manual unload + label + reload | 4–6 min | [FORUM] |
| Full manual cycle sheet-to-sheet | 10–15 min | [FORUM] "12–15 min ballpark"; "10 min incl. offload/labeling" |
| Auto load/unload sheet change | 45–70 s | 45 s (Biesse auto load/unload); ~1 min incl. table cleaning [FORUM: [Woodweb loading](https://www.woodweb.com/cgi-bin/forums/cnc.pl?read=840112)] |
| Parts per sheet (kitchen carcass) | 10–14 | [EST] |

Throughput: 5–6 sheets/h with labels + pilot holes; planning 7/h; 10–12/h with auto-outfeed (kitchens); 20/h tall cabinets [FORUM]; vendor claims 8–15/h [VENDOR: [YM edgebanding](https://www.ymedgebanding.com/cnc-nesting-machine/)]. Sanity: 12 parts × 2.4 m perimeter = 29 m / 15 m/min = 1.9 min cutting + 40 holes × 2.5 s = 1.7 min + 4 tool changes 0.5 min + ramps 0.7 min ≈ 4.8 min — consistent.

### (iii) Attributes
Σ perimeter, part count, hole count & type (system holes dominate variance), tool count, sheet thickness/material (feed), labeling mode, unload mode (manual/pusher/robot), onion-skin/second pass.

### (iv) Setup
Program/tool list change 1–3 min; spoilboard surfacing 5–10 min every 1–3 days; bit change manual 30–90 s [VENDOR]; vacuum pods n/a. Changeover "averages about 2 min" [FORUM].

### (v) Losses [EST]
Spoilboard/vacuum leaks (small parts moving), chip clearing, label printer, bit wear (compression bits 1–2 shifts on melamine): 10–20 % of shift; nesting is typically operator-unload-bound.

### (vi) Operators
1 operator for manual cells (load+unload+label, hence 10–15 min cycles); 2nd person or auto-unload halves the sheet-to-sheet time. A sheet weighs 40–50 kg → 2 people or vacuum lifter for manual loading.

---

## 4. Edge bander (엣지밴더)

### (i) Model
```
T_part = Σ_passes [ (L_edge,i + G) / v_f ] + (N_pass − 1)·t_turn + t_load + t_unload + t_wait_return
Effective edge-m/h = 60·v_f · L/(L+G) · A_minor
```
With a return conveyor, `t_turn` becomes loop time but overlaps with machine feed (one operator); without it, two operators and `t_turn ≈ 0` but labor doubles.

### (ii) Defaults
| Term | Default | Basis |
|---|---|---|
| `v_f` by class | 6–8 / 10–12 / 14–20 / 25–40 m/min | SPEC: EDGETEQ S-200 8–11, S-240 11, S-300 8–14, S-380 8–20, S-800 up to 40; SCM Stefani X/HP 25–30 ([HOMAG S-380](https://www.homag.com/en/product-detail/machines/edge-banders-tenoners/edge-banding-machines/edge-banding-machines-edgeteq-s-380-profiline-8-20-mmin-feed-speed), [Stefani X/HP](https://www.wurthbaermachinery.com/SCM-Stefani-X-HP-Two-Coil-Edgebander.html)) |
| `G` gap | 0.45 m (12 m/min class) | 350 mm "reduced gap" Stefani X/HP; 350–650 mm on a 12 m/min machine [SPEC]; HOMAG sells "workpiece gap optimization" as an option; IMA with return listed "≈35 mm" (likely a listing error—verify) |
| Corner-rounding feed cap | 11 m/min (vs 16 without) | [Höchsmann WTP](https://wtp.hoechsmann.com/lexikon/39016/vorschubgeschwindigkeit) |
| `t_turn` manual (part < 1 m) | 3–5 s | [EST] |
| `t_load/unload` | 3–6 s each | [EST] |
| Passes per part | 2 (carcass) / 4 (door, Doucet) | [Doucet BT3](https://www.doucetinc.com/en/resources/4/bt3-complete-review-bt3-return-conveyor-for-edgebander) |

**HOMAG's own "max running metres of edge per hour" table** (its product-finder page; pairings partially garbled in extraction): 11 m/min → 320–360; 14 → 360; 18 → 460; 20 → 640; 25 → 860; 30 → 1070; 35 → 1280; >35 → 1500 m/h ([HOMAG edgebanders](https://www.homag.com/en/machines/edge-banders-tenoners/edgebanders-and-edge-banding-machines)). Dividing by 60·v_f gives an **implied effective factor of 0.45–0.60** (e.g., 1280/2100 = 0.61; 360/840 = 0.43) — a useful default for `L/(L+G)·A`.

Measured/anecdotal output: rated 21 ft/min but realistic average **8 ft/min (≈38 %)** [FORUM: [Woodweb charging for edgebanding](https://woodweb.com/knowledge_base/Charging_for_Edgebanding.html)]; 24" base cabinet: 4 parts edgebanded in 3 min (45 s/part) [FORUM: [Woodweb high-volume](https://woodweb.com/knowledge_base/Streamlining_HighVolume_Cabinet_Production.html)]; dealer claims 20–50 panels/h (SCM ME 25) and 150–200 panels/shift at 23 ft/min with one operator [VENDOR: [Wurth ME25](https://wurthmachinery.com/blog/automatic-edgebanding-for-cabinet-shops-the-scm-me-25-minimax-delivers-professional-results-without-the-complexity/)]; HOMAG: EDGETEQ S-500 + LOOPTEQ O-600 return = **800–1000 parts/shift** [VENDOR: [HOMAG news](https://www.homag.com/en/company/news/news/article/edge-banding-machines-new-equipment-variants-ensure-even-greater-flexibility-and-efficiency)].

### (iii) Attributes
Edge length per pass, number of banded edges, part width (<70–75 mm min), edge thickness (0.4/1/2 mm → trimming/scraping load, sometimes speed), corner rounding on/off, glue type, material (PB vs MDF premill), return-conveyor presence.

### (iv) Setup/changeover
- Glue pot warm-up from cold 10–15 min; from standby (110 °C) ≈ 5 min ([Coast Machinery](https://www.coastmachinery.com/4-tips-on-how-to-maintain-your-edgebanders-glue-pot/), [Woodworking Network](https://www.woodworkingnetwork.com/best-practices-guide/panel-processing/4-tips-edgebander-glue-pot-maintenance)).
- EVA↔PUR: <8 min (roller systems, Kenyon), ~15 min hybrid pot (Casadei), near 0 with dual melting units ([Glue Guns Direct](https://www.gluegunsdirect.com/service-and-advice/misconceptions-about-pur-adhesive-and-how-they-should-be-run/), [Casadei](https://www.casadei-industria.com/en/knowledge/eva-or-pur-glue-for-edge-banding-a-guide-to-choosing-right/)).
- Tape roll change ≈ 5 min (vendor OEE example; a 300 m roll at 20 m/min lasts only 15 min of feed) ([PVC film vendor](https://pvcdecorativefilm.com/how-can-1mm-pvc-edge-banding-optimize-your-wpc-door-line/)); thickness change with automatic trimmer/scraper presets 1–3 min, manual 5–15 min [EST]; colour change on magazine machines <1 min [EST].
- PUR end-of-shift purge/cleaning 10–20 min [EST].

### (v) Losses [EST]
Minor stops (tape jam, glue line check, trimmer chips, first-part inspection) 10–15 %; cleaning 5 %; roll/colour changes 5–10 % in high-mix shops. Net availability ≈ 0.7–0.8.

### (vi) Operators
2 without return (one each end); 1 with return conveyor; vendors claim return halves labor ([KDT Orbit](https://kdt.com.au/product-category/woodworking-machinery/edge-banders/), [HOMAG return](https://www.homag.com/en/machines/automation/return-conveyors)).

---

## 5. Boring (보링)

### (i) CNC point-to-point / vertical center
```
T_part = t_load + t_clamp + Σ_i d_i / v_rapid + N_holes·t_hole + N_groups·t_headshift + N_tc·t_tc + N_flip·t_flip + t_unload
```
- `v_rapid` 25–50 m/min X/Y, 15–25 m/min Z (Skipper V31: 25/50/25; BHX 050/200: 50/50/15) [SPEC: [Höchsmann Skipper V31](https://wtp.hoechsmann.com/en/lexikon/22776/skipper_v_31), [LumbermenOnline BHX](https://www.lumbermenonline.com/find-for-sale/Weeke-Boring-Machine?class=Woodworking&category=Boring+Machine&manufacturer=Weeke&makeid=1953)].
- `t_hole` 0.8–1.5 s for a gang-head group (approach/drill/retract); 1.14 s per hole indexed on a linear-motor drill (metal, patent reference) ([USPTO 5346345](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5346345)); routing/grooving at 8–15 m/min.
- Typical cabinet side (2 rows system holes + hinge/construction holes): **40–90 s** machine, +15–25 s load/unload on a BHX-type vertical [EST]. Horizontal-hole/flip logic can double it; a PLOS ONE study found 42 % of parts limited by slow milled grooves and achieved +56 % drilling efficiency on long-idle panels by replacing milled grooves with sawn grooves and removing flips ([PLOS ONE 2026](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0339912); earlier case study: −14 % drilling occurrences, +3.9 % efficiency, [PMC12068583](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12068583/)).

### Multi-spindle (line) boring machine (다축 보링)
```
T_part = t_load_position + N_strokes·t_stroke + t_unload ; t_stroke ≈ 4–6 s (23-spindle head)
```
[FORUM] 23-spindle: cycle down/drill/up ≈ 5 s; 20–30 s per part total; another estimate 45 s/cycle ([Woodweb boring cycle time](https://woodweb.com/knowledge_base/Boring_Machine_Cycle_Time.html)); theoretical lower bound 3.8 s with 2.5 s load/clamp [VENDOR calc: [Firgelli](https://www.firgelliauto.com/blogs/mechanisms/multiple-drilling-machine)]. Setup (pin/bit arrangement, fence stops) 10–30 min per pattern [EST] — this is the dominant term for small batches.

### Six-sided drilling (6면 드릴)
Claims of "10–20 parts/min" were **not** supported by any source found. Documented rates: 700–800 panels per 8 h (≈1.5–1.7/min, BCD2812D) [VENDOR: [BCAM](https://www.bcamcnc.com/cnc-machine/six-side-drilling-machine/)]; 1.3–1.8 "slices"/min [VENDOR: [Zicar C6D](https://zicarcnc.com/product/cnc-six-sided-drilling-machine-c6d/)]; Chinese daily capacity by configuration (8 h, ~10 parts per full sheet): 2 drill packs 90–110 sheets, 3 packs 110–130, 4 packs dual-channel 160–200, 6 packs dual 220–260 → **≈1.9–5.4 parts/min** ([拓雕](http://m.51stcnc.com/h-nd-62.html)); 3-machine line with drilling unit 3200–3800 parts/10 h ≈ 5.3–6.3/min [VENDOR: 品脉]; HOMAG DRILLTEQ H-330 dual-channel processes two narrow parts simultaneously ([HOMAG CN](https://www.homag.com.cn/%E6%96%87%E7%AB%A0/1439)). Model: `T_part = t_infeed_measure (3–5 s) + max(top,bottom) drilling + side/end drilling + t_outfeed` ≈ 10–30 s; use **12–20 s** for a standard side with dual gantry, 25–40 s single gantry [EST].

### Hinge boring (경첩 보링)
Single-spindle Blum Minipress: 1 s machine cycle per 35 mm cup [listing: [Surplus Record](https://surplusrecord.com/machinery-equipment/woodworking-boring-machines/)]; realistic per hinge incl. positioning 8–15 s; per door (2–3 hinges) 25–45 s; with insertion (press-in hinge) +5 s/hinge [EST].

### Operators
1 per machine; vertical CNC and 6-side machines allow 1 operator to run 2 machines when conveyorized.

---

## 6. Hardware insertion / assembly (하드웨어·조립)

| Operation | Time | Basis |
|---|---|---|
| Dowel glue + insert, dedicated unit | 1.5 s/dowel (40/min, Gannomat Selekta) | [VENDOR: [Woodworking Network](https://www.woodworkingnetwork.com/iwf/iwf-products/automated-dowel-inserter-glues-and-inserts-40-dowels-minute)] |
| CNC-integrated dowel (Holz-Her PinJet) | ~3 s/dowel | [VENDOR] |
| Bore+glue+dowel at 64 mm pitch (Pillar/OMAL) | ≈1 s each; HP5D 10 s + 15–30 s grooves | [VENDOR: [Pillar](https://pillarmachine.com/h49-horizontal-bore-and-dowel-insertion-machine/), [OMAL Velox](https://wurthlac.com/product/118655/OMAL-Velox-1300-Horizontal-Bore-Dowel-Machine)] |
| Manual dowel/cam/minifix insertion | 3–5 s per fitting (MTM-2 class: reach/grasp/position/press) | [EST] |
| Hinge + plate attach manual | 20–30 s per hinge | [EST] |
| Case clamp cycle (auto) | 30 s (Dynma VK-015); closing 20–40 s, infeed 2.4–12 m/min (OCMAC) | [VENDOR: [Scosarg](https://www.scosarg.com/new-machines/assembly/clamping-machines)] |
| Manual/semi-auto clamp | ~3 min per case | [FORUM: [Woodweb adhesives](https://woodweb.com/cgi-bin/forums/adhesives.pl?read=788988)] |
| Carcass box assembly (parts ready) | 7 min (24" base), 10 min (40–50/day), 24–32 min (15–20/day) | [FORUM: [Woodweb productivity](https://woodweb.com/knowledge_base/Cabinetmaking_Productivity.html), [assembler productivity](https://woodweb.com/knowledge_base/Cabinet_Assembler_Productivity.html)] |
| RTA assembly (retail guides) | wall 7–10 min, base 10–15 (or 25–35) min | [VENDOR] |
| Complete cabinet, all labour | 0.425–0.5 box per labour-hour (≈2–2.4 h/box) | [FORUM] |

Model: `T_box = t_setup_jig + N_joints·t_joint + N_hw·t_hw + t_square/clamp + t_back + t_handle`. Default kitchen base: 20 dowels/cams × 4 s + 4 panels positioning 60 s + clamp 30–180 s + back 60 s ≈ **5–8 min with 1 assembler**, 2 assemblers ≈ 60 % of that (not 50 %). No Korean 싱크대 standard-time study was found; the SPS-KHFC 001-0438:2022 standard covers testing only. MTM/MOST: 1 TMU = 0.036 s; use BasicMOST for cycles of seconds–minutes ([Apparel Resources PMTS](https://in.apparelresources.com/business-news/manufacturing/predetermined-motion-time-system-calculate-standard-time-using-mtm-modapts/)). An MTM-based assembly-line case study exists for method reference ([MDPI 2023](https://www.mdpi.com/2076-3417/13/10/6265)).

---

## 7. Finishing (도장)

**Spray (manual):** `T_coat = A_m2 · t_spray,m2 + t_handle + t_flash`; `t_spray,m2` 0.5–1.0 min/m² per face for manual airless/air-assisted incl. overspray passes; a 600×700 door both faces+edges ≈ 1.0 m² → 1–2 min per coat [EST]. **Automatic door spraying:** 20–25 doors/h (Godn SPD2500D), 24 doors/h all sides at 2–2.5 min each (PURETE), 120 single-face doors/h (Karabudak), 150–240 doors per 8-h shift (Yich, Leadertech), conveyor/line speed 3–6 m/min (5–25 m/min conveying) [all VENDOR: [Godn](https://www.godnmac.com/cabinet-door-spraying-machine-spd2500d-3d.html), [PURETE](https://www.puretemac.com/how-automatic-spray-painting-machines-revolutionize-wood-finishing.html), [Karabudak](https://karabudakmakine.com/en/kr-bm-1000-k-automatic-spraying-machine/)].

**Flash-off / drying** [EST — no technical data sheets reachable]: PU 2K: flash-off 10–20 min at 20 °C before next coat/oven; sandable 2–4 h ambient or 30–45 min forced at 40–50 °C; full stack-ability overnight. Water-borne: recoat 2–4 h ambient (consumer source: [Woodworking Advisor](https://woodworkingadvisor.com/how-long-to-wait-between-coats-of-polyurethane-on-hardwood-floors/)), forced 20–30 min at 40 °C. Batch constraint: drying racks/ovens cap WIP → model as a batch server with capacity = rack slots and service = drying time. **UV lines:** roller coater 0–20 m/min [VENDOR: [Weho](https://www.wehomachinery.com/product/uv-roller-coater-machine-for-wood-furniture-cabinet-mdf-melamine-panel)]; patent examples 9 m/min for pigmented UV topcoat on MDF after 2 min flash-off at 49 °C, and 30 m/min for thin layers ([USPTO 5300331](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5300331)). Colour change: manual gun/pot flush 10–20 min; automatic line with gun purge 3–8 min [EST].

**Membrane press:** 4–5 min total cycle (Robo double-table) [VENDOR: [Scosarg](https://www.scosarg.com/robo-press-vacuum-membrane-press)]; 2 min small-shop [FORUM]; Wemhöner Professional 3000 (3.4×1.5 m platen) 20–30 cycles/h; door lay-up 1/min manual to 6/min automated [VENDOR: [Wemhöner](https://www.wemhoener.de/en/applications/doorconcept/)]; short-cycle melamine press 225 cycles/h but realistic time utilization 80 % ([WBPI](https://www.wbpionline.com/analysis/wemhner-presses-on-8522037/)). Model: `T_cycle = t_layup (n_doors × 20–40 s) + t_press (90–180 s) + t_unload`; doors per cycle = platen area / door footprint × 0.6–0.7 packing.

**PET/PUR flat lamination:** 1–25 m/min listed; practical 10–15 m/min for high-gloss PET [VENDOR: [Solwood](https://www.solwoodgroup.com/product-page/pur-hot-melt-flat-panel-laminating-machine-sc-pur-cold-1350)]; profile wrapping 3–65 m/min, doors 25 m/min [VENDOR]. Model as `(L+G)/v_line` with G 0.1–0.3 m and PUR cure WIP hold 24–48 h before edge processing.

---

## 8. Sanding (샌딩)
`T_part = N_pass · (L + G)/v_f + t_flip·(N_sides−1) + t_handle`; `v_f` 2.5–10 m/min (Felder FW classic), 4–18 m/min (Cantek SR52), 5–25 m/min (Chinese); commissioning start 5 m/min [SPEC: [Felder](https://www.felder-group.com/en-us/products/wide-belt-sanding-machines-c1955), [Cantek](https://cantekamerica.com/product/cantek-sr52da-52-two-head-widebelt-sander/)]. Default 6–8 m/min, 1–2 passes/side for lacquer denibbing, 2–3 for calibration; `G` 0.2–0.3 m; belt change 5–10 min [EST]; 1 operator (2 for long panels).

---

## 9. Packing (포장)
`T_pack = t_carton_erect + N_parts·t_place + N_protect·t_corner + t_hw_kit + t_close/tape + N_straps·t_strap + t_label + t_move`.
[EST] KD flat-pack kitchen cabinet (6–10 parts): 3–6 min with 1–2 packers; assembled cabinet with corner boards + stretch/shrink film 2–4 min. Machine terms: automatic strapping 1.5–2.5 s/strap, tabletop semi-auto 2–3 s, pallet strapping 40 s–2 min ([Fromm](https://www.frommpackaging.ca/blog/how-to-choose-a-strapping-machine-in-2026), [Select Pack](https://selectpacktech.com/ergo-strap-machine/)); right-sized box-on-demand reported "few minutes per cabinet down to seconds" for the box-making step [VENDOR: [Packsize](https://www.packsize.com/blog/on-demand-packaging-and-cabinetry-a-match-made-in-heaven)]. Build a BasicMOST sequence model (A-B-G / A-B-P) for fitting; carton size and part count drive it.

---

## 10. Material handling
| Movement | Time | Basis |
|---|---|---|
| Manual 2-person full sheet from stack to saw/router | 25–45 s | [EST]; CNC load/unload loop 45–70 s [FORUM] |
| Vacuum lifter (1 operator) sheet to table | 30–50 s; tilt 6 s/90°, lift 0–10 m/min, vacuum build 2–3 s | [SPEC: [Scosarg lifters](https://www.scosarg.com/new-machines/vacuum-lifters/lifting-boards)]; [EST] |
| Gantry/robot destack | 35–60 s overlapped with cutting | [FORUM 45 s]; vendor "up to 3× throughput" |
| Part to cart (per part) | 4–8 s; cart of 25–40 parts | [EST] |
| Cart move between stations (30 m) | 60–120 s per trip | [EST] |

Handling touches are the real cost: time study found 39 touches/part (beam saw + PTP) vs 13 (nested) and 36 vs 11 process steps ([Woodweb nested vs beam](https://woodweb.com/cgi-bin/forums/cnc.pl?read=778938)).

---

## 11. Cycle-time variability (CV) by machine class
Factory Physics classes (Hopp & Spearman, from the book; not verifiable online this session): low CV < 0.75, moderate 0.75–1.33, high > 1.33; a patent uses <0.5 / 0.5–1 / >1 ([MetricGate Kingman note](https://metricgate.com/docs/hopp-spearman-factory-physics/)). Recommended defaults for the twin **[EST, within-product-type, excluding breakdowns]**:

| Machine | Natural CV | Driver of variance | Suggested distribution |
|---|---|---|---|
| Beam saw, automated | 0.10–0.20 per cut; 0.3–0.5 per sheet across patterns | pattern mix, book count | lognormal on residual |
| Sliding saw | 0.4–0.6 | operator, part mix | lognormal |
| Nesting CNC machine time | 0.15–0.25 same nest type; 0.5+ across (shelf 3–4 min vs vertical 20+ min) | hole count | lognormal, mixture by part family |
| Nesting manual unload | 0.3–0.5 | part count, labelling | triangular (min, mode, 2×mode) |
| Edgebander feed | 0.05–0.10 | — | deterministic |
| Edgebander handling/turn | 0.3–0.5 | part size, operator | lognormal |
| PTP/6-side drilling | 0.1–0.2 per program | hole count | normal/lognormal |
| Line borer | 0.3–0.4 | manual positioning | lognormal |
| Assembly | 0.4–0.7 | cabinet type, skill | lognormal/gamma |
| Finishing manual spray | 0.3–0.5 | area, coats, rework | lognormal |
| Packing | 0.3–0.5 | SKU, carton count | lognormal |
Include separate downtime processes (MTBF/MTTR) rather than inflating CV; cross-day nesting output swings 3–12 sheets/h [FORUM] imply CV ≈ 0.4–0.5 at the daily level.

---

## 12. Attributes to measure on site → model term, and regression forms

| Attribute (per part/order) | Machine | Model term |
|---|---|---|
| Rip count, cross-cut count, head/third cuts, strips | Beam saw | N·t_cut, N_strips·t_transfer |
| Book count, sheet thickness | Beam saw | divisor n_b, feed derate |
| Parts per sheet | Saw/Nesting | labelling, unload |
| Σ cut length, Σ part perimeter | Saw/Nesting | L/v_f |
| Hole count by type (system/construction/hinge), grooves | Nesting, PTP, 6-side | N_holes·t_hole, grooves L/v |
| Tool count per program | Nesting/PTP | N_tc·t_tc |
| Edge length per pass, passes per part, edge thickness, corner rounding | Edgebander | (L+G)/v_f, t_turn, speed cap |
| Return conveyor y/n, operators | Edgebander | t_turn overlap, labor |
| Glue type, tape colour changes per shift | Edgebander | changeover terms |
| Part area, coats, colour, batch/rack size | Finishing | A·t_m2, drying batch |
| Joint/hardware count, cabinet type | Assembly | N·t_joint |
| Carton count, parts per carton | Packing | t_carton, N·t_place |
| Load mode (manual/lifter/auto) | All | t_load |

**Fitting from 10–30 stopwatch cycles** — keep ≤2–3 free parameters, fix slopes from physics where possible:
- Beam saw: `T_sheet = β0 + β1·N_cuts + β2·N_strips` (β1 expected 5–9 s, β2 6–10 s; β0 = load+unload). If only N_cuts available, use `T = β0 + β1·N_cuts`.
- Nesting: `T_machine = β0 + β1·ΣPerimeter + β2·N_holes` with β1 fixed = 1/v_f (measured feed) and fit β0, β2; `T_handling = γ0 + γ1·N_parts`.
- Edgebander: fix feed term `(L+G)/v_f` (measure G once with tape), fit `T_part = Σ feed + γ0 + γ1·N_pass` where γ terms absorb load/turn/unload.
- PTP/6-side: `T = β0 + β1·N_holes + β2·N_grooves_m`.
- Line borer: `T = β0 + β1·N_strokes`.
- Assembly: `T = β0 + β1·N_joints + β2·N_hw` or, with few data, per cabinet-type means with lognormal σ.
- Spray: `T_coat = β0 + β1·A_m2`.
- Packing: `T = β0 + β1·N_parts + β2·N_cartons`.
Use robust (median-based) estimators with n<20; log-transform times before fitting CV; record interrupts separately and exclude them from the base cycle.

---

## 13. Benchmark effective throughput vs rating (small shops)

| Machine | Rated / theoretical | Observed effective | Ratio |
|---|---|---|---|
| Edgebander feed | 21 ft/min rated | 8 ft/min average | **0.38** [FORUM] |
| Edgebander (HOMAG's own m/h table) | 60·v_f | 320–1500 m/h | **0.43–0.61** [VENDOR] |
| Edgebander cell S-500 + return | ~1100 edges/h theoretical at 20 m/min, 0.6 m parts, 0.5 m gap | 800–1000 parts/shift (≈400–500 edges/h at 4 edges) | ≈0.4 [VENDOR] |
| Nesting CNC | vendor 8–15 sheets/h | 5–7 sheets/h manual; 10–12 auto-outfeed | **0.4–0.6** [FORUM] |
| Beam saw | 5-sheet book capability (67 sheets/day planned) | 47 sheets/day single-cutting | **0.7** of plan, ≈0.3 of book capability [FORUM] |
| Short-cycle press | 220–225 cycles/h | 80 % time utilization | 0.8 [VENDOR/WBPI] |
| Six-sided drill | vendor "10–20 parts/min" claims (unsourced) | 1.5–6 parts/min documented | ≈0.2–0.4 vs claim |
| Cabinet assembly | 40–50 boxes/day/assembler (assembly only) | 0.42–0.5 box per labour-hour all-in | — |

Rule of thumb for the twin: **effective = 0.4–0.6 × nameplate** for machine-paced stations in small/medium shops (operator-bound), 0.6–0.8 for automated cells with returns/robots; OEE for ideal-cycle calibration is notoriously mis-estimated by "a factor of 2 or more" ([MTDCNC](https://mtdcnc.com/magazines/why-oee-might-not-be-the-right-metric-for-cnc-productivity/)).

---

### Open items not resolved (sources unreachable / search budget exhausted)
Korean OEM specs (해성/한솔/대성 런닝쏘, 국산 6면드릴 분당 rates — only a 나무신문 note that 한솔 CNC 런닝쏘 handles 0.45–2 m/min soft-edge work), exact Cut Rite/intelliDivide time model internals, PU/water-borne flash-off from coating TDS, HOMAG EDGETEQ gap values per model, and a published woodworking OEE/CV study. These are marked [EST] above and should be the first stopwatch targets on site.

Additional source index: [Woodweb panel processing time](https://woodweb.com/knowledge_base/Panel_Processing_Time_with_and_without_CNC.html), [Woodweb time to produce cabinets with CNC](https://woodweb.com/knowledge_base/Time_Needed_to_Produce_Cabinets_with_a_CNC_Router.html), [HOMAG S-200](https://www.homag.com/en/product-detail/panel-dividing-saw-sawteq-b-130), [Best In Group edgebander guide](https://www.bestingroup.com/edge-banding-machine-station/), [Global Woodmach edge bander selection](https://globalwoodmach.com/edge-banding-machine-for-cabinet-production/), [Elasn gantry loading](https://www.elasn.com/automatic-gantry-loading-and-unloading-machines-for-woodworking/), [Doucet return conveyor](https://www.doucetinc.com/en/resources/4/bt3-complete-review-bt3-return-conveyor-for-edgebander), [Furniture Production BHX](https://furnitureproduction.net/resources/weekes-bhx-cnc-drilling-centres-range-proves-a-success-with-record-sales), [知乎 六面钻](https://zhuanlan.zhihu.com/p/329871931).