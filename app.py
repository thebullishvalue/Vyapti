"""
Vyāpti — Main Streamlit entrypoint.
व्याप्ति (Vyāpti) — "Pervasion": how far a move extends through the whole

VYĀPTI — one oscillator says where breadth stands, two more say which
way it is moving, and the index's own history says whether that reading has
ever mattered. Built on the Aarambh oscillators; the interface and the terminal
output are the Pragyam family's, shared with every member.

Usage:
    streamlit run app.py
"""

from __future__ import annotations

import datetime as dt
from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from breadth import build_analysis, history_start
from breadth import indicators as ind
from breadth import universe as uv
from breadth.data import download_market_data
from breadth.study import CROSSING_TEXT
from config import (
    COMPANY,
    DEFAULT_EVIDENCE,
    DEFAULT_TIMEFRAME,
    EVIDENCE_YEARS,
    PRODUCT_NAME,
    STALE_DATA_DAYS,
    TIMEFRAMES,
    VERSION,
)
from logger_config import capture_library_output, console
from ui import format as fmt
from ui.components import (
    render_control_hint,
    render_empty_state,
    render_nav_brand,
    render_notice_rail,
    render_ticker,
    render_top_bar,
)
from ui.tabs import tab_data, tab_engine, tab_method, tab_record, tab_sectors
from ui.tabs.tab_landing import render_landing_page
from ui.theme import inject_css, progress_bar

PAGE_ICON = ("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAy"
             "NCAyNCI+PHBhdGggZD0iTTMgMTdsNS02IDQgMyA5LTkiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzRDN0RGMCIgc3Ryb2tlLXdp"
             "ZHRoPSIyLjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==")
IST = timezone(timedelta(hours=5, minutes=30))


# ══════════════════════════════════════════════════════════════════════════════
# DATA ACCESS — failures raise inside the cached functions, so they are never cached
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False, max_entries=8)
def load_universe(kind: str, index: str):
    return uv.resolve_universe(kind, index)


@st.cache_data(ttl=300, show_spinner=False, max_entries=5)
def load_market_data(tickers: tuple, start: dt.date, end: dt.date, benchmark, invert: tuple):
    return download_market_data(list(tickers), start, end, benchmark=benchmark, invert=list(invert))


#: Analyses already computed this session, keyed by their inputs (bounded LRU),
#: so moving between markets and back does not recompute.
_RESULTS_MAX = 4


#: The engine's stages as the progress card and the run log show them: the step, and its detail.
#: Phases come from the percentage (RUN_PHASES in ui/theme.py): 1 Constituents · 2 Price Data ·
#: 3 Breadth Engine · 4 Record & Sectors.
_ENGINE_STEPS = {
    "computing the oscillators": ("Computing the Oscillators",
                                  "advances · declines · Custom & Relative Breadth"),
    "measuring the record":      ("Measuring the Record", "zones · crossings · episodes · one and three months on"),
    "reading the sectors":       ("Reading the Sectors", "the same oscillator, sector by sector"),
}


def _step(slot, pct: int, label: str, detail: str = "") -> None:
    """One engine stage: the progress card moves on and the run log opens a numbered, timed step."""
    progress_bar(slot, pct, label, detail)
    console.begin_step(label, detail)


#: The verdict as the run log names it (the page says it in full).
_VERDICT_WORDS = {"FAVOURABLE": "Better than normal", "NORMAL": "About normal", "UNFAVOURABLE": "Worse than normal",
                  "MIXED": "Mixed"}


def _record_line(a) -> str:
    words = _VERDICT_WORDS.get(a.verdict.label)
    if words is None:
        return "Too few cases to judge"
    eps = a.zone_evidence.loc[a.zone, "Episodes"] if a.zone in a.zone_evidence.index else None
    return f"{words} after {a.zone.lower()}" + (f" · {int(eps)} episodes" if eps is not None else "")


