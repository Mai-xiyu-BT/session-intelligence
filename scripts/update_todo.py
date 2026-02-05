#!/usr/bin/env python3
"""
Update TODO status.
"""

import json
import argparse
from datetime import datetime
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


def save_todos(todos):
    """Save TODOs to file."""
    todo_file = get_todo_file()
    with open(todo_file, 'w') as f:
        json.dump(todos, f, indent=2)


def update_todo(todo_id, status=None, priority=None):
    """Update a TODO's status or priority."""
    todos = load_todos()
    
    for todo in todos:
        if todo['id'] == todo_id or todo['id'].startswith(todo_id):
            if status:
                todo['status'] = status
                if status == 'done':
                    todo['completed_at'] = datetime.now().isoformat()
            if priority:
                todo['priority'] = priority
            save_todos(todos)
            return {"success": True, "todo": todo}
    
    return {"success": False, "error": f"TODO not found: {todo_id}"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update TODO status")
    parser.add_argument("todo_id", help="TODO ID (or prefix)")
    parser.add_argument("--status", choices=['pending', 'done'],
                       help="New status")
    parser.add_argument("--priority", choices=['high', 'medium', 'low'],
                       help="New priority")
    
    args = parser.parse_args()
    
    result = update_todo(args.todo_id, args.status, args.priority)
    print(json.dumps(result, indent=2))
