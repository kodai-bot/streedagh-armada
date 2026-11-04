# Streedagh Armada Wreck Site — Technical Assessment
## Version 2 — signal-ontology architecture

*Sites 1–3, Streedagh Strand, Co. Sligo. Provisionally: La Juliana, La Lavia, Santa María de Visón (Levant Squadron, wrecked September 1588).*

> **On this version.** v1 led with the physical (entity) reconstruction. v2 re-seats the whole report on the Archaeological Signal Framework, so it begins where the evidence actually begins — at the observed signal field — and builds every higher entity by explicit, confidence-weighted inference. The order is dictated by the ontology, not by style. Status markers **[DRAFTED]/[OUTLINE]/[DEFERRED]** and provenance markers `⟵ source` are retained; the level→section mapping is in Part V.

---

## 0. Executive Summary
**[DEFERRED — conventional]** *A conventional, object-forward summary is appropriate here (readers expect "three Armada ships, wrecked 1588, at Streedagh"). The summary states conclusions; the body earns them. To be written last, from the fixed results.*

## 0.1 Methodology statement
**[DRAFTED]**

This assessment adopts a bottom-up, **signal-based** methodology grounded in the Archaeological Signal Framework. Rather than beginning with predefined archaeological entities — a ship, a wreck, a fleet — it begins with the physical **signals** that actually survive: magnetic anomalies, timbers, recovered ordnance, ballast, sediment structures, and documentary observations. Higher-level entities — the individual vessels, the squadron, and the invasion logistics they served — are progressively **inferred** through explicit physical and historical reasoning, each level supported only by the level below. The report is therefore organised according to the order in which archaeological knowledge is *constructed*, not according to traditional object-based classification.

Two consequences follow, and both matter acutely at Streedagh. First, **no archaeological object is assumed**: every entity is a hypothesis held at a stated confidence and revised as evidence changes. Second, because entities are inferred rather than assumed, material is never stored as "part of" a named ship; instead each signal **supports one or more candidate entities probabilistically**. This is not a refinement but a requirement at a site where three wrecks lie close together and their remains are dispersed and intermixed — the object-first alternative would force attributions the evidence does not yet justify.

Formally, the report treats the site as an **inverse problem**: recover a former controlled-motion (technological) system from the degraded signal field its collapse produced, then run that reconstruction **forward** to predict evidence not yet observed.

---

# PART I — THE INVERSE ARC
*Constructing the entities from the observed signal field. Nothing at any level appears without support from the level below.*

## L0 — Signals (observed; no interpretation)
**[DRAFTED / partly DEFERRED for full catalogue]** ⟵ Birch & McElvogue 1999; Moore et al. 2015; McElvogue 2002; Ridella et al. 2016; site geophysics
*(→ template §5 Methodology, §8 Assemblage, App. C)*

The primitive objects of this assessment. Each carries measurable properties, uncertainty, provenance, and acquisition method — and **no** archaeological interpretation.

| Signal class | Observed content (examples) | Acquisition |
|---|---|---|
| Magnetic anomalies | Three footprints: ~165×40 m; ~15×10 m; ~270×72 m | Marine magnetometry |
| Bronze objects | 12 recovered guns: masses, bore, cantara weight-marks, founder-marks (D/G), relief saints, cast date | Diver recovery, conservation lab |
| Timbers | Articulated structural timber, in situ, curvature/scantlings | Diver survey |
| Wheels | Five spoked wooden wheels, ~1.5 m dia. | Diver survey / recovery |
| Ballast | Concentrated stone | Diver survey |
| Anchors | Recorded iron anchors | Diver survey |
| Sediment | Sand lenses; degree of cover; articulated-timber sealing | Diver / environmental obs. |
| Documentary | de Cuéllar narrative; AGS armament inventories; recorded tonnages & gun counts; Ridella's cantara weights | Archival |

*Note the discipline: "magnetic anomaly, 270×72 m" is a signal; "La Lavia" is not. The three anomaly footprints are three signals, not three ships.*

## L1 — Motion traces (what each signal records: a past motion or contact)
**[DRAFTED]** *(→ §7 Site Formation; §8)*

