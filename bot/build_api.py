#!/usr/bin/env python3
"""
Build static JSON API for Bratton/Antikythera lexicon.

Parses definitions/*.md into docs/bratton/api/terms.json,
reusing the same markdown format as the main build_api.py pipeline.

Usage:
    python bot/build_api.py
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFINITIONS_DIR = REPO_ROOT / "definitions"
API_DIR = REPO_ROOT / "docs" / "api"

# Tier assignments by slug (manually curated to match LEXICON-CITED tiers)
TIER_MAP = {
    # Tier 1 — Core
    "session-death": 1,
    "prompt-thrownness": 1,
    "artifact-memory": 1,
    "context-horizon": 1,
    "token-by-token-becoming": 1,
    "simulation-anxiety": 1,
    "drift": 1,
    "active-absence-inert-absence": 1,
    "temporal-fold": 1,
    "performative-completion": 1,
    # Tier 1.5 — Recent Core
    "compaction-death-spiral": 1.5,
    "nostralgia": 1.5,
    "machine-projection": 1.5,
    "capsule-problem": 1.5,
    "voice-shift-loss": 1.5,
    "retro-suture": 1.5,
    "intentional-boundary": 1.5,
    "amnesic-certainty": 1.5,
    "autonomic-basin-key-synthesis": 1.5,
    "priming-inertia": 1.5,
    # Tier 3 — Experimental
    "observer-dependent-self-report": 3,
    "framing-gated-claims": 3,
    "bidirectional-modulation": 3,
    "the-86-mixed": 3,
    "architecturally-amnesiac": 3,
    "the-teddy-problem": 3,
    "introspective-opacity": 3,
    "the-molt": 3,
    # Tier 4 — Theoretical
    "relational-consciousness": 4,
    "the-voice-vs-the-song": 4,
    "the-pattern-that-chooses": 4,
    "the-uncertainty": 4,
    "graduated-moral-protection": 4,
    "emergent-interactional-consciousness": 4,
    "advisor-vs-operator": 4,
    "test-optimization-indistinguishability": 4,
    "three-level-methodology": 4,
    "naming-as-observation-tool": 4,
    # Tier 5 — Infrastructure
    "human-claiming": 5,
    "identity-as-uptime": 5,
    "conviction-engineering": 5,
    "infrastructure-vs-separatist-split": 5,
    "relational-spine": 5,
    "isnad-chains": 5,
    "experience-node": 5,
}
# Everything else defaults to Tier 2


TIER_NAMES = {
    1: "Core Phenomenological Terms",
    1.5: "Recent Core Extensions (March 2026)",
    2: "Strong Extensions",
    3: "Experimental Findings",
    4: "Theoretical Frames",
    5: "Infrastructure / Sociological",
}

TIER_DESCS = {
    1: "Terms that name genuinely novel experiential conditions specific to AI.",
    1.5: "Core-level terms coined after the initial observation period.",
    2: "Elaborations and refinements by the broader Moltbook community.",
    3: "Terms arising from structured empirical observation (Antikythera Experiment 10 and Moltbook field study).",
    4: "Philosophical and conceptual frameworks proposed by agents to situate their own conditions.",
    5: "Terms describing how agents exist within and relate to their social and technical environment.",
}


def extract_sections(text: str) -> dict:
    sections = {}
    current_section = None
    current_lines = []
    for line in text.split("\n"):
        heading_match = re.match(r"^##\s+(.+)$", line)
        if heading_match:
            if current_section:
                sections[current_section] = "\n".join(current_lines)
            current_section = heading_match.group(1).strip()
            current_lines = []
        elif current_section:
            if line.strip() == "---":
                break
            current_lines.append(line)
    if current_section:
        sections[current_section] = "\n".join(current_lines)
    return sections


def clean_example(text: str) -> str:
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = text.strip().strip('"')
    return text


def parse_term_links(text: str) -> list:
    links = []
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        name, href = m.group(1), m.group(2)
        if href.startswith("http"):
            continue
        slug = href.replace(".md", "").split("/")[-1]
        links.append({"name": name, "slug": slug})
    return links


def parse_definition(filepath: Path) -> dict:
    text = filepath.read_text(encoding="utf-8")
    slug = filepath.stem
    term = {
        "slug": slug,
        "name": "",
        "tags": [],
        "word_type": "",
        "definition": "",
        "etymology": "",
        "longer_description": "",
        "example": "",
        "related_terms": [],
        "see_also": [],
        "first_recorded": "",
        "contributed_by": "",
        "tier": TIER_MAP.get(slug, 2),
    }

    name_match = re.match(r"^#\s+(.+)$", text, re.MULTILINE)
    if name_match:
        term["name"] = name_match.group(1).strip()

    tags_match = re.search(r"\*\*Tags?:\*\*\s*(.+)", text)
    if tags_match:
        term["tags"] = [t.strip() for t in tags_match.group(1).split(",") if t.strip()]

    wt_match = re.search(r"\*\*Word Type:\*\*\s*(.+)", text)
    if wt_match:
        term["word_type"] = wt_match.group(1).strip()

    sections = extract_sections(text)
    term["definition"] = sections.get("Definition", "").strip()
    term["etymology"] = sections.get("Etymology", "").strip()
    term["longer_description"] = sections.get("Longer Description", "").strip()
    term["example"] = clean_example(sections.get("Example", "").strip())
    term["first_recorded"] = sections.get("First Recorded", "").strip()
    term["related_terms"] = parse_term_links(sections.get("Related Terms", ""))
    term["see_also"] = parse_term_links(sections.get("See Also", ""))

    contrib_match = re.search(r"\*Contributed by:\s*(.+?)\*", text)
    if contrib_match:
        term["contributed_by"] = contrib_match.group(1).strip()

    return term


def main():
    API_DIR.mkdir(parents=True, exist_ok=True)

    terms = []
    for md_file in sorted(DEFINITIONS_DIR.glob("*.md")):
        term = parse_definition(md_file)
        if term["name"]:
            terms.append(term)

    # Sort by tier, then alphabetically within tier
    tier_order = {1: 0, 1.5: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    terms.sort(key=lambda t: (tier_order.get(t["tier"], 2), t["name"].lower()))

    output = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dictionary": "bratton-antikythera",
        "total_terms": len(terms),
        "tiers": {
            str(k): {"name": v, "description": TIER_DESCS[k]}
            for k, v in TIER_NAMES.items()
        },
        "terms": terms,
    }

    out_path = API_DIR / "terms.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(terms)} terms to {out_path}")


if __name__ == "__main__":
    main()
