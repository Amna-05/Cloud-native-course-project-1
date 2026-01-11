#!/usr/bin/env python3
"""Verify LinkedIn post meets quality standards for engagement."""
import re
import sys
import argparse
from pathlib import Path

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def check_structure(content):
    """Check if post has required structural elements."""
    issues = []

    # Check length (should be 200-500 words for optimal engagement)
    word_count = len(content.split())
    if word_count < 80:
        issues.append(f"✗ Too short ({word_count} words). Aim for 150-400 words.")
    elif word_count > 600:
        issues.append(f"✗ Too long ({word_count} words). Mobile users will scroll past. Aim for 150-400 words.")

    lines = content.strip().split('\n')

    # Check for hook in first 2 lines
    hook_section = '\n'.join(lines[:3]).lower()
    has_hook = any([
        '?' in hook_section,  # Question
        any(word in hook_section for word in ['problem', 'struggling', 'challenge', 'broken', 'mistake', 'loss', 'wrong']),  # Pain
        any(word in hook_section for word in ['surprising', 'secret', 'why', 'here\'s', 'discovered', 'learned']),  # Insight
    ])

    if not has_hook:
        issues.append("✗ No clear hook in first 2-3 lines. Start with a pain point or question.")

    # Check for substance (bullets or structured points)
    # Match: "- text" or "• text" or "* text" or "1. text" or lines starting with caps followed by colon
    bullet_pattern = r'(^[\s]*[-*]\s+.{15,}|^[\s]*\d+\.\s+.{15,}|^[A-Z][a-z]+.*?[:→\-])'
    # Also search for bullet character (•) using explicit Unicode
    substance_lines = []
    for line in lines:
        # Check for standard bullets or numbered lists
        if re.search(bullet_pattern, line, re.MULTILINE):
            substance_lines.append(line)
        # Check for bullet point character (•) or other Unicode bullets
        elif '\u2022' in line or '\u2023' in line or '\u25cf' in line:
            substance_lines.append(line)

    if len(substance_lines) < 2:
        issues.append(f"✗ Missing substantive points. Found {len(substance_lines)}, need at least 3 bullets or structured points.")

    # Check for specific number or proof point
    number_pattern = r'(\d+%|\d+[-/]\d+|[\$£€]\d+|~?\d+\+?(?:\s+(?:users|companies|people|clients|hours|weeks|days|months)))'
    has_proof = bool(re.search(number_pattern, content, re.IGNORECASE))

    if not has_proof:
        issues.append("✗ No specific proof point (number, statistic, result). Add '40% reduction', '500 companies', etc.")

    # Check for CTA
    cta_pattern = r'(reply|comment|share|dm|message|discuss|let me know|what|tell me|your thoughts|ask|reach out|book|contact|link)'
    has_cta = bool(re.search(cta_pattern, content, re.IGNORECASE))

    if not has_cta:
        issues.append("✗ No clear CTA. Ask for comments ('What's your experience?'), shares, or replies.")

    # Check for stage alignment (TOFU/MOFU/BOFU indicators)
    funnel_keywords = {
        'TOFU': ['trend', 'question', 'framework', 'insight', 'why', 'problem'],
        'MOFU': ['how', 'guide', 'process', 'step', 'analyze', 'framework', 'methodology'],
        'BOFU': ['result', 'save', 'reduce', 'improve', 'roi', 'deliver', 'client', 'proven']
    }

    matches = {stage: sum(1 for keyword in keywords if keyword in content.lower())
               for stage, keywords in funnel_keywords.items()}

    if max(matches.values()) == 0:
        issues.append("⚠ Post doesn't clearly indicate TOFU/MOFU/BOFU stage. Add clearer funnel positioning.")

    return issues, word_count, matches

def main():
    parser = argparse.ArgumentParser(description='Verify LinkedIn post quality')
    parser.add_argument('--post', type=str, help='Path to post file or post text')
    parser.add_argument('--verbose', action='store_true', help='Show detailed analysis')
    args = parser.parse_args()

    if not args.post:
        print("✗ No post provided. Use --post 'path/to/post.txt' or --post 'inline text'")
        sys.exit(1)

    # Try to read as file, fall back to direct text
    try:
        post_path = Path(args.post)
        if post_path.exists():
            content = post_path.read_text(encoding='utf-8')
        else:
            content = args.post
    except Exception:
        content = args.post

    if not content.strip():
        print("✗ Post is empty")
        sys.exit(1)

    issues, word_count, stage_analysis = check_structure(content)

    if args.verbose:
        print(f"\nPost Analysis (verbose):")
        print(f"  Word count: {word_count}")
        print(f"  Funnel stage indicators: {stage_analysis}")

    if issues:
        print("\nPost Quality Issues:")
        for issue in issues:
            print(f"  {issue}")
        print("\n✗ Post needs improvement before publishing")
        sys.exit(1)
    else:
        print(f"✓ LinkedIn post meets quality standards ({word_count} words)")
        if args.verbose:
            print(f"  Stage indicators: {stage_analysis}")
        sys.exit(0)

if __name__ == "__main__":
    main()
