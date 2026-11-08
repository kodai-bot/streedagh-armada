"""
What went to the bottom at Streedagh on the wreck day: the mass budget, layer by layer.

    .venv/bin/python 1_signal_field/seabed_mass_budget.py        (or: make mass)

Layer 1 (this script, now): ORDNANCE AND MUNITIONS, per ship and combined: guns, shot, powder,
lead and match. It is built from stated counts (the Lisbon muster, 9 May 1588) times unit
masses that are themselves sourced, with every assumption a named prior.

Layer 2: THE WHOLE SHIP, from the measured dimensions (AGS GA 223/28 via Martin 1984 App. 11;
Juliana from the v0.7 §28.2 envelope). A hull-form model gives the displacement on the day;
the ballast is scaled from the Santa Maria de la Rosa's excavated mound; the stores come from
Medina Sidonia's ration scale; the people are taken out (the site is a war grave, and the dead
are not counted as mass). What is left of the displacement after the named loads is split into
hull, rig and metal, and the residue is reported, not hidden. Last, each part is divided into
what went to the seabed that day and what floated to the strand (Cuellar's timber-covered beach).

Why not the earlier figure (~601 t durable, site assessment v2 L3.2)? It came from the v1
model, which went from wartime toneladas to displacement. v0.7 §2 retires that chain:
toneladas are an administrative rating, not a mass. Here a mass only enters from a count or a
weight with a stated unit.

Sources (page numbers are Martin's own; scan markers sit at the top of each page):
  Martin 1984 p. ix      libra = 460 g; quintal = 100 libras
  Martin 1984 pp. 114-115 guns of the five ships from Sicily (Levant squadron), by class and
                          calibre in libras (AGS GA 221/39, 26 Sep 1587)
  Martin 1984 p. 371      Trinidad de Escala [77], 22 guns: 35 + 21 + 38 shots fired on
                          2, 4 and 8 August 1588
  Martin 1984 App. 4      Lisbon muster: guns, shot, powder, lead, match per ship
  Martin 1984 App. 11     the six ships' measured dimensions and ratings (p. 411); what the
                          three measures are (p. 409)
  Martin 1984 p. 130      La Trinidad Valencera's normal draught "in the order of four metres"
  Martin 1984 p. 139      Santa Maria de la Rosa, 945 tons
  Martin 1984 p. 150      the Rosa's ballast mound, 30 x 12 m, 0.75 m deep: "about 90 tonnes"
  Martin 1984 p. 174      Girona's draught about 4.5 m
  Martin 1984 p. 217      San Juan de Sicilia's 28 ft rudder: draught about 20 ft
  Martin 1984 pp. 349-50  the daily ration (Instructions to Shipmasters, Lisbon, 21 April 1588)
  Ridella et al. 2016     Juliana's recovered guns by weight mark (juliana_guns.csv)

Writes output/mass_budget_report.md and output/mass_budget.json.

Every prior is drawn once per draw and shared by the three ships (one shipbuilding tradition,
one squadron, one storm): the open questions are systematic, so the combined interval must not
narrow by averaging three independent errors.
"""

import csv
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "output")
N = 100_000
SEED = 20261107

LIBRA_KG = 0.460                 # Martin p. ix
QUINTAL_KG = 100 * LIBRA_KG      # 46.0 kg
CODO_M = 33 / 48 * 0.8359        # 0.57468125 m (v0.7 §27-28; Martin p. 409 prints 547.7 mm, an arithmetic slip)

SHIPS = {"La Juliana": "Juliana", "La Lavia (almiranta)": "Lavia", "Santa Maria de Vison": "Vison"}

# ── priors (HYPOTHESIS unless marked) ─────────────────────────────────────────
PRIORS = {
    "shot_fired_frac": ((0.03, 0.20), "uniform. Trinidad de Escala, a Levanter of 22 guns, fired 94 shots in "
                        "three actions (Martin p. 371): 94 / (22 x 50) = 8.5% of a 50-per-gun issue. Widened "
                        "for actions not recorded"),
    "powder_used_frac": ((0.05, 0.40), "uniform. Powder also fed the arquebuses and muskets, so it went faster "
                         "than great shot; no ship's record of it is held"),
    "lead_used_frac": ((0.0, 0.30), "uniform. Lead was cast into small-arms bullets as needed"),
    "match_used_frac": ((0.05, 0.40), "uniform. Match burns whenever guns or arquebuses stand ready"),
    "unitemised_gun_t": ((0.35, 0.55, 1.20), "triangular (min, mode, max) tonnes per gun not itemised. Mode = mean "
                         "of Juliana's nine recovered guns (0.55 t); max widened because the Levant list includes "
                         "16-19 lb medios canones and the recovered sample is the light, accessible tier. "
                         "Drawn once per draw and shared by all three ships (systematic, not per gun)"),
}

