import numpy as np
rng = np.random.default_rng(15880921)
N = 200_000
def tri(a,m,b,n=N): return rng.triangular(a,m,b,n)

# Payload ceilings (non-ballast embarked mass, t) from the hull model:
# median and 95th percentile per ship.
payload_cap = {
    "La Juliana":           (450, 579),
    "La Lavia":             (381, 489),
    "Santa Maria de Vison": (349, 448),
}
# tonnage scaler relative to La Juliana (860 t)
scale = {"La Juliana":1.00, "La Lavia":728/860, "Santa Maria de Vison":666/860}

# ---- Bottom-up DURABLE component masses for La Juliana (t); others scaled ----
# (triangular min, mode, max). Grounded in the finds + Trinidad Valencera template.
def components(name):
    s = scale[name]
    c = {}
    c["ballast_stone"]        = tri(120,180,240)*s      # ballast mound (mostly survives)
    c["ship_ironwork"]        = tri(8,14,22)*s          # bolts, knees-fastenings, nails, chainplates
    c["anchors_iron"]         = tri(3,5,8)              # 3-5 anchors ~1.2 t each (≈ size-independent)
    c["ordnance_bronze"]      = tri(6,12,20)*s          # bronze guns (sacre,minion,esmeril,pedrero...)
    c["ordnance_iron"]        = tri(4,9,16)*s           # iron guns
    c["siege_carriage_iron"]  = tri(1,3,6)*s            # wheel bosses/tyres + carriage ironwork
    c["shot_iron"]            = tri(2,5,10)*s
    c["shot_stone"]           = tri(1,3,6)*s
    c["lead"]                 = tri(1,4,9)*s            # sheeting, ingots, musket/shot lead
    c["ceramic_botijas"]      = tri(1,3,7)*s            # olive jars & storage ceramics
    # consumable/organic bulk (food, water-casks, fodder, cordage, timber cargo, powder):
    c["organic_bulk"]         = tri(80,150,250)*s
    return c

# ---- survival fractions (triangular) ----
def surv():
    return dict(
        bronze  = tri(0.95,0.99,1.00),
        iron    = tri(0.55,0.75,0.90),   # as concretion
        lead    = tri(0.85,0.93,0.99),
        stone   = tri(0.97,0.99,1.00),
        ceramic = tri(0.60,0.80,0.95),
        organic = tri(0.02,0.06,0.15),   # high-energy sand; survives only where buried
    )

def q(x): return np.percentile(x,[5,50,95])

print("=== Surviving archaeological mass by class (t): median [5th-95th] ===\n")
grand = {k:np.zeros(N) for k in ["bronze","iron","lead","stone","ceramic","organic"]}
for name in payload_cap:
    c = components(name); f = surv()
    iron_total  = c["ship_ironwork"]+c["anchors_iron"]+c["ordnance_iron"]+c["siege_carriage_iron"]+c["shot_iron"]
    stone_total = c["ballast_stone"]+c["shot_stone"]
    surv_mass = dict(
        bronze  = c["ordnance_bronze"]*f["bronze"],
        iron    = iron_total*f["iron"],
        lead    = c["lead"]*f["lead"],
        stone   = stone_total*f["stone"],
        ceramic = c["ceramic_botijas"]*f["ceramic"],
        organic = c["organic_bulk"]*f["organic"],
    )
    for k in grand: grand[k]+=surv_mass[k]
    durable = sum(surv_mass[k] for k in ["bronze","iron","lead","stone","ceramic"])
    asloaded = sum(c.values())                      # total durable+organic as loaded
    cap_med, cap_hi = payload_cap[name]
    print(f"--- {name} ---")
    for k in ["bronze","iron","lead","stone","ceramic","organic"]:
        v=q(surv_mass[k]); print(f"   {k:9s}{v[1]:6.1f} [{v[0]:5.1f}-{v[2]:6.1f}]")
    d=q(durable); print(f"   DURABLE total (excl organic): {d[1]:6.0f} [{d[0]:.0f}-{d[2]:.0f}] t")
    al=q(asloaded)
    print(f"   as-loaded durable+organic: {al[1]:.0f} [{al[0]:.0f}-{al[2]:.0f}] t  |  hull-model payload cap: {cap_med}-{cap_hi} t (95th)")
    print()

print("=== ALL THREE SHIPS COMBINED — surviving mass on site (t) ===")
tot_durable=np.zeros(N)
for k in ["bronze","iron","lead","stone","ceramic","organic"]:
    v=q(grand[k]); print(f"   {k:9s}{v[1]:6.0f} [{v[0]:5.0f}-{v[2]:6.0f}]")
