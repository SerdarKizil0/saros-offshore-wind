"""
Independent numerical check of the manuscript's headline numbers.
=================================================================
Run from the repository root:  python docs/review/verify_numbers.py

Needs only the committed files (config/, results/*.json, results/*.npz) plus
numpy and scipy. It does NOT need the ERA5 parquet. It reproduces the Monte
Carlo bit-for-bit, decomposes the deterministic-vs-MC gap, and quantifies the
sensitivities quoted in docs/PRE_SUBMISSION_REVIEW.md.
"""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import os; os.chdir(ROOT)
import numpy as np
from scipy import stats
from scipy.special import gamma
from config.site import SITE
from config.turbine import TURBINE, SCENARIOS
from config.turbine import POWER_CURVE_ORIGINAL_MS_KW as POWER_CURVE_MS_KW  # review targets the pre-2A curve
from config.emissions import GRID_CO2, OFFSHORE_WIND_CO2

tz = np.trapezoid
W = json.load(open('results/weibull_aep_results.json'))
MC = json.load(open('results/monte_carlo_results.json'))
k0, c0, sc = MC['base_weibull']['k'], MC['base_weibull']['c'], MC['base_weibull']['sigma_c_interannual']

print("== SITE ==")
print(SITE.area_km2, SITE.centroid_lat, SITE.centroid_lon, SITE.ew_extent_km, SITE.ns_extent_km, SITE.era5_area_request)
# ERA5 grid points inside request box
lats=[l for l in np.arange(39,42.01,0.25) if SITE.era5_south<=l<=SITE.era5_north]
lons=[l for l in np.arange(25,28.01,0.25) if SITE.era5_west<=l<=SITE.era5_east]
print("ERA5 0.25 grid points in box: lats",lats,"lons",lons)

print("\n== Power curve Cp ==")
A = np.pi*82**2
for v,p in POWER_CURVE_MS_KW:
    if 3.5<=v<=13:
        print(f"{v:5.1f} m/s  {p:6.0f} kW  Cp={p*1000/(0.5*1.225*A*v**3):.3f}")

pc_ms=[p[0] for p in POWER_CURVE_MS_KW]; pc_kw=[p[1] for p in POWER_CURVE_MS_KW]
v=np.arange(0,30,0.1); p=np.interp(v,pc_ms,pc_kw,left=0,right=0); p[v>=25]=0
def cf(k,c,pg=p):
    return tz(pg*stats.weibull_min.pdf(v,k,0,c),v)/9500
print("\n== Deterministic: empirical vs Weibull-based ==")
cfw=cf(k0,c0)
print(f"empirical gross CF {W['aep']['cf_gross_pct']:.2f}%  | Weibull(k0,c0) gross CF {cfw*100:.2f}%  ratio {cfw*100/W['aep']['cf_gross_pct']:.4f}")
nf=0.92*0.95*0.97
print(f"Weibull-based net per MW at nominal losses: {cfw*8766*nf/1000:.3f} GWh/MW ; empirical {W['aep']['net_aep_per_mw_gwh']:.3f}")
# with cut-in zeroing as in script 04
p2=p.copy(); p2[v<3.5]=0
print(f"  (cut-in zeroed) Weibull gross CF {cf(k0,c0,p2)*100:.2f}%")

print("\n== Triangular medians ==")
def trimed(a,m,b):
    Fc=(m-a)/(b-a)
    return a+np.sqrt(0.5*(b-a)*(m-a)) if Fc>=0.5 else b-np.sqrt(0.5*(b-a)*(b-m))
def trimean(a,m,b): return (a+m+b)/3
for nm,(a,m,b) in {'wake':(0.05,0.08,0.12),'avail':(0.92,0.95,0.97),'elec':(0.02,0.03,0.04),'grid':(434,624.2,713.4),'lca':(8,11,14)}.items():
    print(f"{nm:6s} mode {m}  median {trimed(a,m,b):.4f}  mean {trimean(a,m,b):.4f}")
nf_mean=(1-trimean(0.05,0.08,0.12))*trimean(0.92,0.95,0.97)*(1-0.03)
print(f"net factor nominal {nf:.5f} vs mean-of-triangulars {nf_mean:.5f}  ratio {nf_mean/nf:.4f}")

