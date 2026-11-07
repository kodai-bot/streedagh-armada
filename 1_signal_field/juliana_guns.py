"""
La Juliana's recovered guns and her muster, as signals.

    .venv/bin/python 1_signal_field/juliana_guns.py        (or: make guns)

Reads two source tables in data/:
    juliana_guns.csv          the nine recovered guns attributed to Dorino II Gioardi
                              (Ridella et al. 2016, tab. 1; reconstruction §29)
    lisbon_muster_1588.csv    the Levant squadron at the Lisbon muster, 9 May 1588
                              (Martin 1984, App. 4, pp. 448-449)

and upserts into data/streedagh_store_v3.json:
    one L0 signal per gun     mass as p05/median/p95, founder, casting year, saint,
                              recovery year; position UNKNOWN (geometry null)
    one documentary signal    per Streedagh ship from the muster, with derived ratios
                              (tons per soldier, tons per seaman, shot per gun)

Each gun also gets candidate mounting stations from stated rules. Those are
HYPOTHESIS, tagged with the rule's source, and kept out of `components` so the
attribution estimator never uses them as evidence.

Writes output/juliana_guns_report.md. Run attribution_estimator.py afterwards.
"""

import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "output")
STORE = os.path.join(DATA, "streedagh_store_v3.json")
CANTARO_KG = 47.65          # Genoese cantaro, calibrated on the same founders' guns (Ridella et al. 2016)

STREEDAGH = {"La Juliana": "JUL", "La Lavia (almiranta)": "LAV", "Santa Maria de Vison": "VIS"}

# Mounting rules. HYPOTHESIS: each is a general statement applied to these guns.
RULES = {
    "heavy_low": ("Heavy pieces (about 1 t) sit low: gun weight high above the centre of buoyancy "
                  "limits what a ship can carry", "Martin 1984, p. 195"),
    "petriere_low": ("Petrieri were 'very probably placed in the lower deck, firing through the gun ports'",
                     "Ridella et al. 2016, p. 29 (San Giorgio wreck)"),
    "light_any": ("Light carriage guns (about 0.3-0.55 t) can be worked on the main deck or the lower "
                  "castle decks", "general; weak"),
    "very_light_high": ("Small anti-personnel pieces go on the castleworks, to fire down on boarders "
                        "in the waist", "Martin 1984, p. 298 (said of swivel guns; applied here by analogy)"),
}
STATIONS = ["lower deck", "main deck", "castle deck 1", "castle deck 2+"]


def stations(g):
    """Candidate stations (indices into STATIONS) and the rule used."""
    hi = g["mass_kg_high"]
    if "Petriere" in g["type"]:
        return [0, 1], "petriere_low"
    if hi >= 800:
        return [0, 1], "heavy_low"
    if hi >= 250:
        return [1, 2], "light_any"
    return [2, 3], "very_light_high"


