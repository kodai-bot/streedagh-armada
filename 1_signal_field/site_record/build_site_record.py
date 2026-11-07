"""
Build the Streedagh site record: one signal_schema (v0.4) bundle, in JSON.

    .venv/bin/python 1_signal_field/site_record/build_site_record.py      (or: make site)

Reads the hand-edited tables in ../data/ and writes streedagh_site.json beside this
script. Design: ../SITE_SIGNAL_DESIGN.md. Validate with the schema's own CLI:

    cd Signal_Pipeline/signal_schema && uv run signal-schema validate \
        ../../Archaeology/Armada/1_signal_field/site_record/streedagh_site.json

What goes in: the recovered guns, the Lisbon muster, the observed relations at Site 1,
Cuéllar's letter (125 coded passages, from ../../3_cuellar_worldline/data/) and the
inferences built on them. The reconstruction's inputs and the magnetometry come next.
Positions are absent: none are held yet.

Records follow the schema's rules: detections hold only what was observed or stated
(verbatim where stated); every class word ("saker", "petriere", "Type C") is a label
inference by whoever used it; dates on a path are path_event inferences, never fields.
"""

import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
CUELLAR = os.path.join(os.path.dirname(os.path.dirname(HERE)), "3_cuellar_worldline")
OUT = os.path.join(HERE, "streedagh_site.json")
P = "pipeline.streedagh"                      # producer name in every minted id
CANTARO_KG = 47.65
V = "0.3.0"                                  # record schema versions used by the examples


def tau(year, month=1, day=1.0, calendar="gregorian"):
    """Years before J2000.0 (mirrors signal_schema/src/signal_schema/tau.py; Meeus ch. 7)."""
    y, m = (year - 1, month + 12) if month <= 2 else (year, month)
    b = 0
    if calendar == "gregorian":
        a = y // 100
        b = 2 - a + a // 4
    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + day + b - 1524.5
    return round((2451545.0 - jd) / 365.25, 4)


def tau_year(year):
    return {"semantic": "time.tau", "interval": [tau(year + 1), tau(year)], "unit": "a"}


def tau_days(lo, hi):
    """Gregorian dates 'YYYY-MM-DD', inclusive, as a τ interval (whole days)."""
    a, b = [int(x) for x in lo.split("-")], [int(x) for x in hi.split("-")]
    return {"semantic": "time.tau", "interval": [tau(b[0], b[1], b[2] + 1.0), tau(a[0], a[1], float(a[2]))], "unit": "a"}