def _result_card(a) -> dict:
    """What the run produced, for the run log's closing card."""
    counted = a.data.close.shape[1]
    last = a.last
    card = {
        "As of": fmt.when(a.asof),
        "Universe": f"{a.universe.name} · {counted} of {len(a.universe.tickers)} {a.universe.unit.lower()} priced",
        "History": f"{len(a.panel):,} sessions · {a.years:.1f} years",
        "Zone": f"{a.zone.title()} · Relative Breadth {last['Relative_Breadth']:.3f}",
        "Direction": str(last.get("Direction", "—")).title(),
        "Record": _record_line(a),
        "Sectors": f"{len(a.sectors)} read" if len(a.sectors) else "none with 5 or more members",
    }
    if a.recent:
        k, ago = a.recent[0]
        card["Last crossing"] = f"{CROSSING_TEXT[k].removeprefix('Breadth ').lower()}, {ago} sessions ago"
    return card


def _run(params: dict, slot) -> object | None:
    """The analysis for ``params``: from this session's store when it has one (a replay prints
    nothing), else computed as a family-console run: the request, each stage as a numbered,
    timed step, the result card and the closing line."""
    key = (params["kind"], params["index"], params["asof"], params["years"])
    cache = st.session_state.setdefault("results_cache", {})
    if key in cache:
        cache[key] = cache.pop(key)
        return cache[key]

    console.header(f"{PRODUCT_NAME.upper()} · Breadth Analysis", VERSION)
    console.main_header("Request", {"Market": params["kind"], "Index": params["index"],
                                    "As of": f"{params['asof']:%Y-%m-%d}", "Record": f"{params['years']} years"})
    try:
        _step(slot, 4, "Resolving Constituents", f"{params['index']} · NSE · Wikipedia")
        universe = load_universe(params["kind"], params["index"])
        start = history_start(params["asof"], params["asof"], params["years"])
        _step(slot, 25, "Downloading Prices",
              f"{len(universe.tickers)} {universe.unit.lower()} · Yahoo Finance · since {start:%b %Y}")
        data = load_market_data(tuple(universe.tickers), start, params["asof"], universe.benchmark,
                                tuple(universe.invert))
        analysis = build_analysis(universe, data, start, params["asof"],
                                  progress=lambda pct, k: _step(slot, pct, *_ENGINE_STEPS[k]))
    except Exception as exc:
        console.end_step(f"{type(exc).__name__}: {exc}", "fail")
        console.end_run("FAILED")
        raise
    console.end_step()
    progress_bar(slot, 100, "Analysis Complete", "the read, its record and the sectors")
    slot.empty()
    if analysis is None:
        console.warning("Not enough sessions with constituents trading to read breadth.")
        console.end_run()
        return None
    console.summary("Result", _result_card(analysis))
    for n in notices_for(analysis, params["asof"]):
        (console.warning if n["kind"] == "warning" else console.info)(f"{n['title']}: {n['body']}")
    console.end_run()
    cache[key] = analysis
    while len(cache) > _RESULTS_MAX:
        cache.pop(next(iter(cache)))
    return analysis


def window_view(a, tf: str) -> pd.DataFrame:
    """The analysis panel cut to the page's chart window (cumulative series re-anchored)."""
    end = a.asof
    if tf == "MAX":
        start = a.panel.index[0]
    elif tf == "YTD":
        start = pd.Timestamp(end.year, 1, 1)
    else:
        start = end - dt.timedelta(days=TIMEFRAMES.get(tf) or 365)
    view = ind.window(a.panel, start, end)
    return view if len(view) >= 2 else ind.window(a.panel, a.panel.index[-30], end)


#: Tape symbols for sector names a desk abbreviates (GICS and NSE industries).
#: Anything not listed is shortened by ``tape_symbol``. The tape cuts at 12
#: characters, which made "Consumer Discretionary" and "Consumer Staples" the
#: same symbol.
SECTOR_TAPE = {
    "Information Technology": "TECH", "Communication Services": "COMMS", "Consumer Discretionary": "CONS DISC",
    "Consumer Staples": "STAPLES", "Health Care": "HEALTH", "Healthcare": "HEALTH", "Real Estate": "REAL EST",
    "Financial Services": "FIN SERV", "Financials": "FINANCIALS", "Industrials": "INDUSTRIALS",
    "Fast Moving Consumer Goods": "FMCG", "Automobile and Auto Components": "AUTO",
    "Oil Gas & Consumable Fuels": "OIL & GAS", "Metals & Mining": "METALS", "Capital Goods": "CAP GOODS",
    "Consumer Durables": "DURABLES", "Consumer Services": "CONS SERV", "Construction Materials": "CEMENT",
    "Media Entertainment & Publication": "MEDIA", "Telecommunication": "TELECOM", "Precious Metals": "PRECIOUS",
    "Industrial Metals": "IND METALS", "Grains & Oilseeds": "GRAINS", "EM ex-Asia": "EM",
}


