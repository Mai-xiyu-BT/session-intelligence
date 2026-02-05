---
name: session-intelligence
description: Intelligent analysis of OpenClaw session logs to extract insights, TODOs, time tracking, and work patterns. Use when the user wants to analyze their conversation history, generate work summaries, track time spent on tasks, extract action items, or understand their productivity patterns across sessions. Automatically processes session JSONL files to provide actionable intelligence.
---

# Session Intelligence

## Overview

Analyzes OpenClaw session logs to extract actionable insights:
- Work summaries (daily/weekly/monthly)
- TODO extraction and tracking
- Time and cost analytics
- Topic categorization
- Productivity patterns

## When This Skill Activates

- User asks about "what did I work on"
- Requests for "summary of last week"
- "Extract my TODOs" or "what should I do next"
- Time tracking or cost analysis queries
- Pattern recognition across sessions

## Core Capabilities

### 1. Work Summaries

Generate summaries of work across time periods:

```bash
# Daily summary
python3 scripts/generate_summary.py --period day

# Weekly summary
python3 scripts/generate_summary.py --period week

# Custom date range
python3 scripts/generate_summary.py --from 2025-01-01 --to 2025-01-31
```

### 2. TODO Extraction

Automatically extract and manage TODOs:

```bash
# Extract TODOs from all recent sessions
python3 scripts/extract_todos.py --days 7

# Mark TODO as done
python3 scripts/update_todo.py "TASK_ID" --status done

# List all pending TODOs
python3 scripts/list_todos.py --status pending
```

### 3. Time & Cost Analytics

Track time spent and costs:

```bash
# Daily cost breakdown
python3 scripts/cost_analysis.py --period day

# Weekly productivity report
python3 scripts/productivity_report.py --week

# Most active topics
python3 scripts/topic_analysis.py --top 10
```

### 4. Session Search

Advanced search across all sessions:

```bash
# Find all sessions about a topic
python3 scripts/search_sessions.py --query "machine learning"

# Find sessions with specific tool usage
python3 scripts/search_sessions.py --tool browser

# Export sessions to markdown
python3 scripts/export_sessions.py --from 2025-01-01 --format markdown
```

## Workflow

### Weekly Review

1. Generate weekly summary: `generate_summary.py --period week`
2. Extract TODOs: `extract_todos.py --days 7`
3. Check costs: `cost_analysis.py --period week`
4. Review patterns: `productivity_report.py --week`

### Daily Standup

1. Yesterday's summary: `generate_summary.py --period day --offset 1`
2. Today's TODOs: `list_todos.py --status pending`
3. Time allocation: `topic_analysis.py --day`

### Project Retrospective

1. Export all sessions: `export_sessions.py --format markdown`
2. Topic breakdown: `topic_analysis.py --full`
3. Cost summary: `cost_analysis.py --period month`

## Output Formats

### Summary Format
```markdown
# Work Summary (Jan 1-7, 2025)

## Overview
- Sessions: 12
- Messages: 245
- Cost: $3.47
- Time tracked: 8.5 hours

## Topics
1. Code Review (3.2h)
2. Documentation (2.1h)
3. Research (3.2h)

## Key Accomplishments
- Completed API integration
- Fixed authentication bug
- Deployed to staging

## TODOs Extracted
- [ ] Write tests for new endpoint
- [ ] Update documentation
```

### TODO Format
```json
{
  "id": "todo_abc123",
  "text": "Write tests for auth module",
  "source_session": "session_id",
  "created": "2025-01-15T10:30:00Z",
  "status": "pending",
  "priority": "high"
}
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `generate_summary.py` | Create work summaries for any time period |
| `extract_todos.py` | Extract and save TODOs from sessions |
| `list_todos.py` | List and filter TODOs |
| `update_todo.py` | Update TODO status |
| `cost_analysis.py` | Analyze costs and usage |
| `productivity_report.py` | Generate productivity insights |
| `topic_analysis.py` | Categorize and analyze topics |
| `search_sessions.py` | Search across all sessions |
| `export_sessions.py` | Export sessions to various formats |

## Configuration

Store preferences in `~/.config/session-intelligence/config.json`:

```json
{
  "default_period": "week",
  "exclude_topics": ["personal", "chat"],
  "cost_budget": 10.00,
  "todo_storage": "~/.config/session-intelligence/todos.json"
}
```

## Data Privacy

All analysis happens locally. No data is sent to external services.
