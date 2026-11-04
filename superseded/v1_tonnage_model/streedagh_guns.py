import numpy as np
rng = np.random.default_rng(15881221)
N = 100_000
def tri(a,m,b,n=N): return rng.triangular(a,m,b,n)

# Documented ship's armament (number of guns "of various weights of shot")
guns = {"La Juliana":32, "La Lavia":25, "Santa Maria de Vison":18}

# Per-gun mass bands (kg) by class, and the fraction of a Levant nao's armament
# in each class. Light swivels sat high/accessible; heavy battery sat low/buried.
classes = {
    "esmeril/pedrero (swivel)": (dict(a=80,  m=150,  b=300 ), 0.40, "light"),
    "minion/falcon":            (dict(a=300, m=450,  b=650 ), 0.34, "light"),
    "sacre/media-culebrina":    (dict(a=700, m=1100, b=1600), 0.20, "heavy"),
    "culebrina/canon":          (dict(a=1600,m=2200, b=3000), 0.06, "heavy"),
}

print("=== Ship's armament mass (documented gun counts) ===\n")
tot_mass=np.zeros(N); tot_light=np.zeros(N); tot_heavy=np.zeros(N)
for ship,n in guns.items():
    m_ship=np.zeros(N); light=np.zeros(N); heavy=np.zeros(N)
    for cls,(band,frac,tier) in classes.items():
        ncls = n*frac                                   # expected count in class
        mass = ncls*tri(**band)/1000.0                  # tonnes
        m_ship+=mass
        if tier=="light": light+=mass
        else:             heavy+=mass
    tot_mass+=m_ship; tot_light+=light; tot_heavy+=heavy
    q=lambda x:np.percentile(x,[5,50,95])
    print(f"{ship} ({n} guns): total {q(m_ship)[1]:.1f} t  |  light(top) {q(light)[1]:.1f} t  |  heavy(buried) {q(heavy)[1]:.1f} t")

q=lambda x:np.percentile(x,[5,50,95])
print(f"\nAll three ships' ARMAMENT (75 guns): {q(tot_mass)[1]:.0f} t [{q(tot_mass)[0]:.0f}-{q(tot_mass)[2]:.0f}]")
print(f"  light/accessible tier: {q(tot_light)[1]:.0f} t   heavy/buried tier: {q(tot_heavy)[1]:.0f} t")

# Embarked SIEGE TRAIN (cargo, additional to armament) — implied by the carriage wheels.
# Heavy battering pieces stowed low in holds; deepest and least likely yet exposed.
siege_guns = tri(2, 5, 9)                                # total across the three ships
siege_mass = siege_guns*tri(2000,2500,3000)/1000.0      # tonnes
print(f"\nPossible embarked SIEGE TRAIN: {q(siege_guns)[1]:.0f} heavy guns ~ {q(siege_mass)[1]:.0f} t [{q(siege_mass)[0]:.0f}-{q(siege_mass)[2]:.0f}] (all buried)")

# Recovered-to-date check
print("\n13 guns recovered so far, ~36 t of bronze ordnance modelled across the 3 sites.")
print("75 documented armament guns - 13 recovered = ~62 still on/under the sites, PLUS any siege train.")
print("Light tier dominates by COUNT; heavy+siege tier dominates by MASS and remains buried.")
