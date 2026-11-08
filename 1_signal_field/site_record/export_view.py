"""
The site record as page data: one compact JSON for the web pages and the downstream planning tools.

    .venv/bin/python 1_signal_field/site_record/export_view.py      (or: make view)

Reads only site_record/streedagh_site.json (run `make site` first) and writes
output/site_view.json. Nothing is re-derived: every value is copied from a record, and every
item carries `ref`, the id of the record it came from, so a page can always say where a number
came from. Positions stay null until real ones are held (the record says why for each).

Also writes output/signal_chains.json: every trace followed from the act of looking, through the
carriers that hold it, to what is inferred from it (for the "From trace to ship" page).

Replaces the v3 store and its GeoJSON view (superseded/v3_store/), whose coordinates were
placeholders.
"""

import datetime as dt
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RECORD = os.path.join(HERE, "streedagh_site.json")
OUT = os.path.join(os.path.dirname(HERE), "output", "site_view.json")
P = "pipeline.streedagh"
SHIPS = {"src:ship-juliana": "Juliana", "src:ship-lavia": "Lavia", "src:ship-vison": "Vison"}
MUSTER_ROW = {"Juliana": "75", "Lavia": "69", "Vison": "76"}


def qv(q):
    """a quantity as {value | interval, unit}, keeping only what a page needs."""
    out = {}
    if "value" in q:
        out["value"] = q["value"]
    if "interval" in q:
        out["interval"] = q["interval"]
    if "absent" in q:
        out["absent"] = q["absent"]["reason"]
    u = q.get("unit")
    out["unit"] = u["verbatim"] if isinstance(u, dict) else u
    if q.get("note"):
        out["note"] = q["note"]
    out["basis"] = q.get("basis", {}).get("kind")
    return out


def verbatim(det):
    h = det.get("extension", {}).get("historical_observation", {})
    v = h.get("verbatim", {})
    return {"text": v.get("text"), "locator": v.get("locator"), "observer_role": h.get("observer_role")} if v else None


