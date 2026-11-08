# Signal field

- `streedagh_site_assessment_v2.md`: the assessment rebuilt on the Archaeological Signal
  Framework. Part I is the inverse arc (signals to entities). Part II covers site formation as the
  production of a signal field. Part III is the forward arc (predicting what has not yet been
  observed).
- `v01_to_V3_reconciliation.md`: how the signal store moved from the v0.1 schema to SignalObject v3.
- `data/juliana_guns.csv` (the nine recovered guns attributed to Dorino II Gioardi; Ridella et al. 2016
  tab. 1), `data/lisbon_muster_1588.csv` (the Levant squadron at the Lisbon muster; Martin 1984 App. 4)
  and `data/juliana_attribution_v3.csv` (each gun's posterior for Juliana from the retired v3
  estimator, frozen 2026-11-08) feed the site record below. The v3 store, its estimator and its
  GeoJSON view are in `../superseded/v3_store/`: their coordinates were placeholders.
- `seabed_mass_budget.py` (`make mass`): what went to the bottom on the wreck day, layer by layer.
  Layer 1, done: ordnance and munitions per ship from the muster counts times sourced units (libra
  460 g, quintal 46 kg; shot calibres from the Sicilian ships' gun list, `data/levant_guns_1587.csv`;
  Juliana's weight-marked guns), with the Channel expenditure as stated priors. Layer 2: the whole
  ship. A hull-form model on the measured dimensions (`data/ship_ratings_1588.csv`, AGS GA 223/28 via
  Martin 1984 App. 11; Juliana from the v0.7 envelope) gives the laden displacement; the wreck-day
  load is built up from the hull, ballast (scaled from the Rosa's mound, Martin p. 150), what was left
  of the rations (pp. 349-350), arms and siege cargo; each part is split into seabed and strand.
  Checked by putting the May loading back aboard. Ranks which priors drive the answer.
  Report: `output/mass_budget_report.md`. Site assessment v2 L3.2 now quotes these figures (revised
  2026-11-07); the earlier ~601 t came from the superseded v1 tonnage-to-mass chain.
- `museum_capacity.py` (`make museum`): capacity brackets for a museum and conservation facility if
  1/8, 1/4, 1/3, 1/2 or all of the seabed material survives and is raised: guns, timber volume, PEG
  tank and years, freeze-dryer years, concreted iron and its tanks, floor areas. From the budget's
  own draws; every assumption stated. Report: `output/museum_capacity_report.md`. Sources:
  [Vasa Museum](https://www.vasamuseet.se/en/research/conservation),
  [Mary Rose Trust](https://maryrose.org/news/mary-rose-enters-final-phase-of-conservation/),
  [Bremen cog](https://en.wikipedia.org/wiki/Bremen_cog) and its
  [800 m³ tank](https://artsandculture.google.com/asset/the-800-cubic-metre-preservation-tank-for-the-cog-german-maritime-museum-dsm/ngH1Fn5b8Xit_A),
  [La Belle freeze-dryer](https://stories.tamu.edu/?p=288715),
  [QAR lab report](https://qaronline.org/20050708-qar-lab-report/open),
  [National Museum of Ireland](https://museum.ie/ga-IE/Collections-Research/Conservation/Conservation-Projects/Armada-Cannons-and-Gun-Carriage-Wheel).
- `site_record/` (`make site`): **the site record**, one bundle in the new signal schema
  (`Signal_Pipeline/signal_schema`, v0.4), built by `build_site_record.py` from the CSVs in `data/` and
  validated by the schema's own CLI. Design: `SITE_SIGNAL_DESIGN.md`. So far: the recovered guns, the
  Lisbon muster, what the divers reported at Site 1 and how it lay, path events (cast in Genoa 1570;
  to the seabed 21-26 Sep 1588), attributions, mounting-station hypotheses and the break-up prediction,
  and Cuéllar's letter: 125 coded passages, each with its verbatim span in Crawford's translation
  (`../3_cuellar_worldline/data/cuellar_spans.csv`), the coding as label inferences, and the 31
  worldline nodes as dated event sources; the six ships measured in 1588 with metric conversions and
  the rating-formula check; the Sicilian gun list; layers 1 and 2 of the mass budget as per-ship predictions; the 1985
  magnetometer spreads (`data/magnetometry_1985.csv`) with the test of spread area against iron mass.
  Positions are absent until recovery coordinates are found.
- `site_record/export_view.py` (`make view`): the site record as page data, `output/site_view.json`.
  Every value is copied from a record and carries that record's id; positions are null.
- `finds_study_plan.md`: the plan for the guns, rudder and anchor.
- `SPEC_astro_tide_module.md`: spec for the astronomical and tidal module. The sun/moon half is now
  implemented in `../3_cuellar_worldline/sun_moon.py`; tides are not done yet.
- `what-streedagh-still-holds-v2.md`: the public article.
- `environment/`: results copied from the frozen legacy pipeline
  (`Signal_Pipeline/legacy/archaeo_data_pipeline`) for 21 Sep 1588: new moon, spring tide, sun
  times. Its sunrise and sunset are given in UTC; `sun_moon.py` uses local mean time (UTC − 35 min).