# ── layer 2 ───────────────────────────────────────────────────────────────────
RHO_SEA = 1.025                  # t/m3
AZUMBRE_L = 2.016                # Castilian azumbre in litres: the standard metrological equivalence, not from Martin
CUARTILLO_L = AZUMBRE_L / 4
ROSA_TONELADAS = 945             # Martin p. 139
ROSA_BALLAST_T = 90.0            # Martin p. 150: mound 30 x 12 m, 0.75 m deep, "about 90 tonnes" in air
WAR_FIFTH = 1.2                  # toneladas = machos + one fifth (App. 11; verified in ratings_check)
MACHOS = {"Juliana": 860 / WAR_FIFTH, "Lavia": 607.125, "Vison": 472.0}   # Juliana: v0.7 §26, 716.7 derived
# siege train and army stores carried as cargo, tonnes (lo, hi). Valencera's issue of May 1588 (Martin pp. 115-116):
# 3 battery cannon on sea carriages, 6 field-carriage sets and limbers, 190 quintals of powder (8.7 t), 400 iron
# balls of 40 libras (7.4 t), platforms, hoists, wheel parts: some 30-50 t. Juliana's five 1.5 m spoked wheels show
# she carried part of the train (site assessment v2 §2), so her floor is above zero.
CARGO_T = {"Juliana": (10.0, 60.0), "Lavia": (0.0, 60.0), "Vison": (0.0, 60.0)}
CAPACITY = os.path.join(HERE, "..", "2_reconstruction", "output", "capacity.json")

# (distribution, params, basis). All HYPOTHESIS except where a page is cited as the constraint.
PRIORS2 = {
    "lwl_over_esloria": ("uniform", (0.815, 0.95), "esloria is the main-deck length from stem to sternpost (Martin "
                         "p. 409). The waterline lies between that and the keel, which Martin takes as 53/65 of the "
                         "esloria for Lavia, after Veitia Linage's 700-ton galleon (App. 1 n. 5, p. 506)"),
    "bwl_over_manga": ("uniform", (1.00, 1.08), "manga is the beam taken internally at midships (p. 409); add frames "
                       "and planking on both sides, less any narrowing at the waterline"),
    "normal_draught_over_puntal": ("uniform", (0.65, 0.95), "the draught fully laden. Puntal runs from under the main deck to the bottom of the hold "
                            "(p. 409). Martin's draughts: Valencera about 4 m normal (p. 130), Girona about 4.5 m "
                            "(p. 174), San Juan de Sicilia about 20 ft from her 28 ft rudder (p. 217). For Lavia's "
                            "6.18 m puntal this range gives 4.0-5.9 m"),
    "block_coeff": ("uniform", (0.45, 0.62), "full-bodied Mediterranean merchant hulls; no lines survive. The rating "
                    "formula's own (M/2) x 0.97 treats the hold as 0.485 of its box: a hint, not evidence"),
    "lightship_frac": ("uniform", (0.35, 0.55), "hull, rig, ground tackle and fittings as a share of the fully laden "
                       "displacement. No surviving figure for these hulls: the leading open question (see drivers)"),
    "rig_share": ("uniform", (0.08, 0.15), "masts, yards, sails and cordage as a share of the lightship"),
    "metal_share": ("uniform", (0.04, 0.10), "iron in the lightship: bolts and fastenings (these Levant hulls were "
                    "iron-fastened, Martin p. 217), anchors, chain-plates, galley ironwork"),
    "ballast_scale": ("uniform", (0.6, 1.5), "multiplies the Rosa's 90 t (p. 150) at 945 toneladas (p. 139), scaled "
                      "by machos as a volume proxy. Wide: the mound is what survived, and ballasting varied"),
    "cargo_u": ("uniform", (0.0, 1.0), "position in each ship's cargo range (CARGO_T), shared: siege train and "
                "army stores beyond the ship's own munitions"),
    "liquid_days": ("uniform", (0.0, 15.0), "days of wine and water left. Six months' rations at Lisbon, replenished "
                    "at Corunna, 50% wastage allowed; it was the unintended voyage home without water that caused "
                    "the privations (p. 349). The ships had put in to the Irish coast"),
    "solid_days": ("uniform", (10.0, 60.0), "days of biscuit, meat, fish, cheese, pulses, oil left (same basis)"),
    "cask_tare": ("uniform", (0.10, 0.25), "cask mass as a share of the liquid it holds (Valencera's restored pipa "
                  "held about 591 l, p. 351)"),
    "person_t": ("uniform", (0.060, 0.075), "one person with clothing, in tonnes. In the displacement, not in the "
                 "seabed mass"),
    "arms_kg_per_soldier": ("uniform", (6.0, 14.0), "arquebus or musket, morion, sword, bandolier, share of pikes"),
    "timber_retained": ("uniform", (0.25, 0.60), "share of hull timber that stayed on the seabed: the lower hull under "
                        "the ballast (anchors and guns lie over the Site 1 concretion; the rudder over a gun), while "
                        "castles, decks and upper works broke up and drove ashore (Cuellar's strand of timber)"),
    "rig_retained": ("uniform", (0.10, 0.50), "masts and spars float; wet cordage and sails partly sink with the wreck"),
    "stores_retained": ("uniform", (0.20, 0.80), "full casks sit near neutral buoyancy; biscuit dissolves"),
    "cargo_retained": ("uniform", (0.50, 1.00), "siege cargo is mostly dense (battery guns, shot, ironwork); the "
                       "wheels, planks and baulks float"),
}

