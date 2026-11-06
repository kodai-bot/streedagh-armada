"""
Stepped-castle capacity test for La Juliana (reconstruction v0.7, §26–§28).

    .venv/bin/python 2_reconstruction/stepped_castle_capacity.py      (or: make capacity)

Recomputes, from the stated inputs alone, every table in the capacity
argument and checks each figure against the value printed in the document:

    §27.1  codo = 33/48 vara                         DERIVED
    §27.4  machos × 1.2 = wartime toneladas          DERIVED check
    §28.1  comparator ships in metres                DERIVED
    §28.2  Juliana's dimensions, three methods       INFERRED
    §28.3  stepped-castle areas                      DERIVED from HYPOTHESIS geometry
    §28.4  m² per soldier                            DERIVED
    §26.4 / §26.6  the same test on the earlier v0.4 envelope (superseded, kept as a check)

It then does one thing the document does not tabulate (marked "computed here"):
it varies the number of castle levels, fore and aft, to find the fewest levels
that reach the 1.5 m²-per-soldier benchmark in each case.

Writes output/capacity_report.md and output/capacity.json (the data for the
web page). Exits 1 if any recomputed figure disagrees with the document by more
than its last printed digit.
"""

import json
import os
import sys
from itertools import product

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")

# ── Inputs ───────────────────────────────────────────────────────────────────
VARA_M = 0.8359                 # §27.1, SOURCE / working input
CODO_RATIO = 33 / 48            # §27.1, SOURCE / working input
CODO_MARTIN_M = 0.5477          # §27.1, printed in Martin 1984; FLAGGED (incompatible with the two above)
WAR_FACTOR = 1.2                # §27.3, one fifth added for war service
JULIANA_TONELADAS = 860         # §26.1, SOURCE

# §26.1: esloria, manga, puntal (codos), machos, recorded toneladas. SOURCE.
SHIPS = {
    "Santa María de Visón": (47.5, 16, 10, 472, 566),
    "La Lavia":             (51, 18.25, 10.75, 607, 728),
    "Regazona":             (59, 21, 12, 1079, 1294),
    "Galeón del Duque":     (68, 17, 11, 801, 961),
}
BROAD = ["Santa María de Visón", "La Lavia", "Regazona"]   # galleon excluded: different E:M family (§28.2)

SOLDIERS = [290, 307.5, 325]    # personnel envelope used in §26.5/§28.4
MARINERS = (65, 70)             # retained in the waist and on the weather deck; not counted against castle area
BENCHMARK = (1.5, 2.0)          # m² per soldier, previously cited range
LOWER_SHARES = [0, 0.25, 0.40, 0.55]   # share of one net lower principal deck added (§26.6)

SCENARIOS = ["low", "central", "high"]
# §26.3 geometry, low / central / high. All HYPOTHESIS except as noted.
GEOMETRY = {
    "planform":     (0.72, 0.76, 0.80),   # main-deck area / (L × B), hull taper
    "fore_len":     (0.24, 0.27, 0.30),   # forecastle length / L
    "fore_wid":     (0.72, 0.78, 0.84),   # forecastle mean width / B
    "aft_len":      (0.30, 0.35, 0.40),   # aftercastle length / L
    "aft_wid":      (0.82, 0.88, 0.93),   # aftercastle mean width / B
    "third":        (0.40, 0.50, 0.60),   # shortened third aft level / aft footprint
    "deduction":    (0.35, 0.30, 0.25),   # masts, stairs, framing, hatches, guns
    "access":       (0.75, 0.82, 0.88),   # usable share of open roof surface
}
# Floor rule (§26.3): forecastle two full levels; aftercastle two full levels + a shortened third.
DOC_LEVELS = {"fore": 2, "aft": 2, "aft_top": True}
# Superseded v0.4 envelope (§26.3), before the codo was fixed
V04_LB = {"low": (29.50, 10.60), "central": (31.25, 11.15), "high": (33.00, 11.70)}

