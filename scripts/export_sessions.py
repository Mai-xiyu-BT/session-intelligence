#!/usr/bin/env python3
"""
Export sessions to various formats (Markdown, JSON).
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path


def get_sessions_dir():
    """Get the sessions directory path."""
    return Path.home() / ".openclaw" / "agents" / "main" / "sessions"


def export_to_markdown(sessions, output_file):
    """Export sessions to Markdown."""
    with open(output_file, 'w') as f:
        f.write("# Session Export\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        
        for session in sessions:
            f.write(f"## Session: {session['id'][:8]}\n\n")
            f.write(f"**Date:** {session.get('date', 'Unknown')}\n\n")
            
            for msg in session.get('messages', []):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                
                if role == 'user':
                    f.write(f"**User:** {content}\n\n")
                elif role == 'assistant':
                    f.write(f"**Assistant:** {content[:500]}")
                    if len(content) > 500:
                        f.write("...")
                    f.write("\n\n")
            
            f.write("---\n\n")


def export_sessions(from_date=None, to_date=None, format='json'):
    """Export sessions to specified format."""
    sessions_dir = get_sessions_dir()
    
    if not sessions_dir.exists():
        return {"error": "Sessions directory not found"}
    
    # Parse dates
    if from_date:
        from_dt = datetime.fromisoformat(from_date)
    else:
        from_dt = datetime.now() - timedelta(days=7)
    
    if to_date:
        to_dt = datetime.fromisoformat(to_date)
    else:
        to_dt = datetime.now()
    
    sessions = []
    
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
                
                if not (from_dt <= ts <= to_dt):
                    continue
                
                session_data = {
                    'id': jsonl_file.stem,
                    'date': ts.isoformat(),
                    'messages': []
                }
                
                f.seek(0)
                for line in f:
                    try:
                        msg = json.loads(line)
                        if msg.get('type') == 'message':
                            role = msg.get('message', {}).get('role', '')
                            content_items = msg.get('message', {}).get('content', [])
                            text = ''
                            for item in content_items:
                                if item.get('type') == 'text':
                                    text = item.get('text', '')
                                    break
                            
                            session_data['messages'].append({
                                'role': role,
                                'content': text
                            })
                    except json.JSONDecodeError:
                        continue
                
                sessions.append(session_data)
        except Exception:
            continue
    
    # Sort by date
    sessions.sort(key=lambda s: s.get('date', ''))
    
    # Export
    if format == 'markdown':
        output_file = f"sessions_export_{datetime.now().strftime('%Y%m%d')}.md"
        export_to_markdown(sessions, output_file)
        return {"exported": len(sessions), "file": output_file}
    else:
        output_file = f"sessions_export_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w') as f:
            json.dump(sessions, f, indent=2)
        return {"exported": len(sessions), "file": output_file}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export sessions")
    parser.add_argument("--from", dest='from_date', help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest='to_date', help="End date (YYYY-MM-DD)")
    parser.add_argument("--format", choices=['json', 'markdown'], default='json')
    
    args = parser.parse_args()
    
    result = export_sessions(args.from_date, args.to_date, args.format)
    print(json.dumps(result, indent=2))
