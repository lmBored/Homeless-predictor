document.addEventListener('DOMContentLoaded', async () => {
    try {
        const [t] = await browser.tabs.query({ active: true, currentWindow: true });
        
        const res = await browser.scripting.executeScript({
            target: { tabId: t.id },
            func: scrape
        });

        const d = res[0].result;
        
        if (!d || (d.pen.length === 0 && d.pro.length === 0)) {
            document.getElementById("results").innerHTML = "<p style='padding:10px;'>No data found.</p>";
            return;
        }

        solve(d);
    } catch (e) {
        document.getElementById("results").innerHTML = "<p style='padding:10px; color:red'>Error: Can't read this page.</p>";
    }
});

function scrape() {
    const f = (el, k) => {
        let txt = el.innerText;
        let m = txt.match(/For now, you are number (\d+) out of (\d+) applications\./i);
        let ad = el.querySelector(".house-thumb-title + p")?.innerText.trim() ||
                 el.querySelector(".house-thumb-title")?.innerText.trim();

        let pr = txt.match(/[\u20AC]\s*(\d+[.,]\d+)/);
        let ar = txt.match(/(\d+)\s*m\s*2/);
        let st = txt.match(/Status:\s*(.+?)(?:\n|$)/);

        if (!m) return null;

        let a = ad || "Unknown";
        a = a.replace(/\s+(Eindhoven|Amsterdam|Utrecht|Rotterdam).*/i, "");

        return {
            k: k,
            addr: a,
            pos: parseInt(m[1]),
            tot: parseInt(m[2]),
            r: pr ? parseFloat(pr[1].replace(',', '.')) : 0,
            sz: ar ? parseInt(ar[1]) : 0,
            st: st ? st[1].trim() : ""
        };
    };

    const get = (sel, k) => {
        let box = document.querySelector(sel);
        if (!box) return [];
        let ls = box.querySelectorAll('.reaction.content-item');
        return Array.from(ls).map(x => f(x, k)).filter(x => x !== null);
    };

    return {
        pen: get('#lopende-reacties', 'pen'),
        pro: get('#afgehandelde-reacties', 'pro')
    };
}

function solve(d) {
    const el = document.getElementById("results");

    let v = d.pro.map(x => x.tot).sort((a,b) => a-b);
    let n = v.length;
    let md = 0;

    if (n > 0) {
        let mid = Math.floor(n / 2);
        md = n % 2 !== 0 ? v[mid] : (v[mid - 1] + v[mid]) / 2;
    } else {
        md = 200;
    }

    function prob(p, tot) {
        let N = Math.max(tot, md);
        let tar = 20 / N;
        let cur = p / tot;

        if (p > 20) {
            let proj = p * (N / tot);
            if (proj > 25) return 0;
        }

        let se = Math.sqrt((cur * (1 - cur)) / tot);
        if (se === 0) return p <= 20 ? 100 : 0;

        let z = (tar - cur) / se;
        return cdf(z) * 100;
    }

    function cdf(x) {
        let t = 1 / (1 + .2316419 * Math.abs(x));
        let d = .3989423 * Math.exp(-x * x / 2);
        let ans = d * t * (.3193815 + t * (-.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
        return x > 0 ? 1 - ans : ans;
    }

    let avg_cut = (20/md*100).toFixed(1);

    let s = `<div class="panel">
        <div class="stat-grid">
            <div class="stat-box"><span class="stat-val">${d.pen.length}</span><span class="stat-lbl">Pending</span></div>
            <div class="stat-box"><span class="stat-val">${d.pro.length}</span><span class="stat-lbl">Processed</span></div>
            <div class="stat-box"><span class="stat-val">${md.toFixed(0)}</span><span class="stat-lbl">Avg</span></div>
            <div class="stat-box"><span class="stat-val">${avg_cut}%</span><span class="stat-lbl">Cut</span></div>
        </div>
    </div>`;

    if (d.pen.length > 0) {
        s += `<div class="section-header"><span>Pending</span></div>
              <table><thead><tr>
              <th width="30%">Addr</th><th>Pos</th><th>Tot</th><th>Rent</th><th>Chance</th>
              </tr></thead><tbody>`;

        let tmp = d.pen.map(x => {
            x.pct = prob(x.pos, x.tot);
            return x;
        }).sort((a, b) => b.pct - a.pct);

        tmp.forEach(x => {
            let cls = "chance-low";
            let str = x.pct.toFixed(1) + "%";

            if (x.pct >= 80) cls = "chance-high";
            else if (x.pct >= 40) cls = "chance-med";

            if (x.pct > 99.5) str = "Likely";
            if (x.pct < 0.5) str = "< 1%";

            let proj = Math.round(x.pos * (Math.max(x.tot, md) / x.tot));

            s += `<tr>
                <td><strong>${x.addr}</strong><br><span style="font-size:10px;color:#888;">${x.sz}m&sup2;</span></td>
                <td>${x.pos}</td>
                <td>${x.tot}</td>
                <td>&euro;${x.r.toFixed(0)}</td>
                <td class="${cls}" title="~${proj}">${str}</td>
            </tr>`;
        });
        s += `</tbody></table>`;
    }

    if (d.pro.length > 0) {
        s += `<div class="section-header" style="margin-top:20px;"><span>Processed</span></div>
              <table><thead><tr>
              <th width="30%">Addr</th><th>Pos</th><th>Tot</th><th>Rent</th><th>Res</th>
              </tr></thead><tbody>`;

        d.pro.sort((a,b) => a.pos - b.pos);

        d.pro.forEach(x => {
            let ok = x.pos <= 20;
            let c = ok ? "chance-high" : "chance-low";
            let t = ok ? "In" : "Out";

            s += `<tr style="opacity: 0.7;">
                <td><strong>${x.addr}</strong><br><span style="font-size:10px;color:#888;">${x.sz}m&sup2;</span></td>
                <td>${x.pos}</td>
                <td>${x.tot}</td>
                <td>&euro;${x.r.toFixed(0)}</td>
                <td class="${c}">${t}</td>
            </tr>`;
        });
        s += `</tbody></table>`;
    }

    el.innerHTML = s;
}
