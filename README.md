<div align="center">

# VYAPTI

**व्याप्ति** · *pervasion*

Market Breadth · Relative Breadth · Custom Breadth · A/D Line

[![Version](https://img.shields.io/badge/version-3.4.2-2B5FD9)](CHANGELOG.md) [![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](requirements.txt) [![Streamlit](https://img.shields.io/badge/streamlit-1.52.2-FF4B4B)](requirements.txt) [![License](https://img.shields.io/badge/license-proprietary-6B7280)](LICENSE) [![Pragyam Family](https://img.shields.io/badge/pragyam-family-0F1217)](#the-pragyam-family)

</div>

> One oscillator says where breadth stands, two more say which way it is moving, and the index's
> own history says whether that reading has ever mattered.

## Overview

*Vyāpti* means pervasion: how far something extends through the whole. Breadth measures exactly that, namely how far a move has spread through an index's members. In Nyāya logic, vyāpti is also the invariable relation that licenses an inference from evidence, which is the system's other half: the record that says whether a reading has ever meant anything before you lean on it.

Reads an index's breadth cycle with the Aarambh oscillators and answers three questions, in this order:

1. **Where is breadth?** Oversold, neutral or overbought, from the Relative Breadth oscillator.
2. **Which way is it moving?** Custom Breadth against Relative Breadth, confirmed or not by the Relative A/D Ratio.
3. **What has that meant?** What the index did next, every previous time breadth was here, compared with any other month.

The page then says what would change the reading, how far away that is in oscillator units, and what happened the previous times it did.

Built with Streamlit and Plotly. Prices from Yahoo Finance; constituents from NSE and Wikipedia.

## What It Does

**Pages.** Each follows the house reading order: TRUST → ANCHOR → STATE → DETAIL → EVENTS.

| Group | Page | Contents |
|---|---|---|
| Engine | **Breadth Engine** (leads) | The Read (state, record, five evidence rows) · Breadth Oscillators (Relative & Custom Breadth with the index on the second axis, Relative A/D Ratio, A/D ratio, A/D line) · Window Statistics · The Reading · Crossing Log |
| Engine | Record | Zone Record cards · By Zone · By Crossing · Oversold Episodes |
| Engine | Sectors | Sector Zones · weekly sector heatmap · Sector Readings · Constituents |
| System | Data | Coverage · Daily Breadth with CSV export |
| System | Method | Counting · The Oscillators · Reads · The Record — rendered from the engine's own constants |

Every page opens on the same shell: a ticker tape of the index and every sector's equal-weighted
level, a command bar with the instrument, zone, Rel Breadth, record, sessions in the zone and as-of date, and a
notice rail for caveats. The [guide](docs/GUIDE.md#the-interface) covers the shell, the rail and
the Read card in full.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py                                  # dashboard
python cli.py --index "NIFTY 500"                     # the same reading in the terminal
python cli.py --universe "US Indexes" --index "S&P 500" --years 10 --json --csv sp500.csv
```

Python 3.10+.

### Tests

```bash
pip install -r requirements-dev.txt
ruff check .
pytest -q
```

CI (GitHub Actions) runs lint and tests on Python 3.10 and 3.13 on every push.

## Project Structure

```
app.py              shell: rail, run, tape, command bar, notice rail, navigation, footer
config.py           product identity, chart windows, record options
cli.py              the same reading as text or JSON, optional CSV
logger_config.py    the family console (shared byte for byte with every member)
breadth/            the engine, no UI: indicators, study (the record), narrative, pipeline,
                    universe (constituents, sectors, tickers), data (Yahoo download)
ui/                 the family's UI layer (theme.css, theme.py, components.py, format.py),
                    verdict.py (the Read card's content), charts.py, tabs/ (one per page)
tests/              74 offline tests (network mocked, synthetic market generator)
docs/               the guide
```

## Documentation

| Document | What it covers |
|---|---|
| [Guide](docs/GUIDE.md) | The interface, the oscillators, how the record is worked out, why it is built this way, universes, the Aarambh spreadsheet correspondence |
| [Changelog](CHANGELOG.md) | Every release, newest first |

## The Pragyam Family

Eleven Streamlit applications built on one design system and one set of components, so a
panel, a table, a chart or a number reads the same in each.

| Product | What it is |
|---|---|
| [**Tattva**](https://github.com/thebullishvalue/Tattva) | Cross-asset fair value, with a call only where its own record supports one |
| [**Nishkarsh**](https://github.com/thebullishvalue/Nishkarsh) | Nifty 50 inference: a top-down forecast and bottom-up breadth, read as one |
| [**Arthagati**](https://github.com/thebullishvalue/Arthagati) | Valuation-anchored market sentiment, tested on data it never saw |
| **Vyapti** · *this repository* | Market breadth: where participation stands, which way it moves, and what that has meant |
| [**Pragyam**](https://github.com/thebullishvalue/Pragyam) | Portfolio curation that spreads risk rather than predicting returns |
| [**Sanket**](https://github.com/thebullishvalue/Sanket) | A market signal screener: what fired, what is about to, and whether it has paid |
| [**Vaaydo**](https://github.com/thebullishvalue/Vaaydo) | An F&O trade screener on option positioning, with futures tickets |
| [**Anumaan**](https://github.com/thebullishvalue/Indicator) | A chart terminal: calibrated risk, stops and exposure, audited on the chart it is on |
| [**Nivesa**](https://github.com/thebullishvalue/Nivesa) | A bond portfolio ledger: cost, yield, duration and cashflows across accounts |
| [**Samhita**](https://github.com/thebullishvalue/Samhita) | A portfolio tracker: live prices, performance and risk against the benchmark |
| [**Swing**](https://github.com/thebullishvalue/Swing) | A portfolio tracker for the swing book, on the same engine as Samhita |

## License

Proprietary. © 2026 @thebullishvalue. All rights reserved. The source is visible here
for reference only: viewing it grants no right to use, copy, modify or distribute it.
See [LICENSE](LICENSE).

## Disclaimer

Vyāpti is a research and decision-support tool, not investment advice. Nothing it shows is
a recommendation to buy or sell any security, and past or measured results do not guarantee
future ones. Every decision made with it is your own.

---

<div align="center"><sub>© 2026 @thebullishvalue · Part of the Pragyam product family</sub></div>
