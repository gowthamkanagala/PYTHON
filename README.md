# 🌐 Population Data Chartbook

> **Project #96 | Python for Good Hackathon**  
> **Domain:** Data & Visualization  
> **Standard:** Python 3.10+ (Standard Library + Matplotlib)

---

## 1. Problem Context & Objective

In academic, public health, policy, and everyday environments, stakeholders frequently experience friction when attempting to visualize and analyze population datasets using manual spreadsheets or fragmented, expensive tools. Without an integrated, automated utility, records are susceptible to calculation errors, misplaced entries, and delayed status insights.

**Population Data Chartbook** is a robust, accessible, beginner-friendly Python application engineered to streamline demographic data handling, enforce strict defensive input validation, ensure reliable local persistence (JSON/CSV), calculate executive summaries, and generate publication-quality visual chartbooks.

---

## 2. Key Capabilities & Features

### Core Features (Must-Have)
- **Interactive Terminal Interface:** Menu-driven command prompt with ANSI styling, clear workflow banners, and formatted tabular views with pagination.
- **Defensive Input Validation:** Real-time sanitization and boundary checks for country names, ISO codes, geographic regions, calendar years, population counts, land area, growth rates, birth/death rates, and median ages.
- **Core Business Logic Engine:** Computes population density (people/km²), natural increase rate (births - deaths), continental aggregations, demographic extremes, and multi-year trajectory comparisons.
- **Local Data Persistence:** Automated serialization and deserialization to JSON (`data/population_records.json`) and CSV (`data/sample_population.csv`), surviving application restarts with atomic file writes.
- **Record Query & Search:** Keyword and category-based filtering tools allowing rapid retrieval by continent, keyword, year, or population threshold.
- **Executive Summary Generation:** Comprehensive aggregation module computing totals, averages, medians, demographic extremes, and continental breakdowns.
- **Visual Data Plotting:** Matplotlib integration rendering horizontal bar charts, continental distribution donut charts, density comparisons on logarithmic scales, annual growth divergences, and multi-year historical trend curves.

### Stretch Features (Good-to-Have)
- **Multi-Format Summary Export:** Generates structured Markdown (`exports/reports/population_chartbook_report.md`), plain-text audit logs (`exports/reports/audit_log_snapshot.txt`), and standardized CSV datasets.
- **Threshold Warning Indicators:** Automated console warning flags highlighting critical demographic breaches (e.g., negative population growth, hyper-density > 1,000/km², mortality deficits, and super-aged populations).
- **Interactive GUI Enhancement:** Built-in lightweight desktop Graphical User Interface (using standard library `tkinter`) with live search filtering, modal input dialogs, and one-click chart generation.
- **Bulk Dataset Import:** Ability to ingest legacy/external CSV files with schema mapping, row-by-row validation, and detailed diagnostic error logging.
- **Storage Corruption Recovery:** Encapsulates file I/O within defensive `try-except` blocks to detect missing or corrupted storage files, back up corrupted data to `.corrupt_<timestamp>.bak`, and restore a clean template seamlessly.

---

## 3. Directory Structure

```text
PYTHON SRS/
├── data/
│   ├── population_records.json       # Primary JSON persistent database
│   ├── sample_population.csv         # Structured CSV persistence copy
│   └── legacy_import_sample.csv      # Sample legacy file for testing bulk imports
├── exports/
│   ├── charts/                       # Generated high-resolution Matplotlib charts
│   │   ├── master_chartbook_dashboard.png
│   │   ├── top_populations.png
│   │   ├── regional_distribution.png
│   │   ├── density_comparison.png
│   │   ├── growth_rates.png
│   │   └── historical_trends.png
│   └── reports/                      # Multi-format executive reports
│       ├── population_chartbook_report.md
│       ├── population_standardized_export.csv
│       └── audit_log_snapshot.txt
├── logs/
│   └── audit.log                     # Live chronological system audit log
├── src/
│   ├── __init__.py
│   ├── models.py                     # PopulationRecord dataclass & ThresholdWarning
│   ├── validator.py                  # Defensive input validation & prompt wrappers
│   ├── storage.py                    # JSON/CSV persistence & corruption recovery
│   ├── analytics.py                  # Aggregation engine & threshold detection
│   ├── visualizer.py                 # Matplotlib publication chart generators
│   ├── exporter.py                   # Markdown, CSV, and text log exporter
│   ├── cli.py                        # Interactive ANSI terminal UI & pagination
│   └── gui.py                        # Lightweight Tkinter desktop GUI
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_validator.py
│   ├── test_storage.py
│   ├── test_analytics.py
│   ├── test_exporter.py
│   └── test_visualizer.py
├── main.py                           # Application entry point with CLI flags
├── run_tests.py                      # Automated test suite runner (34 unit tests)
├── requirements.txt                  # Python dependencies (matplotlib)
└── README.md                         # Documentation & Demo Guide
```

---

## 4. Installation & Requirements

The project runs on **Python 3.10+**. The backend, storage, validation, and GUI components utilize the Python Standard Library. **Matplotlib** is used for visual chart generation.

```bash
# 1. Install dependencies
pip install -r requirements.txt
```

