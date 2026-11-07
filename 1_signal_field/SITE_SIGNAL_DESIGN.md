# Streedagh as a site signal record: design pass

Status: design, 2026-11-07. Built so far: guns, muster, Site 1 relations, Cuéllar's 125 (see `site_record/`). Target schema: `Signal_Pipeline/signal_schema` (v0.4
prototype); its `docs/DESIGN.md` is the canonical design and this note only maps Streedagh onto it.
Related: `robotics/senchas/docs/geometry.md` (the building-scale geometry), the legacy
`LIFECYCLE_VECTOR_DESIGN.md` (March 2026) and `SignalObjectV3_Design.md` (from this site, July 2026).

## 1. Geometry: keep it simple

**Two levels.** The sphere places sites; inside a site, space is flat.

- **Placing a site on the planet.** A site datum in a geographic or national frame: WGS84 lon/lat,
  or Irish Transverse Mercator (ITM, EPSG:2157). Distances between sites, when wanted, come from one
  shared geodesic function. No stored vectors.
- **Recording within a site.** A Euclidean frame in metres: ITM itself, or a local site grid with a
  stated transform to ITM and a sigma. The schema already allows exactly this (DESIGN §3.4: "a local
  grid with a registered transform to ETRS89/ITRF").
- **Time** is one axis, τ in years before J2000.0, positive into the past (DESIGN §1.1). So a site
  record lives in (x, y, z, τ). That is Senchas's space-time cube at site scale, with the same
  conversion from calendar dates (here including Julian/Gregorian, which matters for 1588).

**Is flat space an error at this scale? No.** Over a distance d, the Earth's surface drops away from a
tangent plane by about d²/2R: 8 cm at 1 km, 2 m at 5 km. Streedagh's three wrecks lie within about a
kilometre, and their positions are known to metres at best, so curvature is far below the
uncertainty. ITM's own scale distortion is about 1 part in 10,000. A flat site frame costs nothing.
The sphere matters only for continental questions (where the guns were cast, the Armada's route), and
those are distances between sites, computed when asked.

**What this retires.** The March 2026 design stored a tilted lifecycle vector in celestial (GCRS)
coordinates, with time as length along the radial and motion as tilt. The ideas survive; the storage
does not:

| March 2026 idea | Now |
|---|---|
| Vector length = time depth | the detection's epoch, as τ on the one axis |
| Vector from find spot back to origin (tilt = motion) | `path_event` inferences on the signal: inception (cast, Genoa 1570), displacements (Barcelona, Lisbon, Streedagh, museum) |
| Radial vector at the surface point | the default: a path is vertical in (x, y, τ) at its detected position |
| GCRS coordinates stored | not stored (D7, provisional): a derived view if ever wanted |

So your "distance to the signal" is τ of each detection (1985, 1588, 1589), and "distance to the
source" is the path back through the inference chain. Neither needs a vector in storage, and the path
geometry is a derived view computed by one shared module (DESIGN §6).

**Cube and prism are two different things.** The cube is the space: place × time. A **prism**
(Hägerstrand) is a region inside it: everywhere a moving thing *could* have been between two
detections, given a maximum speed. Both are useful here: Cuéllar's journey between dated nodes is a
chain of prisms, and so is a gun's drift from its mounting to where it was found.

**One more frame, for the ship.** Mounting heights (lower deck, castle deck 2) are positions in the
*ship's own* frame: along the keel, across the beam, height above the keel. That frame belongs to an
inferred object (the reconstruction), so it cannot be a registered survey frame. Proposal: keep
ship-frame positions inside the inferences that use them (mounting stations, castle geometry), and
never mix them with site-frame coordinates. Open question 2 below.

## 2. How each kind of evidence maps in

| Evidence | Records | Notes |
|---|---|---|
| **1985 recovery** (3 guns, Birch & McElvogue 1999; McElvogue 2002) | `Acquisition` (diver recovery, epoch 1985, agents: Streedagh Armada Group) → one `Detection` per gun, `read_from` the publications | We have the publications, not the dive records, so by the schema's rule these detections are *historical observations* (DESIGN §5.4: "a 1985 inspection record counts"). Their certainty sits in their sigmas, not their class. |
| **2015 recovery** (6 attributed guns + 3 not yet itemised; Moore et al. 2015) | as above, epoch 2015, agents: National Monuments Service | The 3 unitemised guns get a bounded record ("3 further guns reported"), not invented detail. |
| What each gun carries | on its detection: weight mark **verbatim** ("20.82", "19.??"), mass as a derived Quantity (× 47.65 kg, with recipe), descriptors: relief saint, founder's D, muzzle Type C, casting year as marked | "Heavy saker", "falcon", "petriere" are **class words**: `label` inferences by the compiler (Ridella), not detection fields. |
| Gun position | `position: {absent: {reason: "not in the project's sources"}}` | Fills in later from survey records without changing anything else. |
| **Observed relations** | `DetectionRelation`: the rudder *overlies* a bronze gun; three anchors and three guns *overlie* the concretion (Birch & McElvogue 1999) | These are seen, not inferred, and they are evidence for the break-up. |
| **Magnetometry** (Birch & McElvogue 1999) | `Acquisition` (remote sensing) → `Detection` with extent geometry (165 × 40 m, 270 × 72 m, 15 × 10 m) | Positions are placeholders today; they stay flagged until real ones exist. |
| **Lisbon muster, 9 May 1588** | `Acquisition` (historical observation, epoch 1588-05-09, observer: the muster clerks) → one `Detection` per ship row (tons, soldiers, seamen, guns, shot, powder…) with verbatim values | The printed copies are `CatalogueEntry` records: the Paz Salas Lisbon edition (1588), and Martin 1984 App. 4 copying it. |
| **Cuéllar's letter, 4 Oct 1589** | `Acquisition` (historical observation, epoch 1589-10-04, observer: Cuéllar) → one `Detection` per coded passage (the 125 signals), verbatim span mandatory | Crawford's translation is a `CatalogueEntry`. The times *inside* the letter (the nights, "we awaited the rising of the moon") are `reported_time`, verbatim; dating them is the worldline's inference. |
| **Dorino's 1569 price note** for Francisco Reul of Barcelona (ASGe, NA, f. 1873) | historical observation, epoch 1569-08-26, read from Ridella et al. 2016 | Evidence for the commissioning path event. |
| **Ship dimensions and ratings** (§26.1) | historical observations from their archival source, once §26.8 identifies it | The codo and every metric conversion are derived Quantities with recipes; the capacity tables are inferences. |
| **Gun identity** | one `Signal` per gun, minted by its first detection | The 1985 sighting and the lift are the same trace: direct attachment. |
| **Where the guns came from** | `path_event` inferences: inception (cast, Genoa, 1570); displacements (to Barcelona; to Lisbon; to Streedagh, 21 Sep 1588; lifted, 1985/2015; museum) | This is the "vector back to the source", as an inference chain with probabilities. |
| **Which ship** | `attribution` inference: gun → `src:ship-juliana` with p (today's estimator output) | Replaces the v3 `entity_attributions` list. |
| **Mounting stations** | inference with basis (Martin p. 195, p. 298; Ridella p. 29) and a falsifier | Ship-frame positions, see §1. |
| **The ships** | `Source` kind `object`: Juliana, Lavia, Visón; support = attribution inferences | Their reconstruction (dimensions, castles) hangs here as inferences. |
| **Dorino II Gioardi's workshop** | `Source` kind `agent` | Links Streedagh to the San Giorgio at Cádiz. |
| **The break-up** | `Source` kind `event`: a motion with a worldline of `source_event` inferences: at anchor → anchors fail → driven onto the outer bar → heel shoreward → castles collapse → release sorted by density → burial | Site assessment v2 L1/L2 and Part II, plus your shoreward-heel hypothesis. |
| **The storm** | `Source` kind `field` (an influence on motion) | Optional at first. |
| **Your hypothesis in your words** | `FieldNote`, verbatim, attached to the break-up source | Kept as written, never parsed. |

## 3. The break-up as a testable prediction

This is where the flat site frame pays off. Define the **shore axis** as an inferred line parallel to
the strand (the bar crest), and for each wreck the **keel line**. For any gun with a position, its
*signed distance inshore of the keel line* is one subtraction in the site frame. The prediction:

> distance inshore increases with mounting height (height rank)

is then a plain rank correlation, and the schema's promotion rule fits it exactly (DESIGN §8): a
prediction stated *before* the positions are seen, naming an independent observable. If the positions
confirm it, the break-up source is promoted; if the light guns lie seaward or at random, the
inference's falsifier fires.

## 4. Build order (when agreed)

1. **Producer** `pipeline.streedagh`, an adapter in `1_signal_field/` that reads the hand-edited CSVs
   (`juliana_guns.csv`, `lisbon_muster_1588.csv`, later `cuellar_signal_map.csv`) and writes schema
   records. The CSVs stay the place to edit.
2. Validate every record with `signal-schema validate`.
3. A **view exporter** that writes today's v3-style store and GeoJSON from the records, so
   `attribution_estimator.py`, `web_data.py` and the pages keep working unchanged.
4. Order of content: guns + muster (small, real, already sourced) → observed relations → Cuéllar's
   125 → reconstruction inputs → magnetometry.

**Not doing now:** GCRS, stored vectors, the ship frame as a registered frame, validator tiers beyond
what the schema already enforces.

## 5. Open questions for Dylan

1. **D7 is still "not yet ruled"** in `signal_schema/docs/decisions.md`. Rule it as: sites placed by
   a geographic or national frame; within a site, a local Euclidean frame; GCRS only ever a derived
   view. That would make Senchas's cube and the archaeology record the same decision.
2. **The ship's own frame**: keep ship-frame positions inside inferences (proposed), or register an
   inferred body frame as a `Frame` with its own uncertainty?
3. **Published recoveries as historical observations**: the schema's rule makes the 1985 and 2015
   lifts "reached through a document". Agree, with certainty carried by sigma?