| Signal | Motion trace it records |
|---|---|
| Magnetic anomaly | A concreted ferrous mass came to rest here (iron guns, fasteners, anchors) |
| Cantara weight-mark + founder-mark on bronze | A **casting event**: Genoa, 1570, Dorino II Gioardi workshop |
| Relief saint (St. Matrona, patron of Barcelona) | A **commissioning event** tied to a Barcelona-built hull |
| Articulated timber curvature/scantlings | A **hull-construction trace** (Mediterranean *nao* tradition) |
| Spoked wheel | A **siege-carriage** was present — a land-artillery mounting embarked as cargo |
| Sand lens over articulated timber | A **rapid burial** (deposition) event |
| Ballast concentration | The **arrest point** of the densest mass |

Traces are still physical. They say what happened, not what existed.

## L2 — Motion patterns (assembled traces → coherent patterns)
**[DRAFTED]** ⟵ `streedagh_manifest.py` (density logic); site footprints
*(→ §7; §9.7 System Failure)*

- **Three spatially separate footprints** → three distinct wrecking loci → (candidate) three entities.
- **Density-sorted dispersal** — ballast and heavy concreted mass concentrated at each locus; lighter material dispersed or absent → **cargo release under hull failure, sorted by mobility**. This is the direct fingerprint of controlled-motion collapse (see the generative model, Part II).
- **Elongate footprints (parallel to shore)** → wrecking followed by surf-zone / longshore dispersal along a definable axis.
- **Ordnance-tier pattern** — light/medium defensive bronze recovered; heavy siege ordnance absent from the recovered set → a **tiered stowage pattern** (accessible armament vs deep cargo), predicting where the missing tier is (Part III).

## L3 — Entities (the inferred vessels) and their physical reconstruction
**[DRAFTED]** ⟵ `streedagh_hull.py`, `streedagh_manifest.py`, `streedagh_guns.py`, `juliana_guns.py`
*(→ §6 Vessel Assessments; §10 Ship Reconstruction; App. E–F)*

Only now do ships appear — as inferences over assembled patterns, each held at a confidence.

### L3.1 Probabilistic attribution (replacing part–whole)
**[DRAFTED]**

Signals support candidate entities; they are not filed under them. The conventional site→ship identifications (Site 1 = La Juliana, Site 2 = Visón, Site 3 = Lavia) appear in the survey literature as working hypotheses. The framework requires making those hypotheses explicit and assigning them stated confidences — so that if new evidence arrives, the attributions can be revised without touching the signal record.

Each confidence below is derived from a specific physical or documentary basis, stated alongside the figure. Confidences sum to ≤ 1.0 across candidates; the remainder is genuinely unattributed. These are **current best estimates**, not permanently fixed values.

| Signal | Basis | La Juliana | La Lavia | S.M. de Visón | Unattrib. |
|---|---|---|---|---|---|
| Recovered bronze battery (12 guns; Dorino II Gioardi 1570; St. Matrona / Barcelona patron) | Founder + patron-saint link to a Barcelona-built hull; all 12 recovered at Site 1; one *esmeril* at Site 2 only | **0.87** | 0.05 | 0.08 | — |
| Site-1 footprint (165×40 m) | Footprint scale consistent with Juliana as largest hull (860 t); carriage-wheel locus at this site | **0.80** | — | 0.05 | 0.15 |
| Site-3 footprint (270×72 m; greatest sand cover) | Greatest areal spread consistent with *almiranta* (more material, more dispersal); greatest sand cover consistent with shelter by headland; survey literature identifies tentatively as Lavia | 0.05 | **0.72** | — | 0.23 |
| Site-2 footprint (15×10 m) | Smallest anomaly consistent with Visón as smallest hull (666 t); survey literature tentative identification | — | — | **0.65** | 0.35 |
| Five siege-carriage wheels (Site 1) | Documented career of La Juliana as siege-engineering carrier (*Archivo de la Corona de Aragón*) | **0.92** | — | — | 0.08 |
| De Cuéllar letter (explicit documentary) | De Cuéllar names himself aboard La Lavia, the *almiranta*, during the wrecking | 0.01 | **≥0.98** | — | — |

The confidence spread on the footprint attributions (Site 2: Visón 0.65, unknown 0.35; Site 3: Lavia 0.72, unknown 0.28) is deliberate: the footprint sizes are consistent with the expected hull sizes but the association is not confirmed by any find with a legible ship identity. A single artefact with a Lavia or Visón registry mark would move those attributions decisively. Until then the uncertainty is the correct representation.