# daily ration, Martin pp. 349-350: 1 1/2 libras biscuit; 1/3 azumbre wine; 3 cuartillos water; plus on set days
# 6 onzas bacon + 2 rice, 6 cheese + 3 beans, 6 fish, 1 1/2 oil + 1/4 cuartillo vinegar. Averaged over the week
# the extras come to about 0.2 kg a day (onza = libra / 16).
ONZA_KG = LIBRA_KG / 16
LIQUID_KG_DAY = (AZUMBRE_L / 3 + 3 * CUARTILLO_L) * 1.0                       # wine + water, ~2.18 kg
SOLID_KG_DAY = 1.5 * LIBRA_KG + ONZA_KG * (2 * (6 + 2) + 2 * (6 + 3) + 1 * 6 + 2 * 1.5) / 7   # ~0.86 kg


def draw2(rng, k):
    dist, prm, _ = PRIORS2[k]
    return rng.uniform(*prm, N)


def dims_m(ship, rng_u):
    """(esloria, manga, puntal) in metres. Lavia and Vison measured; Juliana inside the v0.7 §28.2 envelope,
    one shared position per draw so the three dimensions scale together."""
    if ship == "Juliana":
        env = json.load(open(CAPACITY, encoding="utf-8"))["juliana"]["envelope"]
        lo, hi = np.array(env["low"]), np.array(env["high"])
        return [lo[i] + rng_u * (hi[i] - lo[i]) for i in range(3)]
    name = {"Lavia": "La Lavia Beneziana", "Vison": "Santa Maria de Vison"}[ship]
    r = next(r for r in read("ship_ratings_1588.csv") if r["ship"] == name)
    return [np.full(N, float(r[k]) * CODO_M) for k in ("esloria_codos", "manga_codos", "puntal_codos")]


def ranks(x):
    r = np.empty(N)
    r[np.argsort(x)] = np.arange(N)
    return r


# ferrous mass on the seabed (for the magnetometry comparison). Drawn from a separate generator so that
# adding it leaves every layer 1 and layer 2 figure above unchanged.
PRIORS_FE = {
    "iron_gun_mass_share": ((0.20, 0.50), "share of gun mass in cast or wrought iron. The Sicilian ships' list is 145 "
                            "iron pieces of 271 (Martin pp. 114-115), but mostly the light classes; Juliana's nine "
                            "recovered guns are all bronze"),
    "cargo_iron_share": ((0.15, 0.40), "iron in the siege cargo: the Valencera's issue included 400 iron balls of 40 "
                         "libras (7.4 t) besides wheel irons and fittings, beside bronze battery guns (pp. 115-116)"),
}


RAW = {}                                 # combined draws of the last layer2() run


