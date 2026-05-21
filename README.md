# RTK — Request Token Killer

**RTK v1** | A PostToolUse hook for Claude Code that compresses tool output before it enters the context window.

Built for The Family Office agent stack (Mick / ClaudeClaw). Designed to be adopted by any agent running on Claude Code.

---

## What it does

RTK intercepts tool results after they execute but before they consume context tokens. It applies tool-aware compression — no regex guessing, because it already knows the tool name.

| Tool | Compression |
|---|---|
| `Read` | Cross-turn dedup (same file + same content = 1-line replacement). Truncates at 200 lines (120 head + 60 tail). |
| `Bash` | Deduplicates consecutive repeated lines. Head/tail truncation at 150 lines. |
| `Grep` | Caps at 80 match lines. |
| `Glob` | Caps at 150 paths. |
| `WebFetch` / `WebSearch` | Truncates at 300 lines. |

Skips anything under 500 chars or where compression saves less than 5%. No overhead on small outputs.

**Cross-turn file dedup** is unique to this implementation — if the same file is read again in the same session with identical content, RTK replaces the full content with a single-line marker, saving the entire token cost of that re-read.

---

## Install

### 1. Copy the script

Place `rtk.py` somewhere stable on your machine. Recommended:

```
C:\ClaudeClaw\hooks\rtk.py        # Windows
~/.claude/hooks/rtk.py            # Mac / Linux
```

### 2. Wire into Claude Code settings

Add the following to your `~/.claude/settings.json` (or `C:\Users\<you>\.claude\settings.json` on Windows):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Read|Bash|Grep|Glob|WebFetch|WebSearch",
        "hooks": [
          {
            "type": "command",
            "command": "python \"/path/to/rtk.py\""
          }
        ]
      }
    ]
  }
}
```

### 3. Verify Python

RTK uses stdlib only — no pip installs required.

```bash
python --version   # 3.8+ required
```

---

## Requirements

- Python 3.8+
- Claude Code CLI
- No external dependencies

---

## Roadmap (v2+)

- Relevance-weighted truncation (compress based on what was asked, not just size)
- Prompt cache awareness (structure context to maximize Anthropic cache hits)
- Configurable limits per tool
- Obsidian vault integration for cross-session memory

---

## Part of

[The Family Office](https://github.com/signal1project) agent stack.
