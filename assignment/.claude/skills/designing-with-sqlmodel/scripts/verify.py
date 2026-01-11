#!/usr/bin/env python3
"""Verify SQLModel skill SKILL.md structure and syntax."""
import os
import re
import sys
from pathlib import Path

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def verify_skill():
    """Verify SQLModel skill meets standards."""
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        print("✗ SKILL.md not found")
        sys.exit(1)

    content = skill_md.read_text(encoding='utf-8')

    # Check frontmatter
    if not content.startswith("---"):
        print("✗ Missing YAML frontmatter delimiter")
        sys.exit(1)

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        print("✗ Malformed YAML frontmatter")
        sys.exit(1)

    frontmatter = match.group(1)

    # Check required fields
    if 'name: designing-with-sqlmodel' not in frontmatter:
        print("✗ Missing or incorrect skill name")
        sys.exit(1)

    if 'description:' not in frontmatter:
        print("✗ Missing description field")
        sys.exit(1)

    if 'Use when' not in frontmatter:
        print("✗ Description missing 'Use when' trigger")
        sys.exit(1)

    # Check structure sections
    required_sections = [
        '# SQLModel Schema Designer',
        '## When to Use This Skill',
        '## Quick Start',
        '## Core Concepts',
        '## Key Pattern',
        '## Database Models',
        '## Database Connection',
        '## Instructions',
        '## Common Patterns',
    ]

    body = content.split('---', 2)[-1]
    missing_sections = [s for s in required_sections if s not in body]

    if missing_sections:
        print(f"✗ Missing sections: {', '.join(missing_sections)}")
        sys.exit(1)

    # Check for code examples
    code_blocks = len(re.findall(r'```python', body))
    if code_blocks < 8:
        print(f"✗ Only {code_blocks} code examples. Need at least 8.")
        sys.exit(1)

    # Check for SQLModel patterns
    if 'class Task(SQLModel' not in body and 'class Task(TaskBase' not in body:
        print("✗ Missing SQLModel task example")
        sys.exit(1)

    # Check line count
    lines = content.count('\n')
    if lines < 100:
        print(f"✗ SKILL.md too short ({lines} lines). Should be 150+ lines.")
        sys.exit(1)

    if lines > 600:
        print(f"✗ SKILL.md too long ({lines} lines). Keep under 500 lines.")
        sys.exit(1)

    # Check for references
    references_dir = skill_dir / "references"
    if not references_dir.exists():
        print("✗ Missing references/ directory")
        sys.exit(1)

    reference_files = list(references_dir.glob("*.md"))
    if len(reference_files) == 0:
        print("✗ No reference files in references/ directory")
        sys.exit(1)

    print(f"✓ designing-with-sqlmodel skill valid ({lines} lines, {len(reference_files)} reference files)")
    sys.exit(0)

if __name__ == "__main__":
    verify_skill()
