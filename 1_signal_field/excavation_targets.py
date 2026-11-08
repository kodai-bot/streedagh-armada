"""
Excavation targets at Streedagh: what is on each site (mass) against how exposed it is to motion
(the sea un-burying it), as expected loss per decade if nothing is done.

    .venv/bin/python 1_signal_field/excavation_targets.py        (or: make targets)

Mass per site comes from the seabed mass budget's own per-ship draws (seabed_mass_budget.py, same
seed), mapped to sites by Birch & McElvogue's headings (Site 1 La Juliana, Site 2 Santa Maria de
Visón, Site 3 La Lavia); the site record holds those attributions at 0.80, 0.65 and 0.72.

Exposure comes from what the record says about each site (data/exposure_record.csv): Site 1 has two
dated exposure episodes (1985, 2015) and is "the most dynamic", with material "frequently" exposed;
Sites 2 and 3 have only "isolated finds", and Site 3 the "maximum sand accretion". That is thin, so
the exposure rates are wide stated priors, and the output says which prior decides the ranking.

The model, per site and class of material:
    expected share lost in a decade = 1 - exp(-10 x rate x exposed_share x loss_on_exposure)
where rate is exposure events a year, exposed_share the share of the site uncovered per event, and
loss_on_exposure the share of uncovered material destroyed or carried off (by class: timber and
organics worst, bronze least). It ranks sites for intervention; it is not a forecast of storms.

Within a site, positions are not held, so within-site targets stay qualitative (see the report).
"""

import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
sys.path.insert(0, HERE)
import seabed_mass_budget as sbm  # noqa: E402

SITE_SHIP = {"SITE1": "Juliana", "SITE2": "Vison", "SITE3": "Lavia"}
ATTR_P = {"SITE1": 0.80, "SITE2": 0.65, "SITE3": 0.72}       # site record, from site assessment v2 L3.1
GUNS = {"Juliana": 32, "Vison": 18, "Lavia": 25}
RAISED = {"Juliana": 12, "Vison": 0, "Lavia": 0}             # 1985 and 2015 recoveries, all attributed to Site 1
YEARS = 10
CURVE_YEARS = [0, 5, 10, 15, 20, 25, 30, 40, 50]   # for the page: cumulative loss if nothing is done, same rates

RATE = {   # exposure events per year (an event = enough sand removed to uncover wreck material)
    "SITE1": ((0.05, 0.30), "two dated exposure episodes in about 40 years of watching (1985, 2015) give 0.05; "
                            "'frequently exposed' (Birch & McElvogue p. 271) allows more, unrecorded"),
    "SITE2": ((0.01, 0.08), "'isolated finds' at various times (p. 271); no dated episode held"),
    "SITE3": ((0.005, 0.05), "'isolated finds' and the 'maximum sand accretion', sheltered by Streedagh Point (p. 271)"),
}
SHARED = {
    "exposed_share": ((0.02, 0.15), "share of a site's material uncovered in one event. HYPOTHESIS"),
}
LOSS = {   # share of uncovered material lost (destroyed, abraded beyond record, or carried off) per event
    "timber": ((0.20, 0.60), "organic remains 'attacked by flora and fauna when uncovered' (p. 271); shipworm "
                             "and abrasion. HYPOTHESIS for the numbers"),
    "cargo": ((0.10, 0.40), "mixed wood and iron (wheels, carriages, stores). HYPOTHESIS"),
    "iron": ((0.05, 0.20), "concretions crack and corrode when re-exposed. HYPOTHESIS"),
    "guns": ((0.01, 0.10), "bronze survives, but 'sand abrasion... most notably the bronze artillery' (p. 271) "
                           "and an exposed gun can move or be taken. HYPOTHESIS"),
}
CLASSES = {"timber": "timber_to_seabed", "cargo": "cargo_to_seabed", "iron": "ferrous_to_seabed"}


def q(x, nd=1):
    p5, p50, p95 = np.percentile(x, [5, 50, 95])
    return {"median": round(float(p50), nd), "p05": round(float(p5), nd), "p95": round(float(p95), nd)}


def ranks(x):
    r = np.empty(len(x))
    r[np.argsort(x)] = np.arange(len(x))
    return r


