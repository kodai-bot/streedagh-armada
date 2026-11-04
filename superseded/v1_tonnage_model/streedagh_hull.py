import numpy as np
rng = np.random.default_rng(20260629)
N = 200_000

def tri(a, m, b, n=N):
    return rng.triangular(a, m, b, n)

# Recorded burthen (toneladas de arqueo) for the three Streedagh ships
ships = {
    "La Juliana":          860.0,
    "La Lavia":            728.0,
    "Santa Maria de Vison":666.0,
}

# ---- Parameter ranges (explicit assumptions; min, mode, max) ----
# k: cubic metres of stowage per tonelada de arqueo. Spanish tonelada ~1.4 m3;
#    range covers regional variants (Sevilla/Vizcaya) and rounding in the records.
def model(T):
    T_s   = T * tri(0.88, 1.0, 1.12)            # recorded-tonnage uncertainty ~+-12%
    k     = tri(1.20, 1.42, 1.55)               # m3 per tonelada (stowage)
    Vburt = T_s * k                              # effective burthen/cargo volume

    phi   = tri(0.45, 0.52, 0.58)               # burthen vol / total enclosed hull vol
    Vmould= Vburt / phi                          # total moulded volume to weather deck

    alpha = tri(3.3, 3.5, 3.8)                   # L/B  (eslora / manga) - broad Med nao
    beta  = tri(0.45, 0.50, 0.55)               # D/B  (puntal / manga) - deep merchant hull
    Cbbox = tri(0.45, 0.52, 0.58)               # moulded vol / (L*B*D)

    B = (Vmould / (alpha*beta*Cbbox))**(1/3)     # beam
    L = alpha*B                                  # length on deck (eslora)
    D = beta*B                                   # depth in hold (puntal)

    gamma = tri(0.55, 0.62, 0.70)               # draught / depth
    delta = tri(0.82, 0.87, 0.92)               # waterline length / eslora
    Cbhul = tri(0.50, 0.56, 0.62)               # underwater block coeff
    d   = gamma*D
    Lwl = delta*L
    Vsub= Lwl*B*d*Cbhul
    disp= 1.025*Vsub                             # displacement (tonnes)

    lam = tri(0.42, 0.50, 0.58)                 # lightship / displacement (heavy timber hull+rig)
    dwt = disp*(1-lam)                           # deadweight: ballast+stores+water+people+cargo+guns

    bal = tri(0.25, 0.35, 0.45)                 # ballast fraction of deadweight
    payload = dwt*(1-bal)                        # non-ballast embarked mass (the "cargo budget")

    return dict(B=B, L=L, D=D, draught=d, Vmould=Vmould, disp=disp, dwt=dwt, payload=payload)

def q(x):
    return np.percentile(x, [5, 50, 95])

print(f"{'Ship':24s}{'Beam B (m)':>20s}{'Length L (m)':>22s}{'Depth D (m)':>20s}")
for name, T in ships.items():
    r = model(T)
    b, l, d = q(r['B']), q(r['L']), q(r['D'])
    print(f"{name:24s}"
          f"{b[1]:6.1f} [{b[0]:.1f}-{b[2]:.1f}]   "
          f"{l[1]:6.1f} [{l[0]:.1f}-{l[2]:.1f}]    "
          f"{d[1]:6.1f} [{d[0]:.1f}-{d[2]:.1f}]")

print()
print(f"{'Ship':24s}{'Moulded vol (m3)':>20s}{'Displacement (t)':>20s}{'Deadweight (t)':>18s}{'Payload ex-ballast (t)':>24s}")
for name, T in ships.items():
    r = model(T)
    vm, ds, dw, pl = q(r['Vmould']), q(r['disp']), q(r['dwt']), q(r['payload'])
    print(f"{name:24s}"
          f"{vm[1]:7.0f} [{vm[0]:.0f}-{vm[2]:.0f}] "
          f"{ds[1]:6.0f} [{ds[0]:.0f}-{ds[2]:.0f}] "
          f"{dw[1]:5.0f} [{dw[0]:.0f}-{dw[2]:.0f}] "
          f"{pl[1]:6.0f} [{pl[0]:.0f}-{pl[2]:.0f}]")

print()
print("Upper bounds (95th percentile) — physical ceilings:")
for name, T in ships.items():
    r = model(T)
    print(f"  {name:24s} displacement <= {np.percentile(r['disp'],95):5.0f} t | "
          f"deadweight <= {np.percentile(r['dwt'],95):4.0f} t | "
          f"non-ballast payload <= {np.percentile(r['payload'],95):4.0f} t")
