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
- `SPEC_astro_tide_module.md`: spec for the astronomical and tidal module. The sun/moon half is now
  implemented in `../3_cuellar_worldline/sun_moon.py`; tides are not done yet.
- `what-streedagh-still-holds-v2.md`: the public article.
- `environment/`: results copied from the frozen legacy pipeline
  (`Signal_Pipeline/legacy/archaeo_data_pipeline`) for 21 Sep 1588: new moon, spring tide, sun
  times. Its sunrise and sunset are given in UTC; `sun_moon.py` uses local mean time (UTC − 35 min).