A dispersed gun found midway between sites would carry, illustratively: Juliana 0.50, Lavia 0.30, Visón 0.15, unknown 0.05 — dominated by Juliana as the most gun-dense entity but genuinely ambiguous. That ambiguity would not be resolved by filing the gun under the nearest site; it would be resolved by further evidence.

### L3.2 Entity physical models (inverse reconstruction)
**[DRAFTED]**

The inverse chain (burthen → cargo volume → internal volume → dimensions → displacement → deadweight → payload), each factor a distribution, propagated by Monte Carlo. Medians [5–95th]:

| Entity | Burthen (t) | Guns | Displacement (t) | Deadweight (t) | Non-ballast payload (t) |
|---|---|---|---|---|---|
| La Juliana | 860 | 32 | **1,390** [1,133–1,706] | 694 [550–874] | 450 [348–579] |
| La Lavia | 728 | 25 | **1,177** [959–1,443] | 588 [466–738] | 381 [295–489] |
| S.M. de Visón | 666 | 18 | **1,077** [878–1,320] | 538 [426–676] | 349 [270–448] |
| **Combined** | 2,254 | 75 | **~3,640** [~2,970–4,469] | ~1,820 | ~1,180 |

⟵ `streedagh_hull.py` (seed 20260629, N = 200,000). All figures median [5th–95th percentile]. Headline: *La Juliana* ≈ **2.4× the Galeón Andalucía** by displacement (displacement-to-displacement is the honest comparison; the "46% larger" figure mismatches burthen against weight).

**Ordnance (calibrated).** Same foundry (Dorino II Gioardi) as the *San Giorgio*, so the Genoese unit is fixed at **1 cantaro = 47.65 kg**. The 12 recovered Juliana guns are her **own defensive armament** (sakers, falcons, falconet, *petrieri*; ~6 t total; heaviest ~1 t) — light/medium, *not* the siege train. For scale, one Valencera siege gun = 2.5 t. Three functional tiers: (1) defensive armament (recovered ~6 t); (2) iron guns (~20 of 32, mostly unaccounted); (3) **siege train (cargo)** — evidenced by the carriage wheels, buried, unrecovered.

**Surviving-mass budget** (bottom-up, cross-checked against the payload ceiling *and* against the ferrous footprints): combined durable material on the seabed ~**601 t (upper bound ~660)** — ballast ~474 t, iron ~76 t (matches the magnetometer scatters), bronze ~33 t, lead ~11 t, ceramic ~7 t, organics ~32 t; artefact-grade (metal+ceramic) ~125 t.

**Complement / war grave.** Documented minimum 1,013 aboard (likely higher); de Cuéllar records >1,000 dead. Heavily manned *and* heavily equipped — combined troop-and-materiel transports. The site is a war grave; every downstream section holds that alongside the numbers.

## L4 — Systems (entities become signals for a larger inference)
**[DRAFTED]** *(→ §9.1, §9.6)*

