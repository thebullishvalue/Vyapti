import numpy as np
import pandas as pd
import pytest

from breadth import study


def panel_with(zones, start="2024-01-01"):
    idx = pd.bdate_range(start, periods=len(zones))
    rb = [0.35 if z == "OVERSOLD" else 0.55 if z == "OVERBOUGHT" else 0.45 for z in zones]
    return pd.DataFrame({"Zone": zones, "Relative_Breadth": rb}, index=idx)


def test_debounce():
    flags = pd.Series([True, True, False, True] + [False] * 10 + [True])
    out = study.debounce(flags, cooldown=3)
    assert list(np.flatnonzero(out)) == [0, 14]


def test_episode_spans_merge_close_stretches():
    z = np.zeros(40, dtype=bool)
    z[[2, 3, 4, 9, 10, 30]] = True
    assert study.episode_spans(z, gap=10) == [(2, 10), (30, 30)]
    assert study.episode_spans(z, gap=3) == [(2, 4), (9, 10), (30, 30)]


def test_episodes_table():
    zones = ["NEUTRAL"] * 5 + ["OVERSOLD"] * 3 + ["NEUTRAL"] * 30 + ["OVERSOLD"] * 2
    p = panel_with(zones)
    price = pd.Series(np.arange(100.0, 100.0 + len(p)), index=p.index)
    ep = study.episodes(p, "OVERSOLD", price)
    assert list(ep["Sessions"]) == [3, 2] and list(ep["Ongoing"]) == [False, True]
    assert ep["Index_During_%"].iloc[0] == pytest.approx((107 / 105 - 1) * 100)
    assert ep["Index_1M_%"].iloc[0] == pytest.approx((126 / 105 - 1) * 100)
    assert np.isnan(ep["Index_1M_%"].iloc[1])


def test_zone_and_crossing_evidence_by_hand():
    zones = (["NEUTRAL"] * 40 + ["OVERSOLD"] * 5 + ["NEUTRAL"] * 40 + ["OVERBOUGHT"] * 5) * 3 + ["NEUTRAL"] * 70
    p = panel_with(zones)
    price = pd.Series(100 * 1.001 ** np.arange(len(p)), index=p.index)  # steady rise: every forward return > 0
    zev = study.zone_evidence(p, price)
    assert zev.loc["OVERSOLD", "Sessions"] == 15 and zev.loc["OVERSOLD", "Episodes"] == 3
    assert zev.loc["OVERSOLD", "Up_1M_%"] == 100
    assert zev.loc["OVERSOLD", "Avg_1M_%"] == pytest.approx((1.001 ** 21 - 1) * 100)
    assert zev.loc["ALL", "Time_%"] == 100
    cev = study.crossing_evidence(p, price)
    assert list(cev["Times"]) == [3, 3, 3, 3]
    assert cev.loc["OS_IN", "Last"] == p.index[40 + 2 * 90]


def test_recent_crossings():
    zones = ["NEUTRAL"] * 30 + ["OVERSOLD"] * 4 + ["NEUTRAL"] * 2
    rec = study.recent_crossings(panel_with(zones))
    assert rec == [("OS_OUT", 1), ("OS_IN", 5)]


@pytest.mark.parametrize("up,avg,label", [
    (70, 2.5, "FAVOURABLE"),     # both lean better
    (64, 2.6, "FAVOURABLE"),     # only the average leans, by a lot
    (64, 1.7, "NORMAL"),         # only the average leans, not by enough
    (66, 1.2, "NORMAL"),         # neither leans
    (55, 0.4, "UNFAVOURABLE"),   # both lean worse
    (62, -0.6, "UNFAVOURABLE"),  # only the average leans, by a lot
    (80, 1.0, "FAVOURABLE"),     # only the hit rate leans, by a lot (+18 pts)
    (33, 0.7, "UNFAVOURABLE"),   # the Dow case: hit rate -29 pts, average just inside the band
    (75, 0.3, "MIXED"),          # rises more often, but by less
    (52, 2.0, "MIXED"),          # rises less often, but by more
])
def test_judge(up, avg, label):
    base = pd.Series({"Up_1M_%": 62.0, "Avg_1M_%": 1.0})
    assert study.judge(pd.Series({"Up_1M_%": up, "Avg_1M_%": avg}), base) == label


@pytest.mark.parametrize("episodes,sessions,ok", [(5, 20, True), (4, 60, False), (12, 19, False), (5, 9, False)])
def test_enough_for_zones(episodes, sessions, ok):
    assert study.enough(pd.Series({"Episodes": episodes, "N_1M": sessions})) is ok


def test_enough_for_crossings():
    assert study.enough(pd.Series({"N_1M": study.MIN_EVENTS}), "crossing")
    assert not study.enough(pd.Series({"N_1M": study.MIN_EVENTS - 1}), "crossing")


def test_too_few_sessions_is_too_few_even_with_enough_episodes():
    """The Dow case: 5 episodes but only 9 sessions with a month of follow-through."""
    zev = pd.DataFrame({"Time_%": [1.4, 100.0], "Sessions": [11, 808], "Episodes": [5, np.nan],
                        "Up_1M_%": [33.3, 70.5], "Avg_1M_%": [0.7, 1.2], "N_1M": [9, 787]},
                       index=["OVERSOLD", "ALL"])
    v = study.verdict(zev, "OVERSOLD", "DOW", pd.Timestamp("2023-09-01"))
    assert v.label == "TOO FEW CASES"
    assert "in 5 separate episodes, covering 9 sessions" in v.sentence and "33%" not in v.sentence
    assert "at least 20 sessions with a month of follow-through, so" in v.sentence
    assert "at least 5 separate episodes" not in v.sentence        # episodes were enough; name only the shortfall


def test_verdict_text():
    zones = (["NEUTRAL"] * 40 + ["OVERSOLD"] * 5) * 6 + ["NEUTRAL"] * 40   # 6 episodes, 30 sessions
    p = panel_with(zones)
    rng = np.random.default_rng(0)
    price = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, len(p)))), index=p.index)
    zev = study.zone_evidence(p, price)
    v = study.verdict(zev, "OVERSOLD", "TEST", p.index[0])
    assert v.sentence.startswith("Since Jan 2024, breadth has been oversold in 6 separate episodes")
    assert "an oversold session" in v.sentence
    few = study.verdict(zev, "OVERBOUGHT", "TEST", p.index[0])
    assert few.label == "TOO FEW CASES" and "in 0 separate episodes" in few.sentence
    assert "at least 5 separate episodes and 20 sessions" in few.sentence
