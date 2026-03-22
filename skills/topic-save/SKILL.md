---
name: topic-save
description: Summarize, update, and persist topic memory for the active topic. Use when the user manually triggers a save, or automatically before topic-open switches to a different topic while an active topic exists. Handles session archiving, memory consolidation, topic definition updates, and topic index maintenance. Keywords: topic, memory, save, persist, summarize, session archive, MEMORY.md, TOPIC.md, index.json.
metadata:
  version: "1.0"
  author: feng1st
---

# Topic Save Skill

Summarize, update, and persist `topic_memory` for `active_topic`. Saves a session archive, merges new insights into the topic memory file, and keeps the topic definition and index up to date.

## Global Variables

These variables persist in the system prompt and conversation history throughout the entire session:

- `active_topic`: The name of the currently active topic
- `topic_memory`: The memory content associated with `active_topic`

## Core Rules

**You MUST follow these rules throughout the entire workflow:**

1. **Minimize changes** — only update what has actually changed. Do not rewrite content that is already correct.
2. **Confirm large changes** — if a step would produce a large diff (e.g., rewriting most of `MEMORY.md`), present the proposed changes to the user and wait for confirmation before writing.

## Activation

This skill is activated in one of two ways:

1. **Manual**: The user explicitly triggers `topic-save`.
2. **Automatic**: ALL of the following conditions are met:
   - `active_topic` is not empty AND not "free-topic", AND
   - The `topic-open` skill is about to open a **different** topic

   In this case, save the current `active_topic` before the topic switch proceeds.

## Workflow

### Step 1: Summarize the Active Topic

1.1. Review the conversation history, document changes, and code changes in the current context that are relevant to `active_topic`.

1.2. Produce a concise summary. **Exclude** redundant, outdated, or irrelevant information.

### Step 2: Save Session Archive

2.1. **Skip condition**: If the session contains no substantive actions (e.g., only topic opening/closing, greetings, or trivial Q&A with no code changes, design decisions, or meaningful technical discussion), skip this step entirely — do not create a session archive file.

2.2. **Purpose**: Session archives are historical records. They are NOT loaded during normal conversation — only consulted when tracing topic history, evolution, or resolving decision conflicts.

2.3. Write the session archive to:

```
<PROJECT_ROOT>/topics/<active_topic>/sessions/<yyyyMMdd-HHmmss>-<autogen-name>.md
```

Where `<autogen-name>` is a short, descriptive slug auto-generated from the session content (e.g., `add-retry-logic`, `fix-auth-redirect`).

2.4. The file **MUST** begin with the following header (expand `<active_topic>` to its actual value, but keep `<PROJECT_ROOT>` as-is — do NOT replace it with the actual path):

```markdown
> This file is a historical session archive and may contain outdated information.
> For authoritative conclusions, refer to `<PROJECT_ROOT>/topics/<active_topic>/MEMORY.md`.
```

2.5. Only retain session background and information that may be valuable for future reference.

### Step 3: Update and Save Topic Memory

3.1. **Purpose**: `topic_memory` is a cross-session technical decision summary, loaded into context via `topic-open`. Key content includes:
   - Human-provided code reference instructions (e.g., "for scenario X, refer to class Y")
   - Knowledge or solutions discovered through multi-turn conversations
   - Caveats, anti-patterns, and corrections established through dialogue
   - Related topic references

3.2. Re-read `<PROJECT_ROOT>/topics/<active_topic>/MEMORY.md` into `topic_memory` to ensure no external updates were missed. If the file does not exist, skip this sub-step.

3.3. Merge the summary from Step 1 into `topic_memory`.

3.4. Write the merged `topic_memory` to `<PROJECT_ROOT>/topics/<active_topic>/MEMORY.md`.

3.5. **Merge rules**:
   - Minimize changes — do not rewrite unchanged sections
   - Remove redundant, outdated, or irrelevant content
   - Keep only the latest conclusions — do NOT preserve timelines or historical decision evolution
   - If the resulting diff is large, present it to the user for confirmation before writing

### Step 4: Update Topic Definition

4.1. **Purpose**: The topic definition (`TOPIC.md`) is used for precise topic routing. It should contain: topic boundaries, core code entry points, core code scope, and other information that helps uniquely identify this topic. Keep it short and focused.

4.2. Update `<PROJECT_ROOT>/topics/<active_topic>/TOPIC.md` to reflect the latest state. If this is a new topic, create the file.

### Step 5: Update Topic Index

5.1. **Purpose**: The topic index (`index.json`) is used for coarse topic routing.

5.2. Read `<PROJECT_ROOT>/topics/index.json` (format: `[{"topic": "<name>", "description": "<desc>"}]`). Insert a new entry or update the existing entry for `active_topic`.

5.3. **Validate** that the resulting JSON is well-formed before writing.

## File Structure Reference

```
<PROJECT_ROOT>/
└── topics/
    ├── index.json              # L1: Topic index — coarse routing
    └── <topic_name>/
        ├── TOPIC.md            # L2: Topic definition — precise routing
        ├── MEMORY.md           # L3: Cross-session technical memory — loaded into context
        └── sessions/           # L4: Historical session archives — on-demand only
            └── <yyyyMMdd-HHmmss>-<autogen-name>.md
```

## Examples

### Manual Save

```
User: /topic-save
```

### Automatic Save Before Topic Switch

```
User: /topic-open search-optimization
(active_topic is currently "user-authentication")
```

The skill automatically saves `user-authentication` topic memory before `topic-open` proceeds to switch to `search-optimization`.

## Notes

- Session archive file names use the format `<yyyyMMdd-HHmmss>-<autogen-name>.md` for chronological sorting and quick identification
- `MEMORY.md` should be continuously refined — think of it as a living document that gets sharper over time, not a growing log
- `TOPIC.md` should remain concise — it is an index entry, not a knowledge base
