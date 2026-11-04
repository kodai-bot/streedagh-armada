# Streedagh Armada Wreck Site — Technical Assessment
## Working draft: inverse physical reconstruction within a controlled-motion systems framework

*Sites 1–3, Streedagh Strand, Co. Sligo — La Juliana, La Lavia, Santa María de Visón (Levant Squadron, wrecked 21 September 1588)*

---

## 0. How this draft is organised, and a status key

This is a working scaffold, not a finished report. It deliberately departs from the conventional order (history first, reconstruction last). Our signature method is to **work backwards from the surviving evidence to the physical parameters of the system that produced it**, so the physical assessment is placed *up front* and the historical narrative is deferred to the end, to be written once the parameters are fixed. The integrated frame matters more than the section numbering; the mapping table in §H shows how each block lands in a conventional structure if we need one for a funder or journal.

Each block carries a status marker:

- **[DRAFTED]** — written here from work already done; needs review and refinement, not invention.
- **[OUTLINE]** — argument structure in place, prose to be expanded.
- **[DEFERRED]** — placeholder; to be written last (especially historical background).

Provenance markers (`⟵ source`) point to the model, file, or document a block derives from, so nothing is unsourced when we assemble the final version.

Our work products to date: `streedagh_hull.py` (vessel reconstruction), `streedagh_manifest.py` (cargo / surviving-mass budget; timber section added 2026-07-01), `streedagh_guns.py` (armament model), `juliana_guns.py` (calibrated bronze), `streedagh_HEADLINE.md` (consolidated figures). Primary documentary inputs: Birch & McElvogue 1999 (IJNA 28.3); Ridella et al. 2016 (Archeologia Postmedievale 20, the Cádiz Delta II / *San Giorgio*); Moore, Brady & Kelleher 2015; McElvogue 2002; **Martin 1984** (Colin Martin, *The Equipment and Fighting Potential of the Spanish Armada*, Ph.D. St Andrews — Order of Battle Appendix 4, Ship Types Chapter 6; this is the foundational Armada archaeological source and is now the primary reference for C.1 squadron composition and B.2 siege-train loading).

---

# PART A — FRAMEWORK

## A.1 Thesis: the assemblage as the terminal state of a controlled-motion system
**[DRAFTED]** *(maps to template §1.3 Research Objectives; §9 Systems Reconstruction)*

An army is force that must be *moved* to where it can act. The 1588 enterprise was, at bottom, a machine for the controlled motion of military force across water to a landing — and the Levant squadron's heavy merchant *naos* were the load-bearing elements of that machine: high-capacity vessels converting stored resources (hulls, ordnance, munitions, men, food, money) into delivered force at a target. Read this way, each of the three Streedagh ships is not primarily a "ship" but a **controlled-motion subsystem** with measurable parameters: how much mass it moved, of what kind, under what control surfaces.

A wreck is the *failure* of that system — a sudden, irreversible loss of control of motion. The archaeological site is the system's **terminal state**: the frozen residue of the apparatus at the instant control was lost and for centuries afterward. This gives the whole assessment a single spine:

1. **The parameters of the motion** — what mass the system was built to move (Part B).
2. **The system itself** — the squadron as a distributed logistical machine, and how function was specialised across the three hulls (Part C).
3. **The failure cascade** — the ordered collapse from loss of control to dispersal (Part C.3).
4. **The settling and its foreclosure** — how the released material came to rest and was *ratcheted* into preservation, and how an active sea now threatens to re-mobilise it (Part D).

The ballast mound is the system fully at rest — the densest, least-mobile residue, motion arrested. Lighter material moved further or left the system entirely. The sand is the final arrest. Recovery is the deliberate re-introduction of controlled motion (lifting), racing an environment that periodically re-mobilises and therefore destroys.

This is not decoration on a standard report; it is the organising logic, and it is what lets the three wrecks be treated rigorously as *one* system rather than three case studies.

## A.2 Method: inverse reconstruction
**[DRAFTED]** *(maps to template §5 Methodology; §10 Ship Reconstruction)*

We do not have a manifest. We have documented tonnages and gun counts, the surviving finds, period naval architecture, and — crucially — a calibration source for the ordnance. The method is to **invert** these into physical parameters with explicit assumptions and honest error bars, then **cross-check independent estimates against each other** so the reconstruction is constrained from more than one direction. The two load-bearing cross-checks already in hand:

- The bottom-up **cargo mass budget** (built from finds + analogues) must fit *under* the **payload ceiling** derived independently from the hull reconstruction. It does (§B.3) — the manifest is physically possible, not just plausible.
- The modelled **surviving iron mass** must be consistent with the **recorded magnetometer ferrous footprints**. It is (§B.3) — the survival model is anchored to instrument data.

Every figure below is a stated-assumption Monte Carlo estimate (median with a 5th–95th percentile band), not a point claim. Where a parameter is genuinely unconstrained, that is stated rather than hidden.

---

# PART B — PHYSICAL ASSESSMENT (THE MOTION PARAMETERS)

*This is the heart of the assessment and goes first. It establishes what mass the system was built to move, what it still holds, and is the part where we have made the most progress.*

## B.1 Vessel parameters — hull reconstruction
**[DRAFTED]** ⟵ `streedagh_hull.py`, `streedagh_reconstruction_notes.md`
*(maps to template §6 Individual Vessel Assessments; §10 Ship Reconstruction)*

**The inverse chain (so the logic is legible).** The only hard vessel datum is *burthen* in *toneladas* — a 16th-century measure of **cargo capacity by volume**, not weight, and not displacement. We convert it forward to the physical quantities that matter:

