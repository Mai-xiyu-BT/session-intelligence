# 🧠 Session Intelligence

[![ClawHub](https://img.shields.io/badge/ClawHub-Coming%20Soon-blue)](https://clawhub.com)
[![License](https://img.shields.io/badge/License-PolyForm%20Noncommercial%201.0.0-lightgrey)](LICENSE)

An [OpenClaw](https://openclaw.ai) skill for intelligent analysis of session logs. Extract insights, track TODOs, analyze costs, and understand your productivity patterns.

## Features

- 📊 **Work Summaries** - Daily, weekly, and monthly reports
- ✅ **TODO Extraction** - Automatically capture tasks from conversations
- 💰 **Cost Analytics** - Track spending and usage patterns
- 🔍 **Session Search** - Find past work across all sessions
- 📤 **Export Tools** - Export to Markdown or JSON

## Installation

```bash
clawhub install session-intelligence
```

## Quick Start

### Generate Weekly Summary

```bash
python3 scripts/generate_summary.py --period week --format markdown
```

### Extract TODOs

```bash
python3 scripts/extract_todos.py --days 7
cat ~/.config/session-intelligence/todos.json
```

### List Pending TODOs

```bash
python3 scripts/list_todos.py --status pending
```

### Cost Analysis

```bash
python3 scripts/cost_analysis.py --period week
```

### Export Sessions

```bash
python3 scripts/export_sessions.py --from 2025-01-01 --format markdown
```

## Scripts

| Script | Purpose |
|--------|---------|
| `generate_summary.py` | Create work summaries |
| `extract_todos.py` | Extract TODOs from sessions |
| `list_todos.py` | List and filter TODOs |
| `update_todo.py` | Update TODO status |
| `cost_analysis.py` | Analyze costs |
| `export_sessions.py` | Export sessions |

## TODO Management

Extracted TODOs are stored in `~/.config/session-intelligence/todos.json`:

```json
{
  "id": "todo_abc123",
  "text": "Write tests for auth module",
  "status": "pending",
  "priority": "high",
  "created": "2025-01-15T10:30:00Z"
}
```

### Mark TODO as Done

```bash
python3 scripts/update_todo.py TODO_ID --status done
```

## Cost Tracking

Track your OpenClaw usage costs:

```bash
# Weekly report
python3 scripts/cost_analysis.py --period week

# Custom range
python3 scripts/cost_analysis.py --days 30
```

Output:
```json
{
  "total_cost": 12.34,
  "total_messages": 1234,
  "avg_daily_cost": 1.76,
  "daily_breakdown": {
    "2025-01-01": 1.23,
    "2025-01-02": 2.34
  }
}
```

## Why Session Intelligence?

Your OpenClaw sessions contain valuable work history that's hard to access:
- What did I work on last week?
- What TODOs did I mention?
- How much did I spend?
- What topics keep coming up?

**Session Intelligence** turns your conversation history into actionable insights.

## Privacy

All analysis happens locally on your machine. No data is sent to external services.

## License

PolyForm Noncommercial License 1.0.0

- ✅ Personal use
- ✅ Educational use
- ✅ Open source projects
- ❌ Commercial use (without authorization)

Commercial licensing available upon request.

## Contributing

Contributions welcome! Open an issue or pull request.

---

Made for the OpenClaw community
