## Quick Start
Run baseline analysis:
py analyze_metrics.py --csv metrics.csv

Run What-If scenario (Enterprise scale):
py analyze_metrics.py --csv metrics.csv --hourly_cost 60 --changes_per_month 35 --incident_impact 10000
