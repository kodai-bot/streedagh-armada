"""
report_data.py — Streedagh Armada site assessment: consolidated numbers for the report.

Runs all four Monte Carlo models with their canonical seeds and prints every
quantitative figure that appears in the draft report in a single authoritative pass.
If a number in the draft differs from this output, the draft should be corrected.

Seeds / N (canonical — must not be changed):
  Hull model     seed 20260629  N = 200 000   (streedagh_hull.py)
  Manifest model seed 15880921  N = 200 000   (streedagh_manifest.py cargo section)
  Guns model     seed 15881221  N = 100 000   (streedagh_guns.py)
  Timber model   seed 20260701  N = 200 000   (streedagh_manifest.py timber section)

Note on hull rng sequence: streedagh_hull.py calls model() twice per ship (two separate
print loops), so B/L/D come from rng draws 1-3 and displacement/dwt/payload from draws
4-6.  This script replicates that pattern exactly to guarantee identical output.
"""

import numpy as np

SEP  = "=" * 72
SEP2 = "-" * 72


def pct(arr, ps=(5, 50, 95)):
    return np.percentile(arr, list(ps))


def fmt1(v, u=""):
    """median [5th–95th] to 1 d.p."""
    return f"{v[1]:.1f} [{v[0]:.1f}–{v[2]:.1f}]{u}"


def fmt0(v, u=""):
    """median [5th–95th] to 0 d.p."""
    return f"{v[1]:.0f} [{v[0]:.0f}–{v[2]:.0f}]{u}"


# ─────────────────────────────────────────────────────────────────────────────
# §B.1  HULL RECONSTRUCTION
# ─────────────────────────────────────────────────────────────────────────────

def _hull_draw(T, rng, N):
    """Single Monte Carlo draw for one ship of burthen T toneladas."""
    def tri(a, m, b): return rng.triangular(a, m, b, N)
    T_s    = T  * tri(0.88, 1.0,  1.12)
    k      =      tri(1.20, 1.42, 1.55)
    Vburt  = T_s * k
    phi    =      tri(0.45, 0.52, 0.58)
    Vmould = Vburt / phi
    alpha  =      tri(3.3,  3.5,  3.8 )
    beta   =      tri(0.45, 0.50, 0.55)
    Cbbox  =      tri(0.45, 0.52, 0.58)
    B      = (Vmould / (alpha * beta * Cbbox)) ** (1 / 3)
    L      = alpha * B
    D      = beta  * B
    gamma  =      tri(0.55, 0.62, 0.70)
    delta  =      tri(0.82, 0.87, 0.92)
    Cbhul  =      tri(0.50, 0.56, 0.62)
    d      = gamma * D
    Lwl    = delta * L
    Vsub   = Lwl * B * d * Cbhul
    disp   = 1.025 * Vsub
    lam    =      tri(0.42, 0.50, 0.58)
    dwt    = disp * (1 - lam)
    bal    =      tri(0.25, 0.35, 0.45)
    payload = dwt * (1 - bal)
    return dict(B=B, L=L, D=D, Vmould=Vmould, disp=disp, dwt=dwt, payload=payload, lam=lam)


def section_hull():
    rng  = np.random.default_rng(20260629)
    N    = 200_000
    ships = {
        "La Juliana":           860.0,
        "La Lavia":             728.0,
        "Santa María de Visón": 666.0,
    }

    print(SEP)
    print("§B.1  HULL RECONSTRUCTION")
    print("      seed 20260629 | N = 200 000 | source: streedagh_hull.py")
    print(SEP)

    # — replicate streedagh_hull.py's two-loop rng sequence exactly —
    # Loop 1: B / L / D  (rng draws 1, 2, 3)
    dims = {}
    for name, T in ships.items():
        r = _hull_draw(T, rng, N)
        dims[name] = {k: pct(r[k]) for k in ("B", "L", "D")}

    # Loop 2: displacement / dwt / payload  (rng draws 4, 5, 6)
    mass = {}
    for name, T in ships.items():
        r = _hull_draw(T, rng, N)
        mass[name] = {k: pct(r[k]) for k in ("disp", "dwt", "payload")}

    print(f"\n  {'Ship':26s}  {'Beam B (m)':>22s}  {'Length L (m)':>22s}  {'Depth D (m)':>20s}")
    for name in ships:
        d = dims[name]
        print(f"  {name:26s}  {fmt1(d['B']):>22s}  {fmt1(d['L']):>22s}  {fmt1(d['D']):>20s}")

    print(f"\n  {'Ship':26s}  {'Displacement (t)':>22s}  {'Deadweight (t)':>22s}  {'Payload ex-bal (t)':>20s}")
    for name in ships:
        m = mass[name]
        print(f"  {name:26s}  {fmt0(m['disp']):>22s}  {fmt0(m['dwt']):>22s}  {fmt0(m['payload']):>20s}")

    print(f"\n  Combined displacement (sum of medians): "
          f"{sum(mass[n]['disp'][1] for n in ships):.0f} t")
    print(f"  Combined deadweight  (sum of medians): "
          f"{sum(mass[n]['dwt'][1] for n in ships):.0f} t")
    print(f"  Combined payload     (sum of medians): "
          f"{sum(mass[n]['payload'][1] for n in ships):.0f} t")

    print()
    print("  Draft report B.1 table targets:")
    for name in ships:
        d, m = dims[name], mass[name]
        print(f"    {name}")
        print(f"      B {d['B'][1]:.1f} [{d['B'][0]:.1f}–{d['B'][2]:.1f}] m  "
              f"L {d['L'][1]:.1f} [{d['L'][0]:.1f}–{d['L'][2]:.1f}] m  "
              f"D {d['D'][1]:.1f} [{d['D'][0]:.1f}–{d['D'][2]:.1f}] m")
        print(f"      Displacement {m['disp'][1]:.0f} [{m['disp'][0]:.0f}–{m['disp'][2]:.0f}] t  "
              f"DWT {m['dwt'][1]:.0f} [{m['dwt'][0]:.0f}–{m['dwt'][2]:.0f}] t  "
              f"Payload {m['payload'][1]:.0f} [{m['payload'][0]:.0f}–{m['payload'][2]:.0f}] t")