print("\n== Reproduce MC (seed 2026) ==")
rng=np.random.default_rng(2026); N=10000
k_s=rng.normal(k0,0.04,N); c_s=rng.normal(c0,sc,N)
wake=rng.triangular(0.05,0.08,0.12,N); av=rng.triangular(0.92,0.95,0.97,N); el=rng.triangular(0.02,0.03,0.04,N)
grid=rng.triangular(434,624.2,713.4,N); lca=rng.triangular(8,11,14,N)
gcf=np.array([cf(k_s[i],c_s[i]) for i in range(N)])
aep=gcf*8766/1000*(1-wake)*av*(1-el)
avd=aep*(grid-lca)
S=np.load('results/monte_carlo_samples.npz')
print("max abs diff aep vs npz:", np.abs(aep-S['aep_per_mw']).max(), " avoided:", np.abs(avd-S['avoided_per_mw']).max())
pc=lambda a: np.percentile(a,[10,50,90]).round(3)
print("AEP/MW P10/50/90", pc(aep), " avoided", pc(avd).round(0))
print("median(grid-lca) =", np.median(grid-lca).round(1), " | P50 avoided / P50 AEP =", (np.median(avd)/np.median(aep)).round(1), " | official CM net =", 624.2-11)
print("AEP_P50 x 613.2 =", (np.median(aep)*613.2).round(0), "t/MW ; S3:", (np.median(aep)*613.2*997.5/1e6).round(3),"Mt")
print("with grid fixed at CM, avoided P10/50/90:", pc(aep*(624.2-lca)).round(0))
print("with gen-avg 434:", (np.median(aep)*(434-11)).round(0), " OM 713.4:", (np.median(aep)*(713.4-11)).round(0))

print("\n== Variance decomposition of AEP (one-at-a-time) ==")
base=cf(k0,c0)*8766/1000*nf
for nm,arr in [('k',np.array([cf(x,c0) for x in k_s[:3000]])*8766/1000*nf),
               ('c',np.array([cf(k0,x) for x in c_s[:3000]])*8766/1000*nf),
               ('wake',cf(k0,c0)*8766/1000*(1-wake)*0.95*0.97),
               ('avail',cf(k0,c0)*8766/1000*0.92*av*0.97),
               ('elec',cf(k0,c0)*8766/1000*0.92*0.95*(1-el))]:
    print(f"{nm:6s} CoV {arr.std()/arr.mean()*100:.2f}%")
print("total AEP CoV", (aep.std()/aep.mean()*100).round(2))
vt=avd.var()
print("avoided: CoV", (avd.std()/avd.mean()*100).round(1), " share of var from grid EF ~", ((np.median(aep)*(grid-lca)).var()/vt).round(2))

print("\n== Sensitivities ==")
print(f"alpha 0.149 vs 0.10 speed factor: {1.05**0.149:.5f} vs {1.05**0.10:.5f}  diff {(1.05**0.149/1.05**0.10-1)*100:.2f}%")
print(f"c sigma as LT-mean SE: {sc/np.sqrt(11):.3f} (vs {sc:.3f})")
c_lt=np.random.default_rng(1).normal(c0,sc/np.sqrt(11),3000)
a_lt=np.array([cf(k0,x) for x in c_lt]); print(f"  AEP CoV from c with SE: {a_lt.std()/a_lt.mean()*100:.2f}%")
for b in (-0.10,-0.05,0.05,0.10):
    print(f"wind-speed bias {b:+.0%}: gross CF {cf(k0,c0*(1+b))*100:.1f}%  (AEP change {(cf(k0,c0*(1+b))/cfw-1)*100:+.1f}%)")
# Cp-capped power curve
for cpmax in (0.48,0.45):
    pk=np.minimum(p, cpmax*0.5*1.225*A*v**3/1000); pk[v>=25]=0
    print(f"Cp<= {cpmax}: gross CF {cf(k0,c0,pk)*100:.1f}%  (AEP change {(cf(k0,c0,pk)/cfw-1)*100:+.1f}%)")
# air density
print("\n== Scenarios ==")
for s in SCENARIOS:
    print(s.name, s.n_turbines, s.installed_mw, f"density {s.installed_mw/SITE.area_km2:.1f} MW/km2", f"area/turbine {SITE.area_km2/s.n_turbines:.2f} km2")
print("7Dx5D cell km2:", 7*0.164*5*0.164, " -> N =", SITE.area_km2/(7*0.164*5*0.164))
print("\n== Fuel mix ==")
sh={'gas':0.368,'coal':0.333,'lig':0.299}; ef={'gas':405,'coal':803,'lig':1133}
mix=sum(sh[f]*ef[f] for f in sh); print("mix EF", mix, "ratio to LCA", mix/11, " 1.98/0.029=",1.98/0.029)
E=np.median(aep)*997.5/1000
print("S3 TWh",E.round(3)," conv Mt",(E*mix/1000).round(3)," wind Mt",(E*11/1000).round(4))
print("households M", (E*1e9/3036/1e6).round(3), " cars M", (np.median(avd)*997.5/2/1e6).round(3))
print("share national %", (E/347.9*100).round(2), " 5GW TWh", (np.median(aep)*5).round(2), (np.median(aep)*5/347.9*100).round(2))
print("\n== Weibull stats ==")
print("mean",c0*gamma(1+1/k0)," WPD", 0.5*1.225*c0**3*gamma(1+3/k0), " KS p", W['weibull']['ks_pvalue'])
print("MLE asymptotic SE of k for n=96432 (iid) ~", 0.78*k0/np.sqrt(96432))