def layer2(rng, muster, l1, stone_frac):
    P = {k: draw2(rng, k) for k in PRIORS2}
    rfe = np.random.default_rng(SEED + 1)
    PF = {k: rfe.uniform(*v[0], N) for k, v in PRIORS_FE.items()}
    u_jul = rng.uniform(0, 1, N)
    out, tot, raw = {}, {}, {}
    for ship, r in muster.items():
        E, M, D = dims_m(ship, u_jul)
        lwl, bwl = E * P["lwl_over_esloria"], M * P["bwl_over_manga"]
        t_per_m = RHO_SEA * P["block_coeff"] * lwl * bwl           # tonnes per metre of draught (prismatic)
        T_full = D * P["normal_draught_over_puntal"]
        full = t_per_m * T_full                                    # fully laden displacement
        light = full * P["lightship_frac"]                         # the hull is fixed; loads vary
        rig, metal = light * P["rig_share"], light * P["metal_share"]
        timber = light - rig - metal
        men = int(r["soldiers"]) + int(r["seamen"])
        people = men * P["person_t"]
        ordn = l1[ship]["total"]
        ballast = ROSA_BALLAST_T * MACHOS[ship] / (ROSA_TONELADAS / WAR_FIFTH) * P["ballast_scale"]
        stores = men * (P["liquid_days"] * LIQUID_KG_DAY * (1 + P["cask_tare"]) + P["solid_days"] * SOLID_KG_DAY) / 1000
        arms = int(r["soldiers"]) * P["arms_kg_per_soldier"] / 1000
        lo, hi = CARGO_T[ship]
        cargo = lo + P["cargo_u"] * (hi - lo)
        on_board = light + ordn + ballast + stores + arms + cargo   # everything but the people
        day = on_board + people                                    # displacement on the wreck day
        T_day = day / t_per_m
        # check: the loading at the May muster (six months' rations, Martin p. 349; munitions as mustered)
        may = (light + l1[ship]["mustered"] + ballast + arms + cargo + people
               + men * 180 * (LIQUID_KG_DAY * (1 + P["cask_tare"]) + SOLID_KG_DAY) / 1000)
        seabed = (ordn + ballast + arms + metal + cargo * P["cargo_retained"] + timber * P["timber_retained"]
                  + rig * P["rig_retained"] + stores * P["stores_retained"])
        g, sh = l1[ship]["guns"], l1[ship]["shot"]
        ferrous = (g * PF["iron_gun_mass_share"] + sh * (1 - stone_frac) + metal
                   + cargo * P["cargo_retained"] * PF["cargo_iron_share"])
        parts = {"displacement_full": full, "displacement_day": day, "draught_full_m": T_full,
                 "draught_day_m": T_day, "people": people, "on_board_excl_people": on_board,
                 "ordnance_munitions": ordn, "ballast": ballast, "stores": stores, "personal_arms": arms,
                 "cargo": cargo, "hull_timber": timber, "rig": rig, "metal_fittings_anchors": metal,
                 "to_seabed": seabed, "to_strand": on_board - seabed, "displacement_may": may,
                 "ferrous_to_seabed": ferrous, "timber_to_seabed": timber * P["timber_retained"],
                 "cargo_to_seabed": cargo * P["cargo_retained"], "guns_to_seabed": g, "lead_to_seabed": l1[ship]["lead"]}
        out[ship] = {k: q(v) for k, v in parts.items()}
        out[ship]["may_over_full"] = {k: round(v / 1000, 3) for k, v in q(may / full * 1000).items()}
        out[ship]["overladen_frac"] = round(float((day > full).mean()), 3)
        out[ship]["seabed_share_of_on_board"] = q(seabed / on_board * 1000)
        out[ship]["seabed_share_of_on_board"] = {k: round(v / 1000, 3) for k, v in out[ship]["seabed_share_of_on_board"].items()}
        out[ship]["men"] = men
        out[ship]["dims_m_median"] = [round(float(np.median(x)), 2) for x in (E, M, D)]
        for k, v in parts.items():
            if not k.startswith("draught"):
                tot[k] = tot.get(k, 0) + v
        raw[ship] = seabed
    out["Combined"] = {k: q(v) for k, v in tot.items()}
    RAW.clear()
    RAW.update(tot)                      # the combined draws, for museum_capacity.py
    # which priors drive the combined seabed mass: Spearman rank correlation
    rs = ranks(tot["to_seabed"])
    drivers = {k: round(float(np.corrcoef(ranks(v), rs)[0, 1]), 3) for k, v in P.items()}
    drivers["juliana_envelope_position"] = round(float(np.corrcoef(ranks(u_jul), rs)[0, 1]), 3)
    drivers = dict(sorted(drivers.items(), key=lambda kv: -abs(kv[1])))
    return {"ships": out, "drivers": drivers,
            "priors_ferrous": {k: {"dist": "uniform", "params": v[0], "basis": v[1]} for k, v in PRIORS_FE.items()},
            "constants": {"rho_sea": RHO_SEA, "azumbre_l": AZUMBRE_L, "rosa_toneladas": ROSA_TONELADAS,
                          "rosa_ballast_t": ROSA_BALLAST_T, "machos": {k: round(v, 1) for k, v in MACHOS.items()},
                          "liquid_kg_day": round(LIQUID_KG_DAY, 3), "solid_kg_day": round(SOLID_KG_DAY, 3)},
            "priors": {k: {"dist": v[0], "params": v[1], "basis": v[2]} for k, v in PRIORS2.items()}}