# ─────────────────────────────────────────────────────────────────────────────
# §B.2  ARMAMENT MASS
# ─────────────────────────────────────────────────────────────────────────────

def section_guns():
    rng = np.random.default_rng(15881221)
    N   = 100_000
    def tri(a, m, b): return rng.triangular(a, m, b, N)

    guns_count = {"La Juliana": 32, "La Lavia": 25, "Santa María de Visón": 18}
    classes = {
        "esmeril/pedrero (swivel)": (dict(a=80,   m=150,  b=300 ), 0.40, "light"),
        "minion/falcon":            (dict(a=300,  m=450,  b=650 ), 0.34, "light"),
        "sacre/media-culebrina":    (dict(a=700,  m=1100, b=1600), 0.20, "heavy"),
        "culebrina/cañon":          (dict(a=1600, m=2200, b=3000), 0.06, "heavy"),
    }

    print(SEP)
    print("§B.2  ARMAMENT MASS")
    print("      seed 15881221 | N = 100 000 | source: streedagh_guns.py")
    print(SEP)

    tot_mass  = np.zeros(N)
    tot_light = np.zeros(N)
    tot_heavy = np.zeros(N)

    print()
    for ship, n in guns_count.items():
        m_ship = np.zeros(N)
        light  = np.zeros(N)
        heavy  = np.zeros(N)
        for cls, (band, frac, tier) in classes.items():
            mass_cls = n * frac * tri(**band) / 1000.0
            m_ship  += mass_cls
            if tier == "light":
                light += mass_cls
            else:
                heavy += mass_cls
        tot_mass  += m_ship
        tot_light += light
        tot_heavy += heavy
        qm, ql, qh = pct(m_ship), pct(light), pct(heavy)
        print(f"  {ship} ({n} guns):")
        print(f"    Total {fmt1(qm, ' t')}  |  light/accessible {fmt1(ql, ' t')}  |  heavy/buried {fmt1(qh, ' t')}")

    qT, qL, qH = pct(tot_mass), pct(tot_light), pct(tot_heavy)
    print()
    print(f"  ALL THREE SHIPS — ship's armament (75 guns):")
    print(f"    Total  {fmt0(qT, ' t')}  (5th–95th)")
    print(f"    Light/accessible tier:  {qL[1]:.0f} t")
    print(f"    Heavy/buried tier:      {qH[1]:.0f} t")

    # Siege train
    siege_n    = tri(2, 5, 9)
    siege_mass = siege_n * tri(2000, 2500, 3000) / 1000.0
    qSN, qSM = pct(siege_n), pct(siege_mass)
    print()
    print(f"  Embarked siege train (cargo, buried in holds):")
    print(f"    Gun count  {fmt1(qSN, '')} (median {qSN[1]:.0f})")
    print(f"    Mass       {fmt0(qSM, ' t')}   (buried; evidenced by carriage wheels at Site 1)")
    print()
    print("  Draft report B.2 table targets:")
    print(f"    Light/accessible:  ~{qL[1]:.0f} t  [{qL[0]:.0f}–{qL[2]:.0f}]")
    print(f"    Heavy/buried:      ~{qH[1]:.0f} t  [{qH[0]:.0f}–{qH[2]:.0f}]")
    print(f"    Siege train:       ~{qSM[1]:.0f} t  [{qSM[0]:.0f}–{qSM[2]:.0f}]")
    print(f"    Fleet total:       ~{qT[1]:.0f} t  [{qT[0]:.0f}–{qT[2]:.0f}]")


