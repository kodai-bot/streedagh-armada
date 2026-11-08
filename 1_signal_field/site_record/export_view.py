"""
The site record as page data: one compact JSON for the web pages and the downstream planning tools.

    .venv/bin/python 1_signal_field/site_record/export_view.py      (or: make view)

Reads only site_record/streedagh_site.json (run `make site` first) and writes
output/site_view.json. Nothing is re-derived: every value is copied from a record, and every
item carries `ref`, the id of the record it came from, so a page can always say where a number
came from. Positions stay null until real ones are held (the record says why for each).

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
    print(f"{OUT}: {os.path.getsize(OUT):,} bytes; {len(sites)} sites, {len(guns)} guns, "
          f"{len(predictions)} predictions, {len(findings)} findings")


if __name__ == "__main__":
    main()
