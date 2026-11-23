"""
Vyāpti — Method: how every number in the app is made.

One table per layer, in pipeline order: counting → oscillators → reads →
record. Nothing here is computed; it is the specification, rendered from the
same constants the engine uses so the two cannot drift apart.
"""

from __future__ import annotations

import html as html_mod

import streamlit as st

from breadth.indicators import (
    DIRECTION_BAND,
    FIB_PERIODS,
    MAX_GAP,
    MIN_ASSETS_PER_DAY,
    MIN_COVERAGE,
    MIN_SECTOR_MEMBERS,
    OVERBOUGHT,
    OVERSOLD,
    TREND_MA,
)
from breadth.study import (
    BIG_EDGE_PTS,
    BIG_HIT_PTS,
    COOLDOWN,
    EDGE_PTS,
    EPISODE_GAP,
    HIT_PTS,
    HORIZONS,
    MIN_EPISODES,
    MIN_EVENTS,
    MIN_SESSIONS,
)
from ui.components import panel, render_section_header

_fib = ", ".join(str(p) for p in FIB_PERIODS)


def method_html(rows) -> str:
    """Specification rows as the family's method panel (Nishkarsh's System page): the term on the
    left, the rule as wrapping prose on the right, stacked on a phone. A grid of words is read down,
    not scanned across, so it is not a table: a table cuts a sentence at its column edge."""
    out = []
    for row in rows:
        term, rule, role = (*row, "")[:3]
        tag = f'<span class="role">{html_mod.escape(role)}</span>' if role else ""
        out.append(f'<div class="lookback-row prose"><span class="lbl">{html_mod.escape(term)}{tag}</span>'
                   f'<span class="val">{html_mod.escape(rule)}</span></div>')
    return f'<div class="panel-specs method-specs">{"".join(out)}</div>'


def _section(key: str, context: str, rows) -> None:
    with panel(key, context=context):
        st.markdown(method_html(rows), unsafe_allow_html=True)


COUNTING = (
    ("Advancer / decliner", "A constituent whose close is above / below its previous close"),
    ("Who counts", "Only constituents that traded that session"),
    ("Gaps", f"The previous close is carried across gaps of up to {MAX_GAP} sessions"),
    ("Thin sessions", f"Dropped when fewer than max({MIN_ASSETS_PER_DAY}, {MIN_COVERAGE:.0%} of the "
                      f"universe) traded"),
)

OSCILLATORS = (
    ("A/D Ratio", "Advancers ÷ decliners (advancers when none declined)", "The session"),
    ("Custom Breadth", "10-session EMA of advancers ÷ (advancers + decliners), seeded with the first "
                       "10-session average", "Fast breadth line"),
    ("Relative Breadth", f"(Z + Custom Breadth) ÷ 2, Z = mean of Custom Breadth's {_fib}-session "
                         f"averages", "The instrument: sets the zone"),
    ("Relative A/D Ratio", "Daily change in the A/D ratio blended with its 2, 3 and 5-session averages",
     "Momentum"),
    ("A/D Line", f"Running total of advancers − decliners, against its {TREND_MA}-session average",
     "Longer trend"),
)

READS = (
    ("Zone", f"Oversold below {OVERSOLD:.2f} · Overbought above {OVERBOUGHT:.2f} · Neutral between"),
    ("Direction", f"Improving when Custom Breadth is above Relative Breadth, deteriorating when below; "
                  f"a gap of at least {DIRECTION_BAND} is needed to flip"),
    ("Momentum", "Sign of the Relative A/D Ratio's 3-session average"),
    ("Breadth trend", f"Rising when the A/D line is above its {TREND_MA}-session average"),
    ("Sectors", f"The same oscillator per sector with at least {MIN_SECTOR_MEMBERS} members"),
)

RECORD = (
    ("Horizons", " and ".join(f"{k} ({v} sessions)" for k, v in HORIZONS.items())),
    ("Zones", "Every session grouped by its zone; forward index return measured from that session"),
    ("Crossings", f"Measured from the crossing day; a repeat within {COOLDOWN} sessions is not counted"),
    ("Episodes", f"Zone stretches fewer than {EPISODE_GAP} sessions apart count as one"),
    ("Enough evidence", f"A zone needs {MIN_EPISODES} episodes and {MIN_SESSIONS} sessions with a month of "
                        f"follow-through; a crossing needs {MIN_EVENTS} past occurrences. Otherwise: too few"),
    ("Better / worse", f"The average move leans once it differs by {EDGE_PTS} pts, the hit rate once it differs "
                       f"by {HIT_PTS:.0f} pts. Both leaning the same way decides it; one alone decides it only if "
                       f"large ({BIG_EDGE_PTS} pts / {BIG_HIT_PTS:.0f} pts)"),
    ("Mixed", "The average move and the hit rate lean opposite ways"),
    ("No look-ahead", "Every figure uses only information available on its own date"),
    ("Survivorship", "History uses today's constituents; names that left the index are missing"),
)


def render(a) -> None:  # noqa: ARG001 — the specification does not depend on the run
    render_section_header("Counting", "How each session's advances and declines are counted.", icon="database",
                          accent="cyan")
    _section("method-counting", f"{len(COUNTING)} rules · every session, every constituent", COUNTING)

    render_section_header("The Oscillators", "The Aarambh set — the instrument and its companions.",
                          icon="activity")
    _section("method-osc", f"{len(OSCILLATORS)} oscillators · definition and role", OSCILLATORS)

    render_section_header("Reads", "How the oscillators become words on screen.", icon="target",
                          accent="violet")
    _section("method-reads", f"{len(READS)} reads · the words on every page", READS)

    render_section_header("The Record", "How 'what it has meant' is measured.", icon="shield",
                          accent="emerald")
    _section("method-record", f"{len(RECORD)} rules · zones, crossings and the verdict", RECORD)
