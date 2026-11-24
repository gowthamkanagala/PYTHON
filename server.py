"""Population Data Chartbook — Web Application Server.
Provides an interactive browser dashboard, REST APIs, live chart previews,
and multi-format export downloads.

Usage:
    python server.py               # Starts dev server on http://127.0.0.1:5000
    npm run dev                    # Triggered via npm script
"""

import os
from pathlib import Path
from flask import Flask, jsonify, request, send_file, send_from_directory, render_template_string

from src.storage import StorageManager
from src.models import PopulationRecord
from src.validator import validate_record_dict
from src.analytics import AnalyticsEngine
from src.visualizer import ChartbookVisualizer
from src.exporter import SummaryExporter

app = Flask(__name__)
storage = StorageManager()

# Ensure charts exist on startup
CHARTS_DIR = Path("exports/charts").resolve()
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
if not (CHARTS_DIR / "master_chartbook_dashboard.png").exists():
    visualizer = ChartbookVisualizer(storage.get_all_records())
    visualizer.generate_all_charts()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Population Data Chartbook — Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        body { background-color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; color: #1e293b; }
        .hero-banner { background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); color: white; padding: 2rem 0; margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
        .kpi-card { border: none; border-radius: 12px; box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1); transition: transform 0.2s; }
        .kpi-card:hover { transform: translateY(-2px); }
        .badge-critical { background-color: #ef4444; color: white; }
        .badge-warning { background-color: #f59e0b; color: white; }
        .badge-info { background-color: #0ea5e9; color: white; }
        .table-responsive { max-height: 480px; overflow-y: auto; }
        .chart-img { max-height: 450px; object-fit: contain; width: 100%; border-radius: 8px; border: 1px solid #e2e8f0; }
        .nav-pills .nav-link.active { background-color: #2563eb; }
    </style>
</head>
<body>

<!-- Header Banner -->
<div class="hero-banner">
    <div class="container">
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <h1 class="h3 fw-bold mb-1"><i class="bi bi-globe-americas me-2"></i>Population Data Chartbook</h1>
                <p class="mb-0 text-slate-300 small">Project #96: Data & Visualization | Python for Good Hackathon</p>
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-outline-light btn-sm" onclick="exportReports()"><i class="bi bi-file-earmark-arrow-down me-1"></i>Export Reports</button>
                <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#addRecordModal"><i class="bi bi-plus-circle me-1"></i>Add Record</button>
            </div>
        </div>
    </div>
</div>

<div class="container mb-5">

    <!-- KPI Metric Cards -->
    <div class="row g-3 mb-4">
        <div class="col-md-3 col-sm-6">
            <div class="card kpi-card bg-white p-3">
                <div class="text-muted small text-uppercase fw-semibold">Total Sample Pop</div>
                <div class="h4 fw-bold mb-0 text-primary" id="kpi-pop">—</div>
                <div class="small text-muted" id="kpi-nations">— nations represented</div>
            </div>
        </div>
        <div class="col-md-3 col-sm-6">
            <div class="card kpi-card bg-white p-3">
                <div class="text-muted small text-uppercase fw-semibold">Mean Population</div>
                <div class="h4 fw-bold mb-0 text-dark" id="kpi-avg-pop">—</div>
                <div class="small text-muted" id="kpi-med-pop">Median: —</div>
            </div>
        </div>
        <div class="col-md-3 col-sm-6">
            <div class="card kpi-card bg-white p-3">
                <div class="text-muted small text-uppercase fw-semibold">Avg Density</div>
                <div class="h4 fw-bold mb-0 text-success" id="kpi-density">—</div>
                <div class="small text-muted">people / sq km</div>
            </div>
        </div>
        <div class="col-md-3 col-sm-6">
            <div class="card kpi-card bg-white p-3">
                <div class="text-muted small text-uppercase fw-semibold">Threshold Alerts</div>
                <div class="h4 fw-bold mb-0 text-danger" id="kpi-alerts">—</div>
                <div class="small text-muted">demographic flags active</div>
            </div>
        </div>
    </div>

    <!-- Charts Section -->
    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-white border-0 pt-3 pb-2 d-flex justify-content-between align-items-center">
            <ul class="nav nav-pills card-header-pills" id="chartTabs">
                <li class="nav-item"><a class="nav-link active btn-sm" href="#" onclick="showChart('master')">Master Dashboard</a></li>
                <li class="nav-item"><a class="nav-link btn-sm" href="#" onclick="showChart('top')">Top Populations</a></li>
                <li class="nav-item"><a class="nav-link btn-sm" href="#" onclick="showChart('regional')">Regional Share</a></li>
                <li class="nav-item"><a class="nav-link btn-sm" href="#" onclick="showChart('density')">Density Extremes</a></li>
                <li class="nav-item"><a class="nav-link btn-sm" href="#" onclick="showChart('growth')">Growth Rates</a></li>
                <li class="nav-item"><a class="nav-link btn-sm" href="#" onclick="showChart('trends')">Historical Trends</a></li>
            </ul>
            <button class="btn btn-outline-secondary btn-sm" onclick="regenerateCharts()"><i class="bi bi-arrow-clockwise me-1"></i>Regenerate</button>
        </div>
        <div class="card-body text-center p-3">
            <img id="chartDisplay" src="/charts/master_chartbook_dashboard.png" class="chart-img img-fluid" alt="Chart Preview">
        </div>
    </div>

    <!-- Main Content Tabs (Data Table & Warnings) -->
    <div class="row g-4">
        <div class="col-lg-8">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-white py-3 border-0 d-flex justify-content-between align-items-center">
                    <h5 class="fw-bold mb-0"><i class="bi bi-table me-2"></i>Population Dataset Records</h5>
                    <div class="d-flex gap-2">
                        <input type="text" id="searchInput" class="form-control form-control-sm" placeholder="Search country, code..." onkeyup="filterTable()">
                        <select id="regionFilter" class="form-select form-select-sm" style="width: 140px;" onchange="filterTable()">
                            <option value="ALL">All Regions</option>
                            <option value="Africa">Africa</option>
                            <option value="Americas">Americas</option>
                            <option value="Asia">Asia</option>
                            <option value="Europe">Europe</option>
                            <option value="Oceania">Oceania</option>
                        </select>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0" id="recordsTable">
                            <thead class="table-light small text-uppercase">
                                <tr>
                                    <th>ID</th>
                                    <th>Country</th>
                                    <th>Region</th>
                                    <th>Year</th>
                                    <th class="text-end">Population</th>
                                    <th class="text-end">Density</th>
                                    <th class="text-end">Growth</th>
                                    <th class="text-center">Action</th>
                                </tr>
                            </thead>
                            <tbody id="recordsBody" class="small">
                                <tr><td colspan="8" class="text-center py-4 text-muted">Loading records...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-lg-4">
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-white py-3 border-0 d-flex justify-content-between align-items-center">
                    <h5 class="fw-bold mb-0 text-danger"><i class="bi bi-exclamation-triangle-fill me-2"></i>Threshold Alerts</h5>
                    <span class="badge bg-danger rounded-pill" id="warningBadge">0</span>
                </div>
                <div class="card-body p-0" style="max-height: 480px; overflow-y: auto;">
                    <div class="list-group list-group-flush small" id="warningsList">
                        <div class="p-3 text-muted">Scanning thresholds...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

</div>

<!-- Modal: Add Record -->
<div class="modal fade" id="addRecordModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title fw-bold">➕ Add New Population Record</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="addForm">
                    <div class="row g-2 mb-2">
                        <div class="col-8">
                            <label class="form-label small">Country Name</label>
                            <input type="text" id="m_country" class="form-control form-control-sm" required placeholder="e.g. Netherlands">
                        </div>
                        <div class="col-4">
                            <label class="form-label small">ISO Code</label>
                            <input type="text" id="m_code" class="form-control form-control-sm" required placeholder="NLD" maxlength="3">
                        </div>
                    </div>
                    <div class="row g-2 mb-2">
                        <div class="col-6">
                            <label class="form-label small">Region</label>
                            <select id="m_region" class="form-select form-select-sm">
                                <option>Africa</option>
                                <option>Americas</option>
                                <option>Asia</option>
                                <option selected>Europe</option>
                                <option>Oceania</option>
                            </select>
                        </div>
                        <div class="col-6">
                            <label class="form-label small">Year</label>
                            <input type="number" id="m_year" class="form-control form-control-sm" value="2024" min="1900" max="2100">
                        </div>
                    </div>
                    <div class="row g-2 mb-2">
                        <div class="col-6">
                            <label class="form-label small">Population</label>
                            <input type="number" id="m_pop" class="form-control form-control-sm" required placeholder="17900000">
                        </div>
                        <div class="col-6">
                            <label class="form-label small">Land Area (sq km)</label>
                            <input type="number" step="0.1" id="m_area" class="form-control form-control-sm" required placeholder="41543">
                        </div>
                    </div>
                    <div class="row g-2 mb-2">
                        <div class="col-4">
                            <label class="form-label small">Growth %</label>
                            <input type="number" step="0.01" id="m_growth" class="form-control form-control-sm" value="0.5">
                        </div>
                        <div class="col-4">
                            <label class="form-label small">Birth Rate /1k</label>
                            <input type="number" step="0.1" id="m_birth" class="form-control form-control-sm" value="9.5">
                        </div>
                        <div class="col-4">
                            <label class="form-label small">Death Rate /1k</label>
                            <input type="number" step="0.1" id="m_death" class="form-control form-control-sm" value="9.8">
                        </div>
                    </div>
                    <div class="row g-2 mb-2">
                        <div class="col-6">
                            <label class="form-label small">Urban %</label>
                            <input type="number" step="0.1" id="m_urban" class="form-control form-control-sm" value="92.5">
                        </div>
                        <div class="col-6">
                            <label class="form-label small">Median Age</label>
                            <input type="number" step="0.1" id="m_age" class="form-control form-control-sm" value="42.8">
                        </div>
                    </div>
                    <div class="mb-2">
                        <label class="form-label small">Notes (Optional)</label>
                        <input type="text" id="m_notes" class="form-control form-control-sm" placeholder="Source / notes">
                    </div>
                    <div id="modalError" class="alert alert-danger py-2 small d-none"></div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary btn-sm" onclick="submitRecord()">Save Record</button>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
    let allRecords = [];
    const chartMap = {
        'master': '/charts/master_chartbook_dashboard.png',
        'top': '/charts/top_populations.png',
        'regional': '/charts/regional_distribution.png',
        'density': '/charts/density_comparison.png',
        'growth': '/charts/growth_rates.png',
        'trends': '/charts/historical_trends.png'
    };

    function showChart(key) {
        document.querySelectorAll('#chartTabs .nav-link').forEach(l => l.classList.remove('active'));
        event.target.classList.add('active');
        document.getElementById('chartDisplay').src = chartMap[key] + '?t=' + Date.now();
    }

    async function loadData() {
        try {
            // Load KPI Summary
            const sumRes = await fetch('/api/summary');
            const summary = await sumRes.json();
            document.getElementById('kpi-pop').innerText = Number(summary.total_population).toLocaleString();
            document.getElementById('kpi-nations').innerText = `${summary.unique_countries} unique nations`;
            document.getElementById('kpi-avg-pop').innerText = Number(summary.average_population).toLocaleString();
            document.getElementById('kpi-med-pop').innerText = `Median: ${Number(summary.median_population).toLocaleString()}`;
            document.getElementById('kpi-density').innerText = Number(summary.average_density).toFixed(1);

            // Load Warnings
            const warnRes = await fetch('/api/warnings');
            const warnings = await warnRes.json();
            document.getElementById('kpi-alerts').innerText = warnings.length;
            document.getElementById('warningBadge').innerText = warnings.length;

            const wList = document.getElementById('warningsList');
            wList.innerHTML = warnings.map(w => {
                const bClass = w.level === 'CRITICAL' ? 'badge-critical' : (w.level === 'WARNING' ? 'badge-warning' : 'badge-info');
                return `
                    <div class="list-group-item p-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="badge ${bClass}">${w.level}</span>
                            <span class="fw-bold">${w.country} (${w.year})</span>
                        </div>
                        <div class="text-secondary small">${w.message}</div>
                        <div class="text-muted" style="font-size: 0.75rem;">Metric: <code>${w.metric}</code> = ${Number(w.value).toFixed(2)} (Limit: ${Number(w.threshold).toFixed(2)})</div>
                    </div>
                `;
            }).join('');

            // Load Table
            const recRes = await fetch('/api/records');
            allRecords = await recRes.json();
            renderTable(allRecords);
        } catch (e) {
            console.error("Error loading dashboard data:", e);
        }
    }

    function renderTable(records) {
        const body = document.getElementById('recordsBody');
        if (records.length === 0) {
            body.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">No records match criteria.</td></tr>';
            return;
        }

        body.innerHTML = records.map(r => {
            const growthBadge = r.growth_rate_pct < 0 
                ? `<span class="text-danger fw-bold">${r.growth_rate_pct.toFixed(2)}%</span>` 
                : `<span class="text-success">${r.growth_rate_pct > 0 ? '+' : ''}${r.growth_rate_pct.toFixed(2)}%</span>`;

            return `
                <tr>
                    <td class="text-muted">${r.record_id}</td>
                    <td class="fw-semibold">${r.country} <span class="text-muted">(${r.country_code})</span></td>
                    <td>${r.region}</td>
                    <td>${r.year}</td>
                    <td class="text-end fw-semibold">${Number(r.population).toLocaleString()}</td>
                    <td class="text-end">${Number(r.population_density).toFixed(1)}/km²</td>
                    <td class="text-end">${growthBadge}</td>
                    <td class="text-center">
                        <button class="btn btn-outline-danger btn-sm py-0 px-1" onclick="deleteRecord('${r.record_id}')" title="Delete"><i class="bi bi-trash"></i></button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function filterTable() {
        const q = document.getElementById('searchInput').value.toLowerCase().trim();
        const reg = document.getElementById('regionFilter').value;

        const filtered = allRecords.filter(r => {
            const matchesQuery = !q || r.country.toLowerCase().includes(q) || r.country_code.toLowerCase().includes(q) || r.region.toLowerCase().includes(q);
            const matchesRegion = (reg === 'ALL') || (r.region === reg);
            return matchesQuery && matchesRegion;
        });
        renderTable(filtered);
    }

    async function submitRecord() {
        const payload = {
            country: document.getElementById('m_country').value,
            country_code: document.getElementById('m_code').value,
            region: document.getElementById('m_region').value,
            year: document.getElementById('m_year').value,
            population: document.getElementById('m_pop').value,
            land_area_sq_km: document.getElementById('m_area').value,
            growth_rate_pct: document.getElementById('m_growth').value,
            birth_rate_per_1k: document.getElementById('m_birth').value,
            death_rate_per_1k: document.getElementById('m_death').value,
            urban_population_pct: document.getElementById('m_urban').value,
            median_age: document.getElementById('m_age').value,
            notes: document.getElementById('m_notes').value
        };

        const res = await fetch('/api/records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        const errDiv = document.getElementById('modalError');

        if (!data.success) {
            errDiv.innerText = data.errors.join('\\n');
            errDiv.classList.remove('d-none');
        } else {
            errDiv.classList.add('d-none');
            const modalEl = document.getElementById('addRecordModal');
            bootstrap.Modal.getInstance(modalEl).hide();
            document.getElementById('addForm').reset();
            loadData();
        }
    }

    async function deleteRecord(id) {
        if (!confirm(`Delete record ${id}?`)) return;
        await fetch(`/api/records/${id}`, { method: 'DELETE' });
        loadData();
    }

    async function regenerateCharts() {
        await fetch('/api/charts/regenerate', { method: 'POST' });
        const img = document.getElementById('chartDisplay');
        img.src = img.src.split('?')[0] + '?t=' + Date.now();
    }

    function exportReports() {
        window.open('/api/export/markdown', '_blank');
        window.open('/api/export/csv', '_blank');
    }

    window.onload = loadData;
</script>

</body>
</html>
"""


# ==============================================================================
# REST API Endpoints
# ==============================================================================

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/charts/<path:filename>")
def serve_chart(filename):
    return send_from_directory(CHARTS_DIR, filename)


@app.route("/api/summary", methods=["GET"])
def api_summary():
    engine = AnalyticsEngine(storage.get_all_records())
    summary = engine.compute_executive_summary()
    return jsonify(summary)


@app.route("/api/records", methods=["GET"])
def api_get_records():
    records = [r.to_dict() for r in storage.get_all_records()]
    return jsonify(records)


@app.route("/api/records", methods=["POST"])
def api_add_record():
    payload = request.get_json() or {}
    is_valid, cleaned, errors = validate_record_dict(payload)
    if not is_valid:
        return jsonify({"success": False, "errors": errors}), 400

    rec = PopulationRecord.from_dict(cleaned)
    storage.add_record(rec)
    return jsonify({"success": True, "record": rec.to_dict()})


@app.route("/api/records/<record_id>", methods=["DELETE"])
def api_delete_record(record_id):
    ok = storage.delete_record(record_id)
    return jsonify({"success": ok})


@app.route("/api/warnings", methods=["GET"])
def api_warnings():
    engine = AnalyticsEngine(storage.get_all_records())
    warnings = [w.__dict__ for w in engine.detect_threshold_warnings()]
    return jsonify(warnings)


@app.route("/api/charts/regenerate", methods=["POST"])
def api_regenerate_charts():
    visualizer = ChartbookVisualizer(storage.get_all_records())
    visualizer.generate_all_charts()
    return jsonify({"success": True})


@app.route("/api/export/markdown", methods=["GET"])
def api_export_markdown():
    exporter = SummaryExporter(storage.get_all_records())
    path = exporter.export_markdown_report()
    return send_file(path, as_attachment=True)


@app.route("/api/export/csv", methods=["GET"])
def api_export_csv():
    exporter = SummaryExporter(storage.get_all_records())
    path = exporter.export_standardized_csv()
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🌐 Population Data Chartbook Web Dashboard running at: http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