# ─────────────────────────────────────────────────────────────────────────────
# §B.3  CARGO AND SURVIVING-MASS BUDGET  (artefact manifest)
# ─────────────────────────────────────────────────────────────────────────────

def section_manifest():
    rng = np.random.default_rng(15880921)
    N   = 200_000
    def tri(a, m, b): return rng.triangular(a, m, b, N)

    payload_cap = {
        "La Juliana":           (450, 579),
        "La Lavia":             (381, 489),
        "Santa María de Visón": (349, 448),
    }
    scale = {
        "La Juliana":           1.00,
        "La Lavia":             728 / 860,
        "Santa María de Visón": 666 / 860,
    }

    def components(name):
        s = scale[name]
        c = {}
        c["ballast_stone"]       = tri(120, 180, 240) * s
        c["ship_ironwork"]       = tri(8,   14,  22)  * s
        c["anchors_iron"]        = tri(3,   5,   8)
        c["ordnance_bronze"]     = tri(6,   12,  20)  * s
        c["ordnance_iron"]       = tri(4,   9,   16)  * s
        c["siege_carriage_iron"] = tri(1,   3,   6)   * s
        c["shot_iron"]           = tri(2,   5,   10)  * s
        c["shot_stone"]          = tri(1,   3,   6)   * s
        c["lead"]                = tri(1,   4,   9)   * s
        c["ceramic_botijas"]     = tri(1,   3,   7)   * s
        c["organic_bulk"]        = tri(80,  150, 250) * s
        return c

    def surv():
        return dict(
            bronze  = tri(0.95, 0.99, 1.00),
            iron    = tri(0.55, 0.75, 0.90),
            lead    = tri(0.85, 0.93, 0.99),
            stone   = tri(0.97, 0.99, 1.00),
            ceramic = tri(0.60, 0.80, 0.95),
            organic = tri(0.02, 0.06, 0.15),
        )

    print(SEP)
    print("§B.3  CARGO AND SURVIVING-MASS BUDGET")
    print("      seed 15880921 | N = 200 000 | source: streedagh_manifest.py")
    print(SEP)

    grand = {k: np.zeros(N) for k in ("bronze", "iron", "lead", "stone", "ceramic", "organic")}
    print()
    print(f"  {'Material':12s}  {'La Juliana':>22s}  {'La Lavia':>22s}  {'Santa M. Visón':>22s}")
    print(SEP2)

    per_ship = {}
    for name in payload_cap:
        c = components(name)
        f = surv()
        iron_total  = (c["ship_ironwork"] + c["anchors_iron"] + c["ordnance_iron"]
                       + c["siege_carriage_iron"] + c["shot_iron"])
        stone_total = c["ballast_stone"] + c["shot_stone"]
        sm = dict(
            bronze  = c["ordnance_bronze"] * f["bronze"],
            iron    = iron_total           * f["iron"],
            lead    = c["lead"]            * f["lead"],
            stone   = stone_total          * f["stone"],
            ceramic = c["ceramic_botijas"] * f["ceramic"],
            organic = c["organic_bulk"]    * f["organic"],
        )
        for k in grand:
            grand[k] += sm[k]
        per_ship[name] = sm

    klabels = ("bronze", "iron", "lead", "stone", "ceramic", "organic")
    for k in klabels:
        row = f"  {k:12s}"
        for name in payload_cap:
            v = pct(per_ship[name][k])
            row += f"  {v[1]:5.1f} [{v[0]:4.1f}–{v[2]:5.1f}]"
        print(row)

    print(SEP2)
    print(f"  {'DURABLE':12s}", end="")
    for name in payload_cap:
        dur = sum(per_ship[name][k] for k in klabels if k != "organic")
        v   = pct(dur)
        print(f"  {v[1]:5.0f} [{v[0]:4.0f}–{v[2]:5.0f}]", end="")
    print()

    print()
    print("  ALL THREE SHIPS COMBINED:")
    tot_durable = np.zeros(N)
    for k in klabels:
        v = pct(grand[k])
        tag = " *" if k in ("ballast_stone", "stone") else ""
        print(f"    {k:12s}  {v[1]:6.0f}  [{v[0]:5.0f}–{v[2]:6.0f}]  t{tag}")
        if k != "organic":
            tot_durable += grand[k]
    vd = pct(tot_durable)
    print(f"    {'DURABLE':12s}  {vd[1]:6.0f}  [{vd[0]:5.0f}–{vd[2]:6.0f}]  t  (ballast stone + metal + ceramic)")
    artefact_grade = tot_durable - grand["stone"]
    va = pct(artefact_grade)
    print(f"    {'artefact-grade':12s}  {va[1]:6.0f}  [{va[0]:5.0f}–{va[2]:6.0f}]  t  (metal + ceramic; excl. ballast)")