def main():
    sbm.main(write=False)
    S = sbm.RAW_SHIP
    N = len(next(iter(S.values()))["to_seabed"])
    rng = np.random.default_rng(sbm.SEED + 3)
    rate = {k: rng.uniform(*v[0], N) for k, v in RATE.items()}
    sh = {k: rng.uniform(*v[0], N) for k, v in SHARED.items()}
    loss = {k: rng.uniform(*v[0], N) for k, v in LOSS.items()}     # shared across sites: same materials, same sea

    sites, score = {}, {}
    for site, ship in SITE_SHIP.items():
        lost_frac = {c: 1 - np.exp(-YEARS * rate[site] * sh["exposed_share"] * loss[c]) for c in LOSS}
        mass = {c: S[ship][k] for c, k in CLASSES.items()}
        guns_left = GUNS[ship] - RAISED[ship]       # an upper bound: not every documented gun went down
        lost_t = {c: mass[c] * lost_frac[c] for c in CLASSES}
        lost_guns = guns_left * lost_frac["guns"]
        total_lost = sum(lost_t.values())
        score[site] = total_lost
        k = {c: rate[site] * sh["exposed_share"] * loss[c] for c in LOSS}     # per-year loss intensity by class
        curve = [{"years": t, "all_classes_t": q(sum(mass[c] * (1 - np.exp(-t * k[c])) for c in CLASSES)),
                  "timber_t": q(mass["timber"] * (1 - np.exp(-t * k["timber"])))} for t in CURVE_YEARS]
        sites[site] = {
            "ship_by_heading": ship, "attribution_p": ATTR_P[site],
            "on_seabed_t": {c: q(m) for c, m in mass.items()} | {"all": q(S[ship]["to_seabed"])},
            "guns_documented_not_raised": guns_left,
            "p_any_exposure_in_decade": q(1 - np.exp(-YEARS * rate[site]), 2),
            "lost_per_decade_t": {c: q(v) for c, v in lost_t.items()} | {"all_classes": q(total_lost)},
            "lost_per_decade_share": {c: q(v * 100) for c, v in lost_frac.items()},
            "guns_damaged_or_lost_per_decade": q(lost_guns, 2),
            "loss_curve": curve,
        }
    stack = np.vstack([score[s] for s in SITE_SHIP])
    order = np.argsort(-stack, axis=0)
    p_first = {s: round(float((order[0] == i).mean()), 3) for i, s in enumerate(SITE_SHIP)}
    # which prior decides whether Site 1 stays first: rank correlation with its margin over the next site
    margin = stack[0] - np.maximum(stack[1], stack[2])
    rm = ranks(margin)
    drivers = {f"rate_{k}": round(float(np.corrcoef(ranks(v), rm)[0, 1]), 3) for k, v in rate.items()}
    drivers |= {k: round(float(np.corrcoef(ranks(v), rm)[0, 1]), 3) for k, v in sh.items()}
    drivers |= {f"loss_{k}": round(float(np.corrcoef(ranks(v), rm)[0, 1]), 3) for k, v in loss.items()}
    drivers = dict(sorted(drivers.items(), key=lambda kv: -abs(kv[1])))

    exposure = list(csv.DictReader(open(os.path.join(HERE, "data", "exposure_record.csv"), encoding="utf-8")))
    result = {"generated_by": "excavation_targets.py", "seed": sbm.SEED + 3, "budget_seed": sbm.SEED, "draws": N,
              "years": YEARS, "sites": sites, "p_highest_loss": p_first, "drivers_site1_margin": drivers,
              "exposure_record": exposure,
              "priors": {"rate": {k: {"params": v[0], "basis": v[1]} for k, v in RATE.items()},
                         "shared": {k: {"params": v[0], "basis": v[1]} for k, v in SHARED.items()},
                         "loss_on_exposure": {k: {"params": v[0], "basis": v[1]} for k, v in LOSS.items()}}}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "excavation_targets.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    with open(os.path.join(OUT, "excavation_targets_report.md"), "w", encoding="utf-8") as fh:
        fh.write(report(result))
    for s, d in sites.items():
        l = d["lost_per_decade_t"]["all_classes"]
        print(f"{s} ({d['ship_by_heading']}): on seabed {d['on_seabed_t']['all']['median']} t; lost/decade "
              f"{l['median']} t [{l['p05']}-{l['p95']}]; guns {d['guns_damaged_or_lost_per_decade']['median']}; "
              f"P(highest loss) {p_first[s]:.0%}")
    print("drivers of Site 1's margin:", list(drivers.items())[:4])


