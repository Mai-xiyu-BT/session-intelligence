#!/usr/bin/env python3
"""
Extract TODOs from session logs.
"""

import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys
import uuid


def get_sessions_dir():
    """Get the sessions directory path."""
    home = Path.home()
    return home / ".openclaw" / "agents" / "main" / "sessions"


def get_todo_file():
    """Get the TODO storage file."""
    config_dir = Path.home() / ".config" / "session-intelligence"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "todos.json"


def load_todos():
    """Load existing TODOs."""
    todo_file = get_todo_file()
    if todo_file.exists():
        with open(todo_file, 'r') as f:
            return json.load(f)
    return []


def save_todos(todos):
    """Save TODOs to file."""
    todo_file = get_todo_file()
    with open(todo_file, 'w') as f:
        json.dump(todos, f, indent=2)


def extract_todos_from_text(text, session_id, timestamp):
    """Extract TODOs from text using patterns."""
    todos = []
    
    # Patterns for TODO extraction
    patterns = [
        r'(?:TODO|todo|Todo)[\s:,-]+(.+?)(?:\n|$)',
        r'(?:- \[ \]|\[ \])[\s]*(.+?)(?:\n|$)',
        r'(?:need to|should|must)[\s]+(.+?)(?:\n|$)',
        r'(?:remember to|don\'t forget to)[\s]+(.+?)(?:\n|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            todo_text = match.group(1).strip()
            if len(todo_text) > 5 and len(todo_text) < 200:
                todos.append({
                    'id': f"todo_{uuid.uuid4().hex[:8]}",
                    'text': todo_text,
                    'source_session': session_id,
                    'created': timestamp,
                    'status': 'pending',
                    'priority': 'medium'
                })
    
    return todos


def extract_todos(days=7):
    """Extract TODOs from recent sessions."""
    sessions_dir = get_sessions_dir()
    
    if not sessions_dir.exists():
        return {"error": f"Sessions directory not found"}
    
    cutoff = datetime.now() - timedelta(days=days)
    existing_todos = load_todos()
    existing_texts = {t['text'] for t in existing_todos}
    
    new_todos = []
    
    for jsonl_file in sessions_dir.glob("*.jsonl"):
        if '.deleted.' in jsonl_file.name:
            continue
        
        try:
            with open(jsonl_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if data.get('type') != 'message':
                            continue
                        
                        # Check timestamp
                        ts = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                        if ts < cutoff:
                            continue
                        
                        # Extract text from user messages
                        if data.get('message', {}).get('role') == 'user':
                            content = data.get('message', {}).get('content', [])
                            for item in content:
                                if item.get('type') == 'text':
                                    text = item.get('text', '')
                                    todos = extract_todos_from_text(
                                        text, 
                                        jsonl_file.stem,
                                        data['timestamp']
                                    )
                                    for todo in todos:
                                        if todo['text'] not in existing_texts:
                                            new_todos.append(todo)
                                            existing_texts.add(todo['text'])
                    except (json.JSONDecodeError, ValueError):
                        continue
        except Exception as e:
            print(f"Error reading {jsonl_file}: {e}", file=sys.stderr)
    
    # Merge and save
    all_todos = existing_todos + new_todos
    save_todos(all_todos)
    
    return {
        'extracted': len(new_todos),
        'total': len(all_todos),
        'new_todos': new_todos
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract TODOs from sessions")
    parser.add_argument("--days", type=int, default=7, help="Days to look back")
    parser.add_argument("--format", choices=['json', 'text'], default='json')
    
    args = parser.parse_args()
    
    result = extract_todos(args.days)
    
    if args.format == 'text':
        print(f"Extracted {result['extracted']} new TODOs")
        print(f"Total TODOs: {result['total']}")
        print()
        for todo in result.get('new_todos', []):
            print(f"- [ ] {todo['text']}")
    else:
        print(json.dumps(result, indent=2))
