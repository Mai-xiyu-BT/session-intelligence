#!/usr/bin/env python3
"""
Cost analysis of session usage.
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


def get_sessions_dir():
    """Get the sessions directory path."""
    return Path.home() / ".openclaw" / "agents" / "main" / "sessions"


def analyze_costs(period='week', days=None):
    """Analyze costs for a time period."""
    sessions_dir = get_sessions_dir()
    
    if not sessions_dir.exists():
        return {"error": "Sessions directory not found"}
    
    # Calculate date range
    now = datetime.now()
    if days:
        start_date = now - timedelta(days=days)
    elif period == 'day':
        start_date = now - timedelta(days=1)
    elif period == 'week':
        start_date = now - timedelta(weeks=1)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    else:
        start_date = now - timedelta(days=7)
    
    daily_costs = defaultdict(float)
    total_messages = 0
    session_count = 0
    
    for jsonl_file in sessions_dir.glob("*.jsonl"):
        if '.deleted.' in jsonl_file.name:
            continue
        
        try:
            with open(jsonl_file, 'r') as f:
                first_line = f.readline()
                if not first_line:
                    continue
                
                data = json.loads(first_line)
                ts = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                
                if ts < start_date:
                    continue
                
                date_key = ts.strftime('%Y-%m-%d')
                session_count += 1
                
                # Read all lines to get costs
                f.seek(0)
                for line in f:
                    try:
                        msg = json.loads(line)
                        if msg.get('type') == 'message':
                            total_messages += 1
                            cost = msg.get('message', {}).get('usage', {}).get('cost', {}).get('total', 0)
                            if cost:
                                daily_costs[date_key] += cost
                    except json.JSONDecodeError:
                        continue
        except Exception:
            continue
    
    total_cost = sum(daily_costs.values())
    avg_daily = total_cost / len(daily_costs) if daily_costs else 0
    
    return {
        'period': period if not days else f'{days} days',
        'total_cost': round(total_cost, 4),
        'total_messages': total_messages,
        'sessions': session_count,
        'avg_daily_cost': round(avg_daily, 4),
        'daily_breakdown': dict(sorted(daily_costs.items()))
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cost analysis")
    parser.add_argument("--period", choices=['day', 'week', 'month'], default='week')
    parser.add_argument("--days", type=int, help="Number of days to analyze")
    
    args = parser.parse_args()
    
    result = analyze_costs(args.period, args.days)
    print(json.dumps(result, indent=2))
