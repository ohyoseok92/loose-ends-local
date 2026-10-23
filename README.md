# Loose Ends

An offline, review-first assistant for small promises buried in Markdown notes. It reads a folder of `.md` and `.txt` files, asks a local open-weight model to extract and merge commitments, and writes a short checklist with source lines. Run it whenever you want; unchanged notes are served from cache with **zero model calls**.

This is a new project built for the [Hacktoberfest 2026 Week 3: Slow and Steady challenge](https://dev.to/challenges/hacktoberfest-week3-2026-10-19). It rewards laziness by doing the recurring, low-energy chore of rereading notes. The AI is central: it decides whether a sentence is a commitment, ignores completed work, merges repeat reminders, and suggests a first step. [Watch the deployed demo page](https://ohyoseok92.github.io/loose-ends-local/).

## Demo

The included synthetic notes mention one promise twice, one pull request, a completed invoice, and a later demo outline. A real local `qwen2.5-coder:7b-instruct-q4_K_M` run produced [this checklist](demo-report.md): three tasks, with the repeated promise merged and the paid invoice excluded. Running the command again reused the report without a model call. [Watch the 16-second demo](demo.mp4), which replays the input and verified terminal output as cards.

```text
python loose_ends.py examples/notes --output demo-report.md
Wrote 3 review items to demo-report.md

python loose_ends.py examples/notes --output demo-report.md
Unchanged notes; reused demo-report.md (no model call)
```

## Run locally

1. Install [Ollama](https://ollama.com/download) and Python 3.10+.
2. Pull an open-weight model: `ollama pull qwen2.5-coder:7b-instruct-q4_K_M`.
3. Start Ollama: `ollama serve` (the desktop app may already run the server).
4. Run: `python loose_ends.py path/to/your/notes --output report.md`.

Use `--model` for another installed Ollama model, `--base-url` for a different local Ollama endpoint, and `--force` to rerun the model even when notes are unchanged. The tool has no Python dependencies beyond the standard library.

## Why local AI?

These notes may include names and private commitments. The script sends their content to the Ollama endpoint on `127.0.0.1`; it has no cloud API integration. A local model is swappable and does not need a per-call API bill. Source-line validation rejects any item that lacks a citation to the input notes. The report is a suggestion, never an automatic message or file operation.

## Design and limits

- Reads up to 50 text/Markdown files of up to 100 KB each; hidden files and symlinks are ignored.
- Requests structured JSON at temperature zero, then checks task fields, urgency values, and source-line references.
- Uses a SHA-256 cache of the model, prompt, and note text. Original notes are never modified.
- A model can still miss or misinterpret a promise. Check each suggested action against its source before acting.
- The cache file includes extracted task text. Store the report and cache with the same care as your notes; both are excluded by the default `.gitignore` only when using the standard report name.

## License

MIT. See [LICENSE](LICENSE).