def report(R):
    f = lambda d: f"{d['median']:g} [{d['p05']:g}–{d['p95']:g}]"
    L = ["# Excavation targets: mass against exposure to motion", "",
         f"Generated by `excavation_targets.py` from the seabed mass budget's per-ship draws ({R['draws']:,}; budget "
         f"seed {R['budget_seed']}, this seed {R['seed']}). Median [5th–95th percentile]. Horizon: {R['years']} years "
         "with no intervention.", "",
         "**The question.** Where does doing nothing cost most? Each site's material on the seabed (from the budget) "
         "is set against how often the sea uncovers it and how much of what is uncovered is lost. The answer ranks "
         "sites for monitoring, rescue and excavation. It is not a storm forecast, and the exposure rates rest on "
         "very few records, so they are wide.", "",
         "| Site (ship by heading, p) | on the seabed t | P(any exposure in a decade) | lost per decade t | of which timber t | guns damaged or lost per decade | P(highest loss) |",
         "|---|---|---|---|---|---|---|"]
    for s, d in R["sites"].items():
        L.append(f"| {s.replace('SITE', 'Site ')} ({d['ship_by_heading']}, {d['attribution_p']}) | {f(d['on_seabed_t']['all'])} | "
                 f"{f(d['p_any_exposure_in_decade'])} | {f(d['lost_per_decade_t']['all_classes'])} | "
                 f"{f(d['lost_per_decade_t']['timber'])} | {f(d['guns_damaged_or_lost_per_decade'])} | "
                 f"{R['p_highest_loss'][s]:.0%} |")
    L += ["", "Share of each class lost per decade (%):", "", "| Site | timber | cargo | iron | guns |", "|---|---|---|---|---|"]
    for s, d in R["sites"].items():
        x = d["lost_per_decade_share"]
        L.append(f"| {s.replace('SITE', 'Site ')} | {f(x['timber'])} | {f(x['cargo'])} | {f(x['iron'])} | {f(x['guns'])} |")
    L += ["", "## What decides the ranking", "",
          "Rank correlation of each prior with Site 1's margin over the next-worst site:", "",
          "| prior | rho |", "|---|---|"]
    for k, v in R["drivers_site1_margin"].items():
        L.append(f"| {k} | {v:+.2f} |")
    L += ["", "## Reading it", "",
          "- **Site 1 first, for monitoring and rescue.** It holds the most material and is the most exposed: the "
          "only site with dated exposure episodes (1985, 2015) and the one the divers call 'the most dynamic'. "
          "Timber is what it loses fastest. Be clear what is new here: the ranking mostly restates the record, "
          "because the exposure rates were set from those same descriptions. What the model adds is the scale "
          "(tonnes a decade, with an interval) and which assumption matters most (Site 1's exposure rate, then how "
          "much of a site one storm uncovers).",
          "- **Site 3 holds almost as much and loses least.** Its sand cover is protection. It is the place to "
          "leave alone and to monitor, not to open, unless survey shows the cover thinning.",
          "- **Site 2 is the unknown.** A compact, high-intensity spread with only isolated finds: one dated "
          "exposure record there would change its rank more than any other single fact.",
          "- **Within Site 1** positions are not held, so targets stay qualitative: the site assessment's "
          "predicted buried heavy tier seaward of the ballast and concretion (Part III), and the break-up "
          "prediction that castle guns lie inshore of the keel line (site record). The 1985 account places the "
          "articulated structure, concretions, anchors and guns about 20 m seaward of the wheels.",
          "- **What would sharpen it most:** dated sand-level or exposure records for each site (the NMS "
          "monitoring, if released), and the recent surveys' positions.", "",
          "## The exposure record", "", "| Site | year | what | source |", "|---|---|---|---|"]
    for e in R["exposure_record"]:
        L.append(f"| {e['site']} | {e['year'] or '—'} | {e['what']} | {e['source']} |")
    L += ["", "## Assumptions", "", "| Prior | values | basis |", "|---|---|---|"]
    for grp in ("rate", "shared", "loss_on_exposure"):
        for k, p in R["priors"][grp].items():
            L.append(f"| {grp}: {k} | uniform {p['params']} | {p['basis']} |")
    L += ["", "Guns: documented per ship minus those raised (all 12 raised are from Site 1); an upper bound, since "
          "not every documented gun need have gone down with the ship.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
