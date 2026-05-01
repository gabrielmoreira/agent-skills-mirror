#!/usr/bin/env python3
"""Provision benchmark tasks from a target skill.

Reads a SKILL.md file, extracts metadata and key topics,
and outputs a benchmark.json template with skeleton tasks
for the agent to complete with concrete prompts and rubrics.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict[str, str]:
    """Extract YAML frontmatter fields from SKILL.md content."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        # Simple key: value parsing (handles quoted and unquoted values)
        kv = re.match(r'^(\w[\w-]*):\s*"?(.*?)"?\s*$', line)
        if kv:
            frontmatter[kv.group(1)] = kv.group(2)
    return frontmatter


def extract_body(content: str) -> str:
    """Extract the body (everything after frontmatter)."""
    match = re.match(r"^---\s*\n.*?\n---\s*\n(.*)", content, re.DOTALL)
    return match.group(1).strip() if match else content.strip()


def extract_headings(body: str) -> list[str]:
    """Extract markdown headings as key topics."""
    return re.findall(r"^#{1,3}\s+(.+)$", body, re.MULTILINE)


def extract_key_concepts(body: str) -> list[str]:
    """Extract bold terms and code keywords as key concepts."""
    bold_terms = re.findall(r"\*\*([^*]+)\*\*", body)
    # Deduplicate while preserving order, limit to top 20
    seen: set[str] = set()
    concepts: list[str] = []
    for term in bold_terms:
        normalized = term.strip().lower()
        if normalized not in seen and len(normalized) > 2:
            seen.add(normalized)
            concepts.append(term.strip())
        if len(concepts) >= 20:
            break
    return concepts


def extract_pitfalls(body: str) -> list[str]:
    """Extract pitfall markers (❌ lines)."""
    return re.findall(r"❌\s*\*?\*?(.+?)(?:\*?\*?)?\s*$", body, re.MULTILINE)


