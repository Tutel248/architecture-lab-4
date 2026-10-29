import csv
import argparse
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description="RetailFlow Architecture Cost & Evolution Economics Analyzer")
    parser.add_argument("--csv", type=str, default="metrics.csv", help="Path to input CSV file")
    parser.add_argument("--hourly_cost", type=float, default=35.0, help="Engineering hourly cost in USD")
    parser.add_argument("--changes_per_month", type=int, default=20, help="Number of production changes per month")
    parser.add_argument("--incident_impact", type=float, default=4000.0, help="Average business impact per incident in USD")
    parser.add_argument("--tax_savings_share", type=float, default=0.30, help="Estimated share of Architecture Tax saved by intervention (0.0 to 1.0)")
    parser.add_argument("--investment_hours", type=float, default=120.0, help="One-time investment cost in engineering hours")
    
    # Thresholds
    parser.add_argument("--threshold_modules", type=float, default=3.0, help="Threshold for modules_per_change")
    parser.add_argument("--threshold_hours", type=float, default=20.0, help="Threshold for engineering_hours")
    parser.add_argument("--threshold_rollback", type=float, default=0.05, help="Threshold for rollback_rate (0.05 = 5%)")
    
    return parser.parse_args()

def load_metrics(csv_path):
    data = {}
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                period = row['period'].strip()
                data[period] = {
                    'engineering_hours': float(row['engineering_hours']),
                    'changes': float(row.get('changes', 20)),
                    'modules_per_change': float(row['modules_per_change']),
                    'rollback_rate': float(row['rollback_rate']),
                    'incidents': float(row['incidents'])
                }
    except Exception as e:
        print(f"Error reading CSV file '{csv_path}': {e}")
        sys.exit(1)
        
    if 'baseline' not in data or 'current' not in data:
        print("CSV file must contain at least 'baseline' and 'current' periods.")
        sys.exit(1)
        
    return data

def analyze():
    args = parse_arguments()
    metrics = load_metrics(args.csv)
    
    base = metrics['baseline']
    curr = metrics['current']
    
    # 1. Change Costs
    baseline_change_cost = base['engineering_hours'] * args.hourly_cost
    current_change_cost = curr['engineering_hours'] * args.hourly_cost
    
    # 2. Architecture Tax
    cost_diff_per_change = current_change_cost - baseline_change_cost
    architecture_tax_monthly = cost_diff_per_change * args.changes_per_month
    
    # 3. Expected Failure Costs
    baseline_failure_cost = base['incidents'] * args.incident_impact
    current_failure_cost = curr['incidents'] * args.incident_impact
    failure_cost_delta = current_failure_cost - baseline_failure_cost
    
    # 4. Modules per change % increase
    modules_increase_pct = ((curr['modules_per_change'] - base['modules_per_change']) / base['modules_per_change']) * 100
    
    # 5. Threshold checks
    threshold_violations = []
    if curr['modules_per_change'] > args.threshold_modules:
        threshold_violations.append(f"modules_per_change ({curr['modules_per_change']}) > {args.threshold_modules}")
    if curr['engineering_hours'] > args.threshold_hours:
        threshold_violations.append(f"engineering_hours ({curr['engineering_hours']}) > {args.threshold_hours}")
    if curr['rollback_rate'] > args.threshold_rollback:
        threshold_violations.append(f"rollback_rate ({curr['rollback_rate']*100:.1f}%) > {args.threshold_rollback*100:.1f}%")
        
    # 6. Investment & Break-Even
    investment_cost_usd = args.investment_hours * args.hourly_cost
    monthly_tax_savings = architecture_tax_monthly * args.tax_savings_share
    # Assuming 1 incident reduction as well if incidents > 1
    incident_reduction_savings = args.incident_impact if curr['incidents'] > 1 else 0
    total_monthly_savings = monthly_tax_savings + incident_reduction_savings
    
    break_even_months = investment_cost_usd / total_monthly_savings if total_monthly_savings > 0 else float('inf')

    # Output Report
    print("=" * 70)
    print("RETAILFLOW ARCHITECTURE COST & EVOLUTION ECONOMICS REPORT")
    print("=" * 70)
    print(f"Scenario Parameters:")
    print(f"  - Hourly Rate: ${args.hourly_cost:.2f}/hr")
    print(f"  - Changes/Month: {args.changes_per_month}")
    print(f"  - Incident Business Impact: ${args.incident_impact:.2f}")
    print(f"  - Intervention Investment: {args.investment_hours} hrs (${investment_cost_usd:.2f})")
    print("-" * 70)
    print("COST ANALYSIS:")
    print(f"  - Baseline Change Cost: ${baseline_change_cost:.2f} per change")
    print(f"  - Current Change Cost:  ${current_change_cost:.2f} per change")
    print(f"  - ARCHITECTURE TAX (Monthly): ${architecture_tax_monthly:,.2f}")
    print(f"  - ARCHITECTURE TAX (Annual):  ${architecture_tax_monthly * 12:,.2f}")
    print("-" * 70)
    print("FAILURE ANALYSIS:")
    print(f"  - Baseline Failure Cost: ${baseline_failure_cost:,.2f} / month")
    print(f"  - Current Failure Cost:  ${current_failure_cost:,.2f} / month")
    print(f"  - FAILURE COST DELTA:    ${failure_cost_delta:,.2f} / month")
    print("-" * 70)
    print("METRICS EVOLUTION:")
    print(f"  - Modules touched/change: {base['modules_per_change']} -> {curr['modules_per_change']} (+{modules_increase_pct:.1f}%)")
    print(f"  - Engineering hours/change: {base['engineering_hours']} hrs -> {curr['engineering_hours']} hrs")
    print(f"  - Rollback rate: {base['rollback_rate']*100:.1f}% -> {curr['rollback_rate']*100:.1f}%")
    print("-" * 70)
    print("REVIEW THRESHOLDS CHECK:")
    print(f"  - Total Thresholds Triggered: {len(threshold_violations)} / 3")
    for tv in threshold_violations:
        print(f"    [TRIGGERED] {tv}")
    if len(threshold_violations) >= 2:
        print("  => ALERT: At least 2 thresholds crossed! Architectural review is REQUIRED.")
    else:
        print("  => OK: System parameters within acceptable boundaries.")
    print("-" * 70)
    print("INVESTMENT & BREAK-EVEN ANALYSIS:")
    print(f"  - Estimated Monthly Savings: ${total_monthly_savings:,.2f} / month")
    print(f"  - BREAK-EVEN PERIOD: {break_even_months:.2f} months ({break_even_months * 30:.0f} days)")
    print("=" * 70)

if __name__ == "__main__":
    analyze()
