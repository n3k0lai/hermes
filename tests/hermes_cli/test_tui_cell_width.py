"""TUI panel/banner geometry must use terminal cell width, not codepoint length."""

from __future__ import annotations

import os
import re
from unittest.mock import patch

from hermes_cli.cli_render import (
    _append_panel_line,
    _build_compact_banner,
    _display_width,
    _pad_to_width,
    _panel_box_width,
    _wrap_panel_text,
)


def test_display_width_counts_emoji_as_two_cells():
    assert _display_width("📌") == 2
    assert _display_width("ab") == 2


def test_pad_to_width_pads_and_truncates_by_cells():
    assert _pad_to_width("📌", 4) == "📌  "
    assert _display_width(_pad_to_width("📌hello", 4)) == 4


def test_panel_box_width_accounts_for_wide_title():
    narrow = _panel_box_width("Title", ["ok"], min_width=20, max_width=80)
    wide = _panel_box_width("📌 Title", ["ok"], min_width=20, max_width=80)
    assert wide >= narrow


def test_append_panel_line_right_edge_stable_with_emoji():
    frags: list = []
    _append_panel_line(frags, "b", "c", "📌 Title", 20)
    rendered = "".join(text for _, text in frags).rstrip("\n")
    assert _display_width(rendered) == 22  # box_width + two border glyphs


def test_wrap_panel_text_respects_cell_budget():
    lines = _wrap_panel_text("📌 " + ("word " * 30), 24)
    assert lines
    assert all(_display_width(line) <= 24 for line in lines)


def test_compact_banner_rows_share_one_width():
    os.environ["HERMES_FAST_STARTUP_BANNER"] = "1"
    with patch("shutil.get_terminal_size", return_value=os.terminal_size((80, 24))):
        banner = _build_compact_banner()
    plain = re.sub(r"\[/?[^\]]*\]", "", banner)
    rows = [row for row in plain.splitlines() if row.strip()]
    widths = {_display_width(row) for row in rows}
    assert len(widths) == 1, rows
