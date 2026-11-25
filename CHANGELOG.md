# Changelog

All notable changes to **Vyāpti** are documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

---

## [3.4.5] — 2026-11-25 — *Text keeps its size on an iPhone*
### Fixed
- **Text keeps its size on an iPhone.** iOS Safari enlarges the text of a block it judges too wide to read
  ("text autosizing"): a table that scrolls sideways with long lines in it was drawn with its prose
  columns, and their headers, at twice the size of the rest (found on Nivesa's Audit Trail). The page and
  every table's own iframe now keep the type scale as written (the shared fidelity block, and the table iframe's stylesheet).

---

## [3.4.4] — 2026-11-24 — *Help icons on Paper*
### Fixed
- **Help icons show on Paper.** A widget's (?) is a ring that Streamlit strokes with its own colour, near-white at
  60% from its static dark base, whatever colour the icon is given: on Paper the rail's hints beside Judge against and As of all but vanished.
  The family's fidelity block now makes the stroke follow the colour, the quiet ink, brighter on hover.

---

## [3.4.3] — 2026-11-24 — *The family's tab icon*
### Fixed
- **The browser tab carries the family's mark.** The tab showed Breadth's own line-only glyph, in a
  different blue and weight, while every other member shows Tattva's cobalt ring-and-line icon; it
  now uses the same bytes as theirs, so the family's tabs read as one set.

---

## [3.4.2] — 2026-11-23 — *The heatmap's hover*
### Fixed
- **The sector heatmap's hover says what the cell is.** It printed "%{customdata}": the value was
  handed to Plotly as a grid of numbers to place in the template, and under the family's unified
  hover a heatmap leaves that placeholder unresolved and prints it as text. Each cell's label is now
  written in Python ("0.478 · neutral", the reading and its zone) and the tooltip is one cell's
  (sector, week, Rel Breadth), not a unified box that repeated the week above it. Empty cells show
  no tooltip, and the time-series spike line no longer crosses the grid.

---

## [3.4.1] — 2026-11-23 — *The pages survive a restart*
### Fixed
- **A page link never goes dead.** Before a run there is nothing for the pages to show, and the
  app returned before registering them at all. A session that started on a page's address, or
  restarted under an open one (Streamlit Cloud reboots the app on every push to main, and wakes a
  sleeping app the same way), kept the old page links on screen for pages it had never
  registered: the next click showed the landing page, the address stayed where it was, and every
  link in the rail did nothing until the next run. The pages are now registered on every run,
  hidden before an analysis and each showing the landing page (or a failed run's notice), so every
  address resolves, the stale links go, and Run analysis returns the reader to the page they were on.

---

## [3.4.0] — 2026-11-23 — *Tables, the command bar, and every width*
### Changed
- **The Method page is the family's method panel.** Its four specifications (Counting, The
  Oscillators, Reads, The Record) were set in the data table, which never wraps: rules ran past
  the panel at 1440px (the Record table needed 1,342px of a 1,134px panel) and were cut mid-word on
  a phone. They are now Nishkarsh's System-page panels: a header band counting the rules, the term
  on the left, the rule as wrapping prose in the reading face, stacked under 640px. Each
  oscillator's role sits under its name.
- **The command bar holds short readouts.** It carried a sentence ("turned overbought 1d ago")
  under a long label ("Relative Breadth"), which outgrew its cell, put the bar on two rows at 1024px
  and three at 834px, and scattered its separators. It now reads Rel Breadth · Record · In zone
  (sessions the zone has held) · Window · As of, like every member's bar: one row at 1440px, a tidy
  second row below it. The Crossing Log keeps the history the sentence carried.
- **Daily Breadth fits its panel.** Twelve columns needed 1,190px of a 1,134px panel, so the last
  was cut. The screen uses the app's own short names (Rel Breadth, Rel A/D), states coverage as a
  percentage, shows ratios to two places and breadth to three (it mixed three and four), signs
  momentum, and gives the A/D line the same minus. The CSV keeps every column raw.
- **Every change is signed.** The Crossing Log, the Record's averages and episodes, the sector
  table and the constituents now show +3.63 and −2.71 rather than 3.63 and -2.71, so a column of
  moves reads the same as the rest of the family's.
- The Crossing Log says "Turned overbought", not "Breadth turned overbought" on every row; tables
  name Relative Breadth "Rel Breadth" as the bar and the axes do; chart axes and legend read A/D
  Ratio and A/D Line; the heatmap's scale is titled Rel Breadth, not "RB".
### Fixed
- **The Reading stands as a pair.** Its two cards were asked for with a wider gap than the family's
  two-column rule allows, so the second wrapped under the first and half the page stood empty. They
  sit side by side, at one height.
- **The window control keeps its choice on every page.** It held the choice in its own widget
  state, which Streamlit drops on a page that does not draw it: reaching Sectors from Record showed
  the control with nothing selected. The choice now lives in one session key that each page's
  control starts from and writes back, and clicking the chosen window cannot clear it.
- **The Constituents filter keeps a control's width** instead of spanning the page above its table.
### Checked
- Every page in Paper and Slate at 1440, 1280, 1024, 834 and 390px: nothing wider than the page,
  the family fidelity scan clean but for the family's scrolling-rail rule, type on the family's nine
  tiers in its two faces, and the family's spacing between every block.

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
