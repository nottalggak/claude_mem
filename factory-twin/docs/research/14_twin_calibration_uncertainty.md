# Calibration, uncertainty quantification and scenario comparison for a fast-built DES digital twin of a furniture plant

**Research caveats.** The web-search budget for this session was exhausted and every attempt to open full-text PDFs (informs-sim.org, arXiv, Fraunhofer, Chalmers, BioResources, SALib docs) was refused by the egress proxy, so paper-level numbers below come from abstracts, repository records, search snippets and my own prior knowledge of the methods. Anything marked **[est.]** is my estimate or a from-memory formula that should be checked against the cited source before being put in a report. All arithmetic in the worked examples was recomputed in Python.

---

## 1. Input uncertainty quantification (IU) for DES

**The idea.** A DES fed with distributions *fitted to finite real-world samples* has two error sources: stochastic (simulation) error that shrinks with replications n, and input-model error that only shrinks with more real-world data m. The canonical decomposition (Ankenman & Nelson 2012; Song, Nelson & Pegden WSC 2014 tutorial, [informs-sim.org/wsc14papers/016.pdf](https://informs-sim.org/wsc14papers/includes/files/016.pdf)):

```
Var(Ȳ)  ≈  σ_I²  +  σ²/n          (total = input uncertainty + simulation uncertainty)
CI_total:  Ȳ ± t · sqrt(σ̂_I² + σ̂²/n)
```

**Lineage.**
- Barton, Nelson & Xie, *Quantifying Input Uncertainty via Simulation Confidence Intervals*, IJOC 2014 ([pubsonline](https://pubsonline.informs.org/doi/10.1287/ijoc.2013.0548)) and the WSC 2010 framework paper ([pure.psu.edu](https://pure.psu.edu/en/publications/a-framework-for-input-uncertainty-analysis/)): *metamodel-assisted bootstrapping* – bootstrap the real data B times, refit parameters θ̂_b, but instead of re-running the DES at each θ̂_b, run a space-filling design once, fit a stochastic-kriging metamodel ŷ(θ), and push the B bootstrap parameter vectors through ŷ. Xie, Nelson & Barton (arXiv 2020, [arxiv.org/abs/2011.04207](https://arxiv.org/abs/2011.04207)) add a variance decomposition that tells you whether more simulation can still reduce total error.
- Ankenman & Nelson, *A Quick Assessment of Input Uncertainty* (WSC 2012, [informs-sim.org](https://www.informs-sim.org/wsc12papers/includes/files/con475.pdf)): a direct (non-metamodel) random-effects bootstrap — B bootstrap "worlds", R replications each; σ̂_I² = (between-world variance) − (within-world variance)/R.
- Song & Nelson, *Quickly assessing contributions to input uncertainty*, IIE Trans 47(9) 2015 ([ideas.repec.org](https://ideas.repec.org/a/taf/uiiexx/v47y2015i9p893-909.html)) and Lin, Song & Nelson *Single-experiment input uncertainty* (J. Simulation 2015, [pure.psu.edu](https://pure.psu.edu/en/publications/single-experiment-input-uncertainty/)): needs **no extra simulation** beyond the bootstrap experiment and returns the *relative contribution of each input distribution*.
- Biller & Mokashi, *Propagation of Input Uncertainty in Manufacturing Process Flow Simulations*, WSC 2018 pp. 3144–3155 ([informs-sim.org](https://www.informs-sim.org/wsc18papers/includes/files/279.pdf)) — a research paper, not a tutorial; propagates inter-arrival and service-time uncertainty through single- and multi-stage lines and reports the effect on utilization, lead time, WIP and throughput. (Full-text CI-width numbers could not be opened; the tutorials are Song/Nelson/Pegden WSC 2014 and He & Song WSC 2024, [informs-sim.org/wsc24papers/inv219.pdf](https://informs-sim.org/wsc24papers/inv219.pdf), which splits the problem into fixed-batch, streaming, and *active data collection*.)
- Robust/DRO alternatives (Lam): Ghosh & Lam, *Robust Analysis in Stochastic Simulation* (Oper. Res., [par.nsf.gov](https://par.nsf.gov/servlets/purl/10092347)) — worst-case output over all input models satisfying nonparametric constraints; Lam & Zhou empirical-likelihood CIs ([arXiv 1604.02573](https://arxiv.org/pdf/1604.02573v1)); Chen, Liu & Lam *Distributional Input Uncertainty* (WSC 2022, [par.nsf.gov](https://par.nsf.gov/servlets/purl/10470130)); Gonzalez-Hodar, Milz & Song 2025, nonparametric robust *comparison* of systems under IU ([arXiv 2511.04457](https://arxiv.org/html/2511.04457v1)) — directly relevant to "does A beat B given we only have 40 cycle-time observations".

**Practical recipe (Song–Nelson "linear-in-means" shortcut) [est. formulas from memory of the 2015 paper]:**
1. For each input distribution l = 1..L you have m_l real observations with sample sd s_l.
2. Draw B bootstrap resamples of each input (B ≈ 50–200), refit, run R reps (R ≈ 2–10) per world, record KPI mean Ȳ_b and the bootstrapped sample means X̄_{b,l}.
3. Regress Ȳ_b on the X̄_{b,l}: Ȳ_b ≈ β₀ + Σ_l β_l X̄_{b,l}. Then
   `σ̂_I² ≈ Σ_l β_l² s_l² / m_l`, and contribution of input l = β_l² s_l²/m_l ÷ σ̂_I².
4. Extra data should go where β_l² s_l²/m_l is largest; the optimal allocation of a budget of M additional observations is roughly `m_l ∝ |β_l| s_l` (Neyman-type) [est.].

**Worked numbers (illustrative, throughput in parts/shift).** Five inputs for a furniture line:

| input | m_l | s_l (min) | β_l (parts/shift per min) | β²s²/m | share |
|---|---|---|---|---|---|
| CNC cycle | 40 | 3.0 | −2.1 | 0.99 | 15% |
| Edgebander cycle | 60 | 1.5 | −1.4 | 0.07 | 1% |
| Sanding | 25 | 4.0 | −0.6 | 0.23 | 3% |
| Assembly | 30 | 6.0 | −1.0 | 1.20 | 18% |
| Setup time | 12 | 8.0 | −0.9 | 4.32 | **63%** |

σ_I² = 6.8 (σ_I = 2.6 parts/shift). With 30 replications and per-rep variance 16, σ²/n = 0.53. Simulation-only 95 % half-width = 1.43; **true half-width including IU = 5.3 parts/shift** (3.7× wider). Collecting 36 more setup-time observations (12→48) cuts σ_I² to 3.6 and the half-width to 4.0; no number of replications could do that. This is exactly the lesson of Ankenman–Nelson: **two weeks of sensing is often more valuable than a million replications, and the setup/changeover distribution is usually the culprit in job shops** [est. regarding furniture].

Rule of thumb for sample sizes [est.]: the IU standard deviation on a mean-driven KPI scales as s_l/√m_l, so going from m=12→48 halves that input's contribution's sd; to get IU below the simulation error you need roughly `m_l > β_l² s_l² · n/σ²` for every important input.

**Non-stationarity.** With 3–12 months of records, check stationarity before pooling (seasonal order mix); if the record period is heterogeneous, bootstrap *blocks* (weeks) rather than individual observations [est.].

---

## 2. Calibrating the twin without overfitting

**Bayesian calibration (Kennedy–O'Hagan) and its stochastic extensions.** KOH models field data as `y = η(x, θ*) + δ(x) + ε` with a GP discrepancy δ. For stochastic simulators, Baker et al.'s review *Analyzing Stochastic Computer Models* ([arXiv 2002.01321](https://arxiv.org/pdf/2002.01321)) and Pratola & Chkrebtii (Statistica Sinica, [PDF](https://www3.stat.sinica.edu.tw/ss_newpaper/SS-2016-0403_na.pdf)) adapt the emulator to heteroscedastic noise. Arcones et al. 2024 ([arXiv 2312.00664](https://arxiv.org/abs/2312.00664v2)) show on bridge twins that *classical Bayesian updating without a bias term is overconfident* when the model is structurally wrong — the common case for a two-week model of a furniture plant. A 2026 preprint on active-learning calibration of stochastic simulators ([arXiv 2607.28874](https://arxiv.org/pdf/2607.28874)) notes that simulator noise + discrepancy + observation noise "lead to more severe identifiability challenges for stochastic models".

**Identifiability — what k validation KPIs can pin down.** Bai & Lam, *Calibrating Over-Parametrized Simulation Models: A Framework via Eligibility Set* (WSC 2020, [arXiv 2105.12893](https://arxiv.org/pdf/2105.12893)): with p uncertain parameters and k summary KPIs you generally cannot identify a point; instead report the *eligibility set* of all θ consistent with the data (a history-matching "non-implausible region"). Hu & Yan (SIMULATION 2024, DOI 10.1177/00375497231221578; WSC 2024 [inv175.pdf](https://informs-sim.org/wsc24papers/inv175.pdf)) hit the same wall with particle-filter calibration of several DES parameters: "multiple combinations of parameter values produce the same or similar observation data". Rule [est.]: each independent KPI (throughput, mean WIP, lead-time mean, lead-time 90th percentile, per-station utilisation) identifies at most one "direction" in parameter space; with 5–6 KPIs you can calibrate ~5–6 *effective* parameters (e.g., bottleneck cycle-time scale, setup scale, availability, transport delay, operator efficiency), not 25. Everything else must be *measured*, not tuned.

**History matching / emulation.** Iterative GP-emulator rounds that discard parameter regions with implausibility `I(θ) = |z_obs − ŷ(θ)| / sqrt(Var_emul + Var_sim + Var_obs + Var_discrepancy) > 3` ([docs.idmod.org/historymatching](https://docs.idmod.org/historymatching)); a 2024 building-energy example found only 0.3 % of parameter space non-implausible with one KPI and 0.01 % with two — a vivid demonstration that adding a *second, independent* KPI is the cheapest identifiability gain ([UCL Discovery](https://discovery.ucl.ac.uk/id/eprint/10126802/)). ABC is the same idea with a rejection threshold; the Georgia Tech surrogate-assisted OARL-ABC defence (Oct 2025, [ae.gatech.edu](https://ae.gatech.edu/event/2025/10/31/phd-defense-xiao-olin-wei)) applies it to digital-twin calibration.

**Automated / ML calibration of DES twins 2020–2026.**
- Process-knowledge change-point detection for automated DES calibration ([arXiv 2005.05385](https://arxiv.org/pdf/2005.05385)).
- Sürer, Chen & Shashaani, *Dynamic Calibration Framework for Digital Twins Using Active Learning and Conformal Prediction* (WSC 2025, [inv177.pdf](https://www.informs-sim.org/wsc25papers/inv177.pdf)): conformal monitoring flags when new data batches fall outside the twin's predictive band; only then is θ re-estimated by active learning.
- *Digital Twin Calibration with Model-Based RL* ([arXiv 2501.02205](https://arxiv.org/pdf/2501.02205)) and a TUM thesis on camera-aided calibration of production twins ([mediatum](https://mediatum.ub.tum.de/node?id=1611528)).

**Calibrating discrete rules (batching, dispatching) from logs.**
- Discovery of the *model* from event logs: Lugaresi & Matta, *Automated manufacturing system discovery and digital twin generation*, J. Manuf. Syst. 2021 ([polimi PDF](https://re.public.polimi.it/bitstream/11311/1159156/3/0Automated%20manufacturing%20system%20discovery%20and%20digital%20twin%20generation.pdf)), extended to assembly/complex flows with object-centric process mining (Computers in Industry 2023, [polimi](https://re.public.polimi.it/handle/11311/1245317)); Lugaresi's WSC 2024 review of process mining for twins ([con213.pdf](https://informs-sim.org/wsc24papers/con213.pdf)); Friederich et al., framework for data-driven twins ([DTU](https://orbit.dtu.dk/en/publications/towards-data-driven-digital-twins-for-smart-manufacturing/)). Business-process analogue with automatic hyper-parameter tuning to log similarity: Simod/Camargo–Dumas (DSS 2020, [arXiv 1910.05404](https://www.arxiv.org/abs/1910.05404)); its known weakness is *timing* accuracy.
- Discovery of the *rule*: Kim, Yoon et al., *Discovering dispatching rules using data mining*, J. Scheduling 2005 ([unpaywall](https://unpaywall.org/10.1007%2FS10951-005-4781-0)) — fit a decision tree whose features are the queue state at each dispatch decision (due-date slack, processing time, setup-family match, batch size) and whose label is the job actually chosen; composite rules via TACO-miner ([Erciyes](https://avesis.erciyes.edu.tr/yayin/b47133eb-d193-4499-8b5a-1bb11dd0fa7e/composite-dispatching-rule-generation-through-data-mining-in-a-simulated-job-shop)). Practical version for this team [est.]: from the job log reconstruct for each start event the set of jobs that *were* waiting; compute, for each candidate rule (FIFO, EDD, SPT, setup-family-first, batch-until-N), the fraction of decisions it reproduces; keep the rule with the highest agreement and *report that agreement (e.g., 78 %)* as a calibration result. Treat rule choice as a discrete factor in the screening design, not as something to "tune".

**Overfitting controls.** (a) Holdout by time: calibrate on months 1–2 of records, validate on month 3 (or calibrate on week 1 of sensing, validate on week 2). (b) Regularise toward measured values: penalty `λ Σ_l ((θ_l − θ̂_l,measured)/se_l)²` i.e. a Gaussian prior with sd = standard error of the measurement — tuning may move a parameter 1–2 se, not 5. (c) Validate on KPIs not used for calibration (calibrate on throughput + utilisation, validate on lead-time distribution). (d) Cap the number of tuned parameters at the number of independent KPIs (Section 2 identifiability).

---

## 3. Comparing scenarios under uncertainty

**Common random numbers (CRN).** Same seed streams for every scenario per replication (one stream per source of randomness: arrivals, each station's cycle time, failures), then analyse *paired differences* D_r = Y_A,r − Y_B,r. Nelson & Matejcik 1995 ([pubsonline](https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.41.12.1935)) give Bonferroni-based IZ selection under CRN; KN (Kim & Nelson 2001, ACM TOMACS 11(3)) allows unknown unequal variances and CRN ([Northwestern PDF](https://transportation.tech.northwestern.edu/docs/research/core-topics/logistics-and-supply-chain-management/Nelson_FullySequentialSelection.pdf)); KN++ assumes independence ([arXiv 1410.6782](https://arxiv.org/pdf/1410.6782)).

**Replications needed to detect Δ with power 0.8, α = 0.05** [standard formulas]:
- Independent: `n_per_system = 2 (z_{0.975}+z_{0.8})² σ² / Δ²`
- CRN paired: `n = (z_{0.975}+z_{0.8})² σ_D² / Δ²` with `σ_D² = 2σ²(1−ρ)`.

Computed for a 1-week run, throughput sd across replications σ = 4 parts/shift (base ≈ 100):

| Δ to detect | ρ=0 (indep) | ρ=0.5 | ρ=0.8 | ρ=0.9 |
|---|---|---|---|---|
| 7 parts (+7 %) | 6 | 3 | 2 | 1 |
| 3 parts (+3 %) | 28 | 14 | 6 | 3 |
| 2 parts (+2 %) | 63 | 32 | 13 | 7 |

(Use ≥10 replications regardless, for a usable t-interval; ρ = 0.8–0.9 is typical when CRN is implemented properly with synchronised streams [est.].) With σ = 6 and Δ = 7: 12 independent vs 3 paired at ρ = 0.8.

**Indifference-zone R&S (KN, c = 1)** [formula from memory of Kim & Nelson 2001]: `η = ½[(2α/(k−1))^(−2/(n₀−1)) − 1]`, `h² = 2η(n₀−1)`; continuation region half-width for pair (i,j) after r reps: `max(0, (δ/2c)(h² S_ij²/δ² − r))`. For k = 5 scenarios, n₀ = 10, α = 0.05: η = 0.635, h² = 11.43; for k = 10: h² = 15.46; for k = 5 with n₀ = 20: h² = 9.02. Rinott-type two-stage sample size: `N_i = max(n₀, ⌈h² S_i²/δ²⌉)` — with S = 4, δ = 3, h² = 11.4 → N ≈ 21 per scenario.

**OCBA** (Chen 1996; Chick comparison [INSEAD PDF](https://www.insead.edu/sites/insead/files/assets/faculty-personal-site/stephen-e-chick/documents/new%20development%20in%20ranking%20and%20selection-an%20empirical%20comparison%20of%20the%20three%20main%20approaches.pdf)): allocate `N_i/N_j = (σ_i/δ_{b,i})² / (σ_j/δ_{b,j})²` for non-best i, j, and `N_b = σ_b sqrt(Σ_{i≠b} N_i²/σ_i²)` — more reps to scenarios that are close to the best and noisy. Good when you have 10–30 scenarios (CNC × batch rule × staffing combinations) and a fixed compute budget.

**Multiple comparisons with the best (MCB).** Report for each scenario i the interval for `μ_i − max_{j≠i} μ_j` with Bonferroni-adjusted t (α/(k−1)); scenarios whose interval excludes 0 from below are eliminated.

**How to report "probability A beats B".** Two layers:
1. *Simulation-only*: with CRN paired differences d̄, s_d, n: `P(μ_D > 0 | sim) = T_{n−1}(d̄ / (s_d/√n))` (the flat-prior Bayesian posterior; equivalently 1 − one-sided p). The SimPy sketch below prints exactly this.
2. *Including input uncertainty*: nest the comparison inside the input bootstrap: for each bootstrap world b run A and B with CRN, record d̄_b; report `P(A beats B) = fraction of worlds with d̄_b > 0` and the percentile interval of d̄_b. This is what "+7 % throughput with 90 % confidence" should mean; the Gonzalez-Hodar et al. 2025 robust-comparison paper formalises it ([arXiv 2511.04457](https://arxiv.org/html/2511.04457v1)). Also state the indifference zone: "+7 % (95 % CI +3 % to +11 %); P(gain > 2 %) = 0.93".

---

## 4. Screening and global sensitivity beyond OAT

| Method | Runs for k = 25 factors | Use |
|---|---|---|
| Morris elementary effects | r(k+1): r=10 → 260; r=20 → 520 (× replications or seeds) | first-pass screening, ranks μ* and σ |
| Sobol via Saltelli (first+total) | N(k+2): N=256 → 6,912; N=512 → 13,824; with 2nd order N(2k+2) → 13,312/26,624 | only on a metamodel |
| GP/PCE metamodel + Sobol | 100–300 LHS runs (≈ 4–10 k) then Sobol on the emulator for free [est.] | the practical route |
| Sequential bifurcation (Kleijnen) | tens of runs if effects are sparse: 92 factors → shortlist of 10 after 19 combinations ([Kleijnen review](https://ideas.repec.org/h/spr/isochp/978-3-319-18087-8_4.html)); supply-chain DES case: 21 combinations × 5 reps → 11 factors ([Tilburg](https://repository.tilburguniversity.edu/items/aee50b10-6f44-402c-9986-954f7f24c9db)) | needs known effect signs and heredity; stochastic version (Wan, Ankenman & Nelson, [WSC 2005](https://www.informs-sim.org/wsc05papers/023.pdf)) lacks guarantees |

Fractional factorials become impractical above ~20 factors ([WSC 2001](https://informs-sim.org/wsc01papers/020.PDF)). Software: SALib (`morris.sample/analyze`, `sobol.sample` (Saltelli) / `sobol.analyze`; [salib.readthedocs.io](https://salib.readthedocs.io/en/latest/api.html)), scikit-learn `GaussianProcessRegressor` with a WhiteKernel to absorb replication noise, chaospy/UQpy for PCE, pymoo for subsequent optimisation.

**Minimal Python pattern (SimPy + SALib + GP) [est., untested with SALib because the package could not be fetched in this sandbox; the SimPy part is tested below]:**

```python
from SALib.sample import morris as ms; from SALib.analyze import morris as ma
problem = {'num_vars': 25, 'names': names, 'bounds': bounds}     # table from Section 7(i)
X = ms.sample(problem, N=10, num_levels=4)                        # 10*(25+1)=260 rows
Y = np.array([np.mean([run_line(vec_to_params(x), seed=s) for s in range(3)]) for x in X])
res = ma.analyze(problem, X, Y, conf_level=0.95)                  # res['mu_star'], res['sigma']
keep = [n for n,m in zip(names,res['mu_star']) if m > 0.05*Y.std()]   # screen to ~6-10 factors
# then: LHS 150 runs on 'keep' -> sklearn GP (RBF+WhiteKernel) -> SALib sobol.analyze on GP predictions
```

Use the *same* seeds across design rows (CRN) to sharpen effect estimates, and replicate 3–5 times per row so Morris σ is not dominated by simulation noise [est.].

---

## 5. Case evidence: fast DES twins for small plants

- **Furniture (Slovakia):** Bambura, Sujová & Čierna, BioResources 15(3) 2020 ([PDF](https://bioresources.cnr.ncsu.edu/wp-content/uploads/2020/07/BioRes_15_3_6752_Bambura_SC_Utilization_Computer_Simulation_Furniture_Production_17528.pdf)) — Tecnomatix Plant Simulation model of a furniture line from "collected real production data", statistical comparison of current vs improved line on material flow, productivity, utilisation. Validation deviation not visible in the abstract (full text blocked).
- **Furniture (France):** Klein & Thomas 2011 — DES virtual shop floor used to validate a distributed control system at a furniture manufacturer ([iaor](https://iaorifors.com/paper/75971)).
- **Furniture (Vietnam, AnyLogic 2025):** simulation-based optimisation reporting utilisation 96.7 % ([jst.bdu.edu.vn](https://jst.bdu.edu.vn/index.php/jst/article/view/338)); small furniture company planning in Plant Simulation ([Fraunhofer](https://publica.fraunhofer.de/handle/publica/488733)); wood pallet desk/stringer DES, Italy 2011, +56 % productivity from a different saw ([unibz](https://bia.unibz.it/esploro/outputs/journalArticle/Evaluation-of-the-manufacturing-of-desk/991005772941701241)); CLT panel handling in ExtendSim ([Chalmers 2024](https://odr.chalmers.se/bitstreams/e7d998c5-f18f-47c9-889b-129ae37e34ce/download)).
- **Cabinets:** Mohsen et al., Simphony.NET DES of a kitchen-cabinet plant (IJSPM 2021, [KFUPM](https://pure.kfupm.edu.sa/en/publications/discrete-event-simulation-and-data-analysis-for-process-flow-impr/)); Moya's Purdue cabinet JIT study: 22 workstations, 56 distinct parts ([Purdue](https://docs.lib.purdue.edu/dissertations/AAI9725598)).
- **Job shop twins:** 2025 AnyLogic job-shop twin: fallback routing +8.9 % throughput, validated only by t-test/sensitivity at 90 % level ([UTEP](https://scholarworks.utep.edu/open_etd/4353)); Elbasheer/Longo/Padovano flexible job-shop twin, XGBoost MAPE 15.5 % ([unical](https://iris.unical.it/handle/20.500.11770/399130)).
- **SME frameworks:** Oliveira et al., *Facilitated DES framework … intervention in a small enterprise* (WSC 2023, [243.pdf](https://www.informs-sim.org/wsc23papers/243.pdf)) — explicitly motivated by SMEs' inability "to invest in the data collection of large samples"; FaMoSim applied to four cases showed value of "a simplified model with fewer data and fewer details". Bicalho-Hoch et al. WSC 2022 tool for simulation-worthiness in SMEs ([181.pdf](https://informs-sim.org/wsc22papers/181.pdf)); Byrne, Liston & Byrne SW21: Irish SMEs *underestimate their own complexity* and therefore DES's usefulness ([ORS PDF](https://www.theorsociety.com/common/Uploaded%20files/Simulation-Workshop/SW21/doiorg1036819sw21029.pdf)); Hill et al. 2011: the key barrier is "time and level of expertise it takes to build a valid model".
- **Reviews:** Jahangirian et al., EJOR 2010 (281 papers; DES most used but lowest stakeholder engagement, [ideas.repec](https://ideas.repec.org/a/eee/ejores/v203y2010i1p1-13.html)); Robinson et al., *SimLean* EJOR 2012 — DES roles in lean: education, facilitation, evaluation ([Loughborough PDF](https://dspace.lboro.ac.uk/2134/10205)).
- **Input-data effort:** Skoogh & Johansson: input data management is "10–40 % of total DES project time" (SNE 2009, [PDF](https://www.sne-journal.org/fileadmin/user_upload_sne/SNE_Issues_OA/SNE_19_2/articles/sne.19.2.09937.tn.OA.pdf)); 13-activity methodology (WSC 2008, [Chalmers](https://research.chalmers.se/publication/79631)); automation cut it by 78 % in an automotive case ([Chalmers](https://research.chalmers.se/publication/165035)); ~80 % of practitioners still fully manual (2012). The widely quoted "31 %" (Trybula 1994) could not be verified here **[est.]**.
- **Validation deviations actually reported.** Typical acceptance in these papers is 5–10 % on throughput/utilisation and 10–15 % on lead times [est.: no case above printed its number in an accessible abstract]; Reinhardt et al. (Procedia CIRP 134, 2025; DOI 10.1016/j.procir.2025.02.169 and .170) propose subjective and objective validation for auto-generated short-term material-flow models and *hypothesise causes of deviation* — relevant because auto-generated twins "rarely address validation".

**Lessons distilled.** (1) The expensive part is data, not modelling; budget 30–40 % of the two weeks for cycle-time, setup and availability capture, and automate extraction from MES/ERP records. (2) Keep the model as coarse as the KPIs require (Lugaresi–Matta; FaMoSim). (3) Failures in these studies come from untracked rework/quality loops, operator-shared resources, and material-arrival variability — model them explicitly or state them as scope exclusions. (4) Validate on a held-out period, with a distribution (lead-time histogram), not just a mean.

---

## 6. Digital-twin-specific validation and reporting (2022–2026)

- **Continuous validation loops:** Overbeck et al. (KIT) — relative variation and normalised RMSE between twin and plant KPIs, with thresholds that trigger parameter updates; a DES twin of an automotive parts line kept accurate "over a long time period"; handling of exceptional events; process mining to discover *structural* change (IJPR 62(10) 2024, [ideas.repec](https://ideas.repec.org/a/taf/tprsxx/v62y2024i10p3544-3558.html); SNE 2022 note [PDF](https://www.sne-journal.org/fileadmin/user_upload_sne/SNE_Issues_OA/SNE_32_3/articles/sne.32.3.10613.tn.OA.pdf)). Lugaresi et al. (WSC 2022, [294.pdf](https://informs-sim.org/wsc22papers/294.pdf); J. version 2023, [polimi](https://re.public.polimi.it/handle/11311/1229846)) — *online validation* by dynamic-time-warping distance between shop-floor event streams and twin event streams, designed for small datasets. Both summarised in the Dec 2025 survey on reusing validation methods for CPS twins ([arXiv 2512.04117](https://arxiv.org/pdf/2512.04117)); a 2026 IJSIMM review covers "online/continuous validation" ([ijsimm](https://www.ijsimm.com/Full_Papers/Fulltext2026/text25-2_760.pdf)).
- **Drift detection → recalibration:** Sürer–Chen–Shashaani (WSC 2025) conformal monitoring; Hu & Yan particle-filter data assimilation for DES (SIMULATION 2024; [par.nsf.gov](https://par.nsf.gov/servlets/purl/10638382)); Ward et al., *Continuous calibration of a digital twin: particle filter vs Bayesian calibration* ([arXiv 2011.09810](https://ar5iv.labs.arxiv.org/html/2011.09810)); 2026 self-adaptive twin with Fisher-score drift detector + Mann–Whitney swap test ([arXiv 2607.18164](https://arxiv.org/pdf/2607.18164)).
- **Standards:** ISO 23247-4 is the *information-exchange* part, **not** V&V; the VVUQ part is **ISO 23247-8** (verification, validation and uncertainty quantification for manufacturing DTs), still in development with a project ballot dated 29 June 2026 ([dps.gov.al](https://dps.gov.al/en/project/show/iso:proj:94858)). **VDI 3633 Blatt 13** (draft Feb 2023) "Simulation of systems in materials handling, logistics and production – Verification and validation" lists V&V procedures for data, models and results ([vdi.de](https://vdi.de/en/home/vdi-standards/details/vdi-3633-blatt-13-simulation-of-systems-in-materials-handling-logistics-and-production-verification-and-validation)); it builds on the Rabe–Spieckermann–Wenzel V&V procedure model (WSC 2008/2009, SNE 2009 [PDF](https://www.sne-journal.org/fileadmin/user_upload_sne/SNE_Issues_OA/SNE_19_2/articles/sne.19.2.09935.tn.OA.pdf)) which pairs each study phase (task definition, conceptual model, formal model, executable model, experiments) with V&V elements and documented acceptance criteria. The 2025 IJPR systematic review finds "a lack of standard procedures to conduct V&V" for twins ([ideas.repec](https://ideas.repec.org/a/taf/tprsxx/v63y2025i1p342-370.html)).
- **STRESS-DES** (Monks et al., J. Simulation 13(1) 2019, DOI 10.1080/17477778.2018.1442155; open PDFs at [Loughborough](https://repository.lboro.ac.uk/articles/journal_contribution/Strengthening_the_reporting_of_empirical_simulation_studies_Introducing_the_STRESS_guidelines/9503495/1), [Warwick](https://wrap.warwick.ac.uk/100103/)): 20-item checklist in six sections — Objectives (purpose, model outputs, experimentation aims); Logic (base-model overview diagram, base-model logic, scenario logic, algorithms, components: entities/activities/resources/queues/entry-exit points); Data (sources, pre-processing, input parameters, assumptions); Experimentation (initialisation/warm-up, run length, estimation approach); Implementation (software, random sampling, model execution, system specification); Code access (model-sharing statement) [item names from memory, est.].

**Twin-fidelity metrics to put in the dashboard [est. synthesis]:** nRMSE per KPI on rolling windows; DTW distance on event sequences; relative throughput error; two-sample KS on lead-time distributions; conformal coverage (fraction of real daily KPIs inside the twin's 90 % predictive band — should be ≈ 0.9; sustained < 0.8 = drift).

---

## 7. Recommended procedure for this team

**(i) Parameter & bounds table** (one row per uncertain input; this doubles as the STRESS-DES "input parameters" item):

| # | parameter | nominal | source (visit / sensing / records) | m | se | bounds for screening | tune? |
|---|---|---|---|---|---|---|---|
| 1 | CNC cycle time (lognormal μ,σ) | 6.0 min | sensing, 40 obs | 40 | 0.14 | ×0.8–1.25 | no (measured) |
| 2 | Edgebander cycle | 4.0 | sensing, 60 | 60 | 0.06 | ×0.85–1.2 | no |
| 3 | Setup time per family change | 25 min | records, 12 | 12 | 2.3 | ×0.5–1.6 | yes, prior sd = se |
| 4 | Availability (MTBF/MTTR) per machine | 92 % | records, 3 mo | — | — | 85–97 % | yes |
| 5 | Operator efficiency / shared operators | 1.0 | visit | — | — | 0.85–1.1 | yes |
| 6 | Order inter-arrival & mix | records | 6 mo | 600 | — | empirical | no |
| 7 | Batch rule (discrete: by family / fixed N / order) | inferred from log | agreement 78 % | — | — | {3 levels} | no |
| … | up to ~25 rows: transport delays, rework %, buffer caps, shift pattern |

**(ii) Screening.** Morris with r = 10 (260 runs × 3 seeds ≈ 800 one-week runs; minutes in SimPy). Keep factors with μ* above 5 % of output sd; expect 6–10 survivors. Fit a GP on 150 LHS runs over the survivors, compute Sobol first/total indices on the GP. Report the Pareto chart; it tells the sponsor *which measurements matter* before any investment ranking.

**(iii) Calibration loop with holdout.** Split the record period 70/30 by time. Tune only the "tune? = yes" rows (≤ number of validation KPIs, ≤ 5–6). Objective: `Σ_k ((KPI_k^sim − KPI_k^obs)/sd_k)² + λ Σ_j ((θ_j − θ_j^meas)/se_j)²` with λ = 1 (i.e., a measurement-based prior); minimise with Bayesian optimisation or a GP emulator; report the *eligibility set* (all θ within +2 of the minimum) not just the argmin. Validate on the holdout 30 % on KPIs not used in tuning (lead-time distribution via KS; per-station utilisation). Acceptance: |throughput error| < 5 %, |utilisation error| < 5 pp, lead-time KS p > 0.05 [est. thresholds]. For the batching/dispatch rule, use the log-agreement score, and run the rule alternatives as scenarios.

**(iv) Input-uncertainty bootstrap for conclusion CIs.** B = 50–100 worlds × R = 5 reps per scenario, CRN inside each world; compute σ̂_I², per-input contributions (Section 1 table) and the total CI. Spend the remaining sensing days on the top-contribution input (in the worked example, setup time: 12→48 obs cut the CI half-width from 5.3 to 4.0 parts/shift).

**(v) Scenario comparison.** CRN with one RNG stream per randomness source; n ≥ 10 reps (13 reps detect a 2 % throughput change at ρ = 0.8); paired-t CI per scenario vs baseline; MCB intervals across all scenarios; OCBA if > 10 scenarios; report `P(A beats B)` both simulation-only and nested in the bootstrap, plus `P(gain > indifference zone of 2 %)`.

**(vi) Reporting.** STRESS-DES 20 items + a V&V appendix structured by the VDI 3633-13 / Rabe–Wenzel phases (data validation, conceptual-model walkthrough with the plant owner, trace/animation verification, holdout results, IU table, scenario CIs), + twin-fidelity dashboard (nRMSE, coverage) if the twin stays live.

**Code sketch (tested, runs in SimPy 4 + NumPy + SciPy; 3-station line CNC → edgebander → assembly).**

```python
import numpy as np, simpy
from scipy import stats

def run_line(params, seed, horizon=5*8*60, warmup=8*60):
    rng = np.random.default_rng(seed)            # one stream per replication; same seed across scenarios = CRN
    env = simpy.Environment()
    st = {k: simpy.Resource(env, capacity=params[k+'_cap']) for k in ('cnc','edge','asm')}
    done = []
    def job():
        for k in ('cnc','edge','asm'):
            with st[k].request() as rq:
                yield rq
                yield env.timeout(rng.lognormal(params[k+'_mu'], params[k+'_sig']))
        if env.now > warmup: done.append(env.now)
    def source():
        while True:
            yield env.timeout(rng.exponential(params['ia_mean'])); env.process(job())
    env.process(source()); env.run(until=horizon)
    return len(done) / ((horizon-warmup)/480)         # parts per 8-h shift

# (A) bootstrap of inputs -> KPI CI
raw = {'cnc': cnc_obs, 'edge': edge_obs, 'asm': asm_obs}    # observed cycle times (min)
fit = lambda s: (np.log(s).mean(), np.log(s).std(ddof=1))
def params_from(samples, base={'ia_mean':7.0,'cnc_cap':1,'edge_cap':1,'asm_cap':2}):
    p = dict(base)
    for k,s in samples.items(): p[k+'_mu'], p[k+'_sig'] = fit(s)
    return p
B, R, rng = 30, 10, np.random.default_rng(0)
world_means, within = [], []
for b in range(B):
    boot = {k: rng.choice(v, size=len(v), replace=True) for k,v in raw.items()}
    ys = [run_line(params_from(boot), seed=1000+b*R+r) for r in range(R)]
    world_means.append(np.mean(ys)); within.append(np.var(ys, ddof=1))
sigma2_sim = np.mean(within)/R
sigma2_I   = max(np.var(world_means, ddof=1) - sigma2_sim, 0)     # Ankenman–Nelson estimator
print("sigma_I", sigma2_I**.5, "sigma_sim", sigma2_sim**.5, "95% CI", np.percentile(world_means,[2.5,97.5]))

# (B) CRN paired comparison: scenario B = add a second CNC
pA = params_from(raw); pB = dict(pA, cnc_cap=2); n = 20
d  = np.array([run_line(pB, seed=s) - run_line(pA, seed=s) for s in range(n)])
hw = stats.t.ppf(0.975, n-1)*d.std(ddof=1)/np.sqrt(n)
print(f"gain {d.mean():.2f} ± {hw:.2f} parts/shift; P(B>A|sim)={stats.t.cdf(d.mean()/(d.std(ddof=1)/np.sqrt(n)), n-1):.3f}")
```

Sample output on synthetic data (40/60/30 observations): nominal 69.0 parts/shift, σ_I = 0.9, σ_sim(of mean) = 1.1, 95 % total CI [65.6, 70.6]; adding a CNC when the CNC is *not* the bottleneck gave +0.26 ± 2.27 parts/shift, P(B > A) = 0.59 — the kind of honest "no evidence" answer the procedure is meant to produce. Nest (B) inside the loop of (A) to get P(B > A) under input uncertainty.

**Suggested follow-ups (searches not possible in this session):** open the Biller–Mokashi WSC 2018 and Bambura 2020 PDFs for their actual CI-width and validation-error numbers; obtain Overbeck's nRMSE thresholds from the IJPR 2024 paper; check the KN constants against Kim & Nelson (2001) before citing.