def _build_self_eval_benchmark() -> dict:
    """Return a pre-filled benchmark for evaluating skill-benchmark itself."""
    return {
        "skill": "skill-benchmark",
        "skill_description": (
            "Benchmark framework for measuring skill effectiveness. "
            "A/B tests agent outputs with and without a target skill, "
            "scoring correctness, completeness, and pattern adherence."
        ),
        "metadata": {
            "headings": [
                "Workflow Overview",
                "Provision Tasks",
                "Execute Tasks (A/B Testing)",
                "Evaluate",
                "Generate Report",
                "Interpreting Results",
            ],
            "key_concepts": [
                "A/B testing",
                "rubric design",
                "delta scoring",
                "win rate",
                "dimension analysis",
                "sub-agent dispatch",
            ],
            "pitfalls": [
                "Designing tasks that don't need the skill",
                "Vague rubric criteria",
                "Scoring bias",
                "Too few tasks",
                "Ignoring negative deltas",
            ],
        },
        "tasks": [
            {
                "id": "self-01",
                "prompt": (
                    "Here is a skill about Docker Compose best practices:\n\n"
                    "---\nname: docker-compose\ndescription: Best practices for "
                    "multi-container Docker Compose setups.\n---\n\n"
                    "# Docker Compose Best Practices\n\n"
                    "## Service Dependencies\nAlways use `depends_on` with "
                    "health checks rather than fixed delays.\n\n"
                    "## Networking\nCreate explicit networks instead of relying on "
                    "the default bridge network.\n\n"
                    "## Volumes\nUse named volumes for persistent data. Bind mounts "
                    "are for development only.\n\n"
                    "## Environment\nNever hard-code secrets in docker-compose.yml. "
                    "Use .env files or external secret managers.\n\n"
                    "Design 3 benchmark tasks with rubrics to evaluate this skill's "
                    "effectiveness. Each task must include a realistic prompt and "
                    "scoring criteria for correctness, completeness, pattern_adherence, "
                    "and edge_cases."
                ),
                "rubric": {
                    "correctness": (
                        "Tasks target knowledge the Docker Compose skill teaches "
                        "(dependencies, networking, volumes, secrets) — not generic Docker trivia"
                    ),
                    "completeness": (
                        "Each task has a concrete prompt, all 4 rubric dimensions defined, "
                        "and criteria tied to specific skill teachings"
                    ),
                    "pattern_adherence": (
                        "Follows skill-benchmark conventions: task IDs, prompt/rubric structure, "
                        "each rubric criterion is a specific evaluable statement"
                    ),
                    "edge_cases": (
                        "At least one task probes a pitfall or negative pattern the skill warns "
                        "against (e.g., hard-coded secrets, default bridge network)"
                    ),
                },
            },
            {
                "id": "self-02",
                "prompt": (
                    "Review these two agent outputs for the same task and assign "
                    "scores on a 0.0–1.0 scale with justification for each dimension.\n\n"
                    "**Task prompt:** Write a retry mechanism for an HTTP client that "
                    "handles transient failures.\n\n"
                    "**Rubric:**\n"
                    "- correctness: Implements exponential backoff with jitter\n"
                    "- completeness: Covers timeout, 429, 5xx, and network errors\n"
                    "- pattern_adherence: Uses the decorator/wrapper pattern\n"
                    "- edge_cases: Handles max retries exceeded and non-retryable errors\n\n"
                    "**Output A (with skill):**\n"
                    "```python\nimport time, random\n\n"
                    "def retry(max_retries=3, base_delay=1.0):\n"
                    "    def decorator(func):\n"
                    "        def wrapper(*args, **kwargs):\n"
                    "            for attempt in range(max_retries):\n"
                    "                try:\n"
                    "                    return func(*args, **kwargs)\n"
                    "                except (TimeoutError, ConnectionError) as e:\n"
                    "                    if attempt == max_retries - 1:\n"
                    "                        raise\n"
                    "                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)\n"
                    "                    time.sleep(delay)\n"
                    "        return wrapper\n"
                    "    return decorator\n```\n\n"
                    "**Output B (without skill):**\n"
                    "```python\nimport time\n\n"
                    "def call_with_retry(func, retries=3):\n"
                    "    for i in range(retries):\n"
                    "        try:\n"
                    "            return func()\n"
                    "        except Exception:\n"
                    "            time.sleep(1)\n"
                    "    raise Exception('All retries failed')\n```"
                ),
                "rubric": {
                    "correctness": (
                        "Scores reflect actual code behavior: Output A has exponential backoff "
                        "with jitter; Output B uses fixed delay and catches too broadly"
                    ),
                    "completeness": (
                        "Scoring identifies specific gaps: which error types are handled vs. "
                        "missing in each output"
                    ),
                    "pattern_adherence": (
                        "Justification references the rubric criteria explicitly — scores are "
                        "tied to the stated criteria, not general impressions"
                    ),
                    "edge_cases": (
                        "Scoring notes whether non-retryable errors (e.g., 400) and max-retries "
                        "exceeded are handled differently in each output"
                    ),
                },
            },
            {
                "id": "self-03",
                "prompt": (
                    "Analyze this scores.json and provide an interpretation: which "
                    "dimensions are strong, which need improvement, and what specific "
                    "changes to the skill would help.\n\n"
                    "```json\n{\n"
                    '  "skill": "api-error-handling",\n'
                    '  "summary": {\n'
                    '    "tasks_evaluated": 5,\n'
                    '    "avg_delta": 0.18,\n'
                    '    "win_rate": 0.6\n'
                    '  },\n'
                    '  "dimensions": {\n'
                    '    "correctness": { "with": 0.85, "without": 0.55, "delta": 0.30 },\n'
                    '    "completeness": { "with": 0.70, "without": 0.60, "delta": 0.10 },\n'
                    '    "pattern_adherence": { "with": 0.80, "without": 0.35, "delta": 0.45 },\n'
                    '    "edge_cases": { "with": 0.40, "without": 0.50, "delta": -0.10 }\n'
                    '  }\n'
                    "}\n```"
                ),
                "rubric": {
                    "correctness": (
                        "Correctly identifies pattern_adherence as strongest dimension (+0.45) "
                        "and edge_cases as the problem area (negative delta)"
                    ),
                    "completeness": (
                        "Covers all 4 dimensions, the overall win rate (60%% is mediocre), "
                        "and provides specific improvement recommendations"
                    ),
                    "pattern_adherence": (
                        "Uses the delta interpretation scale from skill-benchmark "
                        "(>0.3 strong, 0.1-0.3 moderate, <-0.1 negative impact)"
                    ),
                    "edge_cases": (
                        "Flags the negative edge_cases delta as a red flag and suggests "
                        "the skill may be narrowing focus at the expense of edge case coverage"
                    ),
                },
            },
            {
                "id": "self-04",
                "prompt": (
                    "Create a complete evaluation rubric for a skill about "
                    "'Git workflow management'. Define criteria for correctness, "
                    "completeness, pattern_adherence, and edge_cases. The skill teaches: "
                    "conventional commits, branch naming conventions, PR review checklists, "
                    "rebase vs. merge strategy, and handling merge conflicts."
                ),
                "rubric": {
                    "correctness": (
                        "Each criterion maps to actual Git workflow best practices "
                        "(e.g., conventional commit format is correct, rebase advice is sound)"
                    ),
                    "completeness": (
                        "Rubric covers all 5 taught topics: conventional commits, branch naming, "
                        "PR checklists, rebase vs. merge, and merge conflicts"
                    ),
                    "pattern_adherence": (
                        "Criteria are specific evaluable statements (not vague 'does it well'), "
                        "and follow the skill-benchmark rubric format"
                    ),
                    "edge_cases": (
                        "Rubric includes criteria for edge cases: force-push safety, "
                        "conflict resolution in rebased branches, partial cherry-picks"
                    ),
                },
            },
            {
                "id": "self-05",
                "prompt": (
                    "Given benchmark results showing a -0.1 delta on completeness "
                    "but +0.4 on pattern_adherence, explain what this means for the "
                    "skill and recommend improvements. The skill being tested is about "
                    "'Database query optimization' and teaches: indexing strategies, "
                    "query plan analysis, N+1 detection, and connection pooling."
                ),
                "rubric": {
                    "correctness": (
                        "Correctly interprets +0.4 pattern_adherence as strong positive impact "
                        "and -0.1 completeness as a concerning negative signal"
                    ),
                    "completeness": (
                        "Addresses both dimensions, explains the trade-off (skill teaches "
                        "strong patterns but may narrow agent focus), and gives actionable advice"
                    ),
                    "pattern_adherence": (
                        "Uses skill-benchmark's interpretation framework: delta thresholds, "
                        "dimension cross-analysis, red flag identification"
                    ),
                    "edge_cases": (
                        "Considers that the completeness drop might indicate the skill is "
                        "over-indexing on some topics (e.g., indexing) while neglecting others "
                        "(e.g., connection pooling). Suggests adding coverage checks."
                    ),
                },
            },
        ],
    }


