import re
import os
from dataclasses import dataclass

@dataclass
class P:
    addr: str
    area: float
    rent: float
    pos: int
    tot: int
    stat: str
    pct: float = 0.0
    z: float = 0.0

    def __post_init__(self):
        self.pct = (self.pos / self.tot) * 100 if self.tot > 0 else 0

def parse(s):
    ans = []
    pat = r'For now, you are number (\d+) out of (\d+) applications\.'
    m = list(re.finditer(pat, s))

    if not m:
        return ans

    for i, x in enumerate(m):
        pos = int(x.group(1))
        tot = int(x.group(2))

        start = m[i-1].end() if i > 0 else 0
        end = x.end()
        blk = s[start:end]

        se = m[i+1].start() if i < len(m) - 1 else len(s)
        sblk = s[x.end():se]

        ap = r"(['\'A-Za-z\s\-]+(?:straat|laan|pad|weg|plein|singel|kade|gracht|hof|dreef)\s+\d+[\s/]*[A-Za-z0-9/]*)\s+(Eindhoven|Amsterdam|Rotterdam|Utrecht|Delft|Groningen|Leiden|Tilburg|Breda|Maastricht)"
        am = re.search(ap, blk, re.IGNORECASE)

        if am:
            ad = am.group(1).strip()
            ct = am.group(2)
        else:
            fp = r"([A-Za-z'\s\-]+\d+[\s/]*[A-Za-z0-9/]*)\s+(Eindhoven|Amsterdam|Rotterdam|Utrecht)"
            fm = re.search(fp, blk)
            if fm:
                ad = fm.group(1).strip()
                ct = fm.group(2)
            else:
                ad = "Unknown"
                ct = ""

        faddr = f"{ad} {ct}".strip()
        ls = ad.split("\n")
        if ls:
            ad = ls[-1].strip()
            faddr = f"{ad} {ct}".strip()

        arp = r'Area measure:\s*(\d+)\s*m\s*2?'
        arm = re.search(arp, blk)
        area = float(arm.group(1)) if arm else 0.0

        rp = r'[€]\s*(\d+[.,]\d+)\s*p/m'
        rm = re.search(rp, blk)
        if rm:
            r = float(rm.group(1).replace(',', '.'))
        else:
            rp2 = r'Total rent:\s*[€]\s*(\d+[.,]\d+)'
            rm = re.search(rp2, blk)
            r = float(rm.group(1).replace(',', '.')) if rm else 0.0

        sp = r'Status:\s*(.+?)(?:\n|$)'
        sm = re.search(sp, sblk)
        st = sm.group(1).strip() if sm else "Unknown"

        ans.append(P(faddr, area, r, pos, tot, st))

    return ans

