#!/usr/bin/env python3
"""
List and filter TODOs.
"""

import json
import argparse
from pathlib import Path


def get_todo_file():
    """Get the TODO storage file."""
    return Path.home() / ".config" / "session-intelligence" / "todos.json"


def load_todos():
    """Load TODOs from file."""
    todo_file = get_todo_file()
    if todo_file.exists():
        with open(todo_file, 'r') as f:
            return json.load(f)
    return []


def list_todos(status=None, priority=None):
    """List TODOs with optional filtering."""
    todos = load_todos()
    
    if status:
        todos = [t for t in todos if t.get('status') == status]
    if priority:
        todos = [t for t in todos if t.get('priority') == priority]
    
    # Sort by status (pending first), then priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    todos.sort(key=lambda t: (
        0 if t.get('status') == 'pending' else 1,
        priority_order.get(t.get('priority'), 1)
    ))
    
    return todos


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List TODOs")
    parser.add_argument("--status", choices=['pending', 'done', 'all'], 
                       help="Filter by status")
    parser.add_argument("--priority", choices=['high', 'medium', 'low'],
                       help="Filter by priority")
    parser.add_argument("--format", choices=['json', 'markdown'], default='markdown')
    
    args = parser.parse_args()
    
    status = None if args.status == 'all' else args.status
    todos = list_todos(status, args.priority)
    
    if args.format == 'markdown':
        print(f"# TODOs ({len(todos)} items)")
        print()
        
        pending = [t for t in todos if t.get('status') == 'pending']
        done = [t for t in todos if t.get('status') == 'done']
        
        if pending:
            print("## Pending")
            for todo in pending:
                checkbox = "- [ ]"
                priority = f" [{todo.get('priority', 'medium').upper()}]" if todo.get('priority') != 'medium' else ""
                print(f"{checkbox}{priority} {todo['text']} (id: {todo['id']})")
            print()
        
        if done:
            print("## Done")
            for todo in done[:10]:  # Show last 10
                print(f"- [x] {todo['text']}")
            if len(done) > 10:
                print(f"... and {len(done) - 10} more")
    else:
        print(json.dumps(todos, indent=2))