def read(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def gun_signal(g):
    lo, hi = float(g["mass_kg_low"]), float(g["mass_kg_high"])
    g["mass_kg_high"] = hi
    st, rule = stations(g)
    mark = g["cantara_mark"]
    legible = mark and "?" not in mark
    comps = [
        {"type": "founder_mark", "value": "Dorino_II_Gioardi", "diagnostic_group": "casting_provenance",
         "basis": "attribution in Ridella et al. 2016 tab. 1"},
        {"type": "casting_year", "value": g["cast"], "diagnostic_group": "casting_provenance"},
    ]
    if g["saint"] and "undetermined" not in g["saint"]:
        comps.append({"type": "saint_relief", "value": "St_" + g["saint"].replace("St. ", "").replace(" ", "_"),
                      "diagnostic_group": "ship_programme"})
    if legible:
        comps.append({"type": "weight_mark", "value": float(mark), "matches_juliana_record": True,
                      "diagnostic_group": "individual_id"})
    return {
        "uari": f"streedagh:SIG-{g['id']}",
        "level": "L0",
        "acquisition_class": "direct_observation",
        "acquisition": {"method": "diver_recovery", "date": g["recovered"]},
        "provenance": [g["ref"], "Ridella et al. 2016 tab. 1"],
        "geometry": None,
        "position": "unknown: recovery coordinates not in the project's sources",
        "phi": {"material": "bronze",
                "phi_quantitative": {"quantity": "mass_t", "p05": round(lo / 1000, 3),
                                     "median": round((lo + hi) / 2000, 3), "p95": round(hi / 1000, 3),
                                     "distribution_basis": g["mass_basis"], "script_ref": "juliana_guns.py"}},
        "gun": {"type": g["type"], "muzzle": g["muzzle"] or None, "saint": g["saint"] or None,
                "cantara_mark": mark or None},
        "components": comps,
        "hypotheses": [{"kind": "mounting_station", "status": "HYPOTHESIS",
                        "candidates": [STATIONS[i] for i in st], "height_rank": st,
                        "rule": RULES[rule][0], "rule_source": RULES[rule][1]}],
        "entity_attributions": [],
    }


def muster_signal(r):
    code = STREEDAGH[r["ship"]]
    n = {k: int(r[k]) for k in ("tons", "soldiers", "seamen", "guns", "shot")}
    return {
        "uari": f"streedagh:DOC-MUSTER-{code}",
        "level": "L2",
        "acquisition_class": "documentary",
        "acquisition": {"method": "muster_list", "date": "1588-05-09"},
        "provenance": [r["source"]],
        "geometry": None,
        "about": f"streedagh:ENT-{code}",
        "record": {**n, "powder_qtx": int(r["powder_qtx"]), "lead_qtx": int(r["lead_qtx"]),
                   "match_qtx": int(r["match_qtx"]), "missing_list": bool(r["missing_list"])},
        "derived": {"status": "DERIVED",
                    "tons_per_soldier": round(n["tons"] / n["soldiers"], 2),
                    "tons_per_seaman": round(n["tons"] / n["seamen"], 2),
                    "shot_per_gun": round(n["shot"] / n["guns"], 1)},
        "components": [],
        "entity_attributions": [],
    }


def report(guns, musters, fleet):
    jul = next(m for m in musters if m["uari"].endswith("JUL"))
    rec = len(guns)
    tot = sum(g["phi"]["phi_quantitative"]["median"] for g in guns)
    L = ["# La Juliana's guns and muster, as signals", "",
         "Generated by `juliana_guns.py`. Sources: Ridella et al. 2016 tab. 1 (guns); Martin 1984 "
         "App. 4 (Lisbon muster, 9 May 1588).", "",
         "## The muster", "",
         "| Ship | tons | soldiers | seamen | guns | shot | tons/soldier | tons/seaman | shot/gun |",
         "|---|---|---|---|---|---|---|---|---|"]
    for m in musters:
        r, d = m["record"], m["derived"]
        L.append(f"| {m['about'].split('-')[-1]} | {r['tons']} | {r['soldiers']} | {r['seamen']} | {r['guns']} | "
                 f"{r['shot']} | {d['tons_per_soldier']} | {d['tons_per_seaman']} | {d['shot_per_gun']} |")
    L += ["", f"Levant squadron at the muster, all ten ships: {fleet['tons_per_soldier']} tons per soldier, "
          f"{fleet['tons_per_seaman']} tons per seaman. Martin's comparisons: Portuguese two-deckers 2.3 and "
          "Castilian galleons 3.5 tons per soldier (p. 196); Armada average 7.5 tons per seaman (p. 393).", "",
          "## Recovered guns", "",
          f"**{rec} of {jul['record']['guns']} guns** are itemised and attributed (Dorino II Gioardi, 1570). "
          "Twelve are reported recovered in all; the other three are not yet itemised in the project's "
          f"sources. The {rec} itemised guns weigh about **{tot:.1f} t** together.", "",
          "| Gun | type | mass t (p05–p95) | recovered | candidate stations (HYPOTHESIS) | rule source |",
          "|---|---|---|---|---|---|"]
    for g in guns:
        q, h = g["phi"]["phi_quantitative"], g["hypotheses"][0]
        rng = f"{q['median']:.2f}" if q["p05"] == q["p95"] else f"{q['p05']:.2f}–{q['p95']:.2f}"
        L.append(f"| {g['gun']['saint'] or g['uari'].split(':')[1]} | {g['gun']['type']} | {rng} | "
                 f"{g['acquisition']['date']} | {', '.join(h['candidates'])} | {h['rule_source']} |")
    L += ["", "## A prediction to test when positions are found (HYPOTHESIS)", "",
          "If the ships grounded on an outer bar in the breaker line, heeled shoreward and broke up fast, "
          "the castles would fall inshore. Guns mounted high should then lie inshore of the keel line, and "
          "heavy low guns near the keel and ballast. Stated as an ordering: distance inshore of the keel "
          "line increases with `height_rank`. Salvage, later storms (the 2015 exposure) and incomplete "
          "recovery all blur this, so it is a tendency to test, not a rule.", ""]
    return "\n".join(L)


def main():
    guns = [gun_signal(g) for g in read("juliana_guns.csv")]
    rows = read("lisbon_muster_1588.csv")
    musters = [muster_signal(r) for r in rows if r["ship"] in STREEDAGH]
    lev = [r for r in rows if r["squadron"] == "Levant" and int(r["no"]) <= 77]
    fleet = {"tons_per_soldier": round(sum(int(r["tons"]) for r in lev) / sum(int(r["soldiers"]) for r in lev), 2),
             "tons_per_seaman": round(sum(int(r["tons"]) for r in lev) / sum(int(r["seamen"]) for r in lev), 2)}

    store = json.load(open(STORE, encoding="utf-8"))
    new = {s["uari"]: s for s in guns + musters}   # existing ids (SIG-G-SEVERO, SIG-G-MATRONA) are replaced in place
    out, seen = [], set()
    for s in store["signals"]:
        if s["uari"] in new:
            out.append(new[s["uari"]]); seen.add(s["uari"])
        else:
            out.append(s)
    out += [s for u, s in new.items() if u not in seen]
    store["signals"] = out
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "juliana_guns_report.md"), "w", encoding="utf-8") as f:
        f.write(report(guns, musters, fleet))
    print(f"{len(guns)} gun signals, {len(musters)} muster signals upserted into {os.path.relpath(STORE, HERE)};"
          f" {len(store['signals'])} signals in the store")


if __name__ == "__main__":
    main()
