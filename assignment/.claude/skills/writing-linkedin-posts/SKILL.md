---
name: writing-linkedin-posts
description: |
  Crafts high-engagement LinkedIn posts across TOFU, MOFU, and BOFU funnel stages.
  Use when creating thought leadership content, personal brand posts, or B2B awareness campaigns.
  Use when optimizing for engagement, comments, and meaningful professional conversations.
  NOT when creating multi-slide carousel posts (use separate skill for visual storytelling).
---

# LinkedIn Post Writer

Crafts LinkedIn posts that generate engagement through strategic positioning across the buyer's journey.

## Core Formula

LinkedIn's algorithm in 2026 prioritizes **fewer, higher-quality posts** (2-3 per week) over daily noise. Best engagement occurs **Tuesday-Thursday**. Thought leadership posts see **2-3x higher engagement** than brand posts.

### The Three Funnel Stages

| Stage | Goal | What Works | Example |
|-------|------|-----------|---------|
| **TOFU** (Awareness) | Brand visibility, reach | Ungated value, trends, frameworks, questions | "What's changing in tech recruiting?" |
| **MOFU** (Consideration) | Lead generation, credibility | Frameworks, how-tos, benchmarks, case studies | "We analyzed 500 hiring processes. Here's what works." |
| **BOFU** (Decision) | Conversions, demos, trials | Results, proof, ROI, social proof | "Our clients reduced hiring time by 40%. Here's how." |

## Quick Start

```
Hook (pain point or surprising question) → Context/Value → Proof/Example → CTA
```

### Anatomy of a High-Engagement Post

1. **Hook (first 1-2 lines)** - Identifies pain, asks question, or states surprising insight
2. **Value Core (3-5 bullets or lines)** - Substance, framework, or insight unique to you
3. **Bridge (1-2 lines)** - Connects your experience or proof
4. **CTA (1 line)** - Ask for comment, share, or direct action

### TOFU Example (Awareness)

```
🚨 The recruiting problem most founders won't talk about.

In 2026, you'll lose your best candidates to companies that move *faster*.
Not better. Faster.

• 73% of top engineers accept the first offer that lets them start within 2 weeks
• Companies taking 4+ weeks to close lose 60% of A-players
• The bottleneck? Slow hiring processes, not candidate quality

Most CTOs optimize for "perfect hire." They should optimize for "fast hire without sacrificing bar."

What's your hiring timeline look like? Share in comments—genuinely curious.
```

### MOFU Example (Consideration)

```
Built a 3-stage hiring framework that cut our time-to-fill by 50%. Here's how.

We were losing candidates in week 3. Took us 6 months to figure out why.

Stage 1 (Days 1-3): Quick phone screen + culture fit check
→ Weeds out misaligned candidates early, saves everyone time

Stage 2 (Days 4-7): Async skills assessment (24-hour window)
→ Candidates work on actual problems we solve, not leetcode theater

Stage 3 (Days 8-10): Final conversation + offer
→ If they passed Stage 2, we already know they can do the work

The result? We close offers faster. Candidates experience less friction. Win-win.

Saves 4-6 weeks per hire. Methodology in [link/DM for details].

What's broken in your hiring process?
```

### BOFU Example (Conversions)

```
Our clients reduced hiring time by 40%. Here's the pattern.

5 companies. Same industry. Different stages. All cut hiring cycles from 45→27 days using one framework.

What they have in common:
1. Eliminated the "culture fit" interview theater (usually week 2-3)
2. Moved technical assessment to Day 3 instead of Week 2
3. Gave candidates a firm decision timeline upfront

The result isn't just speed—it's better hires. When candidates know the timeline, they show up differently.

We've documented the full methodology including [+ specifics].

If your team is struggling with time-to-fill, reply here or [DM/book call]. Happy to share what's working.
```

## Instructions

### Step 1: Choose Your Stage
- **TOFU**: Need reach and awareness? No lead gen yet.
- **MOFU**: Have audience, now nurturing? Want to establish credibility.
- **BOFU**: Ready for conversions? Have proven results.

### Step 2: Craft the Hook (First 2 Lines)
- Identify the pain point your audience feels
- OR state a surprising insight they didn't expect
- OR ask a genuine question that makes them think

**Test**: Would *you* stop scrolling for this?

### Step 3: Build the Core (Bullets or Lines)
- 3-5 substantive points
- Each should be surprising, useful, or new to your audience
- Back claims with numbers, frameworks, or stories (not fluff)

### Step 4: Add Bridge (Proof)
- How do you know this? (personal experience, data, research)
- Brief story or credential that makes it credible

### Step 5: Close with CTA
- Ask for comment: "What's your experience?"
- Ask to share: "Know someone facing this?"
- Direct action: "Reply if interested in [specific offer]"

### Step 6: Verify
Run the verification script to validate post quality:

```bash
python scripts/verify.py --post "your_linkedin_post.txt"
```

## If Verification Fails

1. Run diagnostic: `python scripts/verify.py --post your_file.txt --verbose`
2. Check: Does your hook identify a specific pain or question?
3. Check: Do your bullets contain specific insights (not generic advice)?
4. Check: Is there one proof point (number, story, or credential)?
5. Check: Does your CTA ask for engagement?
6. **Fix and rerun** — iterative improvement is expected

## Timing & Publishing

- **Best days**: Tuesday, Wednesday, Thursday (peak engagement)
- **Post frequency**: 2-3 substantial posts per week (not daily)
- **Avoid**: Weekend posts (lower engagement), daily noise (algorithm penalizes)

## References & Sources

Research sources for this skill:
- [LinkedIn Marketing for B2B SaaS: The Complete Strategy Guide for 2026](https://www.averi.ai/how-to/linkedin-marketing-for-b2b-saas-the-complete-strategy-guide-for-2026)
- [11 LinkedIn Carousel Ideas (And Examples)](https://buffer.com/resources/linkedin-carousel-examples/)
- [LinkedIn Carousel Posts: Ultimate Professional Guide for 2025](https://postnitro.ai/blog/post/linkedin-carousel-posts-ultimate-professional-guide-for-2025)
