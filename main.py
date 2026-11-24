"""Population Data Chartbook — Main Application Entry Point.
Project #96 | Python for Good Hackathon | Domain: Data & Visualization

Usage:
    python main.py                  # Launch Interactive Terminal Interface (CLI)
    python main.py --gui            # Launch Desktop Graphical User Interface (Tkinter)
    python main.py --charts         # Headless chartbook generation
    python main.py --export         # Headless multi-format report export
    python main.py --summary        # Quick executive summary printout
"""

import sys
import argparse
from pathlib import Path

from src.storage import StorageManager
from src.cli import ChartbookCLI
from src.visualizer import ChartbookVisualizer
from src.exporter import SummaryExporter
from src.analytics import AnalyticsEngine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Population Data Chartbook — Interactive Demographic Visualization & Analysis Tool"
    )
    parser.add_argument("--gui", action="store_true", help="Launch the Desktop GUI (Tkinter) instead of the Terminal CLI.")
    parser.add_argument("--charts", action="store_true", help="Generate all visual Matplotlib charts headlessly and exit.")
    parser.add_argument("--export", action="store_true", help="Generate Markdown, CSV, and Audit log exports headlessly and exit.")
    parser.add_argument("--summary", action="store_true", help="Print executive demographic summary to console and exit.")

    args = parser.parse_args()

    # Initialize storage manager (loads or seeds dataset with corruption defense)
    storage = StorageManager()

    if args.gui:
        from src.gui import launch_gui
        launch_gui(storage)
        return

    if args.charts:
        print("Generating all visual charts...")
        visualizer = ChartbookVisualizer(storage.get_all_records())
        results = visualizer.generate_all_charts()
        print(f"Generated {len(results)} charts in 'exports/charts/':")
        for k, p in results.items():
            print(f"  • {k}: {p}")
        return

    if args.export:
        print("Compiling multi-format summary exports...")
        exporter = SummaryExporter(storage.get_all_records())
        results = exporter.export_all()
        print("Export completed:")
        for k, p in results.items():
            print(f"  • {k}: {p}")
        return

    if args.summary:
        engine = AnalyticsEngine(storage.get_all_records())
        summary = engine.compute_executive_summary()
        print("\n=== POPULATION DATA CHARTBOOK — EXECUTIVE SUMMARY ===")
        print(f"Total Records:       {summary['total_records']}")
        print(f"Unique Nations:      {summary['unique_countries']}")
        print(f"Total Population:    {summary['total_population']:,}")
        print(f"Average Population:  {int(summary['average_population']):,}")
        print(f"Median Population:   {int(summary['median_population']):,}")
        print(f"Average Density:     {summary['average_density']:,.2f} people/km²")
        print(f"Average Growth Rate: {summary['average_growth_rate']:+.2f}%\n")
        return

    # Default to Interactive Terminal Interface
    cli = ChartbookCLI(storage)
    cli.run()


if __name__ == "__main__":
    main()