def read(name, folder=DATA):
    with open(os.path.join(folder, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def hdr(family):
    return {"schema": f"signal_schema/{family}/{V}"}


def stated(refs):
    return {"kind": "stated", "refs": refs}


# ── agents ───────────────────────────────────────────────────────────────────
AGENTS = [
    ("sag", "organisation", "Streedagh Armada Group (divers, 1985 discovery and recovery)"),
    ("nms", "organisation", "National Monuments Service, Underwater Archaeology Unit (2015 recovery)"),
    ("muster-clerks", "person", "clerks of the Lisbon muster, May 1588 (unnamed)"),
    ("paz-salas", "organisation", "Pedro de Paz Salas, printer, Lisbon (1588 edition of the muster)"),
    ("martin", "person", "Colin J. M. Martin"),
    ("ridella", "person", "Renato Gianni Ridella and co-authors (2016)"),
    ("birch-mcelvogue", "person", "Steven Birch and Daniel M. McElvogue"),
    ("mcelvogue", "person", "Daniel M. McElvogue"),
    ("moore", "person", "Fionnbarr Moore and co-authors (2015)"),
    ("cuellar", "person", "Francisco de Cuéllar, captain, survivor of La Lavia"),
    ("duro", "person", "Cesáreo Fernández Duro (editor, La Armada Invencible, 1885)"),
    ("crawford", "person", "Robert Crawford (translator, 1897)"),
    ("exclassics", "organisation", "The Ex-classics Project (digital edition, 2021)"),
    ("dylan", "person", "Dylan Foley"),
    ("v1", "software", "build_site_record.py"),
    ("estimator", "software", "attribution_estimator.py v0.2"),
]
A = {k: f"agt:{P}/{k}" for k, _, _ in AGENTS}


def agents():
    out = []
    for k, kind, name in AGENTS:
        rec = {"agent_id": A[k], "kind": kind, "name": name}
        if kind == "software":
            rec["version"] = "0.1"
        out.append(rec)
    return out


# ── catalogue entries ────────────────────────────────────────────────────────
# Source PDFs held locally in sources/ (never committed; see the repo README)
HELD = {
    "martin": ("a0780bfb8d80dbd26c964c554171f294efd700c43bfca7ea34249be6c09b80f1", "sources/ColinMartinPhDThesis.pdf"),
    "ridella": ("392021ca4496353dbbccfaca62c1130970afbe52d939a20e2e122b8ac8e81ced",
                "sources/The_Cadiz-Delta_II_wreck_the_San_Giorgio.pdf"),
    "birch": ("5b6a87d9c7eda206a3a4f07f92b823d2bfd99abf09f4313717c96742db5046f1", "sources/ArmadaWrecksStreedagh.pdf"),
    "cuellar": ("18086133cf90cb8c3063f05b44f6456f44fb47eaacb2727d22b0f2509feda18f", "sources/cuellar.pdf"),
}


def cat(key, designation, compiler, role, native_key, year, fields, mandate, held=None,
        src_acq=(), src_entries=(), fidelity=None):
    raw = []
    if held:
        sha, uri = HELD[held]
        raw = [{"sha256": sha, "media_type": "application/pdf", "kind": "publication", "uri": uri}]
    rec = {**hdr("catalogue_entry"), "entry_id": f"cat:{key}",
           "catalogue": {"designation": designation, "compiler": A[compiler], "mandate": mandate},
           "role": role, "native_key": native_key,
           "compilation_epoch": {"value": year, "calendar": "gregorian", "basis": {"kind": "stated"}},
           "fields_as_published": fields, "raw": raw,
           "source_acquisitions": list(src_acq), "source_entries": list(src_entries)}
    if fidelity:
        rec["fidelity"] = fidelity
    return rec


# ── build ────────────────────────────────────────────────────────────────────
def build():
    guns = read("juliana_guns.csv")
    muster = read("lisbon_muster_1588.csv")
    obs = {r["id"]: r for r in read("site1_observations.csv")}
    rels = read("site1_relations.csv")
    attributed = json.load(open(os.path.join(DATA, "streedagh_store_v3_attributed.json"), encoding="utf-8"))

    B = {"agents": agents(),
         "frames": [{**hdr("frame"), "frame_id": "frm:ITM", "crs": "EPSG:2157", "geographic": False,
                     "vertical_datum": "Malin Head OD",
                     "note": "Irish Transverse Mercator: the site frame (decision D7, 2026-11-07). No positions held yet."}],
         "acquisitions": [], "catalogue_entries": [], "detections": [], "relations": [],
         "signals": [], "inferences": [], "sources": [], "field_notes": []}
    acq, cats, dets, sigs, infs = (B["acquisitions"], B["catalogue_entries"], B["detections"],
                                   B["signals"], B["inferences"])

    # catalogue entries
    cats += [
        cat("paz-salas-1588/levant", "La felicissima armada… (muster, Lisbon: Pedro de Paz Salas, 1588)",
            "paz-salas", "compiler", "Squadron of Levant", 1588, {"absent": {"reason": "not_held"}},
            "printed edition of the fleet muster of 9 May 1588",
            src_acq=[f"acq:{P}/muster-1588"], fidelity="printed within days of the 9 May muster (Martin 1984 p. 439)"),
        cat("martin-1984/app4-p448", "Martin, The Equipment and Fighting Potential of the Spanish Armada (PhD, St Andrews 1984), App. 4",
            "martin", "compiler", "pp. 448-449", 1984, {"table": "Order of Battle, Squadron of Levant (rows 68-77)"},
            "doctoral thesis; appendix tabulating the Armada's order of battle", held="martin",
            src_entries=["cat:paz-salas-1588/levant"],
            fidelity="based on the Paz Salas edition and Medina Sidonia's summary relación of 14 May 1588"),
        cat("ridella-2016/tab1", "Ridella et al., 'The Cadiz-Delta II wreck: the San Giorgio…', Archeologia Postmedievale 20 (2016), tab. 1",
            "ridella", "compiler", "tab. 1", 2016, {"table": "Survived bronze guns cast by Dorino II Gioardi"},
            "journal article; catalogue of one founder's surviving guns", held="ridella",
            src_entries=["cat:mcelvogue-2002", "cat:moore-2015"]),
        cat("mcelvogue-2002", "McElvogue 2002 (1985 Streedagh recoveries)", "mcelvogue", "compiler", "—", 2002,
            {"absent": {"reason": "not_held"}}, "publication of the 1985 recoveries", src_acq=[f"acq:{P}/recovery-1985"]),
        cat("moore-2015", "Moore et al. 2015 (2015 Streedagh recovery)", "moore", "compiler", "—", 2015,
            {"absent": {"reason": "not_held"}}, "report of the 2015 recovery", src_acq=[f"acq:{P}/recovery-2015"]),
        cat("birch-mcelvogue-1999", "Birch & McElvogue, 'La Lavia, La Juliana and the Santa Maria de Vison…', IJNA 28.3 (1999) 265-276",
            "birch-mcelvogue", "compiler", "pp. 265-276", 1999, {"absent": {"reason": "not_held"}},
            "interim report on the three Streedagh wrecks", held="birch",
            src_acq=[f"acq:{P}/site1-survey"]),
    ]

    # acquisitions
    def acquisition(key, method, agent, role, epoch, perturbation, blind, note=None):
        rec = {**hdr("acquisition"), "acquisition_id": f"acq:{P}/{key}", "acquisition_class": "historical_observation",
               "perturbation": perturbation, "agents": [{"agent": A[agent], "role": role}], "method": method,
               "epoch": {"semantic": "time.epoch", **epoch}, "footprint": {"absent": {"reason": "not_held"}},
               "completeness": {"blind_spots": blind}, "resolved": True, "raw": []}
        if perturbation == "removal":
            rec["actuation"] = {"absent": {"reason": "not_recorded", "note": "how each gun was lifted is not in the held sources"}}
        if note:
            rec["note"] = note
        acq.append(rec)
    acquisition("muster-1588", "muster_list", "muster-clerks", "observer",
                {"value": "1588-05-09", "calendar": "gregorian", "basis": stated(["Martin 1984 p. 439"])}, "none",
                "states ships, men, guns and stores as mustered; says nothing of gun types or positions")
    acquisition("recovery-1985", "diver_recovery", "sag", "operator",
                {"value": 1985, "calendar": "gregorian", "basis": stated(["McElvogue 2002", "Ridella et al. 2016 tab. 1"])},
                "removal", "only what was exposed and lifted; recovery positions not held by this project")
    acquisition("recovery-2015", "diver_recovery", "nms", "operator",
                {"interval": ["2015-07", "2015-08"], "calendar": "gregorian",
                 "basis": stated(["Ridella et al. 2016 fig. 14 caption: 'recovered in July-August 2015'"])},
                "removal", "storm-exposed material only; recovery positions not held by this project")
    acquisition("site1-survey", "diver_survey", "sag", "observer",
                {"interval": [1985, 1998], "calendar": "gregorian", "basis": stated(["Birch & McElvogue 1999"])},
                "none", "what sand cover exposed in those seasons; reported as an interim summary")

    # ── guns ─────────────────────────────────────────────────────────────────
    gun_sig = {}
    latest = {}
    for s in attributed["signals"]:
        if s.get("entity_attributions"):
            jul = [a for a in s["entity_attributions"] if a["entity_signal_id"] == "streedagh:ENT-JUL"]
            if jul:
                latest[s["uari"]] = jul[-1]["confidence"]
    for g in guns:
        gid, year = g["id"], g["recovered"]
        a = f"acq:{P}/recovery-{year}"
        det = f"det:{P}/recovery-{year}#{gid}"
        sig = f"sig:{P}/{gid}"
        gun_sig[gid] = sig
        q = []
        mark = g["cantara_mark"]
        if mark and "?" not in mark:
            q.append({"semantic": "phys.mass", "value": float(mark), "unit": {"verbatim": "cantara"},
                      "basis": stated(["weight mark cast on the gun, as read by the compiler"])})
        elif mark:
            q.append({"semantic": "phys.mass", "absent": {"reason": "not_stated_in_carrier"},
                      "note": f"weight mark partly illegible: '{mark}' cantara"})
        lo, hi = float(g["mass_kg_low"]), float(g["mass_kg_high"])
        derived = {"semantic": "phys.mass", "unit": "kg",
                   "basis": {"kind": "derived", "recipe": {"name": "cantara_to_kg", "version": "1",
                                                            "params": {"kg_per_cantaro": CANTARO_KG}},
                             "refs": ["Ridella et al. 2016 (Genoese cantaro calibrated on the same founders)"]}}
        if "estimate" in g["mass_basis"]:
            derived = {"semantic": "phys.mass", "interval": [lo, hi], "unit": "kg",
                       "basis": {"kind": "inference", "refs": ["reconstruction v0.7 §29"],
                                 "caveat": "no weight mark; estimate whose basis is still to be documented"}}
        elif lo == hi:
            derived["value"] = lo
        else:
            derived["interval"] = [lo, hi]
        q.append(derived)
        row = (f"{g['type']} | {g['cast']} | C.ra {mark or 'no mark'} | {g['muzzle'] or '—'} | "
               f"{g['saint'] or '—'} on the reinforce | {year}, wreck of La Juliana, Streedagh Strand | {g['ref']}")
        dets.append({**hdr("detection"), "detection_id": det, "acquisition": a,
                     "read_from": ["cat:ridella-2016/tab1", "cat:mcelvogue-2002" if year == "1985" else "cat:moore-2015"],
                     "detected": True, "position": {"absent": {"reason": "not_held"}},
                     "quantities": q,
                     "descriptors": ([{"term": "relief", "value": g["saint"],
                                       "note": "the figure as identified by the compiler"}] if g["saint"] else []) +
                                    ([{"term": "inscription", "value": g["cast"]}] if g["cast"] and "?" not in g["cast"] else []),
                     "extension": {"historical_observation": {
                         "verbatim": {"text": row, "language": "en", "locator": "Ridella et al. 2016 tab. 1, row for this gun",
                                      "note": "the table row as printed, columns joined with ' | '"},
                         "observer_role": "compiler", "hedges": ["?"] if "?" in (g["cast"] + mark) else []}}})
        sigs.append({**hdr("signal"), "signal_id": sig, "minted_by": det, "direct_detections": [det]})

        # Ridella's class words, as his labels
        infs.append({**hdr("inference"), "inference_id": f"inf:{P}/{gid}/label-ridella", "agent": A["ridella"],
                     "kind": "label", "subject": [sig],
                     "statement": {"type": g["type"], "muzzle_mouldings": g["muzzle"] or None},
                     "label": g["type"], "credence": {"absent": {"reason": "reported_claim"}},
                     "falsifier": {"absent": {"reason": "reported_claim"}}, "basis": [det]})
        # casting: an inception on the path (the "vector back to the source")
        certain = "?" not in g["cast"]
        infs.append({**hdr("inference"), "inference_id": f"inf:{P}/{gid}/cast", "agent": A["v1"],
                     "kind": "path_event", "subject": [sig],
                     "statement": {"signal": sig, "type": "inception", "tau": tau_year(1570),
                                   "to": "Genoa (workshop of Dorino II Gioardi)",
                                   "note": "casting" + ("; year read from the gun" if certain else "; year assigned by the compiler, not read")},
                     "credence": 0.95 if certain else 0.6,
                     "falsifier": "the year on the gun is not its casting year (a recast or later inscription), "
                                  "or a founder other than Dorino is shown to have cast it",
                     "basis": [det, "cat:ridella-2016/tab1"]})
        # attribution to the founder's workshop and to the ship
        infs.append({**hdr("inference"), "inference_id": f"inf:{P}/{gid}/attr-dorino", "agent": A["v1"],
                     "kind": "attribution", "subject": [sig],
                     "statement": {"signal": sig, "source": "src:dorino-gioardi-workshop",
                                   "probability": 0.9 if certain else 0.7},
                     "credence": 0.9 if certain else 0.7,
                     "falsifier": "the founder's mark on this gun is not Dorino's D, or the gun differs from his known work",
                     "basis": [det, "cat:ridella-2016/tab1"]})
        pj = latest.get(f"streedagh:SIG-{gid}")
        if pj is not None:
            infs.append({**hdr("inference"), "inference_id": f"inf:{P}/{gid}/attr-juliana", "agent": A["estimator"],
                         "kind": "attribution", "subject": [sig],
                         "statement": {"signal": sig, "source": "src:ship-juliana", "probability": round(pj, 4),
                                       "note": "posterior from attribution_estimator.py over Juliana / Lavia / Vison / unknown"},
                         "credence": round(pj, 4),
                         "falsifier": "a recovery position shown to lie at another wreck, or a weight mark matching another ship's record",
                         "basis": [det]})
        # arrival on the seabed at Streedagh
        infs.append({**hdr("inference"), "inference_id": f"inf:{P}/{gid}/wreck", "agent": A["v1"],
                     "kind": "path_event", "subject": [sig],
                     "statement": {"signal": sig, "type": "displacement",
                                   "tau": {"semantic": "time.tau", "interval": [tau(1588, 9, 26), tau(1588, 9, 21)], "unit": "a",
                                           "note": "21-26 Sep 1588 Gregorian: the sources give 21 (project), 25 (Martin p. 110) and 26 (Ridella p. 27)"},
                                   "to": "seabed, Streedagh Strand", "note": "the wreck: from the ship to the seabed"},
                     "credence": round(pj, 4) if pj is not None else 0.7,
                     "falsifier": "the gun was not aboard La Juliana when she was wrecked",
                     "basis": [det, f"inf:{P}/{gid}/attr-juliana"] if pj is not None else [det]})

    # ── the muster ────────────────────────────────────────────────────────────
    ship_src = {"La Juliana": "src:ship-juliana", "La Lavia (almiranta)": "src:ship-lavia",
                "Santa Maria de Vison": "src:ship-vison"}
    for r in muster:
        key = r["no"]
        det = f"det:{P}/muster-1588#row-{key}"
        count = lambda col, what: {"semantic": "doc.count.stated", "value": int(r[col]), "unit": "1",
                                   "basis": stated([f"column '{what}'"]), "note": what}
        q = [{"semantic": "doc.rating.stated", "value": int(r["tons"]), "unit": {"verbatim": "tons"},
              "basis": stated(["column 'Tons'"])},
             count("soldiers", "Soldiers"), count("seamen", "Seamen"), count("guns", "Guns"), count("shot", "Shot")]
        q += [{"semantic": "phys.mass", "value": int(r[c]), "unit": {"verbatim": "quintales"},
               "basis": stated([f"column '{lab} (qtx)'"]), "note": lab}
              for c, lab in (("powder_qtx", "Powder"), ("lead_qtx", "Lead"), ("match_qtx", "Match"))]
        dets.append({**hdr("detection"), "detection_id": det, "acquisition": f"acq:{P}/muster-1588",
                     "read_from": ["cat:martin-1984/app4-p448"], "detected": True,
                     "position": {"absent": {"reason": "not_applicable"}}, "quantities": q, "descriptors": [],
                     "extension": {"historical_observation": {
                         "verbatim": {"text": f"{r['no']} {r['ship']} | {r['tons']} | {r['soldiers']} | {r['seamen']} | "
                                              f"{r['guns']} | {r['shot']} | {r['powder_qtx']} | {r['lead_qtx']} | {r['match_qtx']}"
                                              + (f" | 'Safe' list: {r['safe_list']}" if r["safe_list"] else "")
                                              + (" | 'Missing' list: X" if r["missing_list"] else ""),
                                      "language": "en", "locator": r["source"]},
                         "observer_role": "compiler", "reported_target": {"designation_verbatim": r["ship"]},
                         "hedges": []}}})
        if r["ship"] in ship_src:
            infs.append({**hdr("inference"), "inference_id": f"inf:{P}/muster-row-{key}/attr", "agent": A["v1"],
                         "kind": "attribution", "subject": [det],
                         "statement": {"detection": det, "source": ship_src[r["ship"]], "probability": 0.95},
                         "credence": 0.95,
                         "falsifier": "the muster names a different ship of the same name as the one wrecked at Streedagh",
                         "basis": [det, "cat:birch-mcelvogue-1999"]})

    # ── Site 1: what the divers reported, and how the things lay ─────────────
    obs_det = {}
    for k, o in obs.items():
        det = f"det:{P}/site1-survey#{k}"
        obs_det[k] = det
        dets.append({**hdr("detection"), "detection_id": det,
                     "acquisition": f"acq:{P}/recovery-1985" if o["epoch_hi"] == "1985" else f"acq:{P}/site1-survey",
                     "read_from": ["cat:birch-mcelvogue-1999"], "detected": True,
                     "position": {"absent": {"reason": "not_held"}}, "quantities": [], "descriptors": [],
                     "extension": {"historical_observation": {
                         "verbatim": {"text": o["verbatim"], "language": "en", "locator": o["locator"]},
                         "observer_role": "reporter", "hedges": []}}})
        sigs.append({**hdr("signal"), "signal_id": f"sig:{P}/site1-{k}", "minted_by": det, "direct_detections": [det]})
    for i, r in enumerate(rels, 1):
        B["relations"].append({**hdr("detection_relation"), "relation_id": f"rel:{P}/site1-{i}",
                               "a": obs_det[r["a"]], "b": obs_det[r["b"]], "type": r["type"],
                               "agent": A["sag"], "observed_at": "1985/1998",
                               "note": f"as reported in {r['ref']}"})
    # the three guns seen on the concretion are (probably) the three lifted in 1985
    lifted85 = [gun_sig[g["id"]] for g in guns if g["recovered"] == "1985"]
    infs.append({**hdr("inference"), "inference_id": f"inf:{P}/site1-GUNS3/ident", "agent": A["v1"],
                 "kind": "identification", "subject": [f"sig:{P}/site1-GUNS3"] + lifted85,
                 "statement": {"same_as": lifted85, "probability": 0.85,
                               "note": "the three guns on the concretion 'have been lifted'; Ridella's tab. 1 has three 1985 lifts"},
                 "credence": 0.85, "falsifier": "a 1985 recovery record listing different guns from the concretion",
                 "basis": [obs_det["GUNS3"], "cat:ridella-2016/tab1"]})

    # ── hypotheses: mounting stations and the break-up ───────────────────────
    stations = {"heavy": (["lower deck", "main deck"], "Martin 1984 p. 195: gun weight high above the centre of buoyancy limits a ship"),
                "petriere": (["lower deck", "main deck"], "Ridella et al. 2016 p. 29: petrieri 'very probably placed in the lower deck'"),
                "light": (["main deck", "castle deck 1"], "general; weak"),
                "very_light": (["castle deck 1", "castle deck 2+"], "Martin 1984 p. 298 (said of swivel guns; applied by analogy)")}
    for g in guns:
        hi = float(g["mass_kg_high"])
        k = "petriere" if "Petriere" in g["type"] else "heavy" if hi >= 800 else "light" if hi >= 250 else "very_light"
        alts, rule = stations[k]
        infs.append({**hdr("inference"), "inference_id": f"inf:{P}/{g['id']}/station", "agent": A["dylan"],
                     "kind": "explanation", "subject": [gun_sig[g["id"]]],
                     "statement": {"alternatives": alts, "residue": "which of these, and fore or aft: needs the castle model and positions",
                                   "frame": "ship frame (along the keel, across the beam, height above keel); kept inside this inference (D7)",
                                   "rule": rule},
                     "credence": 0.5, "falsifier": "a contemporary armament plan placing this class of gun elsewhere",
                     "basis": [f"inf:{P}/{g['id']}/label-ridella"]})
    breakup_pred = f"inf:{P}/breakup/prediction-inshore"
    infs.append({**hdr("inference"), "inference_id": breakup_pred, "agent": A["dylan"], "kind": "prediction",
                 "subject": [gun_sig[g["id"]] for g in guns],
                 "statement": {"observable": "signed distance inshore of each wreck's keel line, in the site frame (frm:ITM), "
                                             "for every recovered gun with a recovery position",
                               "expected": "distance inshore increases with mounting height (rank correlation > 0): "
                                           "castle pieces inshore, heavy low pieces near the keel and ballast",
                               "stated_before": "2026-11-07; no recovery positions held when stated"},
                 "credence": 0.55,
                 "falsifier": "light guns lie seaward of the keel line, or show no relation to mounting height",
                 "basis": [f"note:{P}/dylan-breakup-2026-11-07"]})

    cuellar(B)

    # ── sources ──────────────────────────────────────────────────────────────
    def supports(src):
        return [i["inference_id"] for i in infs if i["kind"] == "attribution" and i["statement"]["source"] == src]
    for sid, name in (("src:ship-juliana", "La Juliana"), ("src:ship-lavia", "La Lavia"), ("src:ship-vison", "Santa Maria de Vison")):
        sup = supports(sid)
        B["sources"].append({**hdr("source"), "source_id": sid, "kind": "object",
                             "designations": [{"name": name, "from": "cat:martin-1984/app4-p448"}],
                             "support": sup, "recipe": {"name": "attribution_chain", "version": "0.1"},
                             "created_by": sup[0], "status": "candidate"})
    sup = supports("src:dorino-gioardi-workshop")
    B["sources"].append({**hdr("source"), "source_id": "src:dorino-gioardi-workshop", "kind": "agent",
                         "designations": [{"name": "Dorino II Gioardi, gunfounder, Genoa (1519-1587)", "from": "cat:ridella-2016/tab1"}],
                         "support": sup, "recipe": {"name": "attribution_chain", "version": "0.1"},
                         "created_by": sup[0], "status": "candidate"})
    B["sources"].append({**hdr("source"), "source_id": "src:streedagh-breakup-1588", "kind": "event",
                         "designations": [{"name": "the wreck and break-up of the three ships at Streedagh, Sept 1588",
                                           "from": "cat:birch-mcelvogue-1999"}],
                         "support": [breakup_pred] + supports("src:streedagh-breakup-1588"),
                         "recipe": {"name": "breakup_sequence", "version": "0.1",
                                                               "params": {"stages": ["at anchor", "anchors fail", "driven onto the outer bar",
                                                                                     "heel shoreward", "castles collapse",
                                                                                     "release sorted by density", "burial"]}},
                         "created_by": breakup_pred, "status": "candidate",
                         "note": "stages from site assessment v2 (L2, Part II) and Dylan's hypothesis of 2026-11-07"})
    B["field_notes"].append({**hdr("field_note"), "note_id": f"note:{P}/dylan-breakup-2026-11-07", "agent": A["dylan"],
                             "created_at": "2026-11-07", "about": ["src:streedagh-breakup-1588", breakup_pred],
                             "language": "en",
                             "text": ("a guess from cuellars description is the ships are pushed into the heavy surf on a breaker line "
                                      "probably a parallel sandbar (we infer  this is likely as the beach itself is a large parallel "
                                      "sand bar creating a large lagoon, unusual topography in ireland even. the ships lean an break up "
                                      "rapidly and heavy guns would possibly accelrate this as the high castles collapse -- we might "
                                      "hypotheseis the highest mounted swivels might be found inshore from the keel - just a hypothesis "
                                      "but something to test")})
    return B


# ── Cuéllar's letter (Antwerp, 4 Oct 1589) ───────────────────────────────────
# Each coded passage in 3_cuellar_worldline/data/cuellar_signal_map.csv becomes one detection.
# The verbatim span is the located passage in Crawford's translation (cuellar_spans.csv); the
# coder's short gloss ("anchor") is not a quotation, so it lives in the coding inference.
# A report of an event is not a physical trace: no signals are minted (decision D14). The
# detections are attributed straight to event Sources, one per worldline node.
TRUST = {"high": 0.85, "mid": 0.65, "low": 0.4}
SECOND_HAND = {"S002", "S011", "S022", "S092", "S104", "S106", "S107", "S108", "S109", "S119",
               "S124", "S131", "S148", "S150"}      # Cuéllar reports what he heard, not what he saw
HEDGES = ("more than", "about", "would be", "appeared", "may have", "rather more", "(?)",
          "not much fewer", "and odd")
BREAKUP = {"S015": 0.85, "S017": 0.85, "S018": 0.85, "S019": 0.85, "S020": 0.7, "S021": 0.75}
LAVIA = {"S010": ("the Judge Advocate General, Martín de Aranda, sailed in La Lavia "
                  "(site assessment v2; source still to be cited)", 0.8),
         "S013": ("La Lavia was of the Squadron of Levant; Cuéllar says his ship was 'from the Levant'", 0.75)}


def cuellar(B):
    acq, cats, dets, infs, srcs = (B["acquisitions"], B["catalogue_entries"], B["detections"],
                                   B["inferences"], B["sources"])
    coded = read("cuellar_signal_map.csv", os.path.join(CUELLAR, "data"))
    spans = {r["signal_id"]: r for r in read("cuellar_spans.csv", os.path.join(CUELLAR, "data"))}
    nodes = read("worldline_intervals.csv", os.path.join(CUELLAR, "output"))
    a = f"acq:{P}/cuellar-letter-1589"

    acq.append({**hdr("acquisition"), "acquisition_id": a, "acquisition_class": "historical_observation",
                "perturbation": "none", "agents": [{"agent": A["cuellar"], "role": "observer"}],
                "method": "written_report",
                "epoch": {"semantic": "time.epoch", "value": "1589-10-04", "calendar": "gregorian",
                          "basis": stated(["closing line: 'From the City of Antwerp, 4th October, 1589.'"])},
                "footprint": {"absent": {"reason": "not_applicable"}},
                "completeness": {"blind_spots": "one survivor's account, written about a year after the wreck; "
                                                "tells what he saw, suffered or was told, and omits what did not concern him"},
                "resolved": True, "raw": [],
                "note": "the letter itself (Spanish) is reached through Duro's edition and Crawford's translation"})
    cats += [
        cat("duro-1885/cuellar", "Fernández Duro, La Armada Invencible, vol. 2 (Madrid, 1885): Cuéllar's letter",
            "duro", "editor", "Cuéllar's letter", 1885, {"absent": {"reason": "not_held"}},
            "printed edition of Armada documents; first publication of the letter", src_acq=[a]),
        cat("crawford-1897/cuellar", "Crawford (trans.), Narrative of the Spanish Armada, by Captain Francisco de "
            "Cuéllar (1897); Ex-classics Project edition, 2021", "crawford", "translator", "pp. 10-27", 1897,
            {"text": "English running text, pages marked -n-"},
            "English translation of Cuéllar's letter, made 'to follow closely the wording of the original Spanish'",
            held="cuellar", src_entries=["cat:duro-1885/cuellar"],
            fidelity="literal translation (translator's preface, 1897); page numbers are the Ex-classics edition's"),
    ]

    det_of = {}
    for r in coded:
        sid = r["signal_id"]
        sp = spans[sid]
        det = f"det:{P}/cuellar-letter-1589#{sid}"
        det_of[sid] = det
        text = sp["span"]
        note = "Crawford's English, not Cuéllar's Spanish; running page headers removed"
        if "[...]" in text:
            note += "; two nearby passages joined, the gap marked [...]"
        dets.append({**hdr("detection"), "detection_id": det, "acquisition": a,
                     "read_from": ["cat:crawford-1897/cuellar"], "detected": True,
                     "position": {"absent": {"reason": "not_stated_in_carrier"}}, "quantities": [], "descriptors": [],
                     "extension": {"historical_observation": {
                         "verbatim": {"text": text, "language": "en", "locator": f"Crawford trans., p. {sp['page']}",
                                      "note": note},
                         "observer_role": "reporter" if sid in SECOND_HAND else "eyewitness",
                         "hedges": [h.strip() for h in HEDGES if h in text.lower() or h in text]}}})
        stmt = {"signal_class": r["signal_class"], "episode": r["episode"], "gloss": r["anchor"],
                "reading": r["inference"], "page_coded": r["page"]}
        if r["motion_vector"] not in ("", "-"):
            stmt["motion_vector"] = r["motion_vector"]
        if r["magnitude"] not in ("", "-"):
            stmt["magnitude"] = r["magnitude"]
        if sp["covers_gloss"] == "partial":
            stmt["note"] = "the verbatim span carries only part of the gloss; the rest is in the text nearby"
        infs.append({**hdr("inference"), "inference_id": f"inf:{P}/cuellar/{sid}/coding", "agent": A["dylan"],
                     "kind": "label", "subject": [det], "label": r["signal_class"], "statement": stmt,
                     "credence": TRUST[r["trust"]],
                     "falsifier": "the passage, read in Duro's Spanish, does not say this, or says it of another place or time",
                     "basis": [det]})

    # worldline nodes: one event Source each, dated by a source_event
    for n in nodes:
        src = f"src:cuellar/{n['node']}"
        sup = []
        for sid in [x for x in n["signals"].split(";") if x]:
            iid = f"inf:{P}/cuellar/{sid}/at-{n['node']}"
            p = TRUST[next(r["trust"] for r in coded if r["signal_id"] == sid)]
            infs.append({**hdr("inference"), "inference_id": iid, "agent": A["dylan"], "kind": "attribution",
                         "subject": [det_of[sid]],
                         "statement": {"detection": det_of[sid], "source": src, "probability": p},
                         "credence": p, "falsifier": "the passage describes a different moment of the journey",
                         "basis": [det_of[sid], f"inf:{P}/cuellar/{sid}/coding"]})
            sup.append(iid)
        exact = n["lo_date"] == n["hi_date"]
        ev = f"inf:{P}/cuellar/{n['node']}/when"
        infs.append({**hdr("inference"), "inference_id": ev, "agent": A["dylan"], "kind": "source_event",
                     "subject": [src],
                     "statement": {"type": "creation", "outputs": [src], "tau": tau_days(n["lo_date"], n["hi_date"]),
                                   "why": f"{n['lo_date']} to {n['hi_date']} (Gregorian), from the worldline's day counts"
                                          + (f"; light test {n['light_test']}" if n["light_test"] else ""),
                                   "note": "an event Source is created when it happens (the schema has no 'occurrence' type)"},
                     "credence": 0.8 if exact else 0.6,
                     "falsifier": "an independent dated record (English state papers, another survivor) puts this event outside the interval",
                     "basis": [det_of[x] for x in n["signals"].split(";") if x]})
        srcs.append({**hdr("source"), "source_id": src, "kind": "event",
                     "designations": [{"name": n["event"], "from": "cat:crawford-1897/cuellar"}],
                     "support": sup, "recipe": {"name": "cuellar_worldline", "version": "0.1",
                                                "params": {"node": n["node"], "episode": n["episode"]}},
                     "created_by": sup[0], "worldline": [ev], "status": "candidate"})

    # his testimony also bears on the break-up and on his ship
    for sid, p in BREAKUP.items():
        infs.append({**hdr("inference"), "inference_id": f"inf:{P}/cuellar/{sid}/breakup", "agent": A["dylan"],
                     "kind": "attribution", "subject": [det_of[sid]],
                     "statement": {"detection": det_of[sid], "source": "src:streedagh-breakup-1588", "probability": p},
                     "credence": p, "falsifier": "Cuéllar's wreck was not at Streedagh (the identification of his strand fails)",
                     "basis": [det_of[sid]]})
    for sid, (why, p) in LAVIA.items():
        infs.append({**hdr("inference"), "inference_id": f"inf:{P}/cuellar/{sid}/ship", "agent": A["dylan"],
                     "kind": "attribution", "subject": [det_of[sid]],
                     "statement": {"detection": det_of[sid], "source": "src:ship-lavia", "probability": p, "note": why},
                     "credence": p, "falsifier": "a muster or relación placing Cuéllar or the Judge Advocate in another ship",
                     "basis": [det_of[sid], "cat:martin-1984/app4-p448"]})


def main():
    B = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(B, f, ensure_ascii=False, indent=1)
    n = {k: len(v) for k, v in B.items() if isinstance(v, list)}
    print(os.path.relpath(OUT), n)


if __name__ == "__main__":
    main()
