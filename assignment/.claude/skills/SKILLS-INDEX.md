# Assignment Skills Library

> 2 business/content writing skills for non-technical tasks.

## Skills Overview

| Skill | Trigger | Key Value |
|-------|---------|-----------|
| `writing-linkedin-posts` | "Create LinkedIn post", "write thought leadership" | TOFU/MOFU/BOFU framework, engagement optimization |
| `writing-upwork-proposals` | "Write Upwork proposal", "bid on freelance job" | Client-focused format, proof points, high-conversion structure |

## Skill Specifications

### 1. writing-linkedin-posts
**Purpose**: Craft high-engagement LinkedIn content across the buyer's journey.

**Triggers**:
- "Create a LinkedIn post about..."
- "Write thought leadership content"
- "I need a TOFU post for awareness"
- "Optimize my LinkedIn engagement"

**Key Deliverable**: A structured post with hook, substance, and proof that drives comments and professional engagement.

**NOT when**: Creating visual carousel posts (separate skill needed).

**Verification**: `python scripts/verify.py --post "your_post.txt"`
- ✓ 80-500 word count
- ✓ Clear hook (pain or question)
- ✓ 3+ substantive bullets/points
- ✓ 1 proof point (number or stat)
- ✓ Clear CTA
- ✓ Proper funnel stage indicators

---

### 2. writing-upwork-proposals
**Purpose**: Write concise, personalized proposals that win freelance jobs.

**Triggers**:
- "Help me write an Upwork proposal"
- "I need to bid on this Upwork job"
- "Write a freelance proposal for..."
- "Stand out from copy-paste proposals"

**Key Deliverable**: A 80-250 word proposal with specific problem statement, deliverable bullets, proof, and milestone.

**NOT when**: Writing formal contracts, SOWs, or internal docs.

**Verification**: `python scripts/verify.py --proposal "your_proposal.txt"`
- ✓ 80-350 word count
- ✓ Specific problem mention (from job post)
- ✓ 3-4 deliverable bullets
- ✓ 1 testable first milestone
- ✓ 1 proof point (number + link)
- ✓ Concrete timeline and rate
- ✓ Mobile-friendly format

---

## File Structure

```
assignment/
├── .claude/
│   └── skills/
│       ├── SKILLS-INDEX.md (this file)
│       ├── writing-linkedin-posts/
│       │   ├── SKILL.md (153 lines)
│       │   └── scripts/
│       │       └── verify.py
│       └── writing-upwork-proposals/
│           ├── SKILL.md (183 lines)
│           └── scripts/
│               └── verify.py
```

## Running Verification

### Test LinkedIn Skill
```bash
cd assignment/.claude/skills/writing-linkedin-posts
python scripts/verify.py --post "your_post.txt"
```

### Test Upwork Skill
```bash
cd assignment/.claude/skills/writing-upwork-proposals
python scripts/verify.py --proposal "your_proposal.txt"
```

## Design Notes

Both skills follow the **Agent Skills Specification** (agentskills-standard):
- Progressive disclosure (metadata → instructions → resources)
- Token discipline (SKILL.md <500 lines)
- Concrete success criteria (verify.py returns 0/1)
- Real-world patterns (not theory, battle-tested)

The skills are designed to be **immediately useful** without requiring external context—all patterns and formulas are included in SKILL.md.

## What's Next

These 2 skills are foundational. Ready to create 2 more technical skills when needed.

---

*Last updated: 2026-01-11*
