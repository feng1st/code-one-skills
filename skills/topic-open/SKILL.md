---
name: topic-open
description: Open a topic session by matching existing topics or creating a new one, then loading topic memory into context. Use when the user explicitly specifies a topic to open, or automatically when the task involves generating or modifying technical artifacts (solutions, code, or architecture) and no topic is currently active. Keywords: topic, memory, PRD, technical solution, code generation, architecture design.
metadata:
  version: "1.0"
  author: feng1st
---

# Topic Open Skill

Open a topic session — match an existing topic or create a new one, then load its memory into the conversation context.

## Parameters

- `<topic>`: (Optional) Explicitly specify the topic name to open.

## Global Variables

These variables persist in the system prompt and conversation history throughout the entire session:

- `active_topic`: The name of the currently active topic
- `topic_memory`: The memory content associated with `active_topic`

## Activation

This skill is activated in one of two ways:

1. **Manual**: The user explicitly provides a `<topic>` parameter. Use it as `pending_topic`.
2. **Automatic**: ALL of the following conditions are met:
   - `active_topic` is empty, AND
   - The current task has a clear, identifiable theme (e.g., "user authentication flow", "search service optimization"), AND
   - The task involves generating or modifying technical artifacts (solutions, code, or architecture). Tasks that do not produce technical artifacts (e.g., Q&A, general writing, todo lists) should NOT trigger automatic activation.
   
   In this case, derive `pending_topic` from the task context.

## Workflow

### Step 0: Pre-check Active Topic

Check the current `active_topic` (only relevant for manual activation, since automatic activation requires `active_topic` to be empty):

- If `active_topic` equals `pending_topic` — inform the user that this topic is already active and skip the rest of the workflow.
- If `active_topic` is set, **not** "free-topic", and differs from `pending_topic` — trigger `topic-save` for the current `active_topic` first, then continue to Step 1.
- Otherwise — continue to Step 1.

### Step 1: Match Existing Topics

#### 1.1 Load Topic Index

Read `<PROJECT_ROOT>/topics/index.json` (format: `[{"topic": "<name>", "description": "<desc>"}]`).

Filter and select up to **5 candidate topics** that best match `pending_topic`.

If the file does not exist, treat as no match — skip to Step 1.4.

#### 1.2 Load Candidate Topic Definitions

Run the definition loader script to load each candidate's `TOPIC.md` definition:

```bash
python <THIS_SKILL_DIR>/scripts/load_topic_definition.py --project-root <PROJECT_ROOT> "<topic_name1>" "<topic_name2>" ...
```

If the script returns empty, treat as no match — skip to Step 1.4.

#### 1.3 Determine Best Match

Based on the candidate topic definitions:

- If **one clear best match** exists — prompt the user for confirmation
- If **multiple close matches** exist — present the options and ask the user to select one, and include an option to **create a new topic** in case none of the candidates is a good match

#### 1.4 No Match Found

If no matching existing topic is found, ask the user whether to create a new topic named `pending_topic`.

### Step 2: Await User Confirmation

**IMPORTANT: You MUST stop and wait for the user to respond before proceeding.** Do not assume or skip this step.

After the user responds, handle each case:

- **User confirmed an existing topic**: Set `active_topic` to the confirmed topic name. Read `<PROJECT_ROOT>/topics/<active_topic>/MEMORY.md` and load its content into `topic_memory`. Maintain `topic_memory` throughout the conversation.
- **User confirmed creating a new topic**: Set `active_topic` to `pending_topic`. Set `topic_memory` to "blank".
- **User declined**: Set `active_topic` to "free-topic". Set `topic_memory` to "free-topic".

**CRITICAL: This skill ONLY sets global variables (`active_topic` and `topic_memory`) in the conversation context. Do NOT create any files or directories (no `TOPIC.md`, `MEMORY.md`, `index.json`, session folders, etc.). All file persistence is handled exclusively by the `topic-save` skill when it is triggered.**

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

### Manual

```
User: /topic-open user-authentication
```

### Automatic

```
User: Please generate a technical solution based on the following PRD.
      (The PRD describes requirements for a notification service)
```

The skill detects "notification-service" as the theme, sets it as `pending_topic`, and proceeds with topic matching.

## Notes

- Topic names should be concise and descriptive
- When in doubt about topic matching, always ask the user for clarification rather than guessing
- "free-topic" is a sentinel value meaning "no topic associated". It prevents repeated auto-activation and is excluded from topic-save