# ── Figures printed in the document, for the checks ──────────────────────────
DOC = {
    "28.1": {"Santa María de Visón": (27.30, 9.19, 5.75), "La Lavia": (29.31, 10.49, 6.18),
             "Regazona": (33.91, 12.07, 6.90), "Galeón del Duque": (39.08, 9.77, 6.32)},
    "27.4": {"Santa María de Visón": 566.4, "La Lavia": 728.4, "Regazona": 1294.8,
             "Galeón del Duque": 961.2},
    "28.2": {"interpolation": (52.86, 18.89, 11.04, 30.38, 10.86, 6.34),
             "ols": (52.45, 18.40, 10.91, 30.14, 10.57, 6.27),
             "cube_root": (53.90, 19.29, 11.36, 30.98, 11.08, 6.53)},
    "28.2_central": (30.50, 10.84, 6.38),
    # main, fore fp, aft fp, enclosed gross, open gross, net enclosed, net open, net total
    "28.3": {"low": (229.4, 55.1, 78.4, 298.3, 133.5, 193.9, 65.1, 258.9),
             "central": (251.2, 69.6, 101.8, 393.7, 171.4, 275.6, 98.4, 374.0),
             "high": (274.7, 86.5, 127.7, 505.2, 214.3, 378.9, 141.4, 520.3)},
    # m²/soldier: upperworks only, +25 %, +40 %, +55 % lower deck
    "28.4": {("low", 290): (0.89, 1.02, 1.10, 1.18), ("low", 307.5): (0.84, 0.96, 1.04, 1.11),
             ("low", 325): (0.80, 0.91, 0.98, 1.05),
             ("central", 290): (1.29, 1.44, 1.53, 1.62), ("central", 307.5): (1.22, 1.36, 1.44, 1.53),
             ("central", 325): (1.15, 1.29, 1.37, 1.45),
             ("high", 290): (1.79, 1.97, 2.08, 2.18), ("high", 307.5): (1.69, 1.86, 1.96, 2.06),
             ("high", 325): (1.60, 1.76, 1.85, 1.95)},
    "26.4": {"low": (225.1, 54.0, 76.9, 292.7, 131.0, 190.2, 63.8, 254.1),
             "central": (264.8, 73.4, 107.3, 415.1, 180.7, 290.5, 103.7, 394.3),
             "high": (308.9, 97.3, 143.6, 568.0, 240.9, 426.0, 159.0, 585.0)},
    # added lower area m², then m²/soldier @290, @307.5, @325
    "26.6": {("low", 0.25): (36.6, 1.00, 0.95, 0.89), ("low", 0.40): (58.5, 1.08, 1.02, 0.96),
             ("low", 0.55): (80.5, 1.15, 1.09, 1.03),
             ("central", 0.25): (46.3, 1.52, 1.43, 1.36), ("central", 0.40): (74.1, 1.62, 1.52, 1.44),
             ("central", 0.55): (102.0, 1.71, 1.61, 1.53),
             ("high", 0.25): (57.9, 2.22, 2.09, 1.98), ("high", 0.40): (92.7, 2.34, 2.20, 2.09),
             ("high", 0.55): (127.4, 2.46, 2.32, 2.19)},
}

AREA_KEYS = ["main_gross", "fore_fp", "aft_fp", "enclosed_gross", "open_gross",
             "net_enclosed", "net_open", "net_upper"]


# ── Model ────────────────────────────────────────────────────────────────────
def codo_m():
    return CODO_RATIO * VARA_M


def juliana_estimates():
    """§28.2: Juliana's esloria/manga/puntal (codos) by three methods from its rating."""
    machos = JULIANA_TONELADAS / WAR_FACTOR
    dims = lambda name: np.array(SHIPS[name][:3], dtype=float)
    lav, reg = SHIPS["La Lavia"][3], SHIPS["Regazona"][3]
    t = (machos - lav) / (reg - lav)
    interp = dims("La Lavia") + t * (dims("Regazona") - dims("La Lavia"))
    m = np.array([SHIPS[s][3] for s in BROAD], dtype=float)
    ols = np.array([np.polyval(np.polyfit(m, [SHIPS[s][i] for s in BROAD], 1), machos) for i in range(3)])
    cube = dims("La Lavia") * (machos / lav) ** (1 / 3)
    return machos, {"interpolation": interp, "ols": ols, "cube_root": cube}


def envelope(estimates):
    """Low = smallest, central = mean, high = largest of the three methods, per dimension (metres)."""
    a = np.array(list(estimates.values())) * codo_m()
    return {"low": a.min(axis=0), "central": a.mean(axis=0), "high": a.max(axis=0)}


