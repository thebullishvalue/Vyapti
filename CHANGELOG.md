# Changelog

All notable changes to **Vyāpti** are documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

---

## [3.3.0] — 2026-11-22 — *Into the family*
### Added
- **The family console.** `logger_config.py` is the console every member of the Pragyam family
  shares, byte for byte. A run now writes its trace to the terminal: the request (market, index,
  as-of date, record length), each stage as a numbered, timed step, a result card (as of, the
  universe and how much of it priced, history, zone, direction, the record's verdict, sectors, the
  last crossing), the page's notices, and the closing line with its time, warnings and errors.
  Before, a run printed nothing. A run served from the session's store is a replay and prints
  nothing; third-party output (yfinance, Python warnings) is routed into the run as dimmed lines
  instead of raw stderr; the masthead prints once per process.
- **Every stage on the progress card.** `build_analysis` takes an optional `progress(pct, key)`
  hook, and the card now walks all four phases: Resolving Constituents (Constituents), Downloading
  Prices (Price Data), Computing the Oscillators (Breadth Engine), Measuring the Record and Reading
  the Sectors (Record & Sectors), then Analysis Complete. Before, the last phase was only ever the
  100% frame, and the oscillators, record and sectors were one undivided step.
### Fixed
- **The rail's date input and calendar follow the appearance.** The stylesheet came from
  Arthagati, which has no date input, so only the inner field was styled: in Paper the field kept a
  near-black frame from Streamlit's static dark base, and the calendar opened near-black on a white
  page. The field is now the family's input well, the date reads in the data face, and the calendar
  is painted from the app's own tokens, weekday row and chosen-day disc included.
- **"Overbought is common here" is a note, not a warning.** The Read card drew it in the short
  colour (the line Arthagati uses for what argues against its call), while overbought is drawn in
  neutral ink everywhere else, because it has no record of mattering. It now reads in neutral ink;
  the red line is kept for a real risk ("oversold readings can deepen").
- **The landing page's engine panels have one-line headers.** "Relative Breadth" and "Direction &
  Momentum" with their kickers wrapped to two lines at 1440px and 1280px, so the three header bands
  stood at different heights. The panels are now Breadth · Direction · Record, each kicker in the
  same form (Claim · Confirmation · Check), one line at both widths, as in the rest of the family.
### Docs
- The README in the family layout, the detail in `docs/GUIDE.md`, the family's proprietary
  `LICENSE`, the family `.gitignore`, and this changelog, which takes over the release history the
  README carried.

---

## [3.2.1] — 2026-11-22 — *Verdict logic*
### Changed
- One evidence threshold used everywhere: episodes *and* sessions for zones, occurrences for
  crossings.
- A large hit-rate gap counts on its own.
- A MIXED verdict when the hit rate and the average move disagree.
- "Too few" names its actual shortfall.

---

## [3.2.0] — 2026-11-22 — *Vyāpti*
### Changed
- Renamed Market Breadth → Vyāpti and moved to this repository. Development up to here happened in
  `thebullishvalue/Breadth`; its full history is preserved in this one.

---

## [3.1.0] — 2026-11-22 — *The family interface*
### Changed
- Adopted the shared UI layer of Tattva, Arthagati and Pragyam: the Graphite design system with
  Paper/Slate appearances, tape / command bar / notice rail shell, `st.navigation` pages in house
  reading order, Tattva's read card, panel-anchored chart windows, the institutional table, and the
  family landing page.

---

## [3.0.0] — 2026-11-22 — *The Aarambh oscillators*
### Changed
- Rebuilt around the Aarambh oscillators. The zone is the headline; direction, momentum and the
  A/D-line trend support it.
- Evidence uses only real-time information and is sized by episode.
- A plain-language reading with "what would change it" replaces the indicator dashboard.
- Sectors are read with the same oscillator.
- An as-of date allows historical replay.

---

## [2.0.0] — 2026-11-22 — *Institutional indicator set*
### Added
- The institutional indicator set (superseded in 3.0.0; see the audit of v2.0 in the
  [guide](docs/GUIDE.md#why-it-is-built-this-way)).

---

## [1.9.0] — *Correctness audit*
### Fixed
- Correctness audit.
