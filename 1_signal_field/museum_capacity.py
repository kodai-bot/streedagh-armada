"""
Museum and conservation capacity brackets for Streedagh: what a facility would have to hold and treat
if an eighth, a quarter, a third, a half or all of the estimated seabed material survives and is raised.

    .venv/bin/python 1_signal_field/museum_capacity.py        (or: make museum)

Reads the seabed mass budget's own draws (seabed_mass_budget.py, layer 2; same seed), so the
uncertainty in what went down carries straight through. The survival fraction is a planning bracket,
not an estimate: it is applied to every class alike, although bronze survives better than timber.

Per bracket it gives: guns (and how many are still to raise), hull timber volume and wet mass, the
tank and time to treat that timber by PEG immersion or by freeze-drying, concreted iron and its
desalination tanks and time, and floor areas for wet storage and gun display. Ballast is reported
but not curated (it is normally sampled and left).

Every figure is a stated assumption; each carries its basis, with a source where one exists. These
are the first computed brackets of their kind for this site that we know of: orders of magnitude for
planning, to be replaced by survey and by a conservator's specification.

Sources for the anchors (see PRIORS):
  Vasa Museum: PEG spraying April 1962 - January 1979 (17 years), then about 9 years air-drying
  Mary Rose Trust: PEG spraying 1994 - April 2013 (about 19 years); air-drying to 2016
  Deutsches Schifffahrtsmuseum: Bremen cog, an 800 m3 PEG tank; about 18-20 years in PEG
  Texas A&M (La Belle): freeze-dryer 40 ft long, 8 ft internal diameter; 4-6 months per timber load
  QAR Conservation Lab reports: cannon C4, C19, C21 about four years in electrolytic reduction
  National Museum of Ireland: the 2015 Streedagh guns desalinated in fresh-water tanks; up to two
    years expected for their conservation (2015 estimate)
  Waterlogged wood: dry-matter density about 1.5 g/cm3 (the convention in the Smith formula)
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
sys.path.insert(0, HERE)
import seabed_mass_budget as sbm  # noqa: E402

FRACTIONS = [("1/8", 1 / 8), ("1/4", 1 / 4), ("1/3", 1 / 3), ("1/2", 1 / 2), ("all", 1.0)]
GUNS_DOCUMENTED = 75            # Lisbon muster: 32 + 25 + 18
GUNS_RAISED = 12                # 3 in 1985, 9 in 2015 (6 attributed + 3 not yet itemised)
LA_BELLE_CHAMBER_M3 = np.pi * (8 * 0.3048 / 2) ** 2 * 40 * 0.3048   # 40 ft x 8 ft internal diameter, ~57 m3

PRIORS = {
    "oak_service_density": ((0.75, 1.00), "t/m3 of hull timber in service, seasoned to wet; turns the budget's "
                            "timber mass into volume. HYPOTHESIS"),
    "basic_density_waterlogged": ((0.25, 0.50), "g/cm3 dry matter per wet volume after four centuries; with "
                                  "dry-matter density 1.5 g/cm3 it gives the wet bulk density. HYPOTHESIS"),
    "peg_tank_factor": ((1.5, 3.0), "tank volume per m3 of dismantled timber (packing, solution, access). The "
                        "Bremen cog needed an 800 m3 tank for one ship. HYPOTHESIS"),
    "peg_years": ((10.0, 20.0), "years of PEG treatment: Vasa 17 (spray), Mary Rose about 19 (spray), Bremen cog "
                  "about 18-20 (immersion); dismantled timbers may go faster"),
    "freeze_load_frac": ((0.3, 0.6), "share of a freeze-dryer chamber filled per load. HYPOTHESIS"),
    "freeze_cycle_months": ((4.0, 6.0), "months per freeze-drying load (La Belle, Texas A&M)"),
    "concretion_per_t_iron": ((1.5, 3.0), "tonnes of concretion (iron, corrosion products, sand, shell, trapped "
                              "shot) per tonne of original iron. HYPOTHESIS"),
    "concretion_density": ((1.8, 2.5), "t/m3. HYPOTHESIS"),
    "electrolysis_tank_factor": ((4.0, 10.0), "tank volume per m3 of concreted iron (solution around each "
                                 "object). HYPOTHESIS"),
    "iron_treatment_years": ((2.0, 5.0), "years of desalination or electrolytic reduction per batch: about four "
                             "years for cannon at the QAR lab; small finds faster"),
    "timber_stack_height_m": ((0.4, 0.8), "effective height of timber in wet storage or tanks per m2 of floor. "
                              "HYPOTHESIS"),
    "gun_floor_m2": ((6.0, 12.0), "m2 of floor per gun in storage or display, with access and its carriage "
                     "or cradle. HYPOTHESIS"),
}


def q(x, nd=0):
    p5, p50, p95 = np.percentile(x, [5, 50, 95])
    r = lambda v: round(float(v), nd) if nd else int(round(float(v)))
    return {"median": r(p50), "p05": r(p5), "p95": r(p95)}


def main():
    sbm.main(write=False)
    T = sbm.RAW
    N = len(T["to_seabed"])
    rng = np.random.default_rng(sbm.SEED + 2)
    P = {k: rng.uniform(*v[0], N) for k, v in PRIORS.items()}

    timber_m3 = T["timber_to_seabed"] / P["oak_service_density"]
    wet_density = P["basic_density_waterlogged"] + (1 - P["basic_density_waterlogged"] / 1.5)
    iron = T["ferrous_to_seabed"]
    conc_m3 = iron * P["concretion_per_t_iron"] / P["concretion_density"]
    freeze_m3_per_year = LA_BELLE_CHAMBER_M3 * P["freeze_load_frac"] * 12 / P["freeze_cycle_months"]

    rows = []
    for label, f in FRACTIONS:
        guns = GUNS_DOCUMENTED * f
        tv = timber_m3 * f
        r = {"fraction": label,
             "guns_surviving": round(guns, 1),
             "guns_still_to_raise": round(max(0.0, guns - GUNS_RAISED), 1),
             "timber_m3": q(tv), "timber_wet_t": q(tv * wet_density),
             "peg_tank_m3": q(tv * P["peg_tank_factor"]), "peg_years": q(P["peg_years"], 1),
             "freeze_dryer_years_la_belle_size": q(tv / freeze_m3_per_year, 1),
             "iron_t": q(iron * f), "concretion_t": q(iron * f * P["concretion_per_t_iron"]),
             "electrolysis_tank_m3": q(conc_m3 * f * P["electrolysis_tank_factor"]),
             "iron_treatment_years": q(P["iron_treatment_years"], 1),
             "timber_wet_storage_m2": q(tv / P["timber_stack_height_m"]),
             "gun_floor_m2": q(max(0.0, guns - GUNS_RAISED) * P["gun_floor_m2"]),
             "lead_t": q(T["lead_to_seabed"] * f, 1),
             "ballast_t_not_curated": q(T["ballast"] * f)}
        rows.append(r)

    result = {"generated_by": "museum_capacity.py", "seed": sbm.SEED + 2, "budget_seed": sbm.SEED, "draws": N,
              "guns_documented": GUNS_DOCUMENTED, "guns_already_raised": GUNS_RAISED,
              "la_belle_chamber_m3": round(LA_BELLE_CHAMBER_M3, 1),
              "basis_seabed": {k: q(T[k]) for k in ("to_seabed", "timber_to_seabed", "ferrous_to_seabed",
                                                   "ballast", "cargo_to_seabed")},
              "priors": {k: {"dist": "uniform", "params": v[0], "basis": v[1]} for k, v in PRIORS.items()},
              "brackets": rows}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "museum_capacity.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    with open(os.path.join(OUT, "museum_capacity_report.md"), "w", encoding="utf-8") as fh:
        fh.write(report(result))
    for r in rows:
        print(f"{r['fraction']:>4}: guns {r['guns_surviving']:5.1f} (to raise {r['guns_still_to_raise']:4.1f})  "
              f"timber {r['timber_m3']['median']:4d} m3 [{r['timber_m3']['p05']}-{r['timber_m3']['p95']}]  "
              f"PEG tank {r['peg_tank_m3']['median']:4d} m3  freeze-dryer {r['freeze_dryer_years_la_belle_size']['median']} yr  "
              f"iron {r['iron_t']['median']} t  electrolysis {r['electrolysis_tank_m3']['median']} m3")


def report(R):
    f = lambda d: f"{d['median']:,} [{d['p05']:,}–{d['p95']:,}]"
    b = R["basis_seabed"]
    L = ["# Museum and conservation capacity: brackets", "",
         "Generated by `museum_capacity.py` from the seabed mass budget's own draws "
         f"({R['draws']:,}; budget seed {R['budget_seed']}, capacity seed {R['seed']}). Median [5th–95th percentile].", "",
         "**What this is.** If a given fraction of the material the budget puts on the seabed survives and is raised, "
         "what must a facility hold and treat? The fraction is a planning bracket, not an estimate, and it is "
         "applied to every class alike (in reality bronze survives better than timber). The answers are orders of "
         "magnitude for infrastructure planning, to be replaced by survey and by a conservator's specification.", "",
         f"The basis on the seabed (all three ships): {f(b['to_seabed'])} t in all, of which hull timber "
         f"{f(b['timber_to_seabed'])} t, iron {f(b['ferrous_to_seabed'])} t, ballast {f(b['ballast'])} t, "
         f"cargo {f(b['cargo_to_seabed'])} t. Guns: {R['guns_documented']} documented, {R['guns_already_raised']} "
         "already raised.", "",
         "## Objects and timber", "",
         "| Surviving | guns (still to raise) | hull timber m³ | timber wet mass t | iron t | concretion t | lead t | ballast t (left, sampled) |",
         "|---|---|---|---|---|---|---|---|"]
    for r in R["brackets"]:
        L.append(f"| {r['fraction']} | {r['guns_surviving']:g} ({r['guns_still_to_raise']:g}) | {f(r['timber_m3'])} | "
                 f"{f(r['timber_wet_t'])} | {f(r['iron_t'])} | {f(r['concretion_t'])} | {f(r['lead_t'])} | "
                 f"{f(r['ballast_t_not_curated'])} |")
    L += ["", "## Treatment capacity", "",
          f"Two routes for the timber: PEG immersion (one tank, for years) or freeze-drying in a chamber the size of "
          f"Texas A&M's La Belle machine ({R['la_belle_chamber_m3']} m³), usually after a shorter PEG soak.", "",
          "| Surviving | PEG tank m³ | PEG years | freeze-dryer years (La Belle size) | electrolysis / desalination tanks m³ | iron treatment years per batch |",
          "|---|---|---|---|---|---|"]
    for r in R["brackets"]:
        L.append(f"| {r['fraction']} | {f(r['peg_tank_m3'])} | {f(r['peg_years'])} | "
                 f"{f(r['freeze_dryer_years_la_belle_size'])} | {f(r['electrolysis_tank_m3'])} | {f(r['iron_treatment_years'])} |")
    L += ["", "## Floor area", "",
          "| Surviving | timber wet storage m² | gun storage and display m² (guns still to raise) |", "|---|---|---|"]
    for r in R["brackets"]:
        L.append(f"| {r['fraction']} | {f(r['timber_wet_storage_m2'])} | {f(r['gun_floor_m2'])} |")
    L += ["", "## Reading it", "",
          "- **Timber sets the scale.** Even at an eighth, the hull timber needs a tank of about 100 m³ for a "
          "decade or more. If everything survives, the PEG tank comes out at about 800 m³, the size of the tank the "
          "Bremen cog needed (a check, not an input: the tank factor was not fitted to it). Freeze-drying shortens "
          "the time but needs a chamber the size of Texas A&M's for years.",
          "- **The guns are the smallest volume and the best known.** The National Museum's own process for the "
          "2015 guns (fresh-water tanks, then mechanical cleaning, then de-ionised washes) is the local baseline.",
          "- **Iron is the hidden load.** Concretions hide their contents until X-rayed and opened, and each batch "
          "ties up tanks for years.",
          "- **Not counted:** small finds and organics beyond the hull (casks, the carriage wheels, personal "
          "possessions), staff, money, and display design. Human remains are a matter of protocol, not capacity: "
          "the site is a war grave.", "",
          "## Assumptions", "", "| Prior | values | basis |", "|---|---|---|"]
    for k, p in R["priors"].items():
        L.append(f"| {k} | uniform {p['params']} | {p['basis']} |")
    L += ["", "Sources: Vasa Museum (conservation pages); Mary Rose Trust (conservation timeline); Deutsches "
          "Schifffahrtsmuseum (Bremen cog tank and completion); Texas A&M (La Belle freeze-dryer); QAR Conservation "
          "Lab reports (cannon electrolysis); National Museum of Ireland (Armada cannons and gun-carriage wheel). "
          "Links in the repository README for this folder.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