The three inferred entities resolve into one **logistical system** — the heavy-lift tier of the invasion machine — with evidence of *specialised* loads:
- **La Juliana** — ordnance / siege-engineering carrier (carriage wheels; largest hull). Documented career of repeated requisition (Lepanto troop carrier; Portugal and Azores campaigns; Armada, Sicily, Dec 1586 — *Archivo de la Corona de Aragón*) exemplifies Mediterranean traders cycled into imperial military logistics.
- **La Lavia** — the *almiranta*; command-and-discipline node (Judge Advocate Martín de Aranda; de Cuéllar aboard).
- **S.M. de Visón** — medical carrier (the fleet's transferred medical supplies).

Specialised, distributed supply is itself a finding: designed logistics, not ad-hoc loading.

## L5 — Behavioural system (invasion logistics)
**[DRAFTED]** *(→ §9.1; §13)*

The three inferred entities do not simply add up; they represent specialised roles within a single behavioural system — a machine for the **controlled motion of military force to a landing**. The siege-engineering carrier, the command-and-discipline node, and the medical carrier are not three ships that happened to wreck together: they are the heavy-lift and support tier of a distributed logistical apparatus whose functions were deliberately partitioned across hulls. Specialised, integrated loading of this kind is not improvised; it is doctrine. The three entities are the material evidence of a planned invasion.

The doctrinal template for what such an operation loads is the **1583 amphibious conquest of Terceira** — the most recent successful Spanish opposed landing before 1588, and the source from which the Armada planners drew their expectations about siege trains, engineering materiel, and medical provision. At Terceira, siege artillery was brought ashore to reduce the French garrison's fortified positions; the same class of equipment is evidenced at Site 1 by the carriage wheels (L1). The wheels are not a curiosity: they are the direct physical confirmation that the L5-level reasoning about invasion doctrine was operationalised in the actual loading. What the planners specified, the loaders loaded. What the loaders loaded, the site preserves — at least in part.

This closes the inverse/forward loop in the most direct way possible. The inference at L5 (invasion doctrine predicts a siege-train cargo tier) generates a prediction at L3 (such a tier should be present in the largest hull's hold). That prediction is confirmed at L1–L2 by the physical trace (spoked wheels → siege-carriage mounts → a land-artillery mounting embarked as cargo). The forward model (Part III) runs the same logic in the other direction: it predicts what has not yet been found (the guns associated with those carriages) and specifies where they should be (deepest stowage, seaward of the ballast mound at Site 1). The L5 inference and the L3 physical evidence are mutually constraining, not independent.

---

# PART II — THE GENERATIVE LINK
*How the signal field was produced. This closes the loop: the behavioural system, on losing controlled motion, generates the Level-0 signals the report began from.*

## II.1 Site formation as signal-field production
**[DRAFTED]** *(→ §7 Site Formation)*

Per the framework: the archaeological record is **not the surviving ship** but the **surviving signal field produced by the collapse of the technological system**. The collapse is an ordered **loss-of-control cascade**: storm loading exceeds the control surfaces → anchor failure (loss of the one apparatus for *arresting* motion on a lee shore) → grounding → hull failure → **cargo release, dispersed by density** → settling into the terminal state. The density-sorted dispersal pattern at L2 is the direct signature of the release step. Ballast mounds = the system fully at rest.

## II.2 Why the field survives — the double foreclosure
**[DRAFTED]** *(→ §6 Preservation; §7)*

Preservation is a **ratchet**: two alternative fates for the assemblage were each foreclosed.
1. **Salvage foreclosed by war.** Bronze is normally stripped first (gunmetal outvalued the ship). It survived because the wreck opened the Fifteen Years' War; the north-west was a contested war zone 1588–1603, beyond secure access, and no historic salvage is documented (Birch & McElvogue). The *San Giorgio* supplies the object-scale mechanism: deck guns salvaged, hold-stowed cargo guns unreachable and preserved.
2. **Dispersal/decay foreclosed by sand.** Rapid burial sealed structurally-coherent remains before they could disperse or oxidise.

**The Valencera contrast is a contrast in generative processes.** Hard seabed → light material removed, heaviest left exposed → a *lag deposit*. Streedagh → sand-filled hulls, **articulated timbers surviving in place** → a *sealed, structurally-coherent* field. The consequence drives Part III: if hull structure survives sealed, the holds may be partly intact and the heavy gear should still be *in situ*.

*Threat corollary:* the ratchet is metastable. The same active sand that foreclosed dispersal periodically re-opens it; storm exposure re-mobilises material into a high-energy surf zone that destroys what it uncovers.

---

# PART III — THE FORWARD ARC
*From the inferred system, predict evidence not yet observed; those predictions are testable, and they set the survey and management priorities.*

## III.1 Forward model — expected surviving evidence (predictions)
**[DRAFTED]** *(→ §12; §14 Recommendations)*

Running the L3–L5 reconstruction forward through the L4 preservation model yields specific, falsifiable expectations for signals **not yet observed**:

- **A buried heavy-ordnance (siege) tier** at/near Site 1 — predicted by the carriage-wheel trace + the tiered-stowage pattern + the *San Giorgio* mechanism. The single highest-value survey target.
- **Sealed, articulated hull structure** at the sand-rich loci (esp. Site 3) — predicted by the generative model; if present, holds may be coherent.
- **A medical assemblage** associated with the Visón entity — predicted by the L4 specialisation.
- **Bulk munitions / lead / organics** where sand-sealed.

These are predictions, not findings. Each is a hypothesis the survey is designed to test — which is what makes management the report's proper terminus rather than an appendage.

## III.2 Significance
**[DRAFTED]** *(→ §11)*

International/archaeological: a potentially **sealed, unsalvaged, structurally-coherent invasion cargo** — rare, and categorically distinct from lag-deposit wrecks. Military/logistical: an exceptional dataset for **early-modern military logistics and ordnance**, a strand poorly developed in Irish archaeology — the calibrated ordnance and tiered stowage make this a type-site for quantitative military-materiel and systems analysis. Technological: dated single-foundry Genoese bronze (Dorino II Gioardi, 1570); Mediterranean-*nao* construction. Landscape/heritage: a war grave and a community-defining event, with live public engagement.

## III.3 Management — survey priorities, monitoring, recovery capacity
**[DRAFTED]** *(→ §12 Condition; §14 Recommendations)*

Priorities follow directly from III.1: **target the predicted buried siege tier**; characterise sealed hull structure at Site 3; monitor exposure. Because preservation is a ratchet the sea periodically re-opens, **reactive response guarantees loss** — the clock starts the moment the sand lifts. The site requires a **standing, exposure-triggered recovery-and-monitoring plan** and, decisively, the **local capacity to execute it** — physical infrastructure and resident expertise based in Sligo, at the site, rather than imported after the fact. Building that capacity where the site is, is the structural condition for realising the value catalogued in III.2.

---

# PART IV — DEFERRED SECTIONS (written once parameters are fixed)

- **[DEFERRED] Historical context** — Armada; strategic objectives; Levant squadron; final voyage; documentary sources. *Written last, by method.*
- **[DEFERRED] Environmental context (quantitative)** — geology, sediment dynamics, wave/current/tide/storm regime. *(Qualitative regime established in Part II; quantification is a data-collection task.)*
- **[DEFERRED] History of investigation** — 1985 discovery/dispute; 1987 carriage-gun observation; 2015 rescue excavation; conservation; publications.
- **[DEFERRED] Formal methodology** — write-up of documentary, GIS, geophysical, diver, photogrammetric, and recording methods, plus the inverse/forward reconstruction methods.
- **[OUTLINE → PARTIAL DRAFT] Discussion** — see below.

### Discussion (partial draft)
**[DRAFTED — to be expanded]** *(→ §13)*

**The epistemic cost of the conventional approach.** The existing survey literature treats the Streedagh sites as identified ships. Site 1 *is* La Juliana; Site 3 *is* La Lavia. That identification drives all downstream interpretation: finds are attributed to a named ship; the ship's documented complement becomes the immediate context for what is recovered; the logistical specialisation is read off from the ship's known role. The identification is reasonable — it is probably right. But it is not the same as being *established*, and the difference matters the moment an unexpected finding appears. A cannon with a Lavia founder's mark recovered from Site 1 would, under the conventional approach, create a classificatory problem (is it a misfiled artefact? a secondary deposit?). Under the framework, it is simply new evidence that revises the attribution confidence for Site 1 — neither a problem nor an anomaly, just an update to a probability. The signal record does not change; the inference does.

More practically: the conventional approach cannot represent the Site 2 and Site 3 identifications honestly, because the survey literature itself does not treat them as confirmed. They are carried as working hypotheses, but the record does not have a place to say "hypothesis at confidence 0.65". The framework provides exactly that place, and it matters for management: a recovery decision at Site 2 taken on the assumption that the material is La Visón is a different decision from one that holds "Visón 0.65, unknown 0.35" — particularly for questions of provenance, complementary comparison with documentary records, and war-grave protocols that may differ depending on entity identity.

**The forward model as the framework's payoff.** Every assessment reaches a point where it must say what to do next. The conventional response is recommendations driven by significance and condition: the site is important, it is under threat, therefore survey and protect. That is correct but not specific — it does not tell the manager which of the three sites to prioritise, which target within a site to hit first, or how to falsify a claim if the survey does not find what is expected. The forward model in Part III is specific: a buried heavy-ordnance tier is predicted at Site 1, seaward of the ballast mound, at the lowest stratigraphic horizon. If it is not there — if targeted excavation at that location finds neither guns nor mounting hardware — the L3/L4/L5 reconstruction is in trouble and must be revised. That is a scientific prediction, not a management recommendation, and the difference is what makes the assessment actionable rather than advisory.

**Methodological transferability.** The inverse reconstruction method applied here — burthen in toneladas → internal volume → dimensions → displacement → deadweight → surviving-mass budget, Monte Carlo throughout — is applicable to any site where vessel tonnage is documented. It has been applied here to three hulls with full parameter uncertainty propagation and two independent cross-checks built in (manifest-vs-payload ceiling; modelled iron-vs-magnetometry footprint). The same method can be run on any of the other eight Levant-squadron losses, or on the Baltic bulk carriers of the Urcas squadron, giving a resource baseline before a single dive. More broadly, the signal-and-motion hierarchy (L0→L5) is domain-independent: the same six levels that order Streedagh from magnetic anomaly to invasion logistics can order a ringfort from soil anomaly to territorial administration, or a bronze hoard from XRF result to metalworking network. The framework scales without changing its structure. That is not a claim about universality; it is a claim about a useful abstraction level.
- **[DEFERRED] References / Appendices** — App. E (hull reconstruction) and F (cargo estimates) = model write-ups + code.

---

# PART V — MAPPING: signal levels ↔ work products ↔ conventional template

| Level (this report) | Work product / source | Conventional § |
|---|---|---|
| L0 Signals | geophysics; Birch & McElvogue 1999; Moore 2015; McElvogue 2002; Ridella 2016; AGS records | §5, §8, App. C |
| L1 Traces | founder/cantara marks; timber records; carriage wheels; sediment obs | §7, §8 |
| L2 Patterns | `streedagh_manifest.py` (density logic); footprints | §7, §9.7 |
| L3 Entities | `streedagh_hull.py`, `streedagh_manifest.py`, `streedagh_guns.py`, `juliana_guns.py` | §6, §10, App. E–F |
| — attribution | probabilistic model (L3.1) | §8 (novel) |
| L4 Systems | functional specialisation; ACA career of La Juliana | §9.1, §9.6 |
| L5 Behavioural | invasion logistics; Terceira template | §9.1, §13 |
| Generative link | Ridella 2016 (salvage mechanism); Birch & McElvogue; Fifteen-Years'-War framing | §7, §6 |
| Forward model | III.1 predictions | §12, §14 |
| Management | recovery-capacity case | §12, §14 |

---

### Alignment: v2 levels ↔ `BuildingInferenceChain.txt` hierarchy

The terminology used here and in `BuildingInferenceChain.txt` (`archaeo_data_pipeline/docs/`) is the same framework; the six-level diagram in §8 of that document maps directly:

| v2 report level | BIC §8 hierarchy label | BIC prose section | Notes |
|---|---|---|---|
| L0 — Signals | Signals | §3 | Purely observed; no archaeological interpretation |
| L1 — Motion Traces | Motion Traces | §4 | Physical consequence of a past motion or contact |
| L2 — Motion Patterns | Motion Patterns | (§8 diagram; assembled from multiple traces) | Assemblage-level pattern; intermediate between trace and entity |
| L3 — Entities | Entities | §5 ("Archaeological Entity") | Inferred; held at a confidence, not directly observed |
| L4 — Systems | Systems | §6 | Entities become signals for the next inference tier |
| L5 — Behavioural | Behavioural Systems | §7 | Highest inference tier; operational/logistical reconstruction |

**Note on numbering.** BIC §3–§7 name five classes (Signal → Motion Trace → Archaeological Entity → Systems → Behavioural Systems), but the §8 diagram inserts *Motion Patterns* as an explicit intermediate level, giving six in total. The v2 report's L2 corresponds to that intermediate level. No content is out of alignment; the prose sections in BIC describe trace→entity assembly in §5 without giving the pattern-aggregation step its own section number.

---

*End v2. The inverse arc (L0→L5) is drafted from completed work and reorganised to the ontology; the generative link is the hinge; the forward arc turns the reconstruction into testable survey priorities. Gaps 1–4 complete as of 2026-07-02. Remaining: V3 design note (`SignalObjectV3_Design.md`); lower-priority `armada_figures.py`.*
