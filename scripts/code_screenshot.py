"""Renders code snippets as PNG images for the Milestone 2 report proofs.

Uses pygments to produce a syntax-highlighted image, which is cleaner and more
legible in a report than a photographed editor window.

Usage:
    PYTHONPATH=. python scripts/code_screenshot.py
"""

import argparse
from pathlib import Path

from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import PythonLexer


# Each entry is (output name, source file, first line, last line, caption).
# Line ranges are 1-indexed and inclusive, matching what an editor shows.
SNIPPETS = [
    (
        "acc1_tuple_definitions",
        "agents/n_tuple_network.py",
        23, 39,
        "The 17 tuple patterns: 4 rows, 4 columns, 9 overlapping 2x2 squares.",
    ),
    (
        "acc1_feature_indices",
        "agents/n_tuple_network.py",
        167, 184,
        "Board to lookup-table indices, over all 8 symmetries at once.",
    ),
    (
        "acc1_value_and_update",
        "agents/n_tuple_network.py",
        181, 198,
        "V(s) sums one entry per tuple per symmetry; update() spreads the TD "
        "error back over exactly those entries.",
    ),
    (
        "acc2_td_update",
        "training/td_learning.py",
        108, 133,
        "The TD(0) update over afterstates.",
    ),
    (
        "acc3_evaluate",
        "agents/expectimax_rl_agent.py",
        90, 97,
        "One search, two evaluation functions: the learned value function when a "
        "network is present, the original heuristic when it is not.",
    ),
]


def render(source, first, last, out_path):
    lines = Path(source).read_text().splitlines()
    if last > len(lines):
        raise SystemExit(f"{source} has {len(lines)} lines, asked for {last}")

    snippet = "\n".join(lines[first - 1:last])

    formatter = ImageFormatter(
        font_name="Menlo",
        font_size=28,
        line_numbers=True,
        line_number_start=first,
        line_number_bg="#f5f5f5",
        line_number_fg="#999999",
        style="friendly",
        image_pad=18,
    )

    out_path.write_bytes(highlight(snippet, PythonLexer(), formatter))
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Render report code screenshots.")
    parser.add_argument("--out-dir", default="report_assets")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    captions = []
    for name, source, first, last, caption in SNIPPETS:
        path = render(source, first, last, out_dir / f"{name}.png")
        size_kb = path.stat().st_size / 1024
        print(f"{path}  ({source}:{first}-{last}, {size_kb:.0f} KB)")
        captions.append(f"- `{name}.png` ({source}:{first}-{last}): {caption}")

    index = out_dir / "captions.md"
    index.write_text("\n".join(captions) + "\n")
    print(f"\nCaptions written to {index}")


if __name__ == "__main__":
    main()