def areas(L, B, g, fore=2, aft=2, aft_top=True, lower_share=0.0):
    """Deck areas (m²) for one geometry. `fore`/`aft` are full castle levels; `aft_top` adds the
    shortened third aft level. One exposed roof per castle, whatever its number of levels."""
    main = L * B * g["planform"]
    fore_fp = g["fore_len"] * L * g["fore_wid"] * B
    aft_fp = g["aft_len"] * L * g["aft_wid"] * B
    enclosed = fore * fore_fp + (aft + (g["third"] if aft_top else 0)) * aft_fp
    open_ = (fore_fp if fore else 0) + (aft_fp if aft else 0)
    keep = 1 - g["deduction"]
    net_enc, net_open = enclosed * keep, open_ * keep * g["access"]
    lower = lower_share * main * keep          # share of one net body-deck equivalent
    return {"main_gross": main, "fore_fp": fore_fp, "aft_fp": aft_fp,
            "enclosed_gross": enclosed, "open_gross": open_,
            "net_enclosed": net_enc, "net_open": net_open, "net_upper": net_enc + net_open,
            "lower_added": lower, "troop_area": net_enc + net_open + lower}


def geom(scenario):
    i = SCENARIOS.index(scenario)
    return {k: v[i] for k, v in GEOMETRY.items()}


# ── Checks ───────────────────────────────────────────────────────────────────
class Checker:
    def __init__(self):
        self.rows = []

    def __call__(self, where, label, computed, printed):
        decimals = len(str(printed).split(".")[1]) if "." in str(printed) else 0
        tol = 10 ** -decimals * 1.01          # one unit in the last printed digit
        diff = computed - printed
        self.rows.append((where, label, computed, printed, diff, abs(diff) <= tol, decimals))

    @property
    def failures(self):
        return [r for r in self.rows if not r[5]]

    @property
    def inexact(self):
        """Within one last digit but not the same when rounded: rounding of intermediate values."""
        return [r for r in self.rows if r[5] and round(r[2], r[6]) != r[3]]


def run_checks():
    ck = Checker()
    c = codo_m()
    for s, (E, M, P) in DOC["28.1"].items():
        e, m, p = (x * c for x in SHIPS[s][:3])
        for lab, x, y in (("E m", e, E), ("M m", m, M), ("P m", p, P)):
            ck("§28.1", f"{s} {lab}", x, y)
    for s, v in DOC["27.4"].items():
        ck("§27.4", f"{s} machos × 1.2", SHIPS[s][3] * WAR_FACTOR, v)
    machos, est = juliana_estimates()
    ck("§26.1", "Juliana machos", machos, 716.7)
    for meth, printed in DOC["28.2"].items():
        vals = list(est[meth]) + list(est[meth] * c)
        for lab, x, y in zip(["E codos", "M codos", "P codos", "E m", "M m", "P m"], vals, printed):
            ck("§28.2", f"{meth} {lab}", x, y)
    env = envelope(est)
    for lab, x, y in zip(["E", "M", "P"], env["central"], DOC["28.2_central"]):
        ck("§28.2", f"central {lab} m", x, y)
    for sc in SCENARIOS:
        L, B = env[sc][:2]
        a = areas(L, B, geom(sc))
        for k, y in zip(AREA_KEYS, DOC["28.3"][sc]):
            ck("§28.3", f"{sc} {k}", a[k], y)
        for n in SOLDIERS:
            for share, y in zip(LOWER_SHARES, DOC["28.4"][(sc, n)]):
                ck("§28.4", f"{sc} {n} +{share:.0%}", areas(L, B, geom(sc), lower_share=share)["troop_area"] / n, y)
        L4, B4 = V04_LB[sc]
        a4 = areas(L4, B4, geom(sc))
        for k, y in zip(AREA_KEYS, DOC["26.4"][sc]):
            ck("§26.4", f"{sc} {k}", a4[k], y)
        for share in LOWER_SHARES[1:]:
            a4s = areas(L4, B4, geom(sc), lower_share=share)
            printed = DOC["26.6"][(sc, share)]
            ck("§26.6", f"{sc} +{share:.0%} added m²", a4s["lower_added"], printed[0])
            for n, y in zip(SOLDIERS, printed[1:]):
                ck("§26.6", f"{sc} +{share:.0%} @{n}", a4s["troop_area"] / n, y)
    return ck, machos, est, env


# ── Level sweep (computed here, not tabulated in the document) ───────────────
CONFIGS = [  # (fore full levels, aft full levels, shortened aft top)
    (f, a, t) for f, a, t in product([1, 2, 3], [1, 2, 3], [False, True]) if abs(f - a) <= 1
]