def tape_symbol(name: str) -> str:
    if name in SECTOR_TAPE:
        return SECTOR_TAPE[name]
    words = [w for w in name.replace("&", " ").split() if w.lower() not in {"and", "of", "the"}]
    short = " ".join(words).upper()
    return short if len(short) <= 12 else "".join(w[0] for w in words).upper()


def tape_frame(a) -> pd.DataFrame:
    """The tape: the index, then every sector's equal-weighted level — the run's own data."""
    cols = {a.universe.name if a.uses_index else "EW BASKET": a.price}
    for sector, osc in sorted(a.sector_osc.items()):
        cols[tape_symbol(sector)] = 100 * (1 + osc["EW_Return"].fillna(0)).cumprod()
    return pd.DataFrame(cols).loc[:a.asof].tail(2)


def notices_for(a, asof_requested: dt.date) -> list[dict]:
    out = []
    if a.universe.is_fallback:
        out.append({"kind": "warning", "title": "Substitute constituents",
                    "body": f"The live {a.universe.name} list could not be fetched, so a built-in list of large "
                            f"caps stands in. Every reading describes that list, not the index."})
    if not a.uses_index:
        out.append({"kind": "info", "title": "No index price",
                    "body": f"Yahoo has no usable history for this index, so the record is measured on "
                            f"{a.index_name}."})
    if a.data.missing:
        out.append({"kind": "info", "title": f"{len(a.data.missing)} without prices",
                    "body": f"{len(a.data.missing)} of {len(a.universe.tickers)} constituents returned no price "
                            f"data and are not counted. The Data page lists them."})
    age = (pd.Timestamp(asof_requested) - a.asof).days
    if age > STALE_DATA_DAYS:
        out.append({"kind": "warning", "title": "Older session",
                    "body": f"The latest session with enough data is {fmt.when(a.asof)}, {age} days before "
                            f"the requested date. Every reading describes that session."})
    return out


# ══════════════════════════════════════════════════════════════════════════════
# APPEARANCE & FOOTER
# ══════════════════════════════════════════════════════════════════════════════

#: Paper leads, and the order IS the default (first in the tuple is first run).
APPEARANCES = ("Paper", "Slate")
_THEME_CHOICE = "appearance_choice"


def theme_choice() -> str:
    choice = st.session_state.get(_THEME_CHOICE)
    return choice if choice in APPEARANCES else APPEARANCES[0]


def _render_appearance_control() -> None:
    """The theme switch — last in the rail: the least consequential control gets the least valuable spot."""
    with st.container(key="appearance"):
        st.markdown('<div class="sidebar-title">Appearance</div>', unsafe_allow_html=True)
        mode = st.segmented_control(
            "Appearance", list(APPEARANCES), key="theme_mode", default=theme_choice(),
            label_visibility="collapsed", help="Slate — dark, for working. Paper — light, for reading and print.",
        )
        if mode is not None and mode != theme_choice():
            st.session_state[_THEME_CHOICE] = mode
            st.rerun()


