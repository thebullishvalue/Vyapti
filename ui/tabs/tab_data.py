"""
Vyāpti — Data: the full daily record behind the read.

  1 TRUST   what is it based on?        Coverage
  2 ANCHOR  every session               Daily Breadth
"""

from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from ui import format as fmt
from ui.components import render_kpi_strip, render_note, render_section_header, render_table_panel

COLUMNS = {"Advances": "Advances", "Declines": "Declines", "Unchanged": "Unchanged", "Coverage": "Coverage %",
           "AD_Ratio": "A/D Ratio", "Custom_Breadth": "Custom Breadth", "Relative_Breadth": "Relative Breadth",
           "Rel_AD_Ratio": "Rel A/D Ratio", "AD_Line": "A/D Line", "Zone": "Zone", "Direction": "Direction"}


def daily_table(view: pd.DataFrame) -> pd.DataFrame:
    out = view[list(COLUMNS)].rename(columns=COLUMNS)
    out["Zone"] = out["Zone"].str.title()
    out["Direction"] = out["Direction"].str.title()
    out.index = out.index.date
    out.index.name = "Date"
    return out.iloc[::-1]


def display_table(table: pd.DataFrame) -> pd.DataFrame:
    """The daily table as the page shows it; the CSV keeps every column raw.

    Twelve columns at the names above needed 1,190px in a 1,134px panel at 1440, so the last
    column was cut. The screen uses the app's own short names (Rel Breadth and Rel A/D, as on
    the command bar and the chart axes), states coverage as a percentage, shows every breadth
    value to three places as everywhere else in the app, and signs the one column that is a
    change: momentum."""
    out = table.rename(columns={"Relative Breadth": "Rel Breadth", "Rel A/D Ratio": "Rel A/D",
                                "Coverage %": "Coverage"})
    out["Coverage"] = [f"{v:.0f}%" if pd.notna(v) else fmt.DASH for v in out["Coverage"]]
    out["Rel A/D"] = [fmt.signed(v, 3) for v in out["Rel A/D"]]
    # A level, not a change: no plus, but the same minus as the column beside it.
    out["A/D Line"] = [f"{v:,.0f}".replace("-", "−") if pd.notna(v) else fmt.DASH for v in out["A/D Line"]]
    return out


def render(a, view: pd.DataFrame, tf: str) -> None:
    u, d = a.universe, a.data
    render_section_header(
        "Coverage",
        f"What every reading in the app is based on. Constituents: {u.source}.",
        icon="database", accent="cyan",
    )
    render_kpi_strip([
        {"label": "Priced", "value": f"{d.close.shape[1]} of {len(u.tickers)}",
         "subtext": f"{u.unit} with price data", "color_class": "warning" if d.missing else "neutral"},
        {"label": "Sessions", "value": f"{len(a.panel):,}",
         "subtext": f"since {fmt.when(a.panel.index[0])}", "color_class": "neutral"},
        {"label": "Avg coverage", "value": f"{a.panel['Coverage'].mean():.0f}%",
         "subtext": "share of the universe trading each session", "color_class": "neutral"},
        {"label": "Index", "value": (d.benchmark_ticker or "EW basket"),
         "subtext": ("Yahoo Finance index level" if a.uses_index else "equal-weighted constituents"),
         "color_class": "accent"},
    ], max_cols=4, key="data-coverage")
    if d.missing:
        render_note(f"No price data for {len(d.missing)} symbol(s): " + ", ".join(d.missing[:40])
                    + (" …" if len(d.missing) > 40 else ""))

    render_section_header(
        "Daily Breadth",
        "Every session in the window: the counts and every oscillator, newest first.",
        icon="layers",
    )
    table = daily_table(view)
    render_table_panel(display_table(table), key="data-daily", window=True, index_label="Date",
                       context=f"{u.name} · {tf} · {len(table):,} sessions · newest first",
                       col_precision={"A/D Ratio": 2, "Custom Breadth": 3, "Rel Breadth": 3},
                       sign_color_cols={"Rel A/D"}, max_height=560)
    safe = re.sub(r"[^A-Za-z0-9]+", "_", u.name).strip("_")
    st.download_button("Download CSV", table.to_csv().encode("utf-8"),
                       f"{safe}_breadth_{view.index[0]:%Y%m%d}_{view.index[-1]:%Y%m%d}.csv", "text/csv",
                       type="secondary")
