# Implementation Instruction — Astronomical & Tidal Reconstruction Module

**Target pipeline:** existing signal pipeline (J2000-anchored)
**Deliverable:** one new module, integrated, tested, reproducible
**Primary use case:** physical-constraint reconstruction of the Streedagh Armada wreck, 1588

---

## 0. Fixed context (do not re-derive)

- **Event anchor date:** `1588-09-21` **Gregorian** (Spanish / Cuellar reckoning). The English/Julian label for the same physical day is `1588-09-11`. The Gregorian date is authoritative; the Julian label is metadata only.
- **Site:** Streedagh Strand ≈ `lat +54.402°, lon −8.626°`, height ≈ 0 m (configurable).
- **Pipeline epoch:** J2000.0 = JD `2451545.0` (TT) = 2000-01-01 12:00 TT. **Reuse the pipeline's existing J2000 anchor and time utilities — do not redefine them.**
- **Why J2000 matters here beyond timekeeping:** the tidal harmonic constituents' arguments (Doodson / fundamental astronomical arguments s, h, p, N, p′) are polynomials in `T = Julian centuries from J2000`. The module evaluates them from the same anchor, so the astronomical and tidal branches share one time base.

---

## 1. Purpose

Given a civil date/window and the site, compute Sun and Moon geometry and an **astronomical** tidal reconstruction for that date, with (a) explicit separation of the deterministic astronomical signal from meteorological surge, and (b) a per-output uncertainty tier. Outputs feed the Cuellar event timeline (wreck-window state of tide, darkness, spring/neap range).

---

## 2. Integration constraints

- Conform to existing module/interface conventions; inspect the pipeline first and reuse its J2000 + calendar utilities.
- Pure functions where practical: **config in, structured result out.** No hidden global state.
- **Deterministic and reproducible.** Pin the ephemeris (DE441) and all data sources; emit a provenance block (§6).
- Runs **offline** once ephemeris/tide data are provisioned. The one-time data download is a documented setup step, not a runtime dependency.

---

## 3. Inputs (config object / dataclass)

| Field | Type | Default | Notes |
|---|---|---|---|
| `event_date_gregorian` | date | 1588-09-21 | authoritative |
| `calendar_label_in` | enum | `gregorian` | **required, explicit**; reject/ warn if `julian` passed without conversion (guards the spring↔neap flip) |
| `site` | (lat, lon, height) | Streedagh above | |
| `window` | (start, end) | 1588-09-21 06:00 → 1588-09-22 02:00 LAST | Local Apparent Solar Time by default |
| `delta_t_model` | enum | `espenak_meeus` | 16th-c segment; expect ΔT ≈ +90…+130 s |
| `ephemeris` | str | `de441` | must cover 1588 |
| `tide.constituents_source` | str | nearest standard port (Sligo / Killybegs) | else pyTMD/FES2014 node |
| `tide.model` | enum | `utide` \| `pyTMD:FES2014` | |
| `tide.sea_level_offset_m` | float | −0.4 (STATED ASSUMPTION, citation slot) | 1588 datum vs modern |
| `tide.surge_band_m` | float | 1.5 | applied as ± band, **never** a point value |

---

## 4. Computation requirements

### A. Time
1. Convert `event_date_gregorian` → JD via proleptic Gregorian.
2. `t_j2000 = JD_TT − 2451545.0`; `T = t_j2000 / 36525`.
3. Apply ΔT (16th-c model) to relate TT ↔ UT1. Record ΔT used; note it is the dominant sub-minute timing uncertainty (~2 min level).
4. **Every event carries three time labels:** TT, UT1 (via ΔT), and **Local Apparent Solar Time** (LAST), where LAST is derived from the Sun's *topocentric hour angle* at the site (this is the clock Cuellar reports — "nine o'clock at night" etc.).
5. Unit test: `t_j2000 == 0.0` at 2000-01-01 12:00 TT.

### B. Sun (topocentric, skyfield + DE441)
- Declination; sunrise, solar noon, sunset in **LAST and UT**.
- Civil and nautical twilight ends (constrains the daylight-wreck inference and the darkness of the 01:00 event).
- Equation of time (mean ↔ apparent conversion).
- **Acceptance:** sunset ≈ 17:5x–18:0x LAST (cross-check against first-order estimate 17:57).

