#!/usr/bin/env python3
"""Verify Upwork proposal meets winning standards for job conversion."""
import re
import sys
import argparse
from pathlib import Path

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def check_proposal_quality(content):
    """Check if proposal has winning elements."""
    issues = []

    # Check length (should be 150-300 words, min 80, max 350)
    word_count = len(content.split())
    if word_count < 80:
        issues.append(f"✗ Too short ({word_count} words). Need at least 80 words to establish credibility.")
    elif word_count > 350:
        issues.append(f"✗ Too long ({word_count} words). Clients won't read on mobile. Aim for 150-300 words.")

    # Check for specific opening (not generic)
    opening_lines = '\n'.join(content.split('\n')[:3]).lower()
    generic_phrases = [
        'i am a talented',
        'i have experience',
        'i am an expert',
        'my name is',
        'thanks for the opportunity',
        'interested in this project',
    ]

    is_generic = any(phrase in opening_lines for phrase in generic_phrases)
    if is_generic:
        issues.append("✗ Opening is generic. Start with client's specific pain or project detail (e.g., 'I see your checkout is timing out...')")

    # Check for specific problem mention (shows you read the job)
    specific_keywords = [
        'you mentioned', 'i see your', 'i notice', 'your ', 'based on your',
        'your project', 'your ', 'specifically', 'particular', 'specific'
    ]
    has_specificity = any(keyword in opening_lines for keyword in specific_keywords)

    if not has_specificity:
        issues.append("✗ No specific mention of their project/problem. Reference 2 details from their job post.")

    # Check for deliverable bullets (3-4)
    bullet_pattern = r'(^[\s]*[-*]\s+[A-Za-z].{15,}|^[\s]*\d+\.\s+[A-Za-z].{15,})'
    bullets = []
    for line in content.split('\n'):
        if re.search(bullet_pattern, line):
            bullets.append(line)
        # Check for bullet point character (•) or other Unicode bullets
        elif '\u2022' in line or '\u2023' in line or '\u25cf' in line:
            if len(line) > 20:  # Must have substantive content
                bullets.append(line)

    if len(bullets) < 3:
        issues.append(f"✗ Only {len(bullets)} bullets found. Need 3-4 clear deliverables (e.g., 'Optimize database queries', 'Set up caching layer').")

    # Check for milestone (testable outcome)
    milestone_keywords = ['milestone', 'first week', 'within', 'days', 'by', 'complete']
    has_milestone = any(keyword in content.lower() for keyword in milestone_keywords)

    if not has_milestone:
        issues.append("✗ No testable first milestone. Add: 'First milestone: [specific deliverable] within X days.'")

    # Check for proof point (number + credibility)
    # Pattern: percentage, count, or quantified result
    proof_patterns = [
        r'\d+%',  # Percentage
        r'\d+\+?\s+(?:clients|companies|projects|users|hours)',  # Count
        r'(?:reduced|improved|increased|optimized|fixed).*?\d+',  # Result with number
        r'(?:https?://\S+|portfolio|case study|link)',  # Proof link
    ]

    has_proof = any(re.search(pattern, content, re.IGNORECASE) for pattern in proof_patterns)

    if not has_proof:
        issues.append("✗ No proof point (number + result or link). Add: 'Reduced load time by 45%' or link to relevant work.")

    # Check for timeline (concrete, not vague)
    timeline_keywords = ['week', 'days', 'hours', 'start', 'available']
    has_timeline = any(keyword in content.lower() for keyword in timeline_keywords)

    if not has_timeline:
        issues.append("✗ No concrete timeline. Add: 'Timeline: 2 weeks' or 'Available to start by [date]'")

    # Check for rate/pricing mention (optional but good)
    rate_pattern = r'(\$\d+|hourly|fixed|rate|pricing)'
    has_rate = bool(re.search(rate_pattern, content, re.IGNORECASE))

    if not has_rate:
        # Not critical but good practice
        issues.append("⚠ No rate/pricing mentioned. Consider adding: 'Rate: $X/hr' or 'Fixed: $Y'")

    # Check for mobile-friendliness (no huge paragraphs)
    lines = content.split('\n')
    huge_paragraphs = [line for line in lines if len(line) > 120 and not line.strip().startswith(('•', '-', '*', '1.', '2.', '3.', '4.'))]

    if len(huge_paragraphs) > 2:
        issues.append(f"✗ {len(huge_paragraphs)} long paragraphs (>120 chars). Break into shorter lines for mobile readability.")

    # Check for engagement (question or next step)
    engagement_keywords = ['question', 'discuss', 'chat', 'call', 'talk', 'next', 'schedule', 'available', 'ready']
    has_engagement = any(keyword in content.lower() for keyword in engagement_keywords)

    if not has_engagement:
        issues.append("⚠ No engagement question or next step. Close with: 'Happy to discuss' or 'Let's schedule a call'")

    return issues, word_count, len(bullets)

def main():
    parser = argparse.ArgumentParser(description='Verify Upwork proposal quality')
    parser.add_argument('--proposal', type=str, help='Path to proposal file or proposal text')
    parser.add_argument('--verbose', action='store_true', help='Show detailed analysis')
    args = parser.parse_args()

    if not args.proposal:
        print("✗ No proposal provided. Use --proposal 'path/to/proposal.txt' or --proposal 'inline text'")
        sys.exit(1)

    # Try to read as file, fall back to direct text
    try:
        proposal_path = Path(args.proposal)
        if proposal_path.exists():
            content = proposal_path.read_text(encoding='utf-8')
        else:
            content = args.proposal
    except Exception:
        content = args.proposal

    if not content.strip():
        print("✗ Proposal is empty")
        sys.exit(1)

    issues, word_count, bullet_count = check_proposal_quality(content)

    if args.verbose:
        print(f"\nProposal Analysis (verbose):")
        print(f"  Word count: {word_count}")
        print(f"  Deliverable bullets: {bullet_count}")

    if issues:
        print("\nProposal Quality Issues:")
        for issue in issues:
            print(f"  {issue}")
        print(f"\n✗ Proposal needs improvement before submitting ({word_count} words, {bullet_count} bullets)")
        sys.exit(1)
    else:
        print(f"✓ Upwork proposal meets winning standards ({word_count} words, {bullet_count} bullets)")
        if args.verbose:
            print(f"  ✓ Has specific problem mention")
            print(f"  ✓ Has deliverable bullets")
            print(f"  ✓ Has first milestone")
            print(f"  ✓ Has proof point")
            print(f"  ✓ Mobile-friendly format")
        sys.exit(0)

if __name__ == "__main__":
    main()
