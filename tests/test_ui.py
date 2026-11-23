import datetime

import pandas as pd
import pytest

from breadth import build_analysis
from synthetic import make_market
from ui import charts
from ui.tabs import tab_engine, tab_record, tab_sectors
from ui.verdict import build_read, position


@pytest.fixture(scope="module")
def analysis():
    uni, data = make_market()
    return build_analysis(uni, data, datetime.date(2023, 11, 20), datetime.date(2026, 11, 20))


def test_position():
    assert position(pd.Series([1, 2, 3, 4])) == 1.0
    assert position(pd.Series([1, 3, 4, 2])) == pytest.approx(1 / 3)
    assert position(pd.Series([4, 3, 2, 1])) == 0.0
    assert position(pd.Series([1.0])) == 0.5


def test_read_card_content(analysis):
    r = build_read(analysis)
    assert r["signal"] == analysis.zone
    assert r["trust"]["tier"] in {"favourable", "normal", "unfavourable", "norecord"}
    assert r["signal_class"] in {"buy", "sell", "hold"}
    assert [e["title"] for e in r["evidence"]] == ["Relative Breadth", "Direction", "Momentum",
                                                   "Latest session", "Breadth trend"]
    assert all(0 <= e["value"] <= 1 and e["tone"] in {"supports", "against", "neutral"} for e in r["evidence"])
    assert r["limit"] == analysis.verdict.sentence
    assert "not added into a score" in r["foot"]


def test_record_class_follows_verdict(analysis):
    r = build_read(analysis)
    expected = {"FAVOURABLE": "buy", "UNFAVOURABLE": "sell"}.get(analysis.verdict.label, "hold")
    assert r["signal_class"] == expected


def test_engine_stack_and_heatmap(analysis):
    from breadth.study import events
    view = analysis.panel.tail(130)
    fig = charts.engine_stack(view, analysis.price, "TEST", events(analysis.panel))
    names = {t.name for t in fig.data}
    assert {"Relative Breadth", "Custom Breadth", "TEST", "A/D Line"} <= names
    assert any(s.y0 == 0.40 or s.y1 == 0.40 for s in fig.layout.shapes)   # oversold band drawn
    frame = tab_sectors.heatmap_frame(analysis, view.index[0], view.index[-1])
    assert list(frame.columns) and charts.sector_heatmap(frame).data


def test_page_tables(analysis):
    view = analysis.panel.tail(130)
    stats = tab_engine.window_stats(view)
    assert list(stats["Series"]) == ["Relative Breadth", "Custom Breadth", "Relative A/D Ratio", "A/D Ratio"]
    assert len(tab_record.zone_cards(analysis)) == 4
    assert list(tab_record.zone_table(analysis)["Zone"]) == ["Oversold", "Neutral", "Overbought", "Any session"]
    assert len(tab_record.crossing_table(analysis)) == 4
    log = tab_engine.crossing_log(analysis, view)
    assert log.empty or log["Date"].is_monotonic_decreasing


def test_tape_symbols_are_unique_and_short():
    import app
    names = ["Consumer Discretionary", "Consumer Staples", "Information Technology", "Some New Long Sector Name"]
    syms = [app.tape_symbol(n) for n in names]
    assert len(set(syms)) == len(syms) and all(len(s) <= 12 for s in syms)


def test_window_view(analysis):
    import app
    v = app.window_view(analysis, "3M")
    assert v.index[-1] == analysis.asof and (analysis.asof - v.index[0]).days <= 92
    assert app.window_view(analysis, "MAX").index[0] == analysis.panel.index[0]
    assert app.window_view(analysis, "YTD").index[0].year == analysis.asof.year


def test_overbought_note_is_not_a_risk(analysis):
    """'Overbought is common here' is a neutral note; only a real risk takes the short colour."""
    r = build_read(analysis)
    assert not (r.get("risk") or "").startswith("Overbought is common")
    if r.get("note"):
        assert r["note"].startswith("Overbought is common") and analysis.zone == "OVERBOUGHT"


def test_run_log_record_line(analysis):
    import app
    line = app._record_line(analysis)
    assert line and line[0].isupper() and "\n" not in line
    card = app._result_card(analysis)
    assert {"As of", "Universe", "History", "Zone", "Direction", "Record", "Sectors"} <= set(card)


def test_signed_format():
    from ui import format as fmt
    assert fmt.signed(1.234) == "+1.23" and fmt.signed(-0.641) == "−0.64"
    assert fmt.signed(0.001) == "0.00" and fmt.signed(float("nan")) == fmt.DASH
    assert fmt.signed(1234.5, 1) == "+1,234.5"


def test_daily_table_screen_and_csv(analysis):
    from ui.tabs import tab_data
    raw = tab_data.daily_table(analysis.panel.tail(30))
    shown = tab_data.display_table(raw)
    assert "Rel Breadth" in shown and "Rel A/D" in shown and "Coverage" in shown
    assert raw["Rel A/D Ratio"].dtype.kind == "f"                       # the CSV stays numeric
    assert all(v[0] in "+−0—" for v in shown["Rel A/D"])                 # the screen signs momentum
    assert all(v.endswith("%") or v == "—" for v in shown["Coverage"])


def test_method_panels_are_prose_rows():
    from ui.tabs import tab_method
    html = tab_method.method_html(tab_method.OSCILLATORS)
    assert html.count('class="lookback-row prose"') == len(tab_method.OSCILLATORS)
    assert html.count('class="role"') == len(tab_method.OSCILLATORS)    # every oscillator names its role
    assert 'class="role"' not in tab_method.method_html(tab_method.COUNTING)


def test_pages_registered_before_and_after_a_run():
    """One page table serves both navigations, so every address a browser can hold resolves
    in a fresh session (before Run) as well as after one."""
    import app
    paths = [p[3] for p in app.PAGES]
    assert len(set(paths)) == len(paths) == 5
    assert [p[1] for p in app.PAGES] == ["Breadth Engine", "Record", "Sectors", "Data", "Method"]
    assert callable(app._hidden_pages)


def test_sector_heatmap_hover_is_a_finished_label(analysis):
    """The hover prints labels made in Python; a %{customdata} placeholder printed itself under unified hover."""
    frame = tab_sectors.heatmap_frame(analysis, analysis.panel.index[-130], analysis.panel.index[-1])
    tr = charts.sector_heatmap(frame).data[0]
    assert "customdata" not in tr.hovertemplate and "%{text}" in tr.hovertemplate
    cells = [c for row in tr.text for c in row if c]
    assert cells and all(c.split(" · ")[1] in {"oversold", "neutral", "overbought"} for c in cells)