1. *Burthen (toneladas) → cargo volume.* Each tonelada corresponds to a stowage volume (a barrel-equivalent); we apply a conversion factor `k` (m³ per tonelada) drawn as a range, because the unit was not perfectly standardised.
2. *Cargo volume → internal hull volume.* Cargo space is a fraction `φ` of the ship's internal volume (the rest is structure, ballast, stores, crew space); `φ` is drawn as a range.
3. *Internal volume → principal dimensions.* Using period proportions — length-to-beam `α` (≈3.3–3.8 for a Mediterranean *nao*), depth-to-beam `β` — and block coefficients that describe how "full" the hull is, we solve for beam, length and depth.
4. *Hull form → displacement.* The submerged volume × seawater density gives **displacement** (the ship's actual mass, fully laden).
5. *Displacement → deadweight → payload.* Subtract the lightship mass (a fraction `λ` of displacement) to get **deadweight** (everything carried); subtract ballast and stores to get the **non-ballast payload** — the militarily meaningful figure: guns, siege train, munitions, men and their gear.

Every Greek-letter factor is a distribution, not a constant; the Monte Carlo (200,000 draws) propagates all of them into the output bands.

**Results** (median [5th–95th percentile]):

| Ship | Burthen (t) | Guns | Beam (m) | Length (m) | Depth (m) | Displacement (t) | Deadweight (t) | Non-ballast payload (t) |
|---|---|---|---|---|---|---|---|---|
| La Juliana | 860 | 32 | 13.6 [12.8–14.5] | 48.2 [45.0–51.6] | 6.8 [6.3–7.3] | **1,390** [1,133–1,706] | 694 [550–874] | 450 [348–579] |
| La Lavia | 728 | 25 | 12.9 [12.1–13.7] | 45.6 [42.6–48.8] | 6.4 [6.0–6.9] | **1,177** [959–1,443] | 588 [466–738] | 381 [295–489] |
| Santa María de Visón | 666 | 18 | 12.5 [11.8–13.3] | 44.2 [41.3–47.4] | 6.3 [5.8–6.7] | **1,077** [878–1,320] | 538 [426–676] | 349 [270–448] |
| **Combined** | **2,254** | **75** | — | — | — | **~3,640** [~2,970–4,469] | **~1,820** | **~1,180** |

**Headline for interpretation:** *La Juliana* reconstructs to roughly **2.4× the displacement of the Galeón Andalucía** (~589 t). The widely-repeated "46% larger" compares the ships' *burthen* to the replica's *weight* — two different physical quantities — and understates the contrast. Displacement-to-displacement is the honest comparison, and the public yardstick (the replica) is the smaller object.

## B.2 Ordnance — the calibrated military core
**[DRAFTED]** ⟵ `streedagh_guns.py`, `juliana_guns.py`; Ridella et al. 2016; Birch & McElvogue 1999
*(maps to template §8 Naval Armament; §9.2 Functional Role)*

*Irish maritime archaeology has a poorly-developed conflict / military-materiel strand. The ordnance assemblage at Streedagh is an exceptional dataset for early-modern military logistics, and treating it quantitatively — calibrated masses, functional tiers, a salvage mechanism — is one of the methodological inroads this report intends to make. This section is therefore weighted accordingly.*

**The calibration.** The bronze guns of both *La Juliana* and the Genoese transport *San Giorgio* (Cádiz Delta II) came from the **same foundry — Dorino II Gioardi of Genoa**. Ridella et al. weigh the *San Giorgio's* marked pieces, which fixes the Genoese unit: **1 cantaro = 47.65 kg** (three marked guns agree to within 0.1%). Every weight-marked Juliana gun therefore converts directly to kilograms, with no guesswork.

**The recovered battery is the ship's own armament, not her cargo.** Twelve of *La Juliana's* 32 guns have been raised (3 in 1985, 9 in 2015), and one further piece — an iron *esmeril* — was recovered from *Santa María de Visón*, giving a **fleet total of 13 guns raised to date** against a documented complement of 75. The Juliana pieces were all cast in **1570 — her build year** — and dedicated to saints including **St. Matrona, patron of Barcelona** (where she was built). These are her **defensive fit**: sakers, falcons, a falconet, and stone-throwing *petrieri* — the anti-corsair armament a merchant *nao* carried on and near her decks.

| Recovered Juliana gun (Dorino II Gioardi, 1570) | cantara | Mass |
|---|---|---|
| Heavy Saker (St. Severo) | 20.82 | 992 kg |
| Heavy Saker (St. Giovanni Battista) | ~19.4 | ~924 kg |
| Heavy Falcon (St. Matrona) | 11.12 | 530 kg |
| Heavy Falcon (St. Ilaria) | 10.74 | 512 kg |
| Medium Falcon (St. Sebastiano) | 8.54 | 407 kg |
| Medium Falcon (St. Rocco) | ~7.74 | ~369 kg |
| Falconet (St. Giovanni) | 3.88 | 185 kg |
| Medium *Petriere* ×2 (unmarked) | ~11 est. | ~520 kg each |
| **Recovered bronze total (12 guns)** | | **~6 t; heaviest ~1 t** |

**The scale correction that matters.** The popular figure of "~1.5 t / 183 mm bore / 40–41 lb ball" guns is **not** the Juliana's recovered ordnance. It is the *Trinidad Valencera's* **2.5-tonne** Brussels-cast siege gun, used as a sister-wreck proxy — the National Museum draws exactly this distinction, contrasting that siege piece with the "smaller *pedrero* cannon from the Juliana." The actual recovered Juliana guns are light-to-medium defensive pieces; the heaviest is barely 40% of one Valencera siege gun.

**Three functional tiers (evidenced, not assumed):**

1. **Defensive armament** — light/medium bronze, ~6 t recovered, accessible on/near decks. *Found.*
2. **Iron guns** — roughly the remaining ~20 of the 32; cast- and wrought-iron, prone to corrosion/concretion or early salvage. *Mostly unaccounted.*
3. **Siege train (cargo)** — heavy battering pieces, **evidenced directly by five 1.5 m spoked carriage wheels at Site 1**, stowed deepest as cargo for the land campaign. *Buried; largely unrecovered.* If any approach Valencera scale, the buried siege tier could rival the entire recovered defensive battery in mass.

**The salvage mechanism (why tier 3 is still there).** The *San Giorgio* gives the mechanism directly: her deck armament was salvaged within months of sinking, but **five long-barrelled cargo guns stowed in the hold survived because the salvage hooks of 1587 could not reach the ship's interior**. The *San Giorgio* was herself an Armada artillery transport — Genoese guns shipped as cargo toward Lisbon — which is direct, independent evidence for the heavy-lift / artillery-as-cargo role we attribute to the Streedagh ships. The same logic predicts that at Streedagh the accessible defensive guns are found and the deep siege cargo is not.

**Armament mass model (the 75 documented guns)** ⟵ `streedagh_guns.py`: distributing the documented complement across period type-bands gives the following mass envelope for the three hulls combined:

| Tier | Description | Mass (t) | Band [5th–95th] |
|---|---|---|---|
| Light/accessible | Esmeriles, pedreros — deck-mounted, small-bore | ~17 | [16–19] |
| Heavy/lower | Sakers, minions, falcons — gun-deck, iron + bronze | ~27 | [25–29] |
| Siege train (cargo) | Cañones de batir + field pieces — stowed in hold | ~13 | [7–20] |
| **Fleet total (ship's armament)** | | **~44** | **[41–48]** |

These are coarse relative to the calibrated bronze and should be read as the *armament* envelope, with the calibrated Juliana table above as the firm anchor. The siege train estimate is the widest band because it depends on how the fleet's 12 *cañones de batir* (12 battering cannon plus 21 other field pieces, per Martin 1984 Appendix 3) were distributed across hulls — with the carriage-wheel evidence at Site 1 pointing specifically at Juliana as the carrier.

## B.3 Cargo and surviving-mass budget
**[DRAFTED]** ⟵ `streedagh_manifest.py`, `streedagh_manifest_notes.md`
*(maps to template §8 Artefact Assemblage; §9.3 Estimated Cargo Capacity)*

**Method.** A bottom-up Monte Carlo built from the recorded finds and close analogues (the *Trinidad Valencera* template; the calibrated *San Giorgio* ordnance and anchors), summing the **durable** material classes that can survive four centuries on a seabed, then **cross-checked against the payload ceiling** from §B.1. The as-loaded estimate (~402 t for *La Juliana*) sits comfortably under that ship's payload cap (450–579 t): the manifest is physically consistent, not merely plausible.

**Per-ship surviving durable mass** (median [5th–95th]):

| Ship | Bronze (t) | Iron (t) | Lead (t) | Stone (t) | Ceramic (t) | Organic (t) | Durable total (t) |
|---|---|---|---|---|---|---|---|
| La Juliana | 12.3 [7.9–17.3] | 28.2 [21.7–35.7] | 4.2 [1.9–7.0] | 180.8 [140–221] | 2.8 [1.4–4.7] | 11.5 [5.2–22.1] | **229** [188–270] |
| La Lavia | 10.4 [6.7–14.6] | 24.5 [18.9–30.9] | 3.5 [1.6–5.9] | 153.1 [119–187] | 2.3 [1.2–4.0] | 9.7 [4.4–18.7] | **194** [159–229] |
| Santa María de Visón | 9.5 [6.1–13.4] | 22.7 [17.5–28.6] | 3.2 [1.5–5.4] | 140.1 [109–172] | 2.1 [1.1–3.7] | 8.9 [4.0–17.1] | **178** [146–210] |
| **Combined** | **33** [26–40] | **76** [65–87] | **11** [8–15] | **474** [413–535] | **7** [5–10] | **32** [20–46] | **601** [539–664] |

**Combined surviving durable mass on the seabed today** (median):

| Material | Mass (t) | Note |
|---|---|---|
| Ballast stone | ~474 | dominant surviving mass; the ballast mounds — the system fully at rest |
| Iron (concreted) | ~76 | **matches recorded ferrous footprints**: Site 1 165×40 m, Site 3 270×72 m |
| Bronze ordnance | ~33 | of which ~6 t recovered (the defensive tier; §B.2) |
| Lead | ~11 | sheeting, ingots, shot |
| Ceramic | ~7 | *botijas* / storage vessels |
| Organic residual | ~32 | survives only where sand-sealed |
| **Total durable** | **~601** [539–664] | |
| of which **artefact-grade** (metal + ceramic, ex-ballast) | **~125** | the archaeologically rich fraction |

The iron cross-check is the important one: an independent survival model lands on ~76 t, and the recorded magnetometer scatters are consistent with that order of magnitude. Two methods, one answer — the budget is anchored to instrument data, not just to analogy.

**Structural timber mass — infrastructure sizing parameter** ⟵ `streedagh_manifest.py` (timber section).

The cargo/artefact manifest above does not include the ships' own structural oak. This is a separate quantity, and it bears directly on recovery infrastructure: any lift of a significant hull section brings timber mass that must be conserved. Construction template: *La Trinidad Valencera* (same Levant-squadron class, Martin 1984 Ch.6) — solid-framed oak, 10 cm planking, iron fastenings throughout (all corroded; their mass is already captured in the iron line above). Basis: displacement × lightship fraction × hull-timber fraction of lightship.

| Ship | Full-hull timber (original) | Survival 1/4 | Survival 1/3 | Survival 1/2 |
|---|---|---|---|---|
| La Juliana | 402 [347–462] t | 101 [87–116] t | 134 [116–154] t | 201 [174–231] t |
| La Lavia | 341 [294–391] t | 85 [73–98] t | 114 [98–130] t | 170 [147–196] t |
| Santa María de Visón | 312 [269–358] t | 78 [67–90] t | 104 [90–119] t | 156 [134–179] t |
| **Combined** | **~1,055** t | **264** [243–286] t | **352** [324–382] t | **528** [485–572] t |

Survival scenarios represent the fraction of original hull timber that remained on-site and was buried before dispersal or biological decay: 1/4 is conservative (energetic wreck event, partial burial); 1/2 is optimistic (rapid sand burial of an intact lower hull). At Streedagh, the absence of any recorded salvage and the confirmed presence of articulated timbers at Site 1 favour the upper end of the range. Waterlogged oak density ≈ 900–1000 kg/m³; a single 10×3 m section of lower hull (0.4 m mean timber depth) = ~11–12 t. A hull section with ballast still in place — the likely scenario where the bottom is intact — could reach **20–50 t per lift**. Conservation tank and crane capacity at Sligo quay and the proposed institute should be sized accordingly.

## B.4 Complement — the human payload (and the war grave)
**[DRAFTED]** *(maps to template §9.2; §11 Significance; §12 Condition — sensitivity)*

Documented crew: *Juliana* ~65, *Visón* ~70; *Juliana* additionally carried ~290–325 soldiers. Across the three, a documented minimum complement of **1,013** (807 soldiers + 206 sailors), and very likely higher after inter-ship transfers from lost vessels. Francisco de Cuéllar, aboard *La Lavia*, records **over 1,000 dead and fewer than 300 survivors**. The implication for the motion-system is that these hulls were simultaneously **heavily manned and heavily equipped** — combined troop-and-materiel transports, not one or the other.

The unavoidable corollary: **the site is a war grave.** Any assessment, recovery plan, or public interpretation must hold the quantitative and the commemorative registers together. The same sand that may hold an intact field-hospital assemblage and a buried siege train also holds the dead.

---

# PART C — THE MOTION-SYSTEM

## C.1 The Levant squadron as a logistical (motion) system
**[DRAFTED]** *(maps to template §9.1 Armada as a Logistical System)*
⟵ Martin 1984 (Ph.D. St Andrews), Appendix 4 (Order of Battle) and Chapter 6 (Ship Types)

The Levant squadron was the heavy-lift tier of the Enterprise of England. Under Martín de Bertendona it comprised ten Mediterranean-built merchant *naos* — predominantly Venetian and Ragusan hulls, several forcibly requisitioned into royal service — grouped together precisely because of their enormous carrying capacity. The Lisbon muster of 1588 records the full complement:

| # | Ship | Role | Burthen (t) | Soldiers | Seamen | Guns | Status |
|---|---|---|---|---|---|---|---|
| 68 | La Regazona | *capitana* (flagship) | 1,249 | 344 | 80 | 30 | Returned: Corunna |
| 69 | La Lavia | *almiranta* (vice-flagship) | 728 | 203 | 71 | 25 | **Lost — Streedagh** |
| 70 | La Rata Coronada | — | 820 | 335 | 84 | 35 | Lost |
| 71 | San Juan de Sicilia | — | 800 | 279 | 63 | 26 | Lost |
| 72 | La Trinidad Valencera | — | 1,100 | 281 | 79 | 42 | Lost — Donegal |
| 73 | La Anunciada | — | 703 | 196 | 79 | 24 | Lost |
| 74 | San Nicolás Prodaneli | — | 834 | 274 | 81 | 26 | Returned: Corunna |
| 75 | La Juliana | — | 860 | 325 | 70 | 32 | **Lost — Streedagh** |
| 76 | Santa María de Visón | — | 666 | 236 | 71 | 18 | **Lost — Streedagh** |
| 77 | La Trinidad de Scala | — | 900 | 307 | 79 | 22 | Returned: Santander |

*(Source: Martin 1984, Appendix 4, Order of Battle. Burthen figures in toneladas de arqueo.)*

The choice of these ships was deliberate and documented. When the Venetian merchantmen *Regazona* and *Lavia* inadvisedly docked at Lisbon in February 1588, Philip's commissioners informed their masters that "the king required those vessels... the commissioners reported that these ships were the finest, the best armed and manned of all that lay in Lisbon, and on no account should his Majesty let them go" (Martin 1984, p.210, citing the Venetian ambassador Lippomano). Vigorous Venetian diplomatic protest was of no avail, and Bertendona explained his enthusiasm in a letter to Philip II of 27 February: although he admitted the ships' *grandeza* (overbearing size and magnificence) might carry navigational risks in Atlantic conditions, it would give them "an overwhelming tactical advantage when it came to close-quarter battle." The king acknowledged the navigational point in his reply of 5 July — "I see plainly the truth of what you say, that the Levant ships are less staunch in heavy seas" — but proceeded nonetheless. Of the ten ships, eight were lost; only *La Regazona* (Bertendona's own vessel) and *La Trinidad de Scala* returned safely, an 80% loss rate against the fleet-wide average of approximately 30% (Martin 1984, p.211). Philip II, reviewing casualty returns that autumn, would have had reason to regret his decision.

These ships were selected to carry the heaviest elements of the invasion cargo, and this loading assignment is explicitly documented. Before the Armada sailed from Lisbon, the galleys of Diego Medrano's squadron were employed in "assisting with the delivery of heavy siege artillery and its associated equipment to the Levantine ships" (Martin 1984, p.202). The fleet-level siege train — 12 *cañones de batir* with field carriages, 21 other field pieces, pioneers' tools for 700 men, and 40 mules for the artillery — was stowed in the Levantine holds, the deepest and most inaccessible stowage position in the largest hulls in the fleet. The carriage wheels evidenced at Site 1 are the direct archaeological trace of this documented loading decision.

The squadron's designed terminal state — the endpoint of the motion system — was the junction with the Duke of Parma's army in the Flanders ports. Parma's tercios, approximately 17,000 infantry, were to embark aboard the naos' broad lower decks alongside the siege train, and the convoy was to proceed under naval escort to the Kent beaches. At the landing, the galleys (whose role at Terceira in 1583 had been exactly this: close-support gunboats covering infantry assault from landing craft) would bring the heavy artillery ashore under fire and into position for the march on London. The Streedagh hulls are not, therefore, wrecks of a failed naval battle; they are the undelivered hardware of an unexecuted amphibious operation, arrested at the moment of their terminal failure and frozen in their stowed configuration. The cargo they carry is invasion cargo, loaded for that specific terminal action.

*(Note: the draft's C.2 references de Cuéllar and "Terceira" — the 1582 naval action off the Azores is distinct from the 1583 amphibious conquest of Terceira Island. Martin 1984 p.201 makes clear that the galleys' 1583 close-support role at Terceira is the operational template for 1588. Juliana's presence at the 1583 action has not been confirmed from this source; the claim in C.2 derives from the Catalan archival record via Antoni Martí i Coll and should be cited to that source rather than to Martin.)*

## C.2 Functional specialisation across the three hulls
**[DRAFTED]** *(maps to template §9.2 / §9.6 Fleet-Level Reconstruction)*

The three wrecks are not redundant copies; the evidence points to **specialised loads**, which is itself a finding about coordinated logistics:

- **La Juliana** — the heavy-ordnance / siege-engineering carrier. Evidence: five siege-carriage wheels; the largest hull. She is also the clearest **worked example of the structural pattern** — the same Mediterranean trader repeatedly pulled into imperial military logistics across two decades. Built at Mataró by the Palau family (original name *Santa María, Sant Jaume i Santa Clara*) and captained from launch to loss by Joan Arnau Palau, she served as a troop carrier at Lepanto (1571) and, by royal command, in the **Portugal and Azores campaigns of the early 1580s**, before Philip II commandeered her for the Armada at Sicily on **15 December 1586** *(⟵ Archivo de la Corona de Aragón, from her construction contract and the archival work of Antoni Martí i Coll)*. The amphibious **conquest of Terceira (1583)** is the doctrinal template for what a contested landing required to be loaded — the siege train and engineering gear, i.e. the very cargo tier reconstructed here. We use it as the model for the *load*, without claiming this hull was present at the landing itself. *(Note for revision: distinguish the 1582 naval action off the Azores from the 1583 amphibious conquest; de Cuéllar's "Terceira" may refer to the former — to be resolved against O'Neill and the detailed campaign history.)*
- **La Lavia** — the *almiranta* (vice-flagship), carrying the Judge Advocate General Martín de Aranda: the **command-and-discipline** node of the squadron. De Cuéllar sailed aboard her.
- **Santa María de Visón** — the **medical** carrier: she took on a share of the whole fleet's medical supplies after the dedicated hospital ship was condemned at Laredo. One of the three hulls is, in effect, an Armada field hospital.

This is the fleet-level reconstruction the template asks for: supply was *distributed and specialised* (ordnance, command, medicine), evidence of designed logistics rather than ad-hoc loading.

## C.3 System failure — the loss-of-control cascade
**[DRAFTED]** *(maps to template §9.7 System Failure; §7 Site Formation)*

The wrecking is best read as an **ordered failure cascade** — the sequential loss of the system's motion-control elements:

1. **Storm loading** exceeds the control surfaces (sail, steering) — control of heading and position degrades.
2. **Anchor failure** — the one apparatus for *arresting* motion against weather is lost or drags (the squadron, embayed on a lee shore, cannot hold).
3. **Separation / grounding** — uncontrolled contact with the seabed in the surf zone.
4. **Hull failure** — structural collapse under surf loading.
5. **Cargo release** — the payload exits the vessel and disperses by density: dense ballast and ordnance settle near the hull; lighter material moves out or leaves the system.
6. **Settling into the terminal state** — the assemblage as we find it.

Each step is a loss of a degree of motion-control, and the spatial signature on the seabed (dense material concentrated, light material dispersed) is the direct fingerprint of step 5.

---

# PART D — SITE FORMATION, TAPHONOMY, AND FORECLOSURE

## D.1 Depositional environment and the Valencera contrast
**[DRAFTED]** ⟵ Birch & McElvogue 1999; site magnetometry
*(maps to template §3.3 Sediment Dynamics; §7 Site Formation; §6 Preservation)*

The single most important point in the whole assessment, and the basis for the "world-class" claim: **Streedagh and the *Trinidad Valencera* are non-comparable deposits.**

- **Trinidad Valencera** — came to rest on a **hard seabed**. Lighter material washed away; the heaviest objects were left **exposed** on the bottom. What survives is a lag deposit of the densest items.
- **Streedagh** — the **hulls filled with sand**, and excavators report **articulated ship timbers surviving in place** beneath the overburden. The sites lie parallel to shore: Site 1 (*Juliana*) 165×40 m at 3.8–5.2 m; Site 2 (*Visón*?) a small 15×10 m signature; Site 3 (*Lavia*?) 270×72 m, with the **greatest sand cover**, sheltered by the headland.

The consequence is decisive: if hull structure survives articulated and sand-sealed, then **the holds may be at least partly intact**, and the heavy gear — the buried siege tier (§B.2), bulk munitions, the medical assemblage — **should still be there, where it was stowed.** Streedagh is potentially that rare thing: an **unsalvaged, sand-sealed invasion cargo**, structurally coherent rather than a scatter of the indestructible.

## D.2 The foreclosure (ratchet) model of preservation
**[DRAFTED]** *(maps to template §6 Preservation Processes; §7)*

Preservation here is the product of a **double foreclosure** — a ratchet, in our standing vocabulary, in which two alternative pathways for the assemblage (salvage; dispersal/decay) were each foreclosed, locking the material into survival:

1. **Salvage foreclosed by war.** Bronze guns are normally the first thing stripped from any wreck (gunmetal outvalued the ship). They survived on the surface here because the wrecking opened the **Fifteen Years' War** (O'Sullivan Beare dated the conflict's start to the 1588 Armada arrival): the north-west was a contested war zone **1588–1603**, beyond stable administrative reach, with no secure access for the divers and time that organised salvage needs. Birch & McElvogue found **no documentary evidence of any historic salvage**. The *San Giorgio* mechanism (§B.2) supplies the proximate cause at the object scale; the war supplies it at the regional scale.
2. **Dispersal/decay foreclosed by sand.** Rapid burial in a mobile-sand regime sealed the structurally-coherent remains before they could disperse or oxidise, ratcheting them into the preserved state.

The model is also the **threat model** (§F): the ratchet is not permanent. The same active sand that foreclosed dispersal periodically *re-opens* it — storms strip the cover, re-mobilise the assemblage, and expose it to a high-energy surf zone that destroys what it uncovers. Preservation here is a metastable equilibrium, not a stable one.

---

# PART E — SIGNIFICANCE

**[DRAFTED]** *(maps to template §11 Significance Assessment)*

- **International / archaeological.** A potentially intact, sand-sealed, **unsalvaged invasion cargo** of three specialised transports — structurally coherent rather than a lag deposit — is rare worldwide and distinct in kind from the *Valencera* and most exposed-seabed Armada wrecks.
- **Military / logistical (the inroad).** An exceptional dataset for **early-modern military logistics and ordnance** — a strand poorly developed in Irish archaeology. The calibrated ordnance, the three functional tiers, and the documented siege train make this a type-site for quantitative military-materiel and systems analysis, not just a relic scatter.
- **Technological.** Construction (articulated Mediterranean-*nao* timbers), Genoese bronze gunfounding (a dated, single-foundry assemblage from Dorino II Gioardi, 1570), and anchor/rigging technology.
- **Historical.** Direct material testimony to the invasion logistics, corroborating and extending de Cuéllar and the Spanish/English documentary record; *La Juliana's* documented career of repeated requisition — Lepanto troop carrier, Portugal and Azores campaigns, then Armada (Sicily, 1586) — exemplifies the cycling of Mediterranean traders into imperial military logistics, with the 1583 amphibious conquest of Terceira as the doctrinal template for invasion-equipment loading.
- **Landscape / public heritage.** A war grave and a community-defining event in north Sligo. The heritage organisations in Grange, Co. Sligo — the village nearest Streedagh Strand — have sustained a public campaign for interpretation and display and have been instrumental in keeping the site in public view. Live public engagement is demonstrated by the 2015 Galeón *Andalucía* replica visit, the community drive for a visitor facility, and the advocacy that preceded the 2015 rescue excavation. Grange is the natural gateway settlement for the site.

---

# PART F — CONDITION, THREAT, AND THE RECOVERY-CAPACITY CASE

**[DRAFTED]** *(maps to template §12 Condition Assessment; §14 Recommendations)*

**Condition.** Variable and dynamic. Where sand-sealed, preservation is exceptional (articulated timbers; "superb" gun condition where unexposed). Where exposed, deterioration is rapid. The state of Sites 2 and 3 is largely inferred from their (greater) sand cover.

**Threat.** Active, episodic, and destructive. Storm-driven sand stripping in a high-energy surf zone periodically re-mobilises and exposes material; exposure events are *destructive*, not merely revealing. This is the metastable-equilibrium threat from §D.2.

**The capacity argument (a central recommendation).** A site preserved by a foreclosure that the sea periodically re-opens cannot be stewarded by **reactive response**. Answering each exposure from a standing start — expertise and equipment imported from elsewhere, after the fact — guarantees loss, because the clock starts the moment the sand lifts. What a site of this importance requires is:

- a **standing recovery and monitoring plan**, triggered by exposure rather than improvised after it; and
- the **local capacity to execute it** — physical infrastructure (survey, recovery, conservation) and **resident expertise, based in Sligo**, at the site, rather than dependent on arriving from away.

Building that capacity *where the site is* is the difference between stewarding the wreck complex and merely reacting to it — and it is the structural condition for realising the research and heritage value catalogued in Part E. *(This connects to the wider political economy of who pays for, and therefore controls, archaeological response — to be developed.)*

---

# §13 DISCUSSION

## §13.1 The framework and its predictive test

The analysis in this report rests on a single testable claim: a wreck assemblage is not a random deposit. It is the terminal state of a system that lost control of its motion at a specific place and time, and the structure of the deposit is therefore a function of the system's physical parameters — the masses it carried, how they were stowed, and the physics of the failure event. A framework that makes this claim must also submit it to evidence. The Streedagh record provides four checks.

*First:* dense material should be concentrated near the hull's final position. Magnetometry confirms three ferrous anomalies at Sites 1–3, each consistent in scale with the modelled iron mass per ship (~22–28 t median from §B.3). The footprints are not random scatters; they are elongated parallel to the shore, as the model of a hull settling under surf loading would predict.

*Second:* the accessible defensive tier (bronze guns, mounted near the decks) should be recoverable first; the buried cargo tier (siege ordnance, stowed deepest) should remain unrecovered. Twelve Juliana bronze guns and one Visón iron *esmeril* have been raised — the defensive tier, exactly as the model predicts for accessible bronze. No siege guns have been recovered. The five carriage wheels at Site 1 establish that the siege train was there; the model predicts that the guns associated with those carriages are buried within the footprint, below the level that post-wrecking surf action reached.

*Third:* organic and ceramic material — lighter than the surrounding sediment and the shingle that moves above it — should be absent from exposed surfaces but present where sand-sealed. Martin (1984, p.181) makes this observation precisely at El Gran Grifón, an exposed-rock site: "any material lighter than the shingle, such as wood, bone, or leather, would neither penetrate its surface nor stand any chance of surviving above it. No such material, apart from a cork tampion... has therefore survived on the site." Streedagh is a sand site with documented articulated timbers in situ at Site 1. The prediction — organics survive where burial was rapid — matches.

*Fourth:* no major salvage should have occurred. The double-foreclosure model (§D.2) predicts that the Fifteen Years' War locked out organised bronze-stripping before it could be executed. Birch & McElvogue (1999) found no documentary evidence of any historic salvage at Streedagh. That negative is the predicted outcome of the model, not merely consistent with it.

Four predictions, four confirmations. This does not prove the framework. It establishes that the model is coherent with all available evidence, which earns it the right to make a further positive claim: the buried resource is there, with the structure the model specifies, and it can be located.

## §13.2 The buried resource: what the model says remains

The record of what has been raised is also, by arithmetic, a record of what has not. Against the fleet-level durable mass of ~601 t estimated as surviving on the seabed (§B.3), the recovered material to date represents a small fraction — principally ~6 t of Juliana's bronze ordnance. The buried resource is large and structured.

**By material class, the model predicts that the following remain on site (medians from §B.3):**

- Bronze ordnance: ~27 t unrecovered — the heavier-calibre bronze pieces and essentially the full Lavia and Visón complements
- Iron (concreted): ~76 t total, of which the ~27 t heavy/lower tier of gun-deck ordnance is the largest non-ballast component
- Siege-train ordnance: ~13 t [7–20 t] — the widest band in the model, because distribution across the three hulls is inferred from the carriage-wheel evidence at Site 1 rather than from documents; the band should narrow sharply as soon as targeted excavation is possible at Site 1's ballast mound
- Structural timber: 352 [324–382] t at the 1/3 survival scenario, three ships combined (§B.3) — not an artefact priority but the primary driver of conservation-infrastructure sizing
- Organic and ceramic assemblages, within sand-sealed contexts: medical instruments and chests (Visón), cordage and provisions (all three), judicial records and navigational documents (Lavia, the *almiranta*) — low probability of survival individually but present in sufficient quantity that some proportion in undisturbed burial should remain

**By location:**

The siege train and heavy ordnance are in the deepest stowage — lowest in the hull, immediately above or adjacent to the ballast mound. The ballast mound is already mapped by magnetometry. The undiscovered heavy ordnance is not therefore difficult to locate in principle: it lies within the ferrous footprints already on the charts, at the lowest stratigraphic horizon. The medical assemblage of Visón belongs at the same depth horizon within the Site 2 signature. The command and judicial records of La Lavia are within the Site 3 footprint, and — as the most fragile category in the entire inventory — are the most time-sensitive.

The model yields a recovery priority sequence directly: deepest stowage first, where the material is most archaeologically anomalous (complete, primary, unsalvaged invasion cargo); accessible material last, where it is most vulnerable to the storm cycle but also most familiar in type.

## §13.3 The three hulls as a single system

The most consequential consequence of the motion-system framing is also the simplest: the three ships at Streedagh are not three separate sites. They are one system, and the system's properties are visible only when all three are considered together.

Functional specialisation — siege-engineering carrier, command node, field hospital — is a system property. None of the three hulls has a purpose that can be fully understood in isolation. La Juliana's siege-train evidence is meaningful only as the *load-carrying* element of an invasion machine with a specific terminal action; La Lavia's command function is intelligible only in relation to the squadron she commanded (ten ships, documented here from the Order of Battle); La Visón's medical role is intelligible only in the context of the fleet's total medical establishment, which Martin (1984) documents: five *médicos*, one *cirujano mayor*, four *cirujanos*, sixty-two medical officials — a substantial clinical apparatus distributed across multiple hulls, of which Visón received the largest share after the dedicated hospital ship was condemned at Laredo. No single hull tells the whole story; together, they give a cross-section of a military-logistical system at its moment of terminal failure.

The management consequence is direct: **the three sites must be treated as one complex.** A recovery plan that addresses only Site 1 (the strongest magnetometry signal, the clearest siege-train evidence) without treating Sites 2 and 3 as parts of the same system risks seriously mis-reading what is found. The siege-train hardware at Site 1 is only fully interpretable against the medical assemblage expected at Site 2 and the command record at Site 3. Archaeological value here is proportional to the degree to which the assemblage can be read as a coherent system — and that reading requires all three sites.

A further point from the squadron-level data: three of the eight lost Levant ships — 37.5% — are at Streedagh. The other five lost ships (La Rata Coronada, San Juan de Sicilia, La Anunciada, and two others) are largely unlocated or poorly documented as archaeological sites. La Trinidad Valencera accounts for one further excavated Levant-squadron wreck. Streedagh therefore holds the largest surviving concentration of the squadron's lost tonnage. The storm of 21 September 1588 drove the full embayed squadron onto a single lee shore: what was lost together should be understood together.

## §13.4 What failure analysis yields

The loss-of-control cascade (§C.3) is not narrative decoration. It is a site-formation model, and each step leaves a specific material signature that can be mapped against the physical record.

*Anchor failure* produces anchor(s) and cable on the seabed at or seaward of the hull's final position; a targeted search for anchor deposits would locate the drift path and establish the direction from which the hulls came to rest.

*Hull failure under surf loading* disperses structural timber along the failure axis; the articulated timbers at Site 1 represent the sections that failed last, remaining articulated long enough to be buried. The position and orientation of articulated timber relative to the ballast mound constrains the hull's final attitude.

*Cargo release* gives the spatial layering of the assemblage: ballast concentrated directly under the hull, dense ordnance near the hull, lighter cargo progressively more dispersed. The thickening of the magnetometry signal toward the seaward edge of each footprint — if confirmed on closer inspection — would be the direct map of this step.

The cascade model gives the sequence, and the sequence distinguishes *primary context* (material still in original stowage position, undisturbed by the failure event) from *secondary context* (material moved by the hull breaking up or by post-wrecking surf). The ballast mounds are primary. The scattered iron around the footprint periphery is largely secondary. The siege-train cargo — if the orlop deck and lower hold remained structurally intact long enough for sand burial to occur — may still be in primary context: in the stowage positions that the loading officers at Lisbon specified, in the spatial relationship to the keel that the ship's trim required.

A primary-context siege-train assemblage at Streedagh would be unique in the Armada archaeological record. La Trinidad Valencera yielded field-gun carriages and equipment but in secondary context, dispersed across a hard seabed. Streedagh's sand burial may have preserved the stowage arrangement itself — which is a document about how the Spanish army planned to bring heavy artillery ashore, more precise than any written source.

The methodological contribution for operational and behavioural archaeology is this: the inverse reconstruction method — burthen to dimensions to displacement to deadweight to surviving mass, with stated-assumption Monte Carlo at each step — is transferable to any site where vessel tonnage is documented. The method has two independent cross-checks built in (manifest versus payload ceiling; modelled iron versus magnetometry), which give it scientific standing: it makes predictions that can be falsified by instrument data already in hand, and at Streedagh those predictions hold. The same method applied to any of the other eight unexcavated Levant-squadron losses, or to the Baltic bulk carriers in the Armada's Urcas squadron, would give a recovery-resource baseline before a single dive.

## §13.5 The capacity argument, grounded in physics

The closing argument of Part F — that this site requires local capacity for standing response, not reactive mobilisation after exposure — is a physics argument, not an advocacy position.

The structural timber mass estimates (§B.3) set the first constraint. At the 1/3 survival scenario, ~352 t of waterlogged oak remains across the three sites. Individual hull sections in sand-sealed primary context may weigh 20–50 t waterlogged (a 10×3 m section of solid-framed lower hull at ~0.4 m mean timber depth equals ~11–12 t; with associated ballast still in place the figure rises substantially). No facility currently based in Sligo or its hinterland is configured for lifts in this range; the nearest comparable crane and tank capacity is in Dublin or overseas.

The time constraint is the binding one. The storm that strips the sand cover is the same storm that begins to abrade the exposed timber — immediately. Waterlogged oak that has spent four centuries in anoxic burial does not deteriorate slowly on exposure; it degrades rapidly as oxygenation and biological activity resume. The window between exposure and irreversible damage is measured in days to weeks. The time to mobilise crane barges and the humidified conservation tanks needed for large waterlogged sections is measured in weeks to months. Those two timescales cannot be reconciled by reactive response.

Conservation chemistry adds a second constraint. Waterlogged oak at this state of deterioration has lost its cellular rigidity; it will collapse or deform irreversibly if allowed to dry before consolidant treatment. The Mary Rose conservation programme ran from 1982 to 2013 — thirty-one years — with the hull in permanent humidity-controlled conditions throughout. A large Streedagh timber section would require an equivalent environment from the moment of recovery. That environment cannot be improvised in the field on a storm-response timeline.

The report sets the parameters that bound the infrastructure question. For each parameter — timber mass per lift, total timber mass on site, conservation timeline, storm-exposure risk — there is now a quantified estimate with an explicit uncertainty band. The infrastructure planning that follows this assessment uses these numbers to specify what is needed: crane capacity (minimum lift rating), tank volume (cubic metres of waterlogged material at stated density), response time (days from exposure alert to first lift). Those are engineering specifications, not aspirations. The controlled-motion framework's contribution to the political economy of recovery is exactly this: it turns "this is important" into "this is what is required."

---

# §14 RECOMMENDATIONS

The recommendations below are ordered by the logic established in this report, not by convention. The threat is active and episodic (§D.2, §F); everything that can be destroyed before capacity exists to respond will be destroyed. The ordering principle is therefore: first, reduce the probability of undetected loss; second, build the capacity that converts detection into action; third, use that capacity for the science. Recommendations within each tier are sequenced by dependency — earlier items are preconditions for later ones.

Each recommendation is linked to the specific evidence that justifies it. The aim is a specification, not a wish list.

---

## §14.1 Tier 1 — Immediate: monitoring and trigger protocol

These actions do not require recovery infrastructure and should begin regardless of the state of planning for everything else. Their purpose is to ensure that the next exposure event is detected, characterised, and responded to on the available timescale rather than after the fact.

**R1. Real-time seabed monitoring at all three sites.**
Deploy a network of seabed-level sensors — current meters, turbidity loggers, acoustic profilers — at Sites 1, 2, and 3. Instrument each site independently; the three sites are within the same storm cell but their sand regimes are not identical (Site 3 has the greatest sand cover, sheltered by the headland; Site 2 is the smallest signature and probably the most exposed in its local context). The instruments detect the onset of sand stripping in real time, triggering the response protocol (R3 below). Without this, standing capacity (R7–R9) cannot be activated on a timescale that matters.
*Basis: §D.2 (metastable equilibrium) and §F (the clock starts at sand lift). The critical time window — exposure to irreversible damage — is days to weeks (§13.5). Monitoring is the mechanism that starts the clock.*

**R2. Photogrammetric baseline survey of all three sites.**
A full stereophotogrammetric survey of Sites 1, 2, and 3 at their current exposed state, establishing metric reference geometry for every visible feature. This creates the baseline against which change can be measured — an exposure event detected by R1 can be compared against this baseline to determine what has changed, where, and at what rate. It also provides the geometric control frame for any recovery or excavation operation.
*This needs to happen now, before the next stripping event. It is the cheapest action in this list relative to its value.*

**R3. Written trigger protocol agreed with the National Monuments Service.**
A pre-approved, tested protocol specifying: (a) the sensor thresholds that constitute a trigger event; (b) the named individuals and agencies contacted within the first hour; (c) the sequence of actions from first alert to first diver in the water; (d) the authority to invoke emergency recovery if the exposed material is at risk of imminent destruction. The protocol requires no infrastructure to write; it requires only that the relevant parties — NMS, the site licensee, the proposed institute, the local dive team — have agreed the sequence in advance rather than negotiating it under time pressure during a storm aftermath.
*Basis: §F ("reactive response guarantees loss"). A response protocol that is improvised after a trigger event is not a protocol; it is a sequence of phone calls under duress.*

*Community monitoring note:* The heritage and community organisations based in Grange, Co. Sligo, are the most proximately-located observers for Streedagh Strand — closer to the site than any institutional partner. The trigger protocol should incorporate named contacts within these groups as a first-alert layer, formalising a role that community engagement has demonstrated is viable. This does not substitute for instrument-based monitoring (R1) but extends its reach to the periods and conditions between automated readings.

---

## §14.2 Tier 2: Survey and targeted excavation

These actions generate the scientific return and provide the data to refine the model. They require some capacity (dive team, recording equipment, at minimum a conservation plan for anything lifted) but not the full recovery infrastructure of Tier 3.

**R4. High-resolution magnetometry re-survey and sub-bottom profiling of all three sites.**
A modern re-survey with higher spatial resolution than the existing data, combined with parametric echo-sounder sub-bottom profiling to determine sediment thickness above the principal artefact horizon at each site. The existing magnetometry established the footprint of each site (165×40 m at Site 1, 270×72 m at Site 3); the new survey should resolve internal structure — the gradient between the dense central mound (ballast) and the more diffuse peripheral scatter (dispersed cargo release) — and constrain burial depth. Burial depth is the primary determinant of how much time the response window contains: 0.5 m of sand over an articulated timber horizon gives days; 2 m gives weeks.
*This survey should be treated as precondition for R5; you do not excavate without knowing the depth to target.*

**R5. Targeted excavation at Site 1: the ballast mound and its seaward face.**
A small, carefully planned excavation targeting the lowest stratigraphic horizon immediately adjacent to and seaward of the Site 1 ballast mound. The model (§13.2) predicts that the siege-train ordnance is here — directly above the ballast, in primary stowage context — and that this material has never been disturbed. The excavation has three possible outcomes, all scientifically valuable:

- *Positive:* siege guns and associated field-artillery equipment found in situ. Confirms the model; creates the primary recovery task for Tier 3 infrastructure; definitively establishes Juliana as the siege-train carrier.
- *Negative — material absent:* guns not present at the predicted location. Constrains the model significantly (hull may have been breached before burial, allowing guns to sink clear of the structure); redirects the search to the dispersed iron periphery.
- *Negative — below current penetration depth:* material present but below the excavation's reach. Establishes the burial depth and informs the sub-bottom profiling interpretation; confirms the material is there and protected.

Any iron ordnance encountered must have a conservation plan in place before the excavation begins — iron guns in primary burial context are highly susceptible to mechanical and chemical damage during extraction.

**R6. Timber condition sampling at Site 1.**
Small-core sampling of the articulated timbers already known from Site 1, using standard dendrochronology and wood-density protocols, to assess the state of preservation of the oak. The sample yields: (a) a degradation index (residual density as fraction of reference density) that gives the conservation chemistry baseline; (b) dendrochronological data that may resolve construction provenance (Mediterranean oak has characteristic ring patterns distinguishable from Atlantic European oak); (c) the oak species, cross-checking the Martin 1984 Valencera data (solid-framed oak throughout).
*Basis: §13.5 (the conservation treatment required depends on the degradation state; the Mary Rose figures are a ceiling, not an assumed parameter). The sample must be small enough not to disturb the in-situ archaeology and large enough to run the full diagnostic suite.*

---

## §14.3 Tier 3: Recovery infrastructure

These are the medium-term physical and institutional requirements. They are stated here as specifications derived from the report's parameters, so that infrastructure planning begins from evidence rather than from analogues.

**R7. Sligo quay facility — engineering specification.**
The proposed recovery facility at Sligo quay should be specified against the following parameters derived from this report:

| Parameter | Value | Basis |
|---|---|---|
| Maximum single lift (crane) | 50 t minimum; 80 t desirable | Hull section + in-place ballast (§B.3, §13.5) |
| Crane reach from quay edge | ≥ 15 m | Deck-to-water working geometry |
| Conservation tank volume (initial phase) | ≥ 200 m³ waterlogged capacity | ~50–100 t timber at 900–1000 kg/m³ density |
| Tank environment | Active humidity control; consolidant injection capability | Waterlogged oak deteriorates on exposure; cannot dry before treatment |
| Response time from trigger (R1) to first lift | ≤ 5 days | Storm-exposure damage window (§13.5) |
| Site proximity | Sligo Bay; berthing for crane barge and support vessels | Site is 3–4 km offshore Streedagh Strand |

These are minimum specifications for a functional response capability. The facility should be designed to scale: Phase 1 handles individual artefact recovery and single hull sections; Phase 2 (should a major hull section recovery be attempted) may require a ship hall on the Mary Rose model.

**R8. Conservation laboratory at the proposed marine archaeology institute (ATU/Sligo).**
The quay facility handles the immediate recovery and immersion of large timber. The institute's conservation laboratory handles the subsequent treatment programme: chemical stabilisation (PEG impregnation or equivalent), drying, and permanent storage or display. The laboratory specification depends on the timber condition data from R6, but should be designed to accommodate:
- At least 50 t of waterlogged timber in active treatment at any one time
- Instrumented drying chambers (temperature and humidity controlled)
- Space for artefact processing (metal, ceramic, organic)
- A documented chain of custody linking field recovery → immersion → laboratory treatment → long-term storage

**R9. Resident expertise programme.**
The Tier 3 infrastructure is inert without the people to operate it. The response protocol (R3) names individuals; those individuals must have the specific competence to make decisions under time pressure about fragile, irreplaceable material. The programme should:
- Establish a post (or posts) in maritime archaeology and underwater conservation resident at ATU or equivalent, with the Streedagh complex as a primary research focus
- Build a licensed dive team with documented competence in excavation and artefact recording in the Streedagh environment specifically (not generic recreational dive certification)
- Provide a structured pathway for training in waterlogged-timber conservation, drawing on existing expertise at the NMI, the Mary Rose Trust, or equivalent

*Basis: §F ("resident expertise, based in Sligo, at the site") and §13.5. The point is not expertise in the abstract but expertise within response range. A specialist in Dublin who cannot reach the site in 48 hours is not part of the response capability.*

---

## §14.4 Tier 4: Research programme and interpretation

These recommendations generate the full scientific return from the site and connect its findings to the wider public. They depend on Tiers 1–3 being operational; they cannot substitute for them.

**R10. Levant squadron comparative programme.**
The three Streedagh hulls are most fully interpretable against the other Levant-squadron wrecks. La Trinidad Valencera (Donegal) is the directly comparable site — same squadron, same class of vessel, different preservation environment (hard seabed vs sand). A structured comparative programme between Streedagh and Valencera would test the model across environments, compare cargo assemblages (the Valencera's field-artillery material provides the template for what the Streedagh siege tier should look like), and begin to reconstruct the full logistical picture of all ten ships rather than isolated vessels.
The San Juan de Sicilia (Tobermay Bay, Scotland) and the largely unlocated La Rata Coronada, La Anunciada, and San Nicolás Prodaneli are additional comparators at varying stages of investigation. A fleet-level programme treating the Levant squadron as a single distributed site — managed from multiple national jurisdictions — would represent a significant contribution to early-modern maritime archaeology beyond the Irish context.

**R11. Archival research programme to support the deferred historical sections.**
The deferred sections (§2, §4) cannot be written from existing sources alone. Specific archival gaps:
- Individual ship histories for Juliana, Lavia, Visón from the Archivo de la Corona de Aragón and Archivo General de Simancas — the Catalan archival record for Juliana (via Antoni Martí i Coll) is the current source but should be formally incorporated with full citation
- Resolution of the de Cuéllar/Terceira question (flagged at C.2): whether de Cuéllar's "Terceira" reference is the 1582 naval action or the 1583 amphibious landing, and whether Juliana was present at either
- The O'Sullivan Beare / Fourteen Years' War / Fifteen Years' War chronology for the foreclosure model (D.2): the standard framing dates the war from 1593 (Nine Years' War proper) but O'Sullivan Beare's dating from 1588 is the operative one for the salvage-foreclosure argument; this needs to be sourced and stated precisely
- The 1985 discovery and subsequent salvage dispute documentation, for the history of investigation (§4)

**R12. Public interpretation — connecting parameters to people.**
The report's physical parameters (displacement, timber mass, surviving bronze) are the foundations; the public interpretation layer translates them into the experience of the people who were on these ships. The de Cuéllar account — a survivor's narrative from La Lavia, the vice-flagship — is the natural entry point: a named individual whose experience can be walked through the physical evidence. De Cuéllar names the ships, names the date, gives the number of dead (over 1,000), and describes the wreck event in enough detail that specific passages can be matched against specific physical features of the site.

The proposed interpretive centre at Streedagh should draw explicitly on the quantitative framework as well as the narrative: what 860 toneladas means in concrete terms (the displacement figure, the dimensions, the comparison with the Galeón Andalucía replica that visited in 2015), how the carriage wheels connect to the documented siege train, what the magnetometry footprints look like and why their dimensions match the model. The aim is to give the public the same forensic satisfaction that the archaeological method provides: working backwards from what is found to what was there.

The community heritage organisations based in Grange, Co. Sligo, have made the case for interpretation and display at the village level for years, and have been directly instrumental in raising the site's public profile. The argument made in this report — that the primary conservation and research infrastructure should be anchored at Sligo — is complementary to, not in competition with, that aspiration. Sligo infrastructure enables the Grange gateway rather than displacing it: artefacts conserved in Sligo are the natural source for rotation loans to a Grange interpretive facility; Grange, as the settlement physically closest to the strand, is the self-evident access point for visitors approaching from the sea-side; and community organisations in Grange are the appropriate partners for community archaeology, outreach, and the standing monitoring role that R1 and R3 depend on. A Grange facility positioned as the gateway to the site and as the locus of community-facing interpretation is more achievable, not less, if the heavy infrastructure is properly specified and built at Sligo first.

*The war-grave dimension (§B.4) must be present throughout public interpretation — quantitative and commemorative registers held together, not sequenced.*

---

## §14.5 Priority summary

| Tier | Recommendations | Dependency | Timeline |
|---|---|---|---|
| 1 — Immediate | R1 monitoring, R2 baseline survey, R3 trigger protocol | None | Now |
| 2 — Survey/excavation | R4 re-survey, R5 targeted excavation (Site 1), R6 timber sampling | R2 for geometry; R4 before R5 | 1–3 years |
| 3 — Infrastructure | R7 quay facility spec, R8 conservation lab, R9 resident expertise | R6 informs R8; R7/R9 enable R5 at scale | 2–5 years |
| 4 — Research/interpretation | R10 comparative programme, R11 archival, R12 public interpretation | Tier 3 operational for R10; R11 can begin now | 3–10 years |

One priority overrides the table: if a major sand-stripping event exposes articulated hull structure at any of the three sites before Tier 3 infrastructure exists, the response must still happen. That means R3 (the trigger protocol) and whatever emergency conservation capacity the NMS and NMI can mobilise must be agreed and tested *in advance* of R7–R9 being built. The infrastructure is the permanent solution; the protocol is the interim bridge. Both are required.

---

# PART G — DEFERRED SECTIONS (to be written once parameters are fixed)

- **[DEFERRED] §2 Historical Context** — Spanish Armada; strategic objectives; the Levant squadron; the final voyage; documentary sources (Spanish, English, de Cuéllar, Admiralty, modern research). *Written last, per method.*
- **[DEFERRED] §3 Environmental Context (detail)** — geology, full sediment dynamics, the wave/current/tide/storm regime quantified. *We have the qualitative regime (§D); the quantitative environmental data is a data-collection task.*
- **[DEFERRED] §4 History of Investigation** — 1985 discovery and salvage dispute; 1987 carriage-gun observation; 2015 rescue excavation; conservation programme; publications.
- **[DEFERRED] §5 Methodology (formal)** — to be written up from the methods already used (documentary, GIS, geophysics, diver investigation, photogrammetry, artefact/timber recording, conservation assessment) plus our reconstruction methods (§A.2).
- **[DRAFTED] §13 Discussion** — see above. Five subsections: §13.1 predictive test of the framework; §13.2 the buried resource (what remains and where); §13.3 three hulls as one system; §13.4 failure analysis and site-formation implications; §13.5 the capacity argument grounded in physics.
- **[DRAFTED] §14 Recommendations** — see above.
- **[DEFERRED] References / Appendices** — incl. Appendix E (hull reconstruction) and Appendix F (cargo estimates) = our model write-ups and code.

---

# PART H — MAPPING: OUR WORK PRODUCTS → REPORT SECTIONS

| Work product / dataset | Feeds (this draft) | Conventional template § |
|---|---|---|
| `streedagh_hull.py` + notes | B.1, A.2 | §6, §10, App. E |
| `streedagh_manifest.py` + notes | B.3 | §8, §9.3, App. F |
| `streedagh_guns.py` (armament model) | B.2 | §8, §9.2 |
| `juliana_guns.py` (calibrated bronze) | B.2 | §8, §9.2 |
| `streedagh_HEADLINE.md` (consolidated) | B.1–B.4 | Executive Summary |
| Ridella et al. 2016 (San Giorgio) | B.2 (calibration + salvage mechanism) | §8, §9, §13 |
| Birch & McElvogue 1999 | D.1, B.2, §4 | §4, §6, §7 |
| Moore/Brady/Kelleher 2015; McElvogue 2002 | B.2, §4 | §4, §8 |
| Site magnetometry (Sites 1–3) | B.3 (iron cross-check), D.1 | §3, §7 |
| Complement / de Cuéllar | B.4 | §2, §11, §12 |
| Fifteen-Years'-War framing | D.2 | §2, §7 |

---

*End of working draft. Revision 2026-07-01: (1) B.1 table corrected — Lavia DW 588 t, Visón DW 538 t, all columns now carry 5th–95th bands; (2) B.2 gun count clarified — 12 Juliana + 1 Visón esmeril = 13 fleet total; armament mass table with bands added; (3) B.3 now carries per-ship breakdown table and a new structural-timber subsection (facility-planning parameter, 352 t at 1/3 survival combined); (4) C.1 expanded from outline to full 4-paragraph draft using Martin 1984 Appendix 4 — full Levant Squadron Order of Battle table, Venetian requisition documented, 80% loss rate, siege-train loading confirmed; (5) §13 Discussion written in full (five subsections); (6) §14 Recommendations written in full (four tiers, twelve recommendations); (7) duplicate streedagh_HEADLINE(1).md deleted; (8) Makefile updated with report_data and figures targets; (9) Grange community heritage organisations named in Part E, R3, and R12 — gateway argument articulated. Remaining: report_data.py complete and verified; armada_figures.py; §2/3/4/5 deferred sections.*
