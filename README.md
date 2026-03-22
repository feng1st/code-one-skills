# Code One Skills

A collection of practical skills and tools for R&D workflows.

## Self-Evolving Topic Memory

Two skills that work together to give you **self-evolving, cross-session topic memory**:

- **`topic-open`** — Opens a topic session, loads relevant memory into context
- **`topic-save`** — Summarizes the session, persists memory and archives

### Features

- **Topic Management**: Organize work by topics; quickly switch between them
- **Cross-Session Memory**: Persistent topic memory that **grows smarter** over time
- **Session Archiving**: Automatic session history with timestamped archives

### Workflow

```
1. Open a topic  →  2. Do your work  →  3. Save the topic
   (load memory)     (code, design…)     (persist memory)
```

### Opening a Topic (`topic-open`)

#### Manual

Tell the skill to open a specific topic:

```
Open topic user-authentication
```

Or use the skill name directly:

```
topic-open user-authentication
```

#### Automatic

When you start generating or modifying technical artifacts (solutions, code, or architecture) and no topic is currently active, the skill automatically detects the theme and opens a matching topic:

```
Please generate a technical solution based on the following PRD.
(The PRD describes requirements for a user authentication feature)
```

The skill searches for matching topics, asks you to confirm, and loads the topic's memory into the conversation.

### Saving a Topic (`topic-save`)

#### Manual

```
Save topic
```

Or use the skill name directly:

```
topic-save
```

#### Automatic

When you open a different topic while one is already active, `topic-save` automatically runs first to persist the current topic's memory before switching.

### Example Session

```
You:  Open topic user-authentication
AI:   Found matching topic "user-authentication". Confirm? (Y/n)
You:  y
AI:   Topic opened. Loaded memory from MEMORY.md.
      [Memory includes: API design decisions, component structure, known issues...]

You:  Please add retry logic to the login API.
AI:   [Works with full context of previous decisions...]

You:  Save topic
AI:   Session saved.
      - Archived session to sessions/20260318-171800-add-retry-logic.md
      - Updated MEMORY.md with retry logic decisions
      - Updated TOPIC.md and index.json
```

### How Memory Is Organized

All topic data lives under a `topics/` directory in your project root:

```
topics/
├── index.json                    # Topic index for quick lookup
└── <topic-name>/
    ├── TOPIC.md                  # Topic definition (boundaries, code scope)
    ├── MEMORY.md                 # Cross-session memory (loaded into context)
    └── sessions/
        └── <timestamp>-<name>.md # Session archives (for reference)
```

- **`MEMORY.md`** is the key file — it accumulates technical decisions, lessons learned, and anti-patterns across sessions so you never lose context.
- **`sessions/`** stores historical archives. They are not loaded by default; only consulted when tracing topic history or resolving conflicts.

## Installation

Requires **Python**. Clone this repository and run the install script:

```bash
git clone https://github.com/feng1st/code-one-skills.git
cd code-one-skills
python install.py
```

By default, skills are installed to `~/.claude/` (`%USERPROFILE%\.claude\` on Windows), which is automatically discovered by Claude Code, Cursor, and OpenCode.

To install for a specific tool, pass the target as an argument:

| Command | Target Directory | Discovered By |
|---------|-----------------|---------------|
| `python install.py` | `~/.claude/` | Claude Code, Cursor, OpenCode |
| `python install.py claude` | `~/.claude/` | Claude Code, Cursor, OpenCode |
| `python install.py codex` | `~/.codex/` | Codex, Cursor |
| `python install.py cursor` | `~/.cursor/` | Cursor |
| `python install.py opencode` | `~/.config/opencode/` | OpenCode |

To uninstall:

```bash
python install.py -r          # uninstall from ~/.claude/ (default)
python install.py -r codex    # uninstall from ~/.codex/
```

Run `python install.py -h` for full usage.

## License

[Apache License 2.0](LICENSE)
