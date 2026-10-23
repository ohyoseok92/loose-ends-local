"""Render a short video from the checked-in sample and a real CLI run."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = Path("C:/Windows/Fonts/consola.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/consolab.ttf")
W, H = 1280, 720


def slide(title: str, lines: list[str], destination: Path) -> None:
    image = Image.new("RGB", (W, H), "#101820")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(str(FONT_BOLD), 40)
    body_font = ImageFont.truetype(str(FONT), 26)
    small_font = ImageFont.truetype(str(FONT), 20)
    draw.rounded_rectangle((42, 42, 1238, 678), radius=24, fill="#172533", outline="#3a6075", width=3)
    draw.text((85, 85), title, font=title_font, fill="#95e2cc")
    y = 180
    for line in lines:
        draw.text((88, y), line, font=body_font, fill="#eef5f5")
        y += 52
    draw.text((87, 628), "Loose Ends · Local Qwen2.5-Coder via Ollama · Synthetic sample", font=small_font, fill="#8ca7ae")
    image.save(destination)


def main() -> None:
    slides = [
        ("THE CHORE", ["Monday: promised Mina the API schema by Friday.",
                       "Tuesday: Mina is still waiting for the same schema.",
                       "Also: review a PR; draft a demo outline later.",
                       "Finished: paid the hosting invoice."]),
        ("ONE LOCAL COMMAND", ["$ python loose_ends.py examples/notes --output demo-report.md",
                               "Wrote 3 review items to demo-report.md", "",
                               "Open-weight AI extracts and merges commitments.",
                               "Source lines are validated before display."]),
        ("THE REVIEWABLE RESULT", ["[This Week] Send Mina the API schema",
                                   "  Source: monday.md:3, tuesday.md:3",
                                   "[This Week] Review the open pull request",
                                   "[Later] Draft a one-page demo outline",
                                   "Completed invoice: excluded."]),
        ("SLOW AND STEADY", ["$ python loose_ends.py examples/notes --output demo-report.md",
                              "Unchanged notes; reused demo-report.md (no model call)", "",
                              "Notes stay local. Originals stay untouched.",
                              "You decide whether to act on each suggestion."]),
    ]
    with tempfile.TemporaryDirectory() as folder:
        temporary = Path(folder)
        for index, (title, lines) in enumerate(slides):
            slide(title, lines, temporary / f"frame{index:02d}.png")
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate", "1/4",
            "-i", str(temporary / "frame%02d.png"), "-vf", "fps=24",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(ROOT / "demo.mp4"),
        ], check=True)
    print(ROOT / "demo.mp4")


if __name__ == "__main__":
    main()