def read(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def q(x):
    """median and 5-95% interval, in tonnes, rounded."""
    p5, p50, p95 = np.percentile(x, [5, 50, 95])
    return {"median": round(float(p50), 2), "p05": round(float(p5), 2), "p95": round(float(p95), 2)}


def ratings_check():
    """Martin's 'three percent' formula on the measured dimensions: machos = (M/2) P E (1 - 0.03) / 8."""
    rows = []
    for r in read("ship_ratings_1588.csv"):
        m, p, e = float(r["manga_codos"]), float(r["puntal_codos"]), float(r["esloria_codos"])
        calc = m / 2 * p * e * 0.97 / 8
        rows.append({"ship": r["ship"], "manga_m": round(m * CODO_M, 2), "puntal_m": round(p * CODO_M, 2),
                     "esloria_m": round(e * CODO_M, 2), "machos_stated": float(r["machos"]),
                     "machos_calc": round(calc, 1), "martin_calc": int(r["martin_calc_machos"]),
                     "diff_pct": round(100 * (float(r["machos"]) - calc) / calc, 1),
                     "toneladas_stated": float(r["toneladas"]),
                     "toneladas_over_machos": round(float(r["toneladas"]) / float(r["machos"]), 3)})
    return rows


def shot_mass_kg(rng):
    """Mean mass of one round of great shot, drawn from the Levant list (50 shot were issued per gun)."""
    guns = read("levant_guns_1587.csv")
    n = np.array([int(g["count"]) for g in guns], float)
    lo = np.array([float(g["calibre_lb_lo"]) for g in guns])
    hi = np.array([float(g["calibre_lb_hi"]) for g in guns])
    stone = np.array([g["shot"] == "stone" for g in guns])
    cal = rng.uniform(lo, hi, size=(N, len(guns)))            # libras per ball, per class
    mean_kg = (cal * n).sum(1) / n.sum() * LIBRA_KG
    stone_frac = (cal * n * stone).sum(1) / (cal * n).sum(1)  # by mass
    return mean_kg, stone_frac, int(n.sum())


def main(write=True):
    rng = np.random.default_rng(SEED)
    muster = {SHIPS[r["ship"]]: r for r in read("lisbon_muster_1588.csv") if r["ship"] in SHIPS}
    rec = read("juliana_guns.csv")
    shot_kg, stone_frac, n_listed = shot_mass_kg(rng)
    u = lambda k: rng.uniform(*PRIORS[k][0], N)
    a, m, b = PRIORS["unitemised_gun_t"][0]
    gun_mean_t = rng.triangular(a, m, b, N)   # shared by all three ships: one squadron, one open question

    out, tot, arrays = {}, {}, {}
    for ship, r in muster.items():
        guns_n, shot_n = int(r["guns"]), int(r["shot"])
        if ship == "Juliana":
            known = sum(rng.uniform(float(g["mass_kg_low"]), float(g["mass_kg_high"]), N) for g in rec) / 1000
            n_unk = guns_n - len(rec)
        else:
            known, n_unk = np.zeros(N), guns_n
        # one mean per draw for all unitemised guns: the open question is whether the missing guns
        # as a group are light or heavy, not gun-to-gun scatter (which would average out)
        guns = known + n_unk * gun_mean_t
        shot = shot_n * (1 - u("shot_fired_frac")) * shot_kg / 1000
        powder = int(r["powder_qtx"]) * QUINTAL_KG * (1 - u("powder_used_frac")) / 1000
        lead = int(r["lead_qtx"]) * QUINTAL_KG * (1 - u("lead_used_frac")) / 1000
        match = int(r["match_qtx"]) * QUINTAL_KG * (1 - u("match_used_frac")) / 1000
        parts = {"guns": guns, "shot": shot, "powder": powder, "lead": lead, "match": match}
        parts["total"] = sum(parts.values())
        # what can survive 400 years in sand: bronze/iron guns, iron and stone shot, lead
        parts["durable"] = guns + shot + lead
        out[ship] = {k: q(v) for k, v in parts.items()}
        arrays[ship] = dict(parts, mustered=guns + shot_n * shot_kg / 1000
                            + (int(r["powder_qtx"]) + int(r["lead_qtx"]) + int(r["match_qtx"])) * QUINTAL_KG / 1000)
        out[ship]["as_mustered"] = {"guns": guns_n, "shot": shot_n, "powder_t": round(int(r["powder_qtx"]) * QUINTAL_KG / 1000, 2),
                                    "lead_t": round(int(r["lead_qtx"]) * QUINTAL_KG / 1000, 2),
                                    "match_t": round(int(r["match_qtx"]) * QUINTAL_KG / 1000, 2),
                                    "guns_itemised": len(rec) if ship == "Juliana" else 0}
        for k, v in parts.items():
            tot[k] = tot.get(k, 0) + v
    out["Combined"] = {k: q(v) for k, v in tot.items()}

    l2 = layer2(rng, muster, arrays, stone_frac)
    result = {"layer": "1: ordnance and munitions; 2: the whole ship", "seed": SEED, "draws": N,
              "units": {"libra_kg": LIBRA_KG, "quintal_kg": QUINTAL_KG, "codo_m": CODO_M},
              "shot_mean_kg": q(shot_kg * 1000) | {"guns_in_list": n_listed},
              "stone_shot_mass_frac": q(stone_frac * 1000),
              "priors": {k: {"params": v[0], "basis": v[1]} for k, v in PRIORS.items()},
              "ships": out, "ratings": ratings_check(), "layer2": l2}
    # q() works in tonnes; the two lines above re-scale kg and fractions so the same helper rounds them
    for k in ("shot_mean_kg", "stone_shot_mass_frac"):
        for s in ("median", "p05", "p95"):
            result[k][s] = round(result[k][s] / 1000, 3)
    if not write:
        return result
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "mass_budget.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    with open(os.path.join(OUT, "mass_budget_report.md"), "w", encoding="utf-8") as f:
        f.write(report(result))
    c = out["Combined"]
    print(f"layer 1 (ordnance + munitions), combined: {c['total']['median']} t [{c['total']['p05']}-{c['total']['p95']}]; "
          f"durable {c['durable']['median']} t")
    c2 = l2["ships"]["Combined"]
    print(f"layer 2 (whole ship), combined to seabed: {c2['to_seabed']['median']} t [{c2['to_seabed']['p05']}-"
          f"{c2['to_seabed']['p95']}]; on board excl. people {c2['on_board_excl_people']['median']} t")
    for s_, d in l2["ships"].items():
        if s_ == "Combined":
            continue
        print(f"  {s_:8s} full {d['displacement_full']['median']:6.0f}  day {d['displacement_day']['median']:6.0f}  "
              f"T {d['draught_full_m']['median']:.1f}->{d['draught_day_m']['median']:.1f} m  light {d['hull_timber']['median']+d['rig']['median']+d['metal_fittings_anchors']['median']:5.0f}  "
              f"seabed {d['to_seabed']['median']:5.0f} [{d['to_seabed']['p05']:.0f}-{d['to_seabed']['p95']:.0f}]  overladen {d['overladen_frac']:.1%}  May/full {d['may_over_full']['median']:.2f} [{d['may_over_full']['p05']:.2f}-{d['may_over_full']['p95']:.2f}]")
    print("  drivers:", list(l2["drivers"].items())[:6])


def report(R):
    f = lambda d: f"{d['median']:.1f} [{d['p05']:.1f}–{d['p95']:.1f}]"
    L = ["# What went to the bottom at Streedagh", "", "## Layer 1: ordnance and munitions", "",
         "Generated by `seabed_mass_budget.py`. Tonnes, median [5th–95th percentile], "
         f"{R['draws']:,} draws, seed {R['seed']}.", "",
         "The muster of 9 May 1588 counts each ship's guns, shot, powder, lead and match. Counts become "
         "mass only through sourced units: the libra of 460 g and the quintal of 100 libras (Martin p. ix), "
         "the shot calibres of the Levant squadron's own guns (Martin pp. 114–115), and the weight marks on "
         "Juliana's recovered guns (Ridella et al. 2016). What was used up in the Channel is a prior, stated below.", "",
         "| Ship | guns | shot | powder | lead | match | **total** | durable (guns + shot + lead) |",
         "|---|---|---|---|---|---|---|---|"]
    for s, d in R["ships"].items():
        b = "**" if s == "Combined" else ""
        L.append(f"| {b}{s}{b} | {f(d['guns'])} | {f(d['shot'])} | {f(d['powder'])} | {f(d['lead'])} | "
                 f"{f(d['match'])} | **{f(d['total'])}** | {f(d['durable'])} |")
    L += ["", "As mustered (before the Channel fighting):", "",
          "| Ship | guns (itemised) | shot | powder t | lead t | match t |", "|---|---|---|---|---|---|"]
    for s, d in R["ships"].items():
        if s != "Combined":
            m = d["as_mustered"]
            L.append(f"| {s} | {m['guns']} ({m['guns_itemised']}) | {m['shot']} | {m['powder_t']} | {m['lead_t']} | {m['match_t']} |")
    sm, st = R["shot_mean_kg"], R["stone_shot_mass_frac"]
    L += ["", f"Mean mass of one round: **{sm['median']} kg** [{sm['p05']}–{sm['p95']}], from the "
          f"{sm['guns_in_list']} guns of the five Sicilian ships (calibres drawn uniformly within each class's "
          f"stated range). Stone shot is about {st['median']:.0%} of the shot mass (the pedrero classes); "
          "the rest is iron.", "",
          "## Priors (HYPOTHESIS)", "", "| Prior | values | basis |", "|---|---|---|"]
    for k, p in R["priors"].items():
        L.append(f"| {k} | {p['params']} | {p['basis']} |")
    L += ["", "## Not in this layer", "",
          "Hull timber, ballast, anchors and ground tackle, rig, provisions and water, the soldiers' "
          "personal arms, and cargo (Juliana's siege-carriage wheels): layer 2, below.", "",
          "The people are not counted as mass. The muster lists 976 soldiers and seamen on the three ships "
          "in May; Cuéllar says more than a thousand drowned, and the Lord Deputy reported 1,100 bodies "
          "counted along the strand (Martin p. 111). The site is a war grave.", "",
          "## The measured dimensions (AGS GA 223/28, Martin 1984 App. 11 p. 411)", "",
          f"Codo = 33/48 × 835.9 mm = {CODO_M:.5f} m. Martin's 'three percent' formula, "
          "machos = (manga / 2) × puntal × esloria × 0.97 / 8, recomputed here:", "",
          "| Ship | esloria m | manga m | puntal m | machos stated | machos by formula | diff % | toneladas / machos |",
          "|---|---|---|---|---|---|---|---|"]
    for r in R["ratings"]:
        L.append(f"| {r['ship']} | {r['esloria_m']} | {r['manga_m']} | {r['puntal_m']} | {r['machos_stated']:g} | "
                 f"{r['machos_calc']} | {r['diff_pct']:+} | {r['toneladas_over_machos']} |")
    same = all(round(r["machos_calc"]) == r["martin_calc"] for r in R["ratings"])
    L += ["", f"Recomputed values {'match Martin' + chr(39) + 's bracketed results in every row' if same else 'DIFFER from Martin' + chr(39) + 's brackets: check'}.",
          "", "The formula fits Lavia and Anunciada exactly and Visón within 2.4%; Regazona (+20%) and San "
          "Nicolás (+9%) do not fit (Martin p. 412 suspects 'more fundamental errors' there). Regazona's "
          "stated 1079 machos is one end of the v0.7 §28.2 interpolation for Juliana's dimensions, so that "
          "estimate inherits the misfit. The toneladas are the "
          "machos plus one fifth everywhere except Visón, whose 666 Martin emends to 566. Juliana is not "
          "in this document, so her dimensions stay inferred (reconstruction v0.7 §28.2).", ""]
    return "\n".join(L) + report2(R["layer2"], f)


def report2(R2, f):
    S = R2["ships"]
    c = S["Combined"]
    L = ["", "# Layer 2: the whole ship", "",
         f"**To the seabed on the wreck day, the three ships together: {f(c['to_seabed'])} t.** Of "
         f"{f(c['on_board_excl_people'])} t aboard (people excluded), the rest, {f(c['to_strand'])} t, was "
         "mostly timber, rig and casks that broke away and drove onto the strand.", "",
         "How it is built. The measured dimensions (Lavia, Visón) or the v0.7 envelope (Juliana) give, through "
         "a hull-form model, the displacement fully laden. The hull itself (lightship) is a share of that. On the "
         "wreck day the ship carried the lightship plus named loads, each from a source: layer 1's ordnance; "
         "ballast scaled from the Rosa's excavated mound (Martin p. 150); what was left of the stores, on Medina "
         "Sidonia's ration scale (pp. 349-350); the soldiers' arms; siege cargo (Valencera's issue list, "
         "pp. 115-116; Juliana's five carriage wheels). The draught on the day is then derived, not assumed. "
         "Each part is split into what stayed on the seabed and what floated off.", "",
         "| Ship | hull timber | rig | metal & anchors | ballast | ordnance (L1) | stores | arms | cargo | "
         "**on board** | **to seabed** | to strand |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s, d in S.items():
        b = "**" if s == "Combined" else ""
        L.append(f"| {b}{s}{b} | {f(d['hull_timber'])} | {f(d['rig'])} | {f(d['metal_fittings_anchors'])} | "
                 f"{f(d['ballast'])} | {f(d['ordnance_munitions'])} | {f(d['stores'])} | {f(d['personal_arms'])} | "
                 f"{f(d['cargo'])} | **{f(d['on_board_excl_people'])}** | **{f(d['to_seabed'])}** | {f(d['to_strand'])} |")
    L += ["", "The people are not in these figures. Their mass is in the displacement "
          f"({f(c['people'])} t for the {sum(S[k]['men'] for k in S if k != 'Combined')} mustered in May) "
          "and nowhere else.", "",
          "## Checks", "",
          "| Ship | dims used, m (esloria, manga, puntal) | laden displacement | laden draught m | wreck-day "
          "displacement | wreck-day draught m | May loading / laden | overladen draws |",
          "|---|---|---|---|---|---|---|---|"]
    for s, d in S.items():
        if s == "Combined":
            continue
        m = d["may_over_full"]
        L.append(f"| {s} | {', '.join(str(x) for x in d['dims_m_median'])} | {f(d['displacement_full'])} | "
                 f"{f(d['draught_full_m'])} | {f(d['displacement_day'])} | {f(d['draught_day_m'])} | "
                 f"{m['median']:.2f} [{m['p05']:.2f}–{m['p95']:.2f}] | {d['overladen_frac']:.1%} |")
    L += ["", "The consistency check is the May column. Put the May loading back aboard (six months' rations, "
          "Martin p. 349; munitions as mustered) and the ships come out close to the laden displacement that the "
          "hull model gives from their dimensions. The rations and the hull were not fitted to each other, so this "
          "is a real test of the priors, though not an independent one (both use lightship_frac). On the wreck "
          "day, with the stores mostly gone, they ride about a metre and a half above that line: light, with tall "
          "castles, the windage condition of v0.7 §9 near a lee shore.", "",
          "## Iron on the seabed (for the magnetometry)", "",
          "Ferrous mass to the seabed: iron guns, iron shot, metal fittings and anchors, iron in the siege cargo. "
          "Two extra priors (below), drawn from a separate generator so the figures above do not move.", "",
          "| Ship | ferrous to seabed, t |", "|---|---|"] + [
          f"| {s} | {f(d['ferrous_to_seabed'])} |" for s, d in S.items()] + ["",
          "Birch & McElvogue's magnetometer spreads (165 x 40, 15 x 10, 270 x 72 m) differ in area by a factor of "
          "about 130 where these masses differ by 1.5, so the spreads cannot be read as iron mass; see the site "
          "record, `inf:...magnetometry/spread-vs-mass`.", "",
          "| Prior | values | basis |", "|---|---|---|"] + [
          f"| {k} | uniform {p['params']} | {p['basis']} |" for k, p in R2["priors_ferrous"].items()] + ["",
          "## What drives the answer", "",
          "Spearman rank correlation of each prior with the combined seabed mass:", "",
          "| prior | rho |", "|---|---|"]
    for k, v in R2["drivers"].items():
        L.append(f"| {k} | {v:+.2f} |")
    L += ["", "So the seabed figure is mostly a question about the hull: how much of it stayed (timber_retained) "
          "and how heavy it was (lightship_frac), then the ballast. Each has a field test:", "",
          "- **Timber extent and depth** at Sites 1-3 (probing, sub-bottom profiling): how much lower hull lies "
          "under the ballast.",
          "- **The ballast mounds** themselves, measured as Martin measured the Rosa's (area x depth x packing).",
          "- **The Streedagh rudder's length**, read as Martin read the Tobermory rudder (p. 217): the laden draught.",
          "- **Issue lists for Juliana, Lavia and Visón** like the Valencera's (AGS), for the cargo.", "",
          "## Priors (HYPOTHESIS unless a page is cited as the constraint)", "",
          f"Constants: seawater {R2['constants']['rho_sea']} t/m³; azumbre {R2['constants']['azumbre_l']} l "
          "(standard Castilian equivalence; not from Martin); ration "
          f"{R2['constants']['liquid_kg_day']} kg of wine and water and {R2['constants']['solid_kg_day']} kg of "
          f"food a day; machos used for scaling the ballast {R2['constants']['machos']}.", "",
          "| Prior | values | basis |", "|---|---|---|"]
    for k, p in R2["priors"].items():
        L.append(f"| {k} | {p['dist']} {p['params']} | {p['basis']} |")
    L += ["", "Every prior is drawn once per draw and shared by the three ships, so the combined interval does "
          "not narrow by averaging.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