def config_label(f, a, t):
    return f"fore {f} · aft {a}{' + ½' if t else ''}"


def sweep(env):
    """For every scenario, soldier count and lower-deck share: m²/soldier for each castle
    configuration, and the smallest configuration (fewest levels) that reaches 1.5 m²."""
    out = []
    for sc, n, share in product(SCENARIOS, SOLDIERS, LOWER_SHARES):
        L, B = env[sc][:2]
        rows = []
        for f, a, t in CONFIGS:
            ar = areas(L, B, geom(sc), f, a, t, share)
            rows.append({"fore": f, "aft": a, "aft_top": t, "levels": f + a + (0.5 if t else 0),
                         "per_soldier": round(ar["troop_area"] / n, 3)})
        ok = sorted((r for r in rows if r["per_soldier"] >= BENCHMARK[0]),
                    key=lambda r: (r["levels"], -r["per_soldier"]))
        out.append({"scenario": sc, "soldiers": n, "lower_share": share, "configs": rows,
                    "minimum": ok[0] if ok else None})
    return out


# ── Output ───────────────────────────────────────────────────────────────────
def fmt(x, d=1):
    return f"{x:,.{d}f}"


def report(ck, machos, est, env, sw):
    c = codo_m()
    L = ["# Stepped-castle capacity: recomputed",
         "",
         "Generated by `stepped_castle_capacity.py` from the inputs stated in the reconstruction "
         "(v0.7, §26–§28). Every figure printed in those sections is recomputed and compared below.",
         "",
         f"**Checks: {len(ck.rows)} figures, {len(ck.failures)} disagree, "
         f"{len(ck.inexact)} differ only in the last digit (rounding of intermediate values).**",
         "",
         "## Metrology (§27)",
         "",
         f"codo = 33/48 × {VARA_M} m = **{c:.8f} m** (DERIVED). Martin's printed {CODO_MARTIN_M} m is "
         f"{(1 - CODO_MARTIN_M / c):.1%} shorter and not reachable from the same ratio and vara (FLAGGED).",
         "",
         "| Ship | E codos | M codos | P codos | E m | M m | P m | machos | × 1.2 | recorded toneladas |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for s, (E, M, P, mach, ton) in SHIPS.items():
        L.append(f"| {s} | {E} | {M} | {P} | {E*c:.2f} | {M*c:.2f} | {P*c:.2f} | {mach} | {mach*WAR_FACTOR:.1f} | {ton} |")
    L += ["", "## La Juliana's dimensions (§28.2, INFERRED)", "",
          f"Base rating {JULIANA_TONELADAS} / 1.2 = {machos:.1f} machos. Galleon excluded from the fit.", "",
          "| Method | E codos | M codos | P codos | E m | M m | P m |", "|---|---|---|---|---|---|---|"]
    for meth, v in est.items():
        L.append(f"| {meth} | " + " | ".join(f"{x:.2f}" for x in v) + " | "
                 + " | ".join(f"{x*c:.2f}" for x in v) + " |")
    for sc in SCENARIOS:
        L.append(f"| **{sc}** | | | | " + " | ".join(f"{x:.2f}" for x in env[sc]) + " |")
    L += ["", "## Stepped-castle areas (§28.3)", "",
          "Floor rule: forecastle 2 levels; aftercastle 2 levels + a shortened third. Geometry factors "
          "are HYPOTHESIS (§26.3).", "",
          "| Scenario | L m | B m | " + " | ".join(AREA_KEYS) + " |", "|---" * (3 + len(AREA_KEYS)) + "|"]
    for sc in SCENARIOS:
        a = areas(*env[sc][:2], geom(sc))
        L.append(f"| {sc} | {env[sc][0]:.2f} | {env[sc][1]:.2f} | " + " | ".join(fmt(a[k]) for k in AREA_KEYS) + " |")
    L += ["", "## m² per soldier (§28.4)", "",
          f"Benchmark {BENCHMARK[0]}–{BENCHMARK[1]} m². Mariners ({MARINERS[0]}–{MARINERS[1]}) keep the waist "
          "and weather deck and are not counted here.", "",
          "| Scenario | Soldiers | upperworks | +25 % lower | +40 % lower | +55 % lower |", "|---|---|---|---|---|---|"]
    for sc, n in product(SCENARIOS, SOLDIERS):
        L.append(f"| {sc} | {n} | " + " | ".join(
            f"{areas(*env[sc][:2], geom(sc), lower_share=s)['troop_area']/n:.2f}" for s in LOWER_SHARES) + " |")
    L += ["", "## Fewest castle levels reaching 1.5 m² per soldier (computed here)", "",
          "Not tabulated in the document. Same geometry and deductions; only the number of levels "
          "changes. One exposed roof per castle. Levels count full decks, with ½ for the shortened top.", "",
          "| Scenario | Soldiers | upperworks only | +25 % lower | +40 % lower | +55 % lower |",
          "|---|---|---|---|---|---|"]
    by = {(r["scenario"], r["soldiers"], r["lower_share"]): r for r in sw}
    for sc, n in product(SCENARIOS, SOLDIERS):
        cells = []
        for s in LOWER_SHARES:
            m = by[(sc, n, s)]["minimum"]
            best = max(c["per_soldier"] for c in by[(sc, n, s)]["configs"])
            cells.append(config_label(m["fore"], m["aft"], m["aft_top"]) if m
                         else f"not reached (best {best:.2f})")
        L.append(f"| {sc} | {n} | " + " | ".join(cells) + " |")
    single = {sc: areas(*env[sc][:2], geom(sc), 1, 1, False)["troop_area"] / 290 for sc in SCENARIOS}
    L += ["", "Single-level castles (one deck fore, one aft), upperworks only, 290 soldiers: "
          + ", ".join(f"{sc} {v:.2f} m²" for sc, v in single.items()) + ".", ""]
    L += ["## Check details", ""]
    odd = [r for r in ck.rows if not r[5] or round(r[2], r[6]) != r[3]]
    if odd:
        L += ["| Section | Figure | Recomputed | Printed | Difference | |", "|---|---|---|---|---|---|"]
    for where, lab, x, y, d, ok, dec in odd:
        L.append(f"| {where} | {lab} | {x:.{dec+2}f} | {y} | {d:+.{dec+2}f} | {'ok' if ok else '**DISAGREES**'} |")
    if odd:
        L.append("")
    L.append(f"{'All other' if odd else 'All'} {len(ck.rows) - len(odd)} figures match exactly when rounded as printed.")
    return "\n".join(L) + "\n"


def web_json(machos, est, env, sw):
    c = codo_m()
    return {
        "inputs": {
            "vara_m": VARA_M, "codo_ratio": "33/48", "codo_m": c, "codo_martin_m": CODO_MARTIN_M,
            "war_factor": WAR_FACTOR, "juliana_toneladas": JULIANA_TONELADAS, "juliana_machos": machos,
            "soldiers": SOLDIERS, "mariners": MARINERS, "benchmark": BENCHMARK, "lower_shares": LOWER_SHARES,
        },
        "ships": [{"name": s, "codos": [E, M, P], "m": [E * c, M * c, P * c], "machos": mach,
                   "toneladas": ton, "in_fit": s in BROAD}
                  for s, (E, M, P, mach, ton) in SHIPS.items()],
        "juliana": {"methods": {k: {"codos": list(v), "m": list(v * c)} for k, v in est.items()},
                    "envelope": {sc: list(env[sc]) for sc in SCENARIOS}},
        "geometry": {sc: geom(sc) for sc in SCENARIOS},
        "doc_levels": DOC_LEVELS,
        "areas": {sc: areas(*env[sc][:2], geom(sc)) for sc in SCENARIOS},
        "sweep": sw,
    }


def main():
    ck, machos, est, env = run_checks()
    sw = sweep(env)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "capacity_report.md"), "w", encoding="utf-8") as f:
        f.write(report(ck, machos, est, env, sw))
    with open(os.path.join(OUT, "capacity.json"), "w", encoding="utf-8") as f:
        json.dump(web_json(machos, est, env, sw), f, ensure_ascii=False, separators=(",", ":"),
                  default=lambda o: round(float(o), 4))
    print(f"{len(ck.rows)} figures checked: {len(ck.failures)} disagree, "
          f"{len(ck.inexact)} off by one in the last digit")
    for r in ck.failures:
        print(f"  DISAGREES {r[0]} {r[1]}: computed {r[2]:.4f}, printed {r[3]}")
    print("wrote output/capacity_report.md, output/capacity.json")
    return 1 if ck.failures else 0


if __name__ == "__main__":
    sys.exit(main())