for k in ["bronze","iron","lead","stone","ceramic"]: tot_durable+=grand[k]
d=q(tot_durable)
print(f"\n   TOTAL DURABLE on site (excl. organic): {d[1]:.0f} [{d[0]:.0f}-{d[2]:.0f}] t")
print(f"   of which ballast stone alone:          {q(grand['stone'])[1]:.0f} t (median)")
print(f"   UPPER BOUND (95th pct) durable on site: {d[2]:.0f} t")

# ----  STRUCTURAL TIMBER MASS — recovery infrastructure sizing  ----
# Independent rng so this section can be reordered without affecting existing outputs.
_rng_t = np.random.default_rng(20260701)
def _tri_t(a, m, b): return _rng_t.triangular(a, m, b, N)

# Displacement medians from streedagh_hull.py (point inputs; λ uncertainty captured below)
_disp = {
    "La Juliana":           1390.0,
    "La Lavia":             1177.0,
    "Santa Maria de Vison": 1077.0,
}

print("\n=== Structural timber — recovery infrastructure sizing (t) ===")
print("Basis: hull displacement × lightship fraction (λ) × hull-timber fraction of lightship.")
print("Construction ref: La Trinidad Valencera, same Levant-squadron class (Martin 1984, Ch.6):")
print("  solid-framed oak, 10 cm planking, iron fastenings throughout.")
print("  (Fastenings corrode to concretion — already in ship_ironwork above. Timber mass alone")
print("   survives as an additional component not captured in the cargo/artefact manifest.)")
print("Survival scenarios: fraction of original hull timber remaining sand-sealed on site.")
print("  No recorded salvage at Streedagh (Birch & McElvogue 1999); articulated timbers")
print("  confirmed in situ at Site 1. Scenarios span conservative (1/4) to optimistic (1/2).")
print()

_g25 = np.zeros(N);  _g33 = np.zeros(N);  _g50 = np.zeros(N)

for _name, _d in _disp.items():
    _lam = _tri_t(0.42, 0.50, 0.58)   # lightship fraction (same prior as hull model)
    _tf  = _tri_t(0.50, 0.58, 0.66)   # hull structural timber as fraction of lightship
    # Lightship breakdown: iron fastenings ~8% (corroded, in ship_ironwork above),
    # anchors+cables ~7% (in manifest), rigging ~6% (organic_bulk), masts+spars ~8%
    # (floated away post-wrecking), fixed equipment ~5%, other ~8%.
    # Remaining hull-structure timber (frames, planking, keel, keelson, beams): ~0.50-0.66.
    _t_orig = _d * _lam * _tf
    _t25    = _t_orig * 0.25
    _t33    = _t_orig / 3.0
    _t50    = _t_orig * 0.50
    _g25 += _t25;  _g33 += _t33;  _g50 += _t50
    _o   = q(_t_orig)
    _q25 = q(_t25);  _q33 = q(_t33);  _q50 = q(_t50)
    print(f"   {_name}")
    print(f"     Full-hull timber (original):  {_o[1]:.0f}  [{_o[0]:.0f}-{_o[2]:.0f}] t")
    print(f"     Survival 1/4:  {_q25[1]:.0f}  [{_q25[0]:.0f}-{_q25[2]:.0f}] t")
    print(f"     Survival 1/3:  {_q33[1]:.0f}  [{_q33[0]:.0f}-{_q33[2]:.0f}] t")
    print(f"     Survival 1/2:  {_q50[1]:.0f}  [{_q50[0]:.0f}-{_q50[2]:.0f}] t")
    print()

print(f"   COMBINED (three ships):")
print(f"     Survival 1/4:  {q(_g25)[1]:.0f}  [{q(_g25)[0]:.0f}-{q(_g25)[2]:.0f}] t")
print(f"     Survival 1/3:  {q(_g33)[1]:.0f}  [{q(_g33)[0]:.0f}-{q(_g33)[2]:.0f}] t")
print(f"     Survival 1/2:  {q(_g50)[1]:.0f}  [{q(_g50)[0]:.0f}-{q(_g50)[2]:.0f}] t")
print()
print("   Facility planning note:")
print("   Waterlogged oak density ~900-1000 kg/m3; structural timber retains its gross mass")
print("   when submerged. A single 10x3 m section of lower hull (0.4 m mean timber depth)")
print("   = 11-12 t waterlogged. A significant hull section with ballast still in place")
print("   (likely scenario at Site 1) could reach 20-50 t per lift.")
print("   -> Crane, barge, and conservation-tank capacity at Sligo quay and the proposed")
print("      museum/marine-archaeology institute should be sized for lifts in this range.")
