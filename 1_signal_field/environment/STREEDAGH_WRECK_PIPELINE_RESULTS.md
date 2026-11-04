# Streedagh Armada Wrecks — Signal Pipeline + Environmental Inference Results

**Date of this pass:** 2026-07-09
**Test case:** the three Streedagh Armada wrecks, Co. Sligo (La Juliana, La Lavia, Santa María de Visón)

---

## 1. What was built

### Wreck → Signal adapter
`rmp_pipeline/adapters/wreck_adapter.py` + `run_wrecks.py`

Converts rows of `data/raw/Wrecks20240620_table.csv` into `SignalObject`s, the
same schema every other source in this pipeline uses (RMP monuments,
radiocarbon, onomasticon). New `signal_type = "wreck_site"`, new UARI source
tag `"WR"` (`rmp_pipeline/uari/generator.py`). Defaults to the three confirmed
Streedagh Armada wrecks; reusable for other wrecks via `--wreck-no` /
`--place-contains` / `--year` / `--all`.

**Output:** `data/output/wreck_signals.json` (3 signals: `wr_w07023`,
`wr_w07024`, `wr_w07052`)

### Environmental inference module
`rmp_pipeline/models/environmental_inference.py` +
`rmp_pipeline/inference/tidal_moon_inference.py` + `run_environmental_inference.py`

Reads a signal's historical date + position and computes day/night, moon
phase, and astronomical tidal character — kept as a separate, linked
inference layer (never written into the signal's own φ/τ), consistent with
this pipeline's SENSED/INFERRED separation. Uses astropy's built-in
ephemeris; no new dependencies, no network access needed to run.

**Output:** `data/output/wreck_environmental_inference.json` (1 bundle per signal)

---

## 2. Key data decision: the CSV date discrepancy

The CSV's `Date of Loss` field records **25/09/1588** for all three wrecks,
but the free-text description on all three (and the Cuéllar eyewitness
account — he was aboard La Lavia) states the storm and grounding happened on
**21 September 1588**, consistent with other Armada wrecks logged the same
night elsewhere in the same CSV (San Esteban, La Rata Encoronada). The
narrative date is used as the canonical event date; the CSV's field is kept
alongside it in `raw_temporal_items` rather than overwritten, so the
disagreement stays auditable.

---

## 3. Results for 21 September 1588, Streedagh Strand

| Output | Value | Confidence | Basis |
|---|---|---|---|
| Sunrise | 06:25 UTC | 0.85 | flat-horizon, astropy builtin ephemeris |
| Sunset | 18:30 UTC | 0.85 | flat-horizon, astropy builtin ephemeris |
| Daylight | 12.08 h | 0.85 | (expected: just before the autumn equinox) |
| Moon phase | new moon, 0.8% illuminated | 0.95 | astropy builtin ephemeris |
| Moon age | 0.84 days past new | 0.95 | — |
| Tidal character | **spring tide** (spring/neap index 0.886) | 0.75 | derived directly from Sun-Moon elongation |
| High water | ~05:43 UTC, ~17:58 UTC | 0.6 | Moon's local transits + Sligo Port lag |
| Low water | ~11:50 UTC | 0.6 | midpoint between HW candidates |

The storm that wrecked all three ships coincided with a **new-moon spring
tide** — the water level that night would already have been running higher
than average on the astronomical tide alone, before the storm surge itself
(which this module does not and cannot model) is added on top.

---

## 4. What this deliberately does not claim

- **No absolute tide height / strandline reach.** That needs real harmonic
  constituents for a local port, which we don't have.
- **No storm surge model.** The actual water level on the night was almost
  certainly surge-dominated, not astronomical-tide-dominated — the surge is
  the caller's parameter, not something this module reconstructs.
- **HW/LW clock times are approximate**, built from the Moon's local transits
  plus a constant port lag. The lag currently used is a real reference — Sligo
  Port's high-water lag, ~4h45m–5h00m behind lunar transit (midpoint 4.875h
  used) — rather than an unfounded assumption, but it's still treated as
  constant year-round, whereas real ports show some spring/neap variation in
  it ("priming and lagging"). That's why `timing_confidence` (0.6) sits below
  the phase/spring-neap confidence (0.75).
- **Calendar:** treated as proleptic Gregorian throughout, matching Spanish/
  Armada-side sources (Cuéllar). Contemporary English/Irish accounts of the
  same era may use the Julian ("Old Style") calendar, ~10 days earlier — using
  a Julian-dated source here without converting would shift the moon phase by
  ~10 days and could flip the spring/neap classification.

---

## 5. Files touched this pass

```
rmp_pipeline/adapters/wreck_adapter.py                 (new)
rmp_pipeline/models/environmental_inference.py         (new)
rmp_pipeline/inference/tidal_moon_inference.py         (new)
rmp_pipeline/uari/generator.py                         (edited: + "WR" tag)
run_wrecks.py                                          (new)
run_environmental_inference.py                         (new)
data/output/wreck_signals.json                         (generated)
data/output/wreck_environmental_inference.json          (generated)
```
