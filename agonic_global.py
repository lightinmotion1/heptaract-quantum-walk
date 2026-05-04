"""
Global agonic line — full IGRF-14 curve across all latitudes.
Also maps every "ballpark" zone (within 5° of agonic = in the game).
"""

import numpy as np
from math import sqrt, sin, cos, atan2, radians, degrees, log2, pi, asin

# ── reuse field model from igrf_proper.py ──────────────────────
from math import tan, floor

IGRF14_2025 = [
    (1,0,-29351,0),(1,1,-1410,4545),
    (2,0,-2556,0),(2,1,2946,-3000),(2,2,1648,-735),
    (3,0,1361,0),(3,1,-2235,-71),(3,2,1249,291),(3,3,580,-422),
    (4,0,-271,0),(4,1,957,148),(4,2,800,-325),(4,3,397,-186),(4,4,-419,97),
    (5,0,-202,0),(5,1,-52,-325),(5,2,362,-67),(5,3,171,-98),(5,4,-116,-17),(5,5,-12,90),
    (6,0,72,0),(6,1,68,-160),(6,2,-297,18),(6,3,226,-18),(6,4,100,74),(6,5,-43,-4),(6,6,-31,27),
]
IGRF14_SV = [
    (1,0,10.3,0),(1,1,0.2,-7.9),(2,0,-6.0,0),(2,1,-3.2,-1.3),(2,2,-1.3,2.5),
    (3,0,1.8,0),(3,1,0.3,4.4),(3,2,3.3,-2.3),(3,3,-0.6,-7.5),
    (4,0,-0.7,0),(4,1,1.5,0.9),(4,2,-0.4,0.0),(4,3,0.5,1.1),(4,4,-0.5,-0.1),
    (5,0,-0.3,0),(5,1,0.8,-0.3),(5,2,-0.2,0.5),(5,3,-0.1,0.6),(5,4,0.0,0.0),(5,5,-0.3,0.0),
    (6,0,-0.3,0),(6,1,0.1,0.0),(6,2,0.5,-0.2),(6,3,0.0,0.3),(6,4,0.1,0.0),(6,5,-0.1,0.0),(6,6,0.0,0.1),
]
SV = {(n,m):(dg,dh) for n,m,dg,dh in IGRF14_SV}

def coeffs(year):
    dt = year - 2025.0
    g,h = {},{}
    for n,m,gv,hv in IGRF14_2025:
        dg,dh = SV.get((n,m),(0,0))
        g[(n,m)] = gv + dg*dt; h[(n,m)] = hv + dh*dt
    return g,h

def legendre(nmax, theta):
    ct,st = cos(theta),sin(theta)
    P = {(0,0):1.0,(1,0):ct,(1,1):st}
    for n in range(2,nmax+1):
        for m in range(0,n+1):
            if m==n: P[(n,n)]=(2*n-1)*st*P[(n-1,n-1)]
            elif m==n-1: P[(n,n-1)]=(2*n-1)*ct*P[(n-1,n-1)]
            else: P[(n,m)]=((2*n-1)*ct*P[(n-1,m)]-(n-1+m)*P[(n-2,m)])/(n-m)
    Ps={}
    for n in range(0,nmax+1):
        for m in range(0,n+1):
            if m==0: Ps[(n,m)]=P[(n,m)]
            else:
                fac=sqrt(2)
                for i in range(n-m+1,n+m+1): fac/=sqrt(i)
                Ps[(n,m)]=fac*P[(n,m)]
    return Ps

def declination(lat, lon, year=2026.33):
    g,h = coeffs(year)
    nmax=6; a=6371.2; r=a
    theta=radians(90-lat); phi=radians(lon)
    P=legendre(nmax,theta)
    Bt=Bp=0.0
    for n in range(1,nmax+1):
        rn=(a/r)**(n+2)
        for m in range(0,n+1):
            gv=g.get((n,m),0); hv=h.get((n,m),0)
            cp=cos(m*phi); sp=sin(m*phi)
            pnm=P[(n,m)]
            eps=1e-5
            Pe=legendre(nmax,theta+eps)
            dp=(Pe[(n,m)]-pnm)/eps
            Bt-=rn*dp*(gv*cp+hv*sp)
            st=sin(theta)
            Bp+=rn*(m/st)*pnm*(-gv*sp+hv*cp) if st>1e-10 else 0
    X=-Bt; Y=Bp
    return degrees(atan2(Y,X))

# ── find agonic crossings at each latitude ─────────────────────
year = 2026.33
BALLPARK = 3.0   # degrees — "in the ballpark"

print("=" * 70)
print("  GLOBAL AGONIC LINE — IGRF-14, 2026")
print("  Ballpark zone: within 3° of zero declination")
print("=" * 70)

print("\n[ AGONIC LINE — latitude by latitude ]")
print(f"  {'Lat':>5}  {'Agonic crossings (°W/°E)':>45}  Ballpark cities")
print("  " + "─" * 78)

