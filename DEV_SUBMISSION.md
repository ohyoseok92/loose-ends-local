---
title: Loose Ends: a local AI that rereads my notes so I don't have to
published: false
tags: devchallenge, hf26challenge, opensource, ai
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

## What I Built

I keep short daily notes. Promises disappear into them: a file to send, a pull request to review, a plan to draft later. Re-reading every note to maintain a separate task list is exactly the sort of small chore I postpone.

**Loose Ends** scans a folder of Markdown or text notes and produces one reviewable checklist. A local open-weight model recognizes commitments, drops completed items, merges repeated reminders, and proposes a concrete first step. The checklist links back to the exact note lines. It never sends messages or edits the source notes.

The "slow and steady" part is the rerun: when the notes have not changed, a SHA-256 cache returns the last report with zero model calls. I can run it each morning without spending tokens on the same text.

## Demo

I ran the tool against two small synthetic notes. Monday says I promised Mina an API schema and should review a pull request; Tuesday repeats the promise and adds a later demo outline. The model produced three checklist items, merged the duplicate, and ignored a completed hosting invoice.

```text
python loose_ends.py examples/notes --output demo-report.md
Wrote 3 review items to demo-report.md

python loose_ends.py examples/notes --output demo-report.md
Unchanged notes; reused demo-report.md (no model call)
```

[View the sample input and actual output](REPO_URL) and [watch the short demo](VIDEO_URL).

## Code

[Source, setup instructions, and MIT license](REPO_URL). The Python CLI uses only the standard library and a local Ollama endpoint. No account or cloud key is needed to run it.

## How I Built It

The reader walks `.md` and `.txt` files, labels each line `filename:line`, and limits file counts and sizes. The prompt asks a local `qwen2.5-coder:7b-instruct-q4_K_M` model for structured JSON: task, urgency, next step, reason, and source lines. Validation discards any response without a real source token. The renderer groups items by `today`, `this_week`, `later`, or `unknown`.

I tested the actual Ollama run on an RTX 4060 laptop. It returned three tasks from the sample notes; a second run reused the report. The model took roughly twelve seconds on its first call in this run. Performance will vary by model and hardware.

This is intentionally review-first. Automatic mail sending or moving files would turn an extraction error into a real-world mistake. The tool instead gives me a compact checklist and evidence so I can decide what to do.

## Why Does Open Innovation Matter?

My notes can contain private work and people's names. Running an open-weight model through local Ollama keeps the note text on my machine, rather than sending it to a hosted model API. I can swap the model, inspect the prompt and validation, and rerun at no per-call charge. That makes a small daily chore worth automating.

## The Lazy Payoff

The sample run turned two notes into three review items and merged one repeated promise. The next run needed no inference at all. I still check the cited lines before acting: a local model can be wrong, and the evidence is part of the product.