def calc(ls):
    if not ls: return {}
    n = len(ls)
    ts = [x.tot for x in ls]
    ps = [x.pct for x in ls]

    mu = sum(ts) / n
    mup = sum(ps) / n

    st = sorted(ts)
    sp = sorted(ps)

    if n % 2 == 1:
        med = st[n // 2]
        medp = sp[n // 2]
    else:
        med = (st[n//2 - 1] + st[n//2]) / 2
        medp = (sp[n//2 - 1] + sp[n//2]) / 2

    var = sum((x - mu) ** 2 for x in ts) / n
    sd = var ** 0.5
    varp = sum((x - mup) ** 2 for x in ps) / n
    sdp = varp ** 0.5

    q1 = st[int(n * 0.25)]
    q3 = st[int(n * 0.75)]
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr

    for x in ls:
        x.z = (x.tot - mu) / sd if sd > 0 else 0

    io = [x for x in ls if x.tot < low or x.tot > high]
    zo = [x for x in ls if abs(x.z) > 2]

    t5 = 5 / (mup / 100) if mup > 0 else 0
    t10 = 10 / (mup / 100) if mup > 0 else 0
    t20 = 20 / (mup / 100) if mup > 0 else 0

    return {
        'n': n, 'mu': mu, 'med': med, 'sd': sd,
        'mup': mup, 'medp': medp, 'sdp': sdp,
        'q1': q1, 'q3': q3, 'iqr': iqr,
        'low': low, 'high': high,
        'io': io, 'zo': zo,
        't5': t5, 't10': t10, 't20': t20
    }

def prt(h, r, a=None):
    if not r: return
    w = [len(x) for x in h]
    for rr in r:
        for i, c in enumerate(rr):
            w[i] = max(w[i], len(str(c)))

    if a is None: a = ['<'] * len(h)
    sep = '+' + '+'.join('-' * (x + 2) for x in w) + '+'

    print(sep)
    hr = '|'
    for i, x in enumerate(h):
        hr += f' {x:^{w[i]}} |'
    print(hr)
    print(sep)

    for rr in r:
        s = '|'
        for i, c in enumerate(rr):
            if a[i] == '>': s += f' {str(c):>{w[i]}} |'
            elif a[i] == '^': s += f' {str(c):^{w[i]}} |'
            else: s += f' {str(c):<{w[i]}} |'
        print(s)
    print(sep)

def solve(ls, st):
    print("Applications")
    h = ['Address', 'Area', 'Rent', 'Pos', 'Tot', 'Pct', 'Stat']
    d = []
    for x in sorted(ls, key=lambda k: k.pct):
        d.append([x.addr[:30], f"{x.area:.0f}m2", f"{x.rent:.2f}", str(x.pos), str(x.tot), f"{x.pct:.1f}%", x.stat[:20]])
    prt(h, d, ['<', '>', '>', '>', '>', '>', '<'])
    print()

    print("Stats")
    sh = ['Metric', 'Total', 'Pct']
    sd = [
        ['Count', f"{st['n']}", f"{st['n']}"],
        ['Mean', f"{st['mu']:.1f}", f"{st['mup']:.2f}%"],
        ['Median', f"{st['med']:.1f}", f"{st['medp']:.2f}%"],
        ['Std', f"{st['sd']:.1f}", f"{st['sdp']:.2f}%"],
        ['Q1', f"{st['q1']:.0f}", "-"],
        ['Q3', f"{st['q3']:.0f}", "-"],
        ['IQR', f"{st['iqr']:.0f}", "-"],
    ]
    prt(sh, sd, ['<', '>', '>'])
    print()

    print("Outliers")
    print(f"IQR [{st['low']:.1f}, {st['high']:.1f}]")
    if st['io']:
        for x in st['io']: print(f"    -> {x.addr}: {x.tot}")
    else: print("None")

    print("Z-Score (|Z| > 2)")
    if st['zo']:
        for x in st['zo']: print(f"    -> {x.addr}: {x.tot} (Z={x.z:.2f})")
    else: print("None")

    fil = [x for x in ls if abs(x.z) <= 2]
    if len(fil) < len(ls):
        fm = sum(x.pct for x in fil) / len(fil)
        print("Filtered")
        print(f"Cnt: {len(fil)}")
        print(f"Mn Pct: {fm:.2f}%")
    print()

    print("Thresholds")
    th = ['Cut', 'Max', 'Msg']
    td = [
        ['Top 5', f"<= {st['t5']:.0f}", "Top 5 threshold"],
        ['Top 10', f"<= {st['t10']:.0f}", "Top 10 threshold"],
        ['Top 20', f"<= {st['t20']:.0f}", "Top 20 threshold"],
    ]
    prt(th, td, ['<', '>', '<'])
    print()

    print("Top 20")
    yes = [x for x in ls if x.pos <= 20]
    no = [x for x in ls if x.pos > 20]

    print(f"Yes: {len(yes)}")
    print(f"No:  {len(no)}")

    if yes:
        print("Yes")
        yh = ['Addr', 'Pos', 'Tot', 'Pct']
        yd = [[x.addr[:35], str(x.pos), str(x.tot), f"{x.pct:.1f}%"] for x in sorted(yes, key=lambda k: k.pos)]
        prt(yh, yd, ['<', '>', '>', '>'])

    if no:
        print("No")
        nh = ['Addr', 'Pos', 'Tot', 'Pct', 'Req']
        nd = []
        for x in sorted(no, key=lambda k: k.pos):
            req = int(20 * x.tot / x.pos)
            nd.append([x.addr[:30], str(x.pos), str(x.tot), f"{x.pct:.1f}%", str(req)])
        prt(nh, nd, ['<', '>', '>', '>', '>'])
    print()

    print("Best 5")
    sl = sorted(ls, key=lambda k: k.pct)
    for i, x in enumerate(sl[:5], 1):
        ok = "Y" if x.pos <= 20 else "N"
        print(f"    {i}. [{ok}] {x.addr}")
        print(f"       Pos {x.pos}/{x.tot} = {x.pct:.1f}% | {x.rent} | {x.area}")

if __name__ == "__main__":
    fn = "asdf.txt"
    if not os.path.exists(fn):
        print("Where file")
        exit()

    with open(fn, 'r', encoding='utf-8') as f:
        txt = f.read()

    if not txt.strip():
        exit()

    data = parse(txt)
    if not data:
        print("Nein data")
        exit()

    s = calc(data)
    solve(data, s)