# ─────────────────────────────────────────────────────────────────────────────
# §B.3 (cont.)  STRUCTURAL TIMBER — recovery infrastructure sizing
# ─────────────────────────────────────────────────────────────────────────────

def section_timber():
    rng = np.random.default_rng(20260701)
    N   = 200_000
    def tri(a, m, b): return rng.triangular(a, m, b, N)

    disp_med = {
        "La Juliana":           1390.0,
        "La Lavia":             1177.0,
        "Santa María de Visón": 1077.0,
    }

    print()
    print(SEP)
    print("§B.3 (cont.)  STRUCTURAL TIMBER — recovery infrastructure sizing")
    print("      seed 20260701 | N = 200 000 | source: streedagh_manifest.py timber section")
    print("      Basis: displacement × lightship fraction λ × hull-timber fraction of lightship")
    print("      Construction ref: La Trinidad Valencera (Martin 1984 Ch.6) —")
    print("        solid-framed oak, 10 cm planking, iron fastenings (corroded, not counted here)")
    print(SEP)

    g25 = np.zeros(N);  g33 = np.zeros(N);  g50 = np.zeros(N)
    print()
    print(f"  {'Ship':26s}  {'Original (t)':>18s}  {'1/4 survival':>16s}  {'1/3 survival':>16s}  {'1/2 survival':>16s}")
    print(SEP2)

    for name, d_med in disp_med.items():
        lam = tri(0.42, 0.50, 0.58)
        tf  = tri(0.50, 0.58, 0.66)
        t_orig  = d_med * lam * tf
        t25     = t_orig * 0.25
        t33     = t_orig / 3.0
        t50     = t_orig * 0.50
        g25 += t25;  g33 += t33;  g50 += t50
        o, q25, q33, q50 = pct(t_orig), pct(t25), pct(t33), pct(t50)
        print(f"  {name:26s}  {fmt0(o):>18s}  {fmt0(q25):>16s}  {fmt0(q33):>16s}  {fmt0(q50):>16s}")

    print(SEP2)
    q25c, q33c, q50c = pct(g25), pct(g33), pct(g50)
    print(f"  {'COMBINED':26s}  {'':>18s}  {fmt0(q25c):>16s}  {fmt0(q33c):>16s}  {fmt0(q50c):>16s}")
    print()
    print("  Planning note: waterlogged oak ~900–1000 kg/m³.")
    print("  A 10×3 m hull section (0.4 m mean timber depth) = 11–12 t waterlogged.")
    print("  With in-situ ballast: lift requirement rises to 20–50 t per section.")
    print("  → Minimum crane rating at Sligo quay: 50 t; 80 t desirable.")


# ─────────────────────────────────────────────────────────────────────────────
# §B.4  COMPLEMENT (documentary, not Monte Carlo)
# ─────────────────────────────────────────────────────────────────────────────

def section_complement():
    print()
    print(SEP)
    print("§B.4  COMPLEMENT — documentary figures (Martin 1984 Appendix 4; no Monte Carlo)")
    print(SEP)
    data = [
        ("La Juliana",           860,  32, 325, 70, 395),
        ("La Lavia",             728,  25, 203, 71, 274),
        ("Santa María de Visón", 666,  18, 236, 71, 307),
    ]
    print()
    print(f"  {'Ship':26s}  {'Burthen':>8s}  {'Guns':>6s}  {'Soldiers':>10s}  {'Seamen':>8s}  {'Total':>7s}")
    print(SEP2)
    tot_sol = tot_sea = tot_all = 0
    for name, burt, guns, sol, sea, total in data:
        print(f"  {name:26s}  {burt:8d}  {guns:6d}  {sol:10d}  {sea:8d}  {total:7d}")
        tot_sol += sol;  tot_sea += sea;  tot_all += total
    print(SEP2)
    print(f"  {'COMBINED':26s}  {'2,254':>8s}  {'75':>6s}  {tot_sol:10d}  {tot_sea:8d}  {tot_all:7d}")
    print()
    print("  De Cuéllar (La Lavia): 'over 1,000 dead, fewer than 300 survivors' across three ships.")
    print("  Complement was higher than muster if inter-ship transfers from lost vessels occurred.")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("STREEDAGH ARMADA WRECK SITE — REPORT DATA")
    print("Authoritative numerical output for streedagh_site_assessment_DRAFT(1).md")
    print()

    section_hull()
    print()
    section_guns()
    print()
    section_manifest()
    section_timber()
    section_complement()

    print()
    print(SEP)
    print("END OF REPORT DATA — check draft against these figures.")
    print(SEP)