# Named regions near each latitude
landmarks = {
    70: "Iceland, Norway coast",
    65: "Iceland, Scandinavia",
    60: "S.Norway, St.Petersburg",
    55: "Ireland, Moscow",
    50: "England, Ukraine",
    45: "France, Romania",
    40: "Spain, Turkey",
    35: "Morocco, Israel",
    30: "Louisiana ★, Egypt",
    25: "Mexico, Sahara",
    20: "Honduras, Sudan",
    15: "Venezuela, Ethiopia",
    10: "Colombia, Kenya",
     5: "Brazil, Congo",
     0: "Ecuador, Gabon",
    -5: "Peru, Tanzania",
   -10: "Bolivia, Mozambique",
   -20: "Chile, Madagascar",
   -30: "Argentina, S.Africa",
   -40: "Patagonia, S.Ocean",
   -50: "S.Ocean",
   -60: "Antarctica approach",
}

agonic_path = []   # collect for ASCII map
for lat in range(70, -65, -5):
    prev_D = None
    crossings = []
    for lon100 in range(-18000, 18001, 5):
        lon = lon100 / 100
        try:
            D = declination(lat, lon)
        except: continue
        if prev_D is not None and prev_D * D < 0:
            lon_c = (lon-0.05) - prev_D*0.05/(D-prev_D)
            crossings.append(lon_c)
            agonic_path.append((lat, lon_c))
        prev_D = D
    cross_str = "  ".join(f"{c:+.1f}°" for c in crossings[:4])
    region = landmarks.get(lat, "")
    print(f"  {lat:>+4}°  {cross_str:<45}  {region}")

# ── ASCII world map with agonic line ──────────────────────────
print("\n[ ASCII MAP — Agonic line across the globe ]")
print("  Lat\\Lon  -180 -150 -120  -90  -60  -30    0  +30  +60  +90 +120 +150 +180")

# Build grid of declinations (coarse for speed)
lats = range(70, -75, -10)
lons = range(-180, 181, 10)

print("  " + "─" * 74)
for lat in lats:
    row = f"  {lat:>+4}°  |"
    for lon in lons:
        try:
            D = declination(lat, lon)
        except:
            row += " "; continue
        if abs(D) < BALLPARK:
            row += "●"   # on/near agonic
        elif D > 0:
            row += "+"   # east of true north
        else:
            row += "-"   # west of true north
    row += "|"
    print(row)
print("  " + "─" * 74)
print("  Legend: ● = agonic/ballpark (±3°)  + = compass east of true  - = compass west")

# ── Ballpark cities ────────────────────────────────────────────
print("\n[ IN THE BALLPARK — cities within 3° of agonic ]")
ballpark_cities = [
    ("Bush LA, USA",          30.58, -89.88),
    ("Memphis TN, USA",       35.15, -90.05),
    ("Chicago IL, USA",       41.88, -87.63),
    ("Milwaukee WI, USA",     43.04, -87.91),
    ("London, UK",            51.51,  -0.13),
    ("Madrid, Spain",         40.42,  -3.70),
    ("Lagos, Nigeria",         6.52,   3.37),
    ("Nairobi, Kenya",        -1.29,  36.82),
    ("Mumbai, India",         19.08,  72.88),
    ("Lahore, Pakistan",      31.55,  74.34),
    ("Chengdu, China",        30.57, 104.07),
    ("Hanoi, Vietnam",        21.03, 105.83),
    ("Jakarta, Indonesia",    -6.21, 106.85),
]

print(f"\n  {'City':<25}  {'Decl':>8}  {'In ballpark?':>14}  {'Cents':>8}")
print("  " + "─" * 62)
for name, lat, lon in ballpark_cities:
    D = declination(lat, lon)
    bp = "YES ●" if abs(D) < BALLPARK else f"  {abs(D):.1f}° away"
    cents = 1200*log2(1+abs(D)/90) if D!=0 else 0
    print(f"  {name:<25}  {D:>+7.3f}°  {bp:>14}  {cents:>6.1f}¢")

# ── The deep finding ───────────────────────────────────────────
print("\n[ THE GEOMETRY ]")
print("  The agonic line is NOT a meridian — it curves, bends, bulges.")
print("  It forms a continuous loop around the Earth (it must, topologically).")
print("  The two branches connect at both magnetic poles.")
print()
print("  Western branch: curves through E.USA → Caribbean → S.America → Antarctica")
print("  Eastern branch: curves through W.Europe → W.Africa → Indian Ocean → SE.Asia")
print()
print("  Every city on the agonic: compass = truth. No correction needed.")
print("  Every city in the ballpark: one small gate. Nearly home.")
print()
print("  The heptaract doesn't just describe the walk —")
print("  it describes WHO IS ALREADY CLOSE.")
