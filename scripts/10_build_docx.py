"""Build MASTER_pandoc2.md from section files + figures + equation PNGs, then run pandoc."""
import re, subprocess
from pathlib import Path

M = Path(__file__).resolve().parent.parent / 'manuscript'
def read(f): return (M/f).read_text()

def strip_refnotes(text):
    text = re.split(r'\n###?\s+References (newly )?cited', text)[0]
    text = re.split(r'\n---\n\s*\*Figures referenced', text)[0]
    text = re.split(r'\n---\n\s*\*Note:', text)[0]
    return text.rstrip()

S = {k: strip_refnotes(read(f)) for k, f in [
    ('abstract','00_abstract.md'),('intro','01_introduction.md'),
    ('study','02_study_area.md'),('method','03_methodology.md'),
    ('results','04_results.md'),('disc','05_discussion.md'),
    ('concl','06_conclusion.md')]}
S['tables'] = read('tables.md')

def fix(t):
    for a,b in [('Figure F_wind_resource a, b','Figure 4a,b'),('Figure F_wind_resource a–c','Figure 4'),
        ('Figure F_wind_resource c','Figure 4c'),('Figure F_wind_resource d','Figure 4d'),
        ('Figure F_wind_resource','Figure 4'),('Figure F_monte_carlo a–c','Figure 5a–c'),
        ('Figure F_monte_carlo d','Figure 5d'),('Figure F_monte_carlo','Figure 5'),
        ('Figure F7a','Figure 6a'),('Figure F7b','Figure 6b'),('Figure F7','Figure 6'),
        ('Figure F8','Figure 7'),('Figure F3','Figure 3'),('Figure F2','Figure 2'),('Figure F1','Figure 1')]:
        t = t.replace(a,b)
    return t
S = {k: fix(v) for k,v in S.items()}

def figblock(num, fname, caption, width="6.0in"):
    return f'\n\n![**Figure {num}.** {caption}](figures_final/{fname}){{width={width}}}\n\n'

out = ["# Energy Production and Avoided Carbon Emissions of the Gulf of Saros Offshore Wind Candidate Zone, North Aegean Sea: An ERA5-Based Assessment under Uncertainty\n",
"\n*Draft manuscript — target journal: Energies (MDPI). References verified 9 June 2026 (see REFERENCES_VERIFIED.md); to be numbered at submission.*\n\n---\n",
"\n## Abstract\n", "\n"+re.sub(r'^#\s*Abstract\s*\n','',S['abstract']).strip()+"\n",
"\n"+S['intro']+"\n", "\n"+S['study']+"\n",
figblock(1,"figure1.png","Location of the Saros DÜRES offshore wind candidate zone in the North Aegean Sea. Left: regional context; right: the 27-vertex polygon (172.5 km²) with the ERA5 grid overlay."),
"\n"+S['method']+"\n",
figblock(2,"figure2.png","Methodological workflow, from ERA5 reanalysis through Weibull fitting, energy production and avoided-emission estimation, to Monte Carlo uncertainty quantification.","4.5in"),
"\n"+S['results']+"\n",
figblock(3,"figure3.png","Wind rose at 105 m hub height (2014–2024), showing the dominant northeast–east-northeast sectors.","4.5in"),
figblock(4,"figure4.png","Wind resource characterisation: (a) wind-speed distribution and Weibull fit with the turbine power curve; (b) Q–Q plot; (c) monthly climatology; (d) inter-annual variability."),
figblock(5,"figure5.png","Monte Carlo results (10,000 iterations): distributions of (a) specific yield, (b) capacity factor, (c) avoided CO₂ per MW; (d) farm AEP by scenario with P10–P90 ranges."),
figblock(6,"figure6.png","One gigawatt at Saros — the carbon story of the same 2.62 TWh yr⁻¹: the fossil-thermal pathway emits 1.98 Mt CO₂ yr⁻¹ (fuel-resolved) versus 0.029 Mt for offshore wind (≈69× lower), yielding an avoided emission of 1.52 Mt yr⁻¹ under the official combined margin (1.95 Mt under full fossil displacement)."),
figblock(7,"figure7.png","Tangible equivalents by deployment scenario: (a) households supplied; (b) passenger cars displaced."),
"\n"+S['disc']+"\n", "\n"+S['concl']+"\n", "\n---\n\n"+S['tables']+"\n"]

master = "\n".join(out)
# Equation $$ -> PNG
eq_imgs = [f'![](equations/eq{i}.png){{width=2.6in}}' for i in range(1,8)]
eq_imgs[4]='![](equations/eq5.png){width=3.0in}'; eq_imgs[3]='![](equations/eq4.png){width=3.4in}'
counter=[0]
def repl(m):
    i=counter[0]; counter[0]+=1
    return '\n\n'+(eq_imgs[i] if i<len(eq_imgs) else m.group(0))+'\n\n'
master = re.sub(r'\$\$(.+?)\$\$', repl, master, flags=re.DOTALL)
(M/'MASTER_pandoc2.md').write_text(master)
print(f"Master: {len(master.split())} words, {counter[0]} equations, {master.count('figures_final/')} figures")

# Pandoc
r = subprocess.run(['pandoc', str(M/'MASTER_pandoc2.md'), '-o', str(M/'Saros_OWF_manuscript.docx'),
    '--from','markdown+pipe_tables','--resource-path','.'],
    cwd=M.parent, capture_output=True, text=True)
print("pandoc:", r.returncode, r.stderr[:200] if r.stderr else "OK")
