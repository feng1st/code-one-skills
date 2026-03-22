"""Load topic definitions (TOPIC.md) for candidate topics.

Usage:
    load_topic_definition.py --project-root <path> "<topic_name1>" "<topic_name2>" ...

For each topic name provided, reads <project_root>/topics/<topic_name>/TOPIC.md
and outputs the aggregated content in a structured format.

Options:
    --project-root <path>   Project root directory (required for IDE/GUI environments,
                            falls back to cwd-based detection if omitted)

Exit codes:
    0 — success (even if some/all topics are missing)
    1 — unexpected fatal error
"""

import os
import sys


def parse_args(argv):
    """Parse --project-root and topic names from argv.

    Returns (project_root_override, topic_names).
    project_root_override is None if --project-root was not provided.
    """
    project_root_override = None
    topic_names = []
    iterator = iter(argv)

    for arg in iterator:
        if arg == "--project-root":
            project_root_override = next(iterator, None)
        elif arg.startswith("--project-root="):
            project_root_override = arg.split("=", 1)[1]
        else:
            topic_names.append(arg)

    return project_root_override, topic_names


def resolve_project_root(override=None):
    """Determine the project root directory.

    Resolution order:
    1. --project-root argument (passed via override parameter)
    2. PROJECT_ROOT environment variable
    3. Walk up from cwd to find a directory containing 'topics/'
    4. Fall back to cwd as last resort

    Note: The script may be deployed outside the project (e.g., ~/.skills/),
    so we do NOT search relative to the script's own location.
    """
    if override and os.path.isdir(override):
        return os.path.abspath(override)

    env_root = os.environ.get("PROJECT_ROOT", "").strip()
    if env_root and os.path.isdir(env_root):
        return env_root

    cwd = os.getcwd()
    current = cwd
    for _ in range(10):
        if os.path.isdir(os.path.join(current, "topics")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    return cwd


def load_single_topic(project_root, topic_name):
    """Load TOPIC.md for a single topic. Returns content string or None."""
    topic_name = topic_name.strip()
    if not topic_name:
        return None

    topic_file = os.path.join(project_root, "topics", topic_name, "TOPIC.md")

    if not os.path.isfile(topic_file):
        return None

    try:
        with open(topic_file, "r", encoding="utf-8") as file:
            content = file.read().strip()
            return content if content else None
    except (OSError, IOError, UnicodeDecodeError):
        return None


def main():
    project_root_override, topic_names = parse_args(sys.argv[1:])

    if not topic_names:
        print("")
        sys.exit(0)

    project_root = resolve_project_root(project_root_override)
    results = []

    for topic_name in topic_names:
        content = load_single_topic(project_root, topic_name)
        if content is None:
            continue
        results.append(f"## Topic: {topic_name}\n\n{content}")

    if not results:
        print("")
        sys.exit(0)

    print("\n\n---\n\n".join(results))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