def main():
    raw = open(RECORD, "rb").read()
    R = json.loads(raw)
    det = {d["detection_id"]: d for d in R["detections"]}
    inf = {i["inference_id"]: i for i in R["inferences"]}
    by_subject = {}
    for i in R["inferences"]:
        for s in i["subject"]:
            by_subject.setdefault(s, []).append(i)
    attrs = lambda sig: [{"to": SHIPS.get(i["statement"]["source"], i["statement"]["source"]),
                          "p": i["statement"]["probability"], "by": i["agent"].split("/")[-1], "ref": i["inference_id"]}
                         for i in by_subject.get(sig, []) if i["kind"] == "attribution"]

    # the magnetometer spreads
    sites = []
    for d in R["detections"]:
        if not d["detection_id"].startswith(f"det:{P}/magnetometer-1985#"):
            continue
        k = d["detection_id"].split("#")[1]
        sig = f"sig:{P}/mag-{k}"
        label = next((i["label"] for i in by_subject.get(sig, []) if i["kind"] == "label"), None)
        sites.append({"id": k, "ref": d["detection_id"], "signal": sig, "position": None,
                      "position_absent": d["position"]["absent"]["reason"],
                      "quantities": [qv(q) for q in d["quantities"]], "verbatim": verbatim(d),
                      "label_by_authors": label, "attributions": attrs(sig)})

    # the ships: muster, dimensions, predictions
    ships = {}
    for src, name in SHIPS.items():
        m = det.get(f"det:{P}/muster-1588#row-{MUSTER_ROW[name]}")
        dims = det.get(f"det:{P}/ratings-1588#{MUSTER_ROW[name]}")
        s = {"source": src, "muster": {"ref": m["detection_id"], "quantities": [qv(q) for q in m["quantities"]],
                                       "verbatim": verbatim(m)}}
        if dims:
            s["dimensions"] = {"ref": dims["detection_id"], "measured": True,
                               "metres": [qv(q) for q in dims["quantities"] if qv(q)["unit"] == "m"]}
        else:
            j = inf[f"inf:{P}/juliana/dimensions"]
            s["dimensions"] = {"ref": j["inference_id"], "measured": False,
                               "alternatives": j["statement"]["alternatives"], "residue": j["statement"]["residue"]}
        ships[name] = s

    # the recovered guns
    guns = []
    for sg in R["signals"]:
        d = det[sg["minted_by"]]
        if "/recovery-" not in d["detection_id"]:
            continue
        lab = next((i for i in by_subject.get(sg["signal_id"], []) if i["kind"] == "label"), None)
        guns.append({"id": sg["signal_id"].split("/")[-1], "ref": d["detection_id"], "signal": sg["signal_id"],
                     "recovered": d["acquisition"].split("-")[-1], "position": None,
                     "class_by_compiler": lab["label"] if lab else None,
                     "mass": [qv(q) for q in d["quantities"]],
                     "attributions": attrs(sg["signal_id"])})

    # what the divers reported at Site 1
    observations = [{"id": d["detection_id"].split("#")[1], "ref": d["detection_id"], "verbatim": verbatim(d)}
                    for d in R["detections"] if d["detection_id"].startswith(f"det:{P}/site1-survey#")]
    relations = [{"a": r["a"].split("#")[1], "b": r["b"].split("#")[1], "type": r["type"], "ref": r["relation_id"]}
                 for r in R["relations"]]

    # predictions and findings
    def expected(e):
        if not isinstance(e, dict):
            return e
        return {k: (qv(v) if isinstance(v, dict) and "semantic" in v else v) for k, v in e.items()}
    predictions = [{"ref": i["inference_id"], "subject": i["subject"] if len(i["subject"]) <= 3 else f"{len(i['subject'])} records",
                    "observable": i["statement"]["observable"], "expected": expected(i["statement"]["expected"]),
                    "stated_before": i["statement"].get("stated_before"), "credence": i["credence"],
                    "falsifier": i["falsifier"], "check": i["statement"].get("check")}
                   for i in R["inferences"] if i["kind"] == "prediction"]
    findings = [{"ref": i["inference_id"], "by": i["agent"].split("/")[-1],
                 "finding": i["statement"].get("finding"), "alternatives": i["statement"].get("alternatives"),
                 "residue": i["statement"].get("residue"), "credence": i["credence"]}
                for i in R["inferences"] if i["kind"] == "explanation" and i["agent"].endswith(("/budget", "/martin"))]

    view = {
        "generated": dt.date.today().isoformat(),
        "record": {"path": "1_signal_field/site_record/streedagh_site.json",
                   "sha256": hashlib.sha256(raw).hexdigest(),
                   "counts": {k: len(v) for k, v in R.items() if isinstance(v, list)}},
        "positions": {"held": False, "note": "no recovery or survey coordinates are held; every position is null "
                                             "and each record states why"},
        "sites": sites, "ships": ships, "guns": guns,
        "site1": {"observations": observations, "relations": relations},
        "predictions": predictions, "findings": findings,
        "cuellar": {"passages": sum(1 for d in R["detections"] if "/cuellar-letter-1589#" in d["detection_id"]),
                    "events": sum(1 for s in R["sources"] if s["source_id"].startswith("src:cuellar/"))},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(view, f, ensure_ascii=False, indent=1)
    CH = os.path.join(os.path.dirname(OUT), "signal_chains.json")
    ch = chains(R)
    with open(CH, "w", encoding="utf-8") as f:
        json.dump({"generated": view["generated"], "record_sha256": view["record"]["sha256"],
                   "counts": view["record"]["counts"], "chains": ch},
                  f, ensure_ascii=False, separators=(",", ":"))
    print(f"{CH}: {os.path.getsize(CH):,} bytes; {len(ch)} chains")
    SP = os.path.join(os.path.dirname(OUT), "seabed_page.json")
    with open(SP, "w", encoding="utf-8") as f:
        json.dump(seabed_page(R), f, ensure_ascii=False, separators=(",", ":"))
    print(f"{SP}: {os.path.getsize(SP):,} bytes")
    print(f"{OUT}: {os.path.getsize(OUT):,} bytes; {len(sites)} sites, {len(guns)} guns, "
          f"{len(predictions)} predictions, {len(findings)} findings")


# ── chains: one trace followed from the act of looking to the ship (for "From trace to ship") ──
SITE1_TITLE = {"CONCRETION": "The concretion", "ANCHORS": "Three anchors on the concretion",
               "GUNS3": "Three bronze guns on the concretion", "RUDDER": "The rudder",
               "GUN-UNDER-RUDDER": "A bronze gun under the rudder", "WHEELS": "Five spoked wheels"}
TAGS = {"stated": "source", "measured": "source", "derived": "derived", "inference": "inferred"}
KIND_WORD = {"label": "label", "attribution": "attribution", "identification": "identification",
             "path_event": "path event", "source_event": "dated event", "explanation": "explanation",
             "prediction": "prediction"}


def year_of(v):
    """a calendar value ('1588-05-09', '2015-07', 1985) as a decimal year."""
    if isinstance(v, (int, float)):
        return float(v) + 0.5
    parts = [int(x) for x in str(v).split("-")]
    y, m, d = (parts + [7, 1])[:3] if len(parts) == 1 else (parts + [15])[:3] if len(parts) == 2 else parts
    return y + (m - 1) / 12 + (d - 1) / 365.25


def epoch_span(ep):
    if "value" in ep:
        y = year_of(ep["value"])
        return [y, y]
    lo, hi = ep["interval"]
    return [year_of(lo), year_of(hi)]


def tau_span(t):
    if "interval" in t:
        a, b = t["interval"]
        return [round(2000 - max(a, b), 4), round(2000 - min(a, b), 4)]
    return [round(2000 - t["value"], 4)] * 2


def agent_name(R, a):
    return next((x["name"] for x in R["agents"] if x["agent_id"] == a), a)


def chains(R):
    det = {d["detection_id"]: d for d in R["detections"]}
    acq = {a["acquisition_id"]: a for a in R["acquisitions"]}
    cat = {c["entry_id"]: c for c in R["catalogue_entries"]}
    src = {x["source_id"]: x for x in R["sources"]}
    subj = {}
    for i in R["inferences"]:
        for x in i["subject"]:
            subj.setdefault(x, []).append(i)

    def carriers(d):
        out, seen, todo = [], set(), list(d.get("read_from", []))
        while todo:
            e = todo.pop(0)
            if e in seen or e not in cat:
                continue
            seen.add(e)
            c = cat[e]
            if (e not in d.get("read_from", []) and c.get("source_acquisitions")
                    and d["acquisition"] not in c["source_acquisitions"]):
                continue                      # a publication of a different act (e.g. the 2015 recovery for a 1985 gun)
            out.append({"ref": e, "title": c["catalogue"]["designation"], "year": c["compilation_epoch"]["value"],
                        "held": bool(c["raw"]), "by": agent_name(R, c["catalogue"]["compiler"])})
            todo += c.get("source_entries", [])
        return sorted(out, key=lambda c: c["year"])

    def inf_step(i):
        k = i["kind"]
        st = i.get("statement", {})
        claim = isinstance(i.get("credence"), dict)
        tag = ("source" if claim else "hypothesis" if k == "prediction" or i["agent"].endswith("/dylan") and k == "explanation"
               else "inferred")
        step = {"tag": tag, "kind": ("claim by the compiler" if claim else KIND_WORD.get(k, k)), "ref": i["inference_id"],
                "by": agent_name(R, i["agent"]), "credence": None if claim else i.get("credence"),
                "falsifier": None if claim else i.get("falsifier")}
        if k == "label":
            step["text"] = i.get("label")
            step["detail"] = {kk: vv for kk, vv in st.items() if kk in ("gloss", "reading", "type", "muzzle_mouldings", "heading", "motion_vector", "magnitude")}
        elif k == "attribution":
            to = st["source"]
            name = src[to]["designations"][0]["name"] if to in src else to
            kind_src = src[to]["kind"] if to in src else "object"
            step["text"] = (f"attributed to {name}" if kind_src == "agent" else f"part of {name}" if kind_src == "event"
                            else f"belongs to {name}")
            step["p"] = st["probability"]
            step["to"] = to
        elif k == "identification":
            step["text"] = st.get("note", "same trace as " + ", ".join(st.get("same_as", [])))
            step["p"] = st.get("probability")
        elif k == "path_event":
            step["text"] = f"{st['type']}: to {st.get('to', '?')}" + (f" ({st['note']})" if st.get("note") else "")
            step["when"] = tau_span(st["tau"])
        elif k == "source_event":
            step["text"] = st.get("why", "")
            step["when"] = tau_span(st["tau"])
        elif k == "explanation":
            step["text"] = st.get("finding") or ("one of: " + ", ".join(a if isinstance(a, str) else a.get("method", "?") for a in st.get("alternatives", [])))
            step["residue"] = st.get("residue")
        elif k == "prediction":
            step["text"] = st.get("observable")
            exp = st.get("expected")
            step["expected"] = (exp if isinstance(exp, str) else {kk: qv(vv) if isinstance(vv, dict) and "semantic" in vv else vv
                                                                   for kk, vv in exp.items()} if isinstance(exp, dict) else exp)
            step["stated_before"] = st.get("stated_before")
        return step

    order = {"label": 0, "identification": 1, "path_event": 2, "attribution": 3, "explanation": 5, "prediction": 6}

    def chain(cid, group, title, d, sig=None):
        a = acq[d["acquisition"]]
        steps = [{"tag": "source", "kind": "the act of looking", "ref": a["acquisition_id"],
                  "text": a["method"].replace("_", " "), "by": ", ".join(agent_name(R, x["agent"]) for x in a["agents"]),
                  "when": epoch_span(a["epoch"]), "blind_spots": a.get("completeness", {}).get("blind_spots")}]
        v = verbatim(d)
        steps.append({"tag": "source", "kind": "what the carrier says", "ref": d["detection_id"],
                      "quote": v["text"] if v else None, "locator": v["locator"] if v else None,
                      "observer_role": v["observer_role"] if v else None,
                      "hedges": d.get("extension", {}).get("historical_observation", {}).get("hedges", []),
                      "position": None, "position_absent": d["position"].get("absent", {}).get("reason")})
        for q in d.get("quantities", []):
            if "absent" in q:
                continue
            b = q.get("basis", {}).get("kind", "stated")
            steps.append({"tag": TAGS.get(b, "source"), "kind": "quantity" if b != "derived" else "derived quantity",
                          "ref": d["detection_id"], "value": qv(q),
                          "recipe": q.get("basis", {}).get("recipe", {}).get("name")})
        for r in R["relations"]:
            if d["detection_id"] in (r["a"], r["b"]):
                other = r["b"] if r["a"] == d["detection_id"] else r["a"]
                steps.append({"tag": "source", "kind": "observed relation", "ref": r["relation_id"],
                              "text": (f"{r['a'].split('#')[1]} {r['type']} {r['b'].split('#')[1]}"), "other": other,
                              "by": agent_name(R, r["agent"])})
        infs = subj.get(d["detection_id"], []) + (subj.get(sig, []) if sig else [])
        infs = sorted(infs, key=lambda i: (order.get(i["kind"], 4), i["inference_id"]))
        for i in infs:
            st = inf_step(i)
            steps.append(st)
            to = st.get("to")
            if i["kind"] == "attribution" and to in src and to.startswith("src:cuellar/"):
                for e in subj.get(to, []):
                    if e["kind"] == "source_event":
                        steps.append(inf_step(e) | {"of": src[to]["designations"][0]["name"]})
        return {"id": cid, "group": group, "title": title, "signal": sig, "carriers": carriers(d), "steps": steps}

    out = []
    for sg in R["signals"]:
        d = det[sg["minted_by"]]
        did = d["detection_id"]
        if "/recovery-" in did:
            lab = next((i["label"] for i in subj.get(sg["signal_id"], []) if i["kind"] == "label"), "")
            out.append(chain(sg["signal_id"].split("/")[-1], "guns", f"{lab}, raised {d['acquisition'][-4:]}", d, sg["signal_id"]))
        elif "/magnetometer-1985#" in did:
            out.append(chain(did.split("#")[1], "magnetometry", did.split("#")[1].replace("SITE", "Site ") + " spread", d, sg["signal_id"]))
        elif "/site1-survey#" in did:
            k = did.split("#")[1]
            out.append(chain(k, "site1", SITE1_TITLE.get(k, k.title()), d, sg["signal_id"]))
    for name, row in MUSTER_ROW.items():
        for key, grp in ((f"det:{P}/muster-1588#row-{row}", "documents"), (f"det:{P}/ratings-1588#{row}", "documents")):
            if key in det:
                out.append(chain(key.split("/")[-1], grp, f"{name}: {'Lisbon muster, 9 May 1588' if 'muster' in key else 'measured at Lisbon, 1588'}", det[key]))
    for d in R["detections"]:
        if "/cuellar-letter-1589#" in d["detection_id"]:
            sid = d["detection_id"].split("#")[1]
            lab = next((i for i in subj.get(d["detection_id"], []) if i["kind"] == "label"), None)
            out.append(chain(sid, "cuellar", f"{sid}: {lab['statement'].get('gloss', '') if lab else ''}", d))
    return out


# ── "What went down, and what it would take": the budget, the museum brackets, the predictions ──
# The headline figures and predictions come from the site record; the component breakdown and the
# capacity brackets from the budget's own outputs (mass_budget.json, museum_capacity.json), which
# the record's predictions cite. Each component says how it is known and where its anchor comes from.
COMPONENTS = [
    ("hull_timber", "hull_timber", "timber_to_seabed", "Hull timber", "inferred",
     "hull-form model on the measured dimensions (AGS GA 223/28, Martin App. 11 p. 411); the hull taken as 35-55% of the laden displacement (an assumption)"),
    ("ballast", "ballast", "ballast", "Ballast", "inferred",
     "scaled from the Santa María de la Rosa's excavated mound, about 90 t (Martin p. 150)"),
    ("cargo", "cargo", "cargo_to_seabed", "Siege cargo", "inferred",
     "the Valencera's May 1588 issue list as the comparison (Martin pp. 115-116); Juliana's five carriage wheels"),
    ("rig", "rig", "rig_to_seabed", "Masts, yards, sails, cordage", "hypothesis",
     "8-15% of the hull (an assumption)"),
    ("ordnance", "ordnance_munitions", "ordnance_munitions", "Guns, shot, powder, lead, match", "derived",
     "the Lisbon muster's counts (Martin App. 4) times the libra and quintal (Martin p. ix); Juliana's weight-marked guns"),
    ("metal", "metal_fittings_anchors", "metal_fittings_anchors", "Iron fittings and anchors", "inferred",
     "iron-fastened Levant hulls (Martin p. 217); 4-10% of the hull"),
    ("stores", "stores", "stores_to_seabed", "Food, wine, water, casks", "inferred",
     "Medina Sidonia's ration scale (Martin pp. 349-350); days left by 25 September assumed"),
    ("arms", "personal_arms", "personal_arms", "Soldiers' arms", "hypothesis",
     "6-14 kg per soldier mustered (an assumption)"),
]


def seabed_page(R):
    out_dir = os.path.dirname(OUT)
    B = json.load(open(os.path.join(out_dir, "mass_budget.json"), encoding="utf-8"))
    M = json.load(open(os.path.join(out_dir, "museum_capacity.json"), encoding="utf-8"))
    inf = {i["inference_id"]: i for i in R["inferences"]}
    L2 = B["layer2"]["ships"]
    ships = {}
    for ship in ("Combined", "Juliana", "Lavia", "Vison"):
        d = L2[ship]
        comps = [{"key": k, "label": lab, "tag": tag, "basis": basis, "aboard": d[a], "to_seabed": d[sb]}
                 for k, a, sb, lab, tag, basis in COMPONENTS]
        ships[ship] = {"aboard": d["on_board_excl_people"], "to_seabed": d["to_seabed"], "to_strand": d["to_strand"],
                       "people_t": d["people"], "ferrous": d["ferrous_to_seabed"], "components": comps,
                       "ref": f"inf:{P}/mass-budget/" + ("combined" if ship == "Combined" else f"layer2-{ship.lower()}")}
        if ship != "Combined":
            ships[ship] |= {"men": d["men"], "dims_m": d["dims_m_median"], "draught_laden": d["draught_full_m"],
                            "draught_day": d["draught_day_m"], "may_over_laden": d["may_over_full"],
                            "measured": ship != "Juliana"}
    preds = [{"ref": i["inference_id"], "title": i["inference_id"].split("/", 1)[1],
              "observable": i["statement"]["observable"],
              "expected": (i["statement"]["expected"] if isinstance(i["statement"]["expected"], str) else
                           {k: qv(v) if isinstance(v, dict) and "semantic" in v else v
                            for k, v in i["statement"]["expected"].items()}),
              "stated_before": i["statement"].get("stated_before"), "credence": i["credence"],
              "falsifier": i["falsifier"], "by": agent_name(R, i["agent"])}
             for i in R["inferences"] if i["kind"] == "prediction"]
    return {"generated": dt.date.today().isoformat(),
            "record_sha256": hashlib.sha256(open(RECORD, "rb").read()).hexdigest(),
            "headline": inf[f"inf:{P}/mass-budget/combined"]["statement"]["expected"],
            "ships": ships, "drivers": dict(list(B["layer2"]["drivers"].items())[:6]),
            "museum": {"brackets": M["brackets"], "guns_documented": M["guns_documented"],
                       "guns_already_raised": M["guns_already_raised"], "la_belle_chamber_m3": M["la_belle_chamber_m3"],
                       "priors": M["priors"]},
            "predictions": preds}


if __name__ == "__main__":
    main()
