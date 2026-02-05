#!/usr/bin/env python3
"""
Generate work summaries from session logs for any time period.
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys


def get_agent_id():
    """Get current agent ID from environment or default."""
    return "main"  # Default, can be made configurable


def get_sessions_dir():
    """Get the sessions directory path."""
    home = Path.home()
    return home / ".openclaw" / "agents" / get_agent_id() / "sessions"


def parse_timestamp(ts_str):
    """Parse ISO timestamp string."""
    return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))


def get_session_files(sessions_dir, start_date, end_date):
    """Get session files within date range."""
    files = []
    for jsonl_file in sessions_dir.glob("*.jsonl"):
        if '.deleted.' in jsonl_file.name:
            continue
        try:
            # Get first message timestamp
            result = subprocess.run(
                ['head', '-1', str(jsonl_file)],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                ts = parse_timestamp(data['timestamp'])
                if start_date <= ts <= end_date:
                    files.append((jsonl_file, ts))
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    return sorted(files, key=lambda x: x[1])


def analyze_session(jsonl_file):
    """Analyze a single session file."""
    stats = {
        'messages': 0,
        'user_messages': 0,
        'assistant_messages': 0,
        'cost': 0,
        'tools_used': set(),
        'topics': []
    }
    
    try:
        with open(jsonl_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if data.get('type') != 'message':
                        continue
                    
                    stats['messages'] += 1
                    role = data.get('message', {}).get('role', '')
                    
                    if role == 'user':
                        stats['user_messages'] += 1
                    elif role == 'assistant':
                        stats['assistant_messages'] += 1
                    
                    # Cost
                    cost = data.get('message', {}).get('usage', {}).get('cost', {}).get('total', 0)
                    if cost:
                        stats['cost'] += cost
                    
                    # Tools
                    content = data.get('message', {}).get('content', [])
                    for item in content:
                        if item.get('type') == 'toolCall':
                            stats['tools_used'].add(item.get('name', '').split('.')[0])
                        elif item.get('type') == 'text' and role == 'user':
                            text = item.get('text', '')
                            # Simple topic extraction from first 100 chars
                            if len(stats['topics']) < 5 and len(text) > 20:
                                stats['topics'].append(text[:100])
                                
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading {jsonl_file}: {e}", file=sys.stderr)
    
    stats['tools_used'] = list(stats['tools_used'])
    return stats


def generate_summary(period='week', offset=0, from_date=None, to_date=None):
    """Generate work summary."""
    sessions_dir = get_sessions_dir()
    
    if not sessions_dir.exists():
        return {"error": f"Sessions directory not found: {sessions_dir}"}
    
    # Calculate date range
    now = datetime.now()
    
    if from_date and to_date:
        start_date = datetime.fromisoformat(from_date)
        end_date = datetime.fromisoformat(to_date)
    elif period == 'day':
        target = now - timedelta(days=offset)
        start_date = target.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = target.replace(hour=23, minute=59, second=59)
    elif period == 'week':
        target = now - timedelta(weeks=offset)
        start_date = target - timedelta(days=target.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59)
    elif period == 'month':
        target = now - timedelta(days=offset * 30)
        start_date = target.replace(day=1, hour=0, minute=0, second=0)
        # Simple month end calculation
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1) - timedelta(seconds=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1) - timedelta(seconds=1)
    else:
        return {"error": f"Unknown period: {period}"}
    
    # Get sessions
    session_files = get_session_files(sessions_dir, start_date, end_date)
    
    if not session_files:
        return {
            "period": period,
            "date_range": f"{start_date.date()} to {end_date.date()}",
            "message": "No sessions found in this period"
        }
    
    # Analyze all sessions
    total_stats = {
        'sessions': len(session_files),
        'messages': 0,
        'user_messages': 0,
        'assistant_messages': 0,
        'cost': 0,
        'all_tools': set(),
        'topics': []
    }
    
    for jsonl_file, _ in session_files:
        stats = analyze_session(jsonl_file)
        total_stats['messages'] += stats['messages']
        total_stats['user_messages'] += stats['user_messages']
        total_stats['assistant_messages'] += stats['assistant_messages']
        total_stats['cost'] += stats['cost']
        total_stats['all_tools'].update(stats['tools_used'])
        total_stats['topics'].extend(stats['topics'])
    
    total_stats['all_tools'] = list(total_stats['all_tools'])
    total_stats['date_range'] = f"{start_date.date()} to {end_date.date()}"
    total_stats['period'] = period
    
    return total_stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate work summaries")
    parser.add_argument("--period", choices=['day', 'week', 'month'], default='week',
                       help="Time period for summary")
    parser.add_argument("--offset", type=int, default=0,
                       help="Periods ago (0=current, 1=previous)")
    parser.add_argument("--from", dest='from_date', help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest='to_date', help="End date (YYYY-MM-DD)")
    parser.add_argument("--format", choices=['json', 'markdown'], default='json',
                       help="Output format")
    
    args = parser.parse_args()
    
    summary = generate_summary(args.period, args.offset, args.from_date, args.to_date)
    
    if args.format == 'markdown':
        print(f"# Work Summary ({summary.get('date_range', 'Unknown')})")
        print()
        if 'error' in summary:
            print(f"Error: {summary['error']}")
        elif 'message' in summary:
            print(summary['message'])
        else:
            print(f"## Overview")
            print(f"- Sessions: {summary['sessions']}")
            print(f"- Total Messages: {summary['messages']}")
            print(f"- Your Messages: {summary['user_messages']}")
            print(f"- Assistant Messages: {summary['assistant_messages']}")
            print(f"- Total Cost: ${summary['cost']:.4f}")
            print()
            if summary['all_tools']:
                print(f"## Tools Used")
                for tool in summary['all_tools'][:10]:
                    print(f"- {tool}")
                print()
    else:
        print(json.dumps(summary, indent=2))
