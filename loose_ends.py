"""Offline, review-first digest of commitments buried in Markdown notes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

MODEL = "qwen2.5-coder:7b-instruct-q4_K_M"
PROMPT = """You extract actionable commitments from private notes. Return JSON only:
{"tasks": [{"task": "short verb-first task", "when": "today|this_week|later|unknown",
"next_step": "one concrete first action", "sources": ["filename:line"], "reason": "short evidence"}]}
Merge duplicate commitments across notes. Ignore completed tasks, speculation, and tasks that
belong to other people. Never invent a deadline. Cite source line tokens exactly as supplied.
If there are no commitments, return {"tasks": []}.
"""


def collect_notes(folder: Path) -> tuple[str, set[str]]:
    if not folder.is_dir():
        raise ValueError(f"Notes directory does not exist: {folder}")
    chunks: list[str] = []
    valid_sources: set[str] = set()
    files = sorted(p for p in folder.rglob("*") if p.suffix.lower() in {".md", ".txt"} and p.is_file() and not p.is_symlink())
    if len(files) > 50:
        raise ValueError("At most 50 note files are supported per run")
    for path in files:
        relative = path.relative_to(folder).as_posix()
        if any(part.startswith(".") for part in path.relative_to(folder).parts):
            continue
        if path.stat().st_size > 100_000:
            raise ValueError(f"Note exceeds 100 KB: {relative}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            source = f"{relative}:{number}"
            valid_sources.add(source)
            chunks.append(f"[{source}] {line}")
    return "\n".join(chunks), valid_sources


def ask_local_model(notes: str, model: str, base_url: str) -> dict:
    request = urllib.request.Request(
        base_url.rstrip("/") + "/api/chat",
        data=json.dumps({
            "model": model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": notes},
            ],
            "options": {"temperature": 0},
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            payload = json.load(response)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Local Ollama request failed: {exc}") from exc
    return json.loads(payload["message"]["content"])


def validate(result: dict, valid_sources: set[str]) -> list[dict]:
    tasks = result.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("The model response did not contain a tasks array")
    clean = []
    for item in tasks:
        if not isinstance(item, dict):
            continue
        sources = [src for src in item.get("sources", []) if isinstance(src, str) and src in valid_sources]
        task = str(item.get("task", "")).strip()
        next_step = str(item.get("next_step", "")).strip()
        if not (task and next_step and sources):
            continue
        when = str(item.get("when", "unknown"))
        if when not in {"today", "this_week", "later", "unknown"}:
            when = "unknown"
        clean.append({"task": task, "when": when, "next_step": next_step,
                      "sources": sources, "reason": str(item.get("reason", "")).strip()})
    return clean


def render(tasks: list[dict]) -> str:
    lines = ["# Loose Ends", "", "Review these suggestions before acting. Your notes were not changed.", ""]
    if not tasks:
        lines.append("No open commitments found.")
    for group in ("today", "this_week", "later", "unknown"):
        selected = [task for task in tasks if task["when"] == group]
        if not selected:
            continue
        lines += [f"## {group.replace('_', ' ').title()}", ""]
        for item in selected:
            lines += [f"- [ ] **{item['task']}**", f"  - Next: {item['next_step']}",
                      f"  - Source: {', '.join(item['sources'])}"]
            if item["reason"]:
                lines.append(f"  - Why: {item['reason']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notes", type=Path, help="folder of .md or .txt notes")
    parser.add_argument("--output", type=Path, default=Path("loose-ends-report.md"))
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--force", action="store_true", help="rescan even when notes are unchanged")
    args = parser.parse_args()
    try:
        notes, valid_sources = collect_notes(args.notes)
        if not notes.strip():
            raise ValueError("No non-empty .md or .txt notes found")
        fingerprint = hashlib.sha256((args.model + "\n" + PROMPT + "\n" + notes).encode()).hexdigest()
        cache = args.output.with_suffix(".state.json")
        if not args.force and cache.exists() and args.output.exists():
            state = json.loads(cache.read_text(encoding="utf-8"))
            if state.get("fingerprint") == fingerprint:
                print(f"Unchanged notes; reused {args.output} (no model call)")
                return 0
        tasks = validate(ask_local_model(notes, args.model, args.base_url), valid_sources)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render(tasks), encoding="utf-8")
        cache.write_text(json.dumps({"fingerprint": fingerprint, "model": args.model,
                                     "tasks": tasks}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {len(tasks)} review items to {args.output}")
        return 0
    except (ValueError, RuntimeError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