### C. Moon
- Geocentric elongation → phase angle → illuminated fraction.
- Age since new moon; days to nearest syzygy → **spring/neap classifier**.
- Earth–Moon distance; **flag proximity to perigee** (perigean-spring amplification — strengthens the "driven far up-beach" reading if it coincides with new moon).
- Moonrise/set/transit in LAST and UT.
- **Acceptance:** illuminated fraction a few % (near new); classifier returns **SPRINGS**. This result is the calendar-sensitivity canary: a `julian` input would move the Moon ~10 days and return NEAPS — the module must make that impossible to trigger silently (see input guard).

### D. Tide
- Astronomical reconstruction across `window` from harmonic constituents for the nearest standard port via `utide` (`reconstruct`), **or** a pyTMD/FES2014 node nearest Streedagh. Fundamental arguments evaluated from `T` (J2000).
- **Stationarity caveat (document in code):** constituent amplitudes/phases are assumed unchanged since the modern epoch; only the astronomical arguments are propagated back. FES2014 coastal-node resolution in a bay is coarse — prefer local port constituents where available.
- Outputs: HW/LW times (LAST + UT) and heights; daily tidal range; **state of tide (flood/ebb) at named anchors** — wreck window 14:00–16:00, 18:00 (sunset), 21:00 (calm/subsiding), 01:00 (horsemen).
- **Astronomical / surge separation is mandatory.** Return `astro_height(t)` independently. Surge is a caller-supplied band; `total = astro + surge` is reported as a **band** (default ±1.5 m), never a single number. Do **not** bake surge into the astronomical series.
- Apply the configurable 1588 sea-level offset as a stated assumption with a citation slot.

### E. Uncertainty tiers (attach to every output)
- **HIGH:** timing, phase, spring/neap, flood/ebb (astronomically deterministic).
- **LOW:** absolute water height / strandline reach (surge-dominated; Cuellar is describing the surge).
Encode the tier in the result so downstream code cannot treat a LOW-tier height as if it were HIGH.

---

## 5. Outputs (structured result)

Single result object (dataclass → optional JSON), with sections: `provenance`, `time`, `sun`, `moon`, `tide` (timeseries + events + anchor states), each field tagged with its uncertainty tier. Optional CSV export of (i) the tide timeseries and (ii) an events table, matching the existing pipeline's CSV conventions.

---

## 6. Provenance block (required)

`ephemeris_id` (e.g. DE441), `delta_t_model`, `tide_constituents_source`, `tide_model`, `sea_level_offset_m` + citation, `calendar_label_in`, `code_version / git_hash`, `run_timestamp`. Reproducibility is a hard requirement, consistent with the external-timestamped-publication workflow.

---

## 7. Dependencies

`skyfield` (+ DE441 `.bsp`), `numpy`, and one of `utide` / `pytides` / `pyTMD` (+ FES2014 or TPXO grids). Pin all versions. Document the one-time data provisioning (DE441, tide grids) as a setup step.

---

## 8. Acceptance criteria (test suite)

1. `t_j2000 == 0` at J2000.0 (TT).
2. Calendar round-trip: Gregorian 1588-09-21 ↔ Julian 1588-09-11 (10-day offset) verified.
3. Input guard: passing `calendar_label_in=julian` without conversion raises/warns — no silent regime flip.
4. Sun: sunset within a few minutes of 17:57 LAST.
5. Moon: illuminated fraction near new; classifier == SPRINGS.
6. Tide: HW/LW timing stable to inputs; flood/ebb state returned at all four named anchors.
7. Every height output surfaces the surge band; no point-value strandline height anywhere.
8. Determinism: identical inputs → identical outputs; provenance block complete.

---

## 9. Non-goals / cautions

- The module does **not** physically model the storm surge — that is the caller's parameter.
- It does **not** assert an absolute strandline height; all height outputs must expose the surge band and the LOW tier.
- Changing the calendar convention moves the Moon ~10 days and flips spring↔neap. The explicit `calendar_label_in` guard exists to make this misuse impossible to trigger silently.
