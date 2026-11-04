#!/usr/bin/env python3
"""AttributionEstimator (v0.2) — reference estimator for Signal Object V3.

Contract:  signals (V3) -> estimator (this) -> entity_attributions (V3), append-only.

Reads a V3 store, computes each L0 signal's posterior over candidate entities by
Bayesian accumulation of its `components` (with diagnostic_group correlation control)
plus a spatial likelihood, then APPENDS V3 `EntityAttribution` records. Also emits a
GeoJSON view for spatial tooling. Coordinates in the store are PLACEHOLDERS.
"""
import json, math, datetime, os
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

ENTITIES = ["Juliana", "Lavia", "Vison", "Unknown"]
GUN_COUNTS = {"Juliana": 32, "Lavia": 25, "Vison": 18}
JULIANA_SAINTS = {"St_Severo", "St_Giovanni_Battista", "St_Matrona", "St_Ilaria",
                  "St_Sebastiano", "St_Rocco", "St_Giovanni"}
BARCELONA_SAINT = "St_Matrona"
ENT_UARI = {"Juliana": "streedagh:ENT-JUL", "Lavia": "streedagh:ENT-LAV",
            "Vison": "streedagh:ENT-VIS", "Unknown": "streedagh:UNKNOWN"}
UARI_ENT = {v: k for k, v in ENT_UARI.items()}
ENGINE = "attribution_estimator/v0.2"

def prior():
    um = 0.10; tot = sum(GUN_COUNTS.values())
    p = {e: (1 - um) * GUN_COUNTS[e] / tot for e in GUN_COUNTS}; p["Unknown"] = um
    return p

def norm(d): s = sum(d.values()); return {k: v / s for k, v in d.items()}
def apply(post, L): return norm({e: post[e] * L[e] for e in ENTITIES})

# --- likelihood KB: P(diagnostic group observation | entity) ------------------
def lik_casting_provenance(): return {"Juliana": 0.85, "Lavia": 0.25, "Vison": 0.20, "Unknown": 0.15}
def lik_ship_programme(saint):
    L = {e: 0.02 for e in ENTITIES}; L["Unknown"] = 0.05
    if saint in JULIANA_SAINTS: L["Juliana"] = 0.97 if saint == BARCELONA_SAINT else 0.90
    return L
def lik_individual_id(match):
    return {"Juliana": 0.95, "Lavia": 0.05, "Vison": 0.05, "Unknown": 0.05} if match else {e: 1.0 for e in ENTITIES}
def lik_position(dist, scale=150.0):
    return {e: (math.exp(-dist[e] / scale) if e in dist else 0.10) for e in ENTITIES}

def hav(lon1, lat1, lon2, lat2):
    R = 6371000.0; p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1); dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def groups(components):
    g = {}
    for c in components:
        g.setdefault(c.get("diagnostic_group", "_" + c["type"]), []).append(c)
    return g

def estimate(sig, loci, verbose=False):
    lon, lat = sig["geometry"]["coordinates"]
    dist = {e: hav(lon, lat, loci[e][0], loci[e][1]) for e in loci}
    post = prior(); used = []
    def show(step):
        if verbose: print(f"    {step:34s} " + "  ".join(f"{e[:4]}={post[e]:.3f}" for e in ENTITIES))
    if verbose: print(f"  {sig['uari']}")
    show("prior (armament-weighted)")
    post = apply(post, lik_position(dist)); used.append("spatial"); show("+ spatial position")
    g = groups(sig.get("components", []))
    if "casting_provenance" in g:                      # founder_mark + casting_year combined ONCE
        post = apply(post, lik_casting_provenance()); used.append("casting_provenance"); show("+ casting provenance (grouped)")
    if "ship_programme" in g:
        saint = g["ship_programme"][0]["value"]
        post = apply(post, lik_ship_programme(saint)); used.append(f"ship_programme:{saint}"); show(f"+ ship programme ({saint})")
    if "individual_id" in g and g["individual_id"][0].get("matches_juliana_record"):
        post = apply(post, lik_individual_id(True)); used.append("individual_id"); show("+ individual id (weight-mark)")
    return post, used

def entity_attributions(post, used):
    now = datetime.datetime.utcnow().isoformat() + "Z"
    basis = "bayesian component accumulation [" + ", ".join(used) + "]; diagnostic-group correlation control"
    return [{"entity_signal_id": ENT_UARI[e], "confidence": round(post[e], 4),
             "basis": basis, "committed_at": now, "committed_by": ENGINE} for e in ENTITIES]

def geojson_view(store, path):
    feats = []
    for s in store["signals"]:
        top = None
        if s.get("entity_attributions"):
            best = max(s["entity_attributions"], key=lambda a: a["confidence"])
            top = {"entity": UARI_ENT.get(best["entity_signal_id"], "?"), "confidence": best["confidence"]}
        feats.append({"type": "Feature", "geometry": s["geometry"],
                      "properties": {"uari": s["uari"], "level": s["level"],
                                     "acquisition_class": s["acquisition_class"], "top_attribution": top}})
    json.dump({"type": "FeatureCollection", "features": feats}, open(path, "w"), indent=2)

def main():
    store = json.load(open(os.path.join(DATA, "streedagh_store_v3.json")))
    sigs = store["signals"]
    loci = {UARI_ENT[s["uari"]]: s["geometry"]["coordinates"]
            for s in sigs if s.get("level") == "L3" and s["uari"] in UARI_ENT}
    print("=== collapse trace (verbose for the two well-documented guns) ===")
    for s in sigs:
        if s.get("level") != "L0" or not s.get("components"):
            continue
        verbose = s["uari"] in ("streedagh:SIG-G-MATRONA", "streedagh:SIG-G-AMBIG")
        post, used = estimate(s, loci, verbose=verbose)
        s.setdefault("entity_attributions", []).extend(entity_attributions(post, used))  # append-only
        best = max(post, key=post.get)
        print(f"  {s['uari']:26s} -> {best} (p={post[best]:.3f})")
    json.dump(store, open(os.path.join(DATA, "streedagh_store_v3_attributed.json"), "w"), indent=2)
    geojson_view(store, os.path.join(DATA, "streedagh_view.geojson"))
    print("\nWrote streedagh_store_v3_attributed.json  +  streedagh_view.geojson")
    print("\n=== emitted V3 entity_attributions for SIG-G-MATRONA ===")
    m = next(s for s in sigs if s["uari"] == "streedagh:SIG-G-MATRONA")
    print(json.dumps(m["entity_attributions"], indent=2))

if __name__ == "__main__":
    main()
