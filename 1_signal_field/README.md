# Signal field

- `streedagh_site_assessment_v2.md`: the assessment rebuilt on the Archaeological Signal
  Framework. Part I is the inverse arc (signals to entities). Part II covers site formation as the
  production of a signal field. Part III is the forward arc (predicting what has not yet been
  observed).
- `v01_to_V3_reconciliation.md`: how the signal store moved from the v0.1 schema to SignalObject v3.
- `data/streedagh_store_v3.json`: the signal store. `attribution_estimator.py` computes each
  signal's probability of belonging to each candidate ship and writes
  `data/streedagh_store_v3_attributed.json` and `data/streedagh_view.geojson`. Re-running it
  reproduces the saved attributions exactly, except for the `committed_at` timestamps (July 2026).
- `juliana_guns.py` (`make guns`): turns `data/juliana_guns.csv` (the nine recovered guns attributed
  to Dorino II Gioardi; Ridella et al. 2016 tab. 1) and `data/lisbon_muster_1588.csv` (the Levant
  squadron at the Lisbon muster; Martin 1984 App. 4) into signals in the store. Gun positions are
  unknown, so their geometry is null and the estimator skips the spatial term for them. Candidate
  mounting stations are kept as tagged hypotheses, never as evidence. Report:
  `output/juliana_guns_report.md`.
- `site_record/` (`make site`): **the site record**, one bundle in the new signal schema
  (`Signal_Pipeline/signal_schema`, v0.4), built by `build_site_record.py` from the CSVs in `data/` and
  validated by the schema's own CLI. Design: `SITE_SIGNAL_DESIGN.md`. So far: the recovered guns, the
  Lisbon muster, what the divers reported at Site 1 and how it lay, path events (cast in Genoa 1570;
  to the seabed 21-26 Sep 1588), attributions, mounting-station hypotheses and the break-up prediction,
  and Cuéllar's letter: 125 coded passages, each with its verbatim span in Crawford's translation
  (`../3_cuellar_worldline/data/cuellar_spans.csv`), the coding as label inferences, and the 31
  worldline nodes as dated event sources. Positions are absent until recovery coordinates are found. The v3 store above stays as the
  estimator's input until the site record replaces it.
- `finds_study_plan.md`: the plan for the guns, rudder and anchor.
- `SPEC_astro_tide_module.md`: spec for the astronomical and tidal module. The sun/moon half is now
  implemented in `../3_cuellar_worldline/sun_moon.py`; tides are not done yet.
- `what-streedagh-still-holds-v2.md`: the public article.
- `environment/`: results copied from the frozen legacy pipeline
  (`Signal_Pipeline/legacy/archaeo_data_pipeline`) for 21 Sep 1588: new moon, spring tide, sun
  times. Its sunrise and sunset are given in UTC; `sun_moon.py` uses local mean time (UTC − 35 min).
