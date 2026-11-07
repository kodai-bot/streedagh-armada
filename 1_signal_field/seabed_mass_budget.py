"""
What went to the bottom at Streedagh on the wreck day: the mass budget, layer by layer.

    .venv/bin/python 1_signal_field/seabed_mass_budget.py        (or: make mass)

Layer 1 (this script, now): ORDNANCE AND MUNITIONS, per ship and combined: guns, shot, powder,
lead and match. It is built from stated counts (the Lisbon muster, 9 May 1588) times unit
masses that are themselves sourced, with every assumption a named prior.

Layer 2 (next): HULL, BALLAST, STORES AND CARGO, from the measured dimensions (AGS GA 223/28
via Martin 1984 App. 11), which this script already converts and checks. Those terms are the
bulk of the mass and need a hull-form model, so they are not estimated here.

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
  Martin 1984 App. 11     the six ships' measured dimensions and ratings (p. 411)
  Ridella et al. 2016     Juliana's recovered guns by weight mark (juliana_guns.csv)

Writes output/mass_budget_report.md and output/mass_budget.json.
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


def main():
    rng = np.random.default_rng(SEED)
    muster = {SHIPS[r["ship"]]: r for r in read("lisbon_muster_1588.csv") if r["ship"] in SHIPS}
    rec = read("juliana_guns.csv")
    shot_kg, stone_frac, n_listed = shot_mass_kg(rng)
    u = lambda k: rng.uniform(*PRIORS[k][0], N)
    a, m, b = PRIORS["unitemised_gun_t"][0]
    gun_mean_t = rng.triangular(a, m, b, N)   # shared by all three ships: one squadron, one open question

    out, tot = {}, {}
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
        out[ship]["as_mustered"] = {"guns": guns_n, "shot": shot_n, "powder_t": round(int(r["powder_qtx"]) * QUINTAL_KG / 1000, 2),
                                    "lead_t": round(int(r["lead_qtx"]) * QUINTAL_KG / 1000, 2),
                                    "match_t": round(int(r["match_qtx"]) * QUINTAL_KG / 1000, 2),
                                    "guns_itemised": len(rec) if ship == "Juliana" else 0}
        for k, v in parts.items():
            tot[k] = tot.get(k, 0) + v
    out["Combined"] = {k: q(v) for k, v in tot.items()}

    result = {"layer": "1: ordnance and munitions", "seed": SEED, "draws": N,
              "units": {"libra_kg": LIBRA_KG, "quintal_kg": QUINTAL_KG, "codo_m": CODO_M},
              "shot_mean_kg": q(shot_kg * 1000) | {"guns_in_list": n_listed},
              "stone_shot_mass_frac": q(stone_frac * 1000),
              "priors": {k: {"params": v[0], "basis": v[1]} for k, v in PRIORS.items()},
              "ships": out, "ratings": ratings_check()}
    # q() works in tonnes; the two lines above re-scale kg and fractions so the same helper rounds them
    for k in ("shot_mean_kg", "stone_shot_mass_frac"):
        for s in ("median", "p05", "p95"):
            result[k][s] = round(result[k][s] / 1000, 3)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "mass_budget.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    with open(os.path.join(OUT, "mass_budget_report.md"), "w", encoding="utf-8") as f:
        f.write(report(result))
    c = out["Combined"]
    print(f"layer 1 (ordnance + munitions), combined: {c['total']['median']} t [{c['total']['p05']}-{c['total']['p95']}]; "
          f"durable {c['durable']['median']} t")


def report(R):
    f = lambda d: f"{d['median']:.1f} [{d['p05']:.1f}–{d['p95']:.1f}]"
    L = ["# What went to the bottom: layer 1, ordnance and munitions", "",
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
          "personal arms, and cargo (Juliana's siege-carriage wheels). These are most of the mass. They "
          "need a hull model built from the measured dimensions below, not from the toneladas.", "",
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
    return "\n".join(L)


if __name__ == "__main__":
    main()