---

## 5. Usage & Execution Modes

### Mode 1: Interactive Terminal Interface (Default)
Launch the interactive terminal console with ANSI formatting and guided menus:
```bash
python main.py
# or
npm run cli
```

### Mode 2: Interactive Web Dashboard (Dev Server)
Launch the local web dashboard server (accessible via web browser):
```bash
npm run dev
# or
python server.py
```
Open **http://127.0.0.1:5000** in your browser to explore metrics, live charts, record search, and exports.

### Mode 3: Desktop Graphical User Interface (Tkinter GUI)
Launch the visual desktop GUI with live search and table view:
```bash
python main.py --gui
# or
npm run gui
```

### Mode 4: Headless Visual Chart Generation
Generate all high-resolution charts in `exports/charts/` headlessly:
```bash
python main.py --charts
# or
npm run charts
```

### Mode 5: Headless Multi-Format Report Export
Compile Markdown, CSV, and Audit Log reports in `exports/reports/` headlessly:
```bash
python main.py --export
# or
npm run export
```

### Mode 6: Quick Executive Summary
Print an immediate demographic summary to the terminal and exit:
```bash
python main.py --summary
# or
npm run summary
```

---

## 6. What a Good Demo Looks Like (Hackathon Walkthrough)

Follow these steps to conduct an impressive 5-minute hackathon demonstration:

1. **Launch the Terminal Interface:**
   Run `python main.py`. Point out the branded header and clean menu options (0-11).
2. **Browse the Dataset with Pagination:**
   Select Option `[1]`. Show how 38 diverse nations (normal cases, microstates, megacountries) are displayed across pages with fixed-width column alignment. Use `[N]` for next page and `[S]` to sort by population or density.
3. **Demonstrate Defensive Validation:**
   Select Option `[3]` (Add New Record). Intentionally enter invalid data to show how the system catches errors without crashing:
   - Enter a country with numbers like `"Country 123"` -> System rejects and explains valid format.
   - Enter invalid year `"1800"` or non-numeric input `"twenty-twenty"` -> System prompts until valid.
   - Enter a negative population or land area -> Caught by boundary checks.
   - Complete valid input -> Observe calculated density and natural increase metrics displayed immediately.
4. **Display Executive Analytics & Regional Breakdown:**
   Select Option `[6]`. Showcase the summary table: total sample population (5.4+ billion), world share by continent (Asia 67.7%, Americas 14.2%, Africa 11.2%, etc.), and demographic extremes (Monaco highest density, Mongolia lowest density).
5. **Inspect Automated Threshold Warnings:**
   Select Option `[7]`. Show how the system flags critical indicators:
   - 🚨 Demographic contraction (negative growth in Japan, Bulgaria, China)
   - 🚨 Mortality inversion (deaths exceeding births in Germany, Italy)
   - ⚠️ Hyper-density warnings in Singapore and Bangladesh
   - ⚠️ Super-aged population in Japan and Italy
6. **Generate Visual Charts:**
   Select Option `[8]`. Matplotlib produces 6 publication charts including the 4-panel master dashboard.
7. **Compile Multi-Format Exports:**
   Select Option `[9]`. Generate the Markdown report (`exports/reports/population_chartbook_report.md`) and standardized CSV.
8. **Demonstrate Persistence & Corruption Recovery:**
   Exit the program (`[0]`). Re-run `python main.py --summary` to prove all records and updates survive program restarts.
9. **Launch the Desktop GUI:**
   Run `python main.py --gui` to show the optional Tkinter desktop dashboard for non-technical users.

---

## 7. Running the Automated Test Suite

A comprehensive test suite of **34 unit tests** validates models, input boundary limits, JSON/CSV persistence, corruption recovery, analytics, chart generation, and report exporters:

```bash
python run_tests.py
```

Expected output:
```text
Ran 34 tests in 1.454s

OK
```

---

## 8. Domain Constraints & Validation Rules

| Attribute | Valid Domain / Type | Bounds / Rules | Error Handling |
| :--- | :--- | :--- | :--- |
| **Country Name** | `str` | 2 – 70 characters; letters, spaces, hyphens | Prompts until valid |
| **Country Code** | `str` | 2 – 3 alphabetic characters; uppercase | Auto-capitalized |
| **Region** | `str` | Must be: Africa, Americas, Asia, Europe, Oceania | Dropdown / strict match |
| **Year** | `int` | 1900 – 2100 | Range checked |
| **Population** | `int` | 1 – 3,000,000,000 | Commas stripped |
| **Land Area** | `float` | 0.01 – 50,000,000.0 sq km | Non-zero, positive |
| **Growth Rate** | `float` | -15.0% to +15.0% | Percentage parsed |
| **Birth / Death Rate** | `float` | 0.0 – 100.0 per 1,000 | Demographic bounds |
| **Urban Population** | `float` | 0.0% – 100.0% | Percentage bounds |
| **Median Age** | `float` | 10.0 – 90.0 years | Demographic bounds |

---

## 9. License & Authorship

Developed for **Python for Good | Project #96: Population Data Chartbook**.  
Built with Python 3.10+ Standard Library and Matplotlib.