def _render_footer() -> None:
    now = datetime.now(IST)
    st.markdown(
        f'<div class="app-footer"><div class="content">'
        f'© {now.year} <strong>{PRODUCT_NAME}</strong> &nbsp;·&nbsp; {COMPANY}'
        f' &nbsp;·&nbsp; {VERSION} &nbsp;·&nbsp; {now.strftime("%Y-%m-%d %H:%M:%S IST")}'
        f'</div></div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

#: Every page: (group, title, icon, url path). The paths are fixed here, not inferred from
#: the functions, because the same addresses are registered before a run as well as after.
PAGES = (
    ("Engine", "Breadth Engine", ":material/monitoring:", "engine"),
    ("Engine", "Record", ":material/history:", "_page_record"),
    ("Engine", "Sectors", ":material/grid_view:", "_page_sectors"),
    ("System", "Data", ":material/table_chart:", "_page_data"),
    ("System", "Method", ":material/tune:", "_page_method"),
)


def _hidden_pages(render) -> None:
    """Register every page, hidden, each drawing ``render`` (the landing page, or a failed run).

    Before a run there is nothing for the pages to show, and the app used to return before
    registering them at all. A session that starts on a page's address, or restarts under an
    open one (Streamlit Cloud reboots the app on every push to main, and wakes a sleeping one
    the same way), then held links to pages it had never registered: the landing page showed,
    and every link in the rail did nothing until the next run. Registered and hidden, every
    address resolves, the stale links go, and the page the reader was on comes back after Run.
    """
    def page() -> None:
        render()
        _render_footer()

    st.navigation([st.Page(page, title=title, icon=icon, url_path=path, default=(i == 0))
                   for i, (_, title, icon, path) in enumerate(PAGES)], position="hidden").run()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    st.set_page_config(page_title="VYAPTI | Market Breadth", page_icon=PAGE_ICON,
                       layout="wide", initial_sidebar_state="expanded")
    # Resolve the appearance BEFORE anything is styled, so chrome and charts agree on one value.
    st.session_state["theme"] = "light" if theme_choice() == "Paper" else "dark"
    inject_css(theme=st.session_state["theme"])
    # The family console: third-party output routed into the run, and the masthead once per process.
    capture_library_output()
    console.banner(PRODUCT_NAME.upper(), VERSION, "Market Breadth · Relative Breadth · Custom Breadth · A/D Line",
                   {"Maintainer": COMPANY, "Engine": "Aarambh oscillators · zone record · sectors"})
    progress_slot = st.empty()

    # ─── The control rail ──────────────────────────────────────────────────
    # Global controls only; the chart window lives in each page's chart panel.
    # Order by frequency of use: Market → Record → Session → Appearance.
    today = datetime.now(IST).date()
    with st.sidebar:
        render_nav_brand()
        st.markdown('<div class="sidebar-title">Market</div>', unsafe_allow_html=True)
        kind = st.selectbox("Universe", uv.UNIVERSE_KINDS, key="universe_kind")
        options = uv.index_options(kind)
        if len(options) > 1:
            if st.session_state.get("universe_index") not in options:
                st.session_state["universe_index"] = "NIFTY 500" if "NIFTY 500" in options else options[0]
            index = st.selectbox("Index", options, key="universe_index")
        else:
            index = options[0]

        st.markdown('<div class="sidebar-title">Record</div>', unsafe_allow_html=True)
        ev_labels = list(EVIDENCE_YEARS)
        evidence = st.selectbox("Judge against", ev_labels, index=ev_labels.index(DEFAULT_EVIDENCE),
                                key="evidence_years",
                                help="How much history decides what each reading has meant. Longer is "
                                     "more reliable and slower to load.")
        asof = st.date_input("As of", today, max_value=today, key="asof_date",
                             help="Read breadth as it stood on this date.")
        render_control_hint("Oscillators and record always use the full history")

        st.markdown('<div class="sidebar-title">Session</div>', unsafe_allow_html=True)
        wanted = {"kind": kind, "index": index, "asof": asof, "years": EVIDENCE_YEARS[evidence]}
        current = st.session_state.get("run_params")
        label = "Run analysis" if current is None else (
            "Re-run analysis" if wanted == current else f"Run → {index}")
        if st.button(label, type="primary", width="stretch"):
            st.session_state["run_params"] = wanted
            st.rerun()
        if current is not None:
            if st.button("Refresh data", width="stretch",
                         help="Fetch prices again now, bypassing the five-minute cache."):
                load_market_data.clear()
                st.session_state.pop("results_cache", None)
                st.rerun()
            if st.button("Start over", width="stretch", help="Clear this session's results."):
                for k in ("run_params", "results_cache"):
                    st.session_state.pop(k, None)
                st.rerun()
        _render_appearance_control()

    params = st.session_state.get("run_params")
    if params is None:
        _hidden_pages(render_landing_page)
        return

    try:
        a = _run(params, progress_slot)
    except Exception as exc:                                  # noqa: BLE001 — a boundary, not a crash
        progress_slot.empty()
        reason = str(exc)
        _hidden_pages(lambda: render_empty_state(
            "The analysis could not run", reason, eyebrow="Run failed",
            action_label="Check the market in the rail, then Run analysis again"))
        return
    if a is None:
        _hidden_pages(lambda: render_empty_state(
            "Not enough data", "There are no sessions with enough constituents trading to read breadth for this "
            "market and date.", eyebrow="Nothing to read",
            action_label="Choose a later date or another market in the rail"))
        return

    st.session_state["active_instrument"] = a.universe.name
    if st.session_state.get("tf_selected") not in [t for t in TIMEFRAMES if t != "1W"]:
        st.session_state["tf_selected"] = DEFAULT_TIMEFRAME
    tf = st.session_state["tf_selected"]
    view = window_view(a, tf)
    notices = notices_for(a, params["asof"])

    last_two = a.price.tail(2).to_numpy()
    change = float((last_two[1] / last_two[0] - 1) * 100) if len(last_two) == 2 and last_two[0] else None
    age = (pd.Timestamp(min(today, params["asof"])) - a.asof).days
    status_label, status_tone = fmt.age_label(age)
    if params["asof"] < today:
        status_label, status_tone = f"AS OF {a.asof:%d %b %Y}".upper(), "info"

    def _shell(*, windowed: bool = False) -> None:
        """Tape (the world) → command bar (this read) → notice rail (its caveats). Identical on every page."""
        tape = tape_frame(a)
        render_ticker(tape, instruments=tuple(tape.columns))
        # Short readouts, as in every member's bar (Arthagati: Mood · MSF · Regime · Window · As of).
        # A sentence here ("turned overbought 1d ago") outgrew its cell and pushed the bar onto
        # three rows at 834px; the zone is already in the instrument line, so the bar says how
        # long it has held, and the Crossing Log keeps the history.
        held = int(a.last.get("Days_In_Zone", 0) or 0)
        meta = [("Rel Breadth", f"{a.last['Relative_Breadth']:.3f}"),
                ("Record", {"FAVOURABLE": "Better", "NORMAL": "Normal", "UNFAVOURABLE": "Worse", "MIXED": "Mixed"}.get(
                    a.verdict.label, "Too few")),
                ("In zone", f"{held} session{'s' * (held != 1)}"),
                ("As of", fmt.when(a.asof))]
        if windowed:
            meta.insert(-1, ("Window", tf))
        render_top_bar(
            target=f"{a.universe.name} · {a.zone.title()}", price=float(a.price.iloc[-1]), change_pct=change,
            status_label=status_label,
            status_tone={"pos": "success", "warn": "warning", "neg": "danger"}.get(status_tone, status_tone),
            meta_items=meta,
        )
        render_notice_rail(notices)

    def _safe(name: str, fn) -> None:
        try:
            fn()
        except Exception as exc:                              # noqa: BLE001 — one page, not the app
            render_empty_state(f"{name} could not be drawn", str(exc), eyebrow="Page error",
                               action_label="Try Refresh data, or another market")

    def _page_engine() -> None:
        _shell(windowed=True)
        _safe("Breadth Engine", lambda: tab_engine.render(a, view, tf))
        _render_footer()

    def _page_record() -> None:
        _shell()
        _safe("Record", lambda: tab_record.render(a))
        _render_footer()

    def _page_sectors() -> None:
        _shell(windowed=True)
        _safe("Sectors", lambda: tab_sectors.render(a, view, tf))
        _render_footer()

    def _page_data() -> None:
        _shell(windowed=True)
        _safe("Data", lambda: tab_data.render(a, view, tf))
        _render_footer()

    def _page_method() -> None:
        _shell()
        _safe("Method", lambda: tab_method.render(a))
        _render_footer()

    # The engine leads: it is the instrument, and every reading in the app is taken off it.
    render_page = {"Breadth Engine": _page_engine, "Record": _page_record, "Sectors": _page_sectors,
                   "Data": _page_data, "Method": _page_method}
    pages: dict[str, list] = {}
    for i, (group, title, icon, path) in enumerate(PAGES):
        pages.setdefault(group, []).append(
            st.Page(render_page[title], title=title, icon=icon, url_path=path, default=(i == 0)))
    st.navigation(pages, position="sidebar").run()


if __name__ == "__main__":
    main()
