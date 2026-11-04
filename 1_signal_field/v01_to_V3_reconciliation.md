# `signal_attribution v0.1` ↔ Signal Object V3 — reconciliation

**Verdict:** V3 (`SignalObjectV3_Design.md`, pipeline agent, 2026-07-02) is canonical. Our
`v0.1` GeoJSON work folds into it as two things: (a) the **attribution computation layer**
V3's schema implies but does not specify, and (b) a **GeoJSON export view** for spatial tooling.
The canonical store is V3 Pydantic / JSONB; GeoJSON is a projection of it, not the store.

## Already aligned
- Signals as primitives; entities inferred at L3 and treated as signals themselves.
- Probabilistic multi-entity attribution over {Juliana, Lavia, Visón, Unknown}.
- Provenance / acquisition / uncertainty carried on every signal.
- Explicit inter-level links.

## Changes to conform (v0.1 → V3)
| v0.1 | V3 | Note |
|---|---|---|
| `signal_class: "bronze_gun"` (typological) | `acquisition_class: "direct_observation"` | **v0.1 was wrong here.** "gun"/"vessel" moves to `InferenceBundle.typological_label` |
| `attribution: {posterior:{...}}` (one dict) | `entity_attributions: List[EntityAttribution]` | append-only; each entry has `entity_signal_id, confidence, basis, committed_at, committed_by` |
| `measurements: {value,unit,sd,source}` | `phi_quantitative: {p05,median,p95,distribution_basis,seed,script_ref}` | pulls the Monte Carlo distributions into the record; links to `streedagh_*.py` |
| labels inline ("Heavy Saker") | `InferenceBundle` + `evidence_refs` | typology cited to specific φ fields |
| (none) | `worldline: [WorldlineNode]` | Lisbon load → … → seabed_terminal; the controlled-motion path, seabed = terminal state |
| ad-hoc ids (`SIG-G-…`) | UARI scheme | defer to the pipeline's UARI format |

## What our engine ADDS to V3 (feed back to the pipeline agent)
V3 defines the **storage** of attributions but not their **derivation**. Our engine is that layer:

1. **Component accumulation** — a signal's diagnostic sub-signals (founder-mark, saint-relief,
   weight-mark, spatial position) combine by Bayesian product into the posterior that fills
   `entity_attributions`. Reproducible; the derivation is written into `basis`.
2. **`diagnostic_group` correlation control** — correlated components (founder-mark + casting-year
   = one casting event) share a group and combine **once**, preventing over-confidence. *Proposed
   V3.1 addition:* a `diagnostic_group` field on the component/evidence representation.
3. **Append-only emission** — each run appends `EntityAttribution` records
   (`committed_by = engine version`, `committed_at = timestamp`), exactly V3's versioning model.

**Proposed:** V3 adopts `components: List[ComponentSignal]` (with `diagnostic_group`) as the
evidence substrate, and our engine becomes the reference `AttributionEstimator`:
`signals (V3) → estimator (ours) → entity_attributions (V3)`, append-only, reproducible.

## Continuous-infrastructure implication
V3's append-only `entity_attributions` + our estimator = a **living inference state**. A new dive
appends signals/components; the estimator re-runs; every posterior updates; nothing is mutated;
every entity remains a timestamped, sourced hypothesis. That is the continuous-research-infrastructure
proof-of-concept — Streedagh as the first instance, chosen because it is multi-entity, dispersed,
eroding and partially excavated, i.e. every hard case at once.