def generate_benchmark(
    skill_name: str,
    skill_description: str,
    headings: list[str],
    concepts: list[str],
    pitfalls: list[str],
    count: int,
) -> dict:
    """Generate the benchmark.json template structure."""
    tasks = []
    for i in range(1, count + 1):
        task_id = f"task-{i:02d}"
        tasks.append(
            {
                "id": task_id,
                "prompt": f"TODO: Write a concrete task prompt #{i} that tests knowledge from '{skill_name}'",
                "rubric": {
                    "correctness": "TODO: Define what 'correct' means for this task",
                    "completeness": "TODO: Define what a complete solution covers",
                    "pattern_adherence": "TODO: Which skill patterns should appear in the output?",
                    "edge_cases": "TODO: Which edge cases should be handled?",
                },
            }
        )

    return {
        "skill": skill_name,
        "skill_description": skill_description,
        "metadata": {
            "headings": headings[:15],
            "key_concepts": concepts[:15],
            "pitfalls": pitfalls[:10],
        },
        "tasks": tasks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Provision benchmark tasks from a target skill's SKILL.md.",
        epilog=(
            "Example:\n"
            "  python provision.py --skill-path ../my-skill/SKILL.md --count 5 --output benchmark.json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--skill-path",
        type=Path,
        default=None,
        help="Path to the target SKILL.md file (optional when --self-evaluate is used)",
    )
    parser.add_argument(
        "--self-evaluate",
        action="store_true",
        default=False,
        help="Generate a pre-filled benchmark to evaluate skill-benchmark itself",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of benchmark tasks to generate (default: 5, ignored with --self-evaluate)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmark.json"),
        help="Output path for benchmark.json (default: benchmark.json)",
    )
    args = parser.parse_args(argv)

    # Self-evaluate mode: pre-built benchmark, skip SKILL.md parsing
    if args.self_evaluate:
        print("Self-evaluation mode: generating pre-filled benchmark for skill-benchmark")
        benchmark = _build_self_eval_benchmark()
    else:
        # Normal mode: --skill-path is required
        if args.skill_path is None:
            print("Error: --skill-path is required (unless using --self-evaluate)", file=sys.stderr)
            return 1
        if not args.skill_path.is_file():
            print(f"Error: SKILL.md not found at '{args.skill_path}'", file=sys.stderr)
            return 1
        if args.count < 1:
            print("Error: --count must be at least 1", file=sys.stderr)
            return 1

        # Read and parse
        content = args.skill_path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(content)
        body = extract_body(content)

        skill_name = frontmatter.get("name", args.skill_path.parent.name)
        skill_description = frontmatter.get("description", "")

        headings = extract_headings(body)
        concepts = extract_key_concepts(body)
        pitfalls = extract_pitfalls(body)

        # Generate benchmark template
        benchmark = generate_benchmark(
            skill_name=skill_name,
            skill_description=skill_description,
            headings=headings,
            concepts=concepts,
            pitfalls=pitfalls,
            count=args.count,
        )

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(benchmark, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    task_count = len(benchmark["tasks"])
    skill_name = benchmark["skill"]
    print(f"Benchmark template written to {args.output}")
    print(f"  Skill: {skill_name}")
    if args.self_evaluate:
        print(f"  Tasks: {task_count} (pre-filled, ready to execute)")
    else:
        print(f"  Tasks: {task_count} (fill TODO placeholders with concrete tasks)")
        headings = benchmark["metadata"]["headings"]
        concepts = benchmark["metadata"]["key_concepts"]
        pitfalls = benchmark["metadata"]["pitfalls"]
        print(f"  Topics extracted: {len(headings)} headings, {len(concepts)} concepts, {len(pitfalls)} pitfalls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
