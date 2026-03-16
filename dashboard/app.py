from flask import Flask, jsonify, render_template_string
import json
import os

app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EcoCache</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0d1117;
            --surface: #161b22;
            --surface2: #1c2330;
            --border: #30363d;
            --green: #3fb950;
            --green-dim: #1a4a24;
            --green-glow: rgba(63, 185, 80, 0.15);
            --amber: #d29922;
            --amber-dim: #3d2a00;
            --text: #e6edf3;
            --text-muted: #7d8590;
            --text-dim: #484f58;
            --mono: 'DM Mono', monospace;
            --serif: 'Fraunces', serif;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background: var(--bg);
            color: var(--text);
            font-family: var(--mono);
            font-size: 13px;
            min-height: 100vh;
            padding: 0;
        }

        /* Subtle grid background */
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(var(--border) 1px, transparent 1px),
                linear-gradient(90deg, var(--border) 1px, transparent 1px);
            background-size: 40px 40px;
            opacity: 0.15;
            pointer-events: none;
            z-index: 0;
        }

        .container {
            position: relative;
            z-index: 1;
            max-width: 1100px;
            margin: 0 auto;
            padding: 48px 32px;
        }

        /* Header */
        .header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 48px;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-icon {
            width: 36px;
            height: 36px;
            border: 1.5px solid var(--green);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 12px var(--green-glow);
        }

        .logo-icon svg {
            width: 18px;
            height: 18px;
            stroke: var(--green);
            fill: none;
            stroke-width: 1.5;
        }

        .logo-text {
            font-family: var(--serif);
            font-size: 22px;
            font-weight: 300;
            letter-spacing: -0.3px;
            color: var(--text);
        }

        .logo-text span {
            color: var(--green);
        }

        .live-badge {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: var(--text-muted);
            padding: 6px 12px;
            border: 1px solid var(--border);
            border-radius: 20px;
            background: var(--surface);
        }

        .live-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--green);
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.8); }
        }

        /* Stats grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;
            background: var(--border);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 32px;
        }

        .stat-card {
            background: var(--surface);
            padding: 28px 24px;
            position: relative;
            overflow: hidden;
            transition: background 0.2s;
        }

        .stat-card:hover {
            background: var(--surface2);
        }

        .stat-card::after {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--green), transparent);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .stat-card:hover::after {
            opacity: 1;
        }

        .stat-label {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-dim);
            margin-bottom: 16px;
        }

        .stat-value {
            font-family: var(--serif);
            font-size: 40px;
            font-weight: 300;
            color: var(--green);
            line-height: 1;
            margin-bottom: 8px;
            transition: all 0.4s ease;
        }

        .stat-value.updating {
            opacity: 0.5;
        }

        .stat-sub {
            font-size: 11px;
            color: var(--text-muted);
            line-height: 1.4;
        }

        /* Section header */
        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }

        .section-title {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-dim);
        }

        .query-count {
            font-size: 11px;
            color: var(--text-muted);
        }

        /* Table */
        .table-wrap {
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            background: var(--surface);
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        thead tr {
            border-bottom: 1px solid var(--border);
        }

        th {
            padding: 12px 20px;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: var(--text-dim);
            font-weight: 400;
            text-align: left;
        }

        tbody tr {
            border-bottom: 1px solid rgba(48, 54, 61, 0.5);
            transition: background 0.15s;
            animation: rowIn 0.3s ease forwards;
            opacity: 0;
        }

        @keyframes rowIn {
            from { opacity: 0; transform: translateY(-4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        tbody tr:hover {
            background: var(--surface2);
        }

        tbody tr:last-child {
            border-bottom: none;
        }

        td {
            padding: 14px 20px;
            font-size: 12px;
            color: var(--text-muted);
        }

        td.query-text {
            color: var(--text);
            max-width: 380px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 500;
        }

        .badge-hit {
            background: var(--green-dim);
            color: var(--green);
            border: 1px solid rgba(63, 185, 80, 0.3);
        }

        .badge-miss {
            background: var(--amber-dim);
            color: var(--amber);
            border: 1px solid rgba(210, 153, 34, 0.3);
        }

        .sim-bar-wrap {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .sim-bar {
            width: 60px;
            height: 3px;
            background: var(--border);
            border-radius: 2px;
            overflow: hidden;
        }

        .sim-fill {
            height: 100%;
            background: var(--green);
            border-radius: 2px;
            transition: width 0.4s ease;
        }

        .sim-fill.low {
            background: var(--amber);
        }

        /* Empty state */
        .empty {
            padding: 48px;
            text-align: center;
            color: var(--text-dim);
            font-size: 12px;
            line-height: 2;
        }

        /* Footer */
        .footer {
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-dim);
            font-size: 11px;
        }

        .footer-right {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        #last-updated {
            color: var(--text-dim);
        }
    </style>
</head>
<body>
<div class="container">

    <div class="header">
        <div class="logo">
            <div class="logo-icon">
                <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/></svg>
            </div>
            <div class="logo-text">Eco<span>Cache</span></div>
        </div>
        <div class="live-badge">
            <div class="live-dot"></div>
            live · updates every 5s
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Cache hit rate</div>
            <div class="stat-value" id="hit-rate">—</div>
            <div class="stat-sub" id="hit-sub">— of — queries from cache</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Water saved</div>
            <div class="stat-value" id="water">—</div>
            <div class="stat-sub" id="water-sub">mL · — × 500mL bottles</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">CO₂ avoided</div>
            <div class="stat-value" id="carbon">—</div>
            <div class="stat-sub" id="carbon-sub">grams · — km not driven</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Total queries</div>
            <div class="stat-value" id="total">—</div>
            <div class="stat-sub">processed through EcoCache</div>
        </div>
    </div>

    <div class="section-header">
        <div class="section-title">Recent queries</div>
        <div class="query-count" id="query-count"></div>
    </div>

    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Query</th>
                    <th>Result</th>
                    <th>Similarity</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody id="history"></tbody>
        </table>
        <div class="empty" id="empty-state" style="display:none">
            No queries yet. Run some queries through EcoCache to see data here.
        </div>
    </div>

    <div class="footer">
        <div>EcoCache · semantic caching for LLMs</div>
        <div class="footer-right">
            last updated <span id="last-updated">—</span>
        </div>
    </div>

</div>

<script>
    // Smooth incremental updates: only change text/content that's different
    // and update history rows in-place to avoid full-table reflows and flicker.
    function formatStat(n, decimals = 1) {
        if (n === null || n === undefined) return '—';
        const v = Number(n);
        if (isNaN(v)) return String(n);
        return v.toLocaleString(undefined, {minimumFractionDigits: decimals, maximumFractionDigits: decimals});
    }

    function animateValue(el, newVal) {
        newVal = String(newVal);
        if (el.textContent !== newVal) {
            el.classList.add('updating');
            setTimeout(() => {
                el.textContent = newVal;
                el.classList.remove('updating');
            }, 200);
        }
    }

    function createHistoryRow(h, i) {
        const tr = document.createElement('tr');
        tr.style.animationDelay = (i * 0.03) + 's';

        const tdQuery = document.createElement('td');
        tdQuery.className = 'query-text q';
        tdQuery.textContent = h.query_preview || '—';

        const tdBadge = document.createElement('td');
        tdBadge.className = 'badge-cell';
        const badge = document.createElement('span');
        badge.className = h.cached ? 'badge badge-hit' : 'badge badge-miss';
        badge.innerHTML = h.cached ? '&#10003; cache hit' : '&#8594; api call';
        tdBadge.appendChild(badge);

        const tdSim = document.createElement('td');
        tdSim.className = 'sim-cell';
        if (h.similarity > 0) {
            const wrap = document.createElement('div');
            wrap.className = 'sim-bar-wrap';
            const bar = document.createElement('div');
            bar.className = 'sim-bar';
            const fill = document.createElement('div');
            fill.className = (Math.round(h.similarity * 100) > 80) ? 'sim-fill' : 'sim-fill low';
            fill.style.width = Math.round(h.similarity * 100) + '%';
            bar.appendChild(fill);
            wrap.appendChild(bar);
            const simText = document.createElement('span');
            simText.className = 'sim-text';
            simText.style.marginLeft = '8px';
            simText.textContent = Math.round(h.similarity * 100) + '%';
            wrap.appendChild(simText);
            tdSim.appendChild(wrap);
        } else {
            tdSim.innerHTML = '<span style="color:var(--text-dim)">—</span>';
        }

        const tdTime = document.createElement('td');
        tdTime.className = 'time-cell';
        tdTime.textContent = h.timestamp ? new Date(h.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'}) : '—';

        tr.appendChild(tdQuery);
        tr.appendChild(tdBadge);
        tr.appendChild(tdSim);
        tr.appendChild(tdTime);
        return tr;
    }

    function renderHistory(history) {
        const tbody = document.getElementById('history');
        // reuse existing rows where possible
        for (let i = 0; i < history.length; i++) {
            const h = history[i];
            if (i < tbody.children.length) {
                const row = tbody.children[i];
                row.style.animationDelay = (i * 0.03) + 's';
                const q = row.querySelector('.q');
                if (q && q.textContent !== (h.query_preview || '—')) q.textContent = h.query_preview || '—';

                const badgeCell = row.querySelector('.badge-cell');
                if (badgeCell) {
                    const existingBadge = badgeCell.querySelector('.badge');
                    const shouldBeHit = !!h.cached;
                    if (!existingBadge || existingBadge.classList.contains('badge-hit') !== shouldBeHit) {
                        badgeCell.innerHTML = '';
                        const nb = document.createElement('span');
                        nb.className = shouldBeHit ? 'badge badge-hit' : 'badge badge-miss';
                        nb.innerHTML = shouldBeHit ? '&#10003; cache hit' : '&#8594; api call';
                        badgeCell.appendChild(nb);
                    }
                }

                const simCell = row.querySelector('.sim-cell');
                if (simCell) {
                    if (h.similarity > 0) {
                        let fill = simCell.querySelector('.sim-fill');
                        const pct = Math.round(h.similarity * 100);
                        if (!fill) {
                            simCell.innerHTML = '';
                            const wrap = document.createElement('div');
                            wrap.className = 'sim-bar-wrap';
                            const bar = document.createElement('div');
                            bar.className = 'sim-bar';
                            fill = document.createElement('div');
                            fill.className = pct > 80 ? 'sim-fill' : 'sim-fill low';
                            fill.style.width = pct + '%';
                            bar.appendChild(fill);
                            wrap.appendChild(bar);
                            const simText = document.createElement('span');
                            simText.className = 'sim-text';
                            simText.style.marginLeft = '8px';
                            simText.textContent = pct + '%';
                            wrap.appendChild(simText);
                            simCell.appendChild(wrap);
                        } else {
                            fill.style.width = pct + '%';
                            fill.className = pct > 80 ? 'sim-fill' : 'sim-fill low';
                            const simText = simCell.querySelector('.sim-text');
                            if (simText) simText.textContent = pct + '%';
                        }
                    } else {
                        simCell.innerHTML = '<span style="color:var(--text-dim)">—</span>';
                    }
                }

                const timeCell = row.querySelector('.time-cell');
                const newTime = h.timestamp ? new Date(h.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'}) : '—';
                if (timeCell && timeCell.textContent !== newTime) timeCell.textContent = newTime;
            } else {
                tbody.appendChild(createHistoryRow(h, i));
            }
        }
        // remove extra rows
        while (tbody.children.length > history.length) tbody.removeChild(tbody.lastChild);
    }

    function fetchStats() {
        fetch('/api/stats')
            .then(r => r.json())
            .then(d => {
                animateValue(document.getElementById('hit-rate'), (d.hit_rate_pct || 0) + '%');
                animateValue(document.getElementById('water'), formatStat(d.water_saved_ml, 1));
                animateValue(document.getElementById('carbon'), formatStat(d.carbon_saved_g, 1));
                animateValue(document.getElementById('total'), String(d.total_queries || 0));

                document.getElementById('hit-sub').textContent =
                    (d.cache_hits || 0) + ' of ' + (d.total_queries || 0) + ' queries from cache';
                document.getElementById('water-sub').textContent =
                    'mL · ' + formatStat(d.water_saved_bottles, 2) + ' × 500mL bottles';
                document.getElementById('carbon-sub').textContent =
                    'grams · ' + formatStat(d.carbon_equiv_km_driven, 3) + ' km not driven';

                const history = (d.history || []).slice().reverse().slice(0, 25);
                const empty = document.getElementById('empty-state');
                if (history.length === 0) {
                    document.getElementById('history').innerHTML = '';
                    empty.style.display = 'block';
                } else {
                    empty.style.display = 'none';
                    renderHistory(history);
                }

                document.getElementById('query-count').textContent =
                    'showing ' + Math.min(history.length, 25) + ' most recent';
                document.getElementById('last-updated').textContent =
                    new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
            })
            .catch(() => {
                document.getElementById('last-updated').textContent = 'error fetching data';
            });
    }

    fetchStats();
    setInterval(fetchStats, 5000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/stats')
def stats():
    metrics_file = os.path.join(os.path.dirname(__file__), '..', 'savings.json')
    if os.path.exists(metrics_file):
        with open(metrics_file) as f:
            data = json.load(f)
        total = data["total_queries"]
        hits = data["cache_hits"]
        return jsonify({
            "total_queries": total,
            "cache_hits": hits,
            "hit_rate_pct": round(hits / total * 100, 1) if total > 0 else 0,
            "water_saved_ml": round(data["water_saved_ml"], 1),
            "carbon_saved_g": round(data["carbon_saved_g"], 1),
            "water_saved_bottles": round(data["water_saved_ml"] / 500, 2),
            "carbon_equiv_km_driven": round(data["carbon_saved_g"] / 180, 3),
            "history": data.get("history", [])
        })
    return jsonify({
        "total_queries": 0, "cache_hits": 0, "hit_rate_pct": 0,
        "water_saved_ml": 0, "carbon_saved_g": 0,
        "water_saved_bottles": 0, "carbon_equiv_km_driven": 0,
        "history": []
    })

if __name__ == '__main__':
    # Disable the automatic reloader so file changes (e.g. savings.json updates)
    # don't trigger a full server restart which causes the browser to reload.
    app.run(debug=True, port=5000, use_reloader=False)