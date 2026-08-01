# Changelog

All notable changes to this project are documented in this file. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses phase-based
versioning until a first stable release (see [CLAUDE.md](CLAUDE.md) for the phase-gated
delivery workflow).

## [Unreleased]

### Phase 264 - NAS Live Verification of Phase 263 (draft)

Ops evidence gate after Phase 263 ingest primary tip diagnostic. See
[docs/architecture/decisions/0265-phase-264-nas-live-verify-phase-263.md](docs/architecture/decisions/0265-phase-264-nas-live-verify-phase-263.md).

### Phase 263 - Ingest Primary Tip Diagnostic (draft)

Surface primary tip beside winning ingest tip when dual-source tips diverge. See
[docs/architecture/decisions/0264-phase-263-ingest-primary-tip-diagnostic.md](docs/architecture/decisions/0264-phase-263-ingest-primary-tip-diagnostic.md).

### Phase 262 - NAS Live Verification of Phase 261

Ops evidence gate after Phase 261 tip fix. Live verify passed 2026-07-31 (``d092cf2``;
AAPL tip advanced ``2026-07-29`` → ``2026-07-30``, lag ``2`` → ``1``, tip source
``polygon``). See
[docs/architecture/decisions/0263-phase-262-nas-live-verify-phase-261.md](docs/architecture/decisions/0263-phase-262-nas-live-verify-phase-261.md).

#### Added

- ADR-0263: live tip refresh evidence for dual-source / cross-source fill fix.

#### Explicitly out of scope

Inventing closes, default-on calibration, orders.

### Phase 261 - Provider Tip Ahead of Store Tip

Dual-source ingest tip catch-up and cross-source fill that extends a stale primary tip so
post-ingest research can advance evidence tip without inventing closes. See
[docs/architecture/decisions/0262-phase-261-provider-tip-ahead-of-store.md](docs/architecture/decisions/0262-phase-261-provider-tip-ahead-of-store.md).

#### Changed

- Ingest refreshes primary and secondary independently when secondary is configured;
  expose ``latest_trading_date_source``.
- Cross-source component fill unions session dates even when primary already has 20 bars.

#### Explicitly out of scope

Inventing primary closes from secondary, calibration default-on, orders.

### Phase 260 - NAS Live Verification of Phase 259

Ops evidence gate after Phase 259 ingest-run latest trading date. Live verify passed
2026-07-31 (``f60cb0b``; AAPL ``latest_trading_date=2026-07-30`` with store tip
``2026-07-29``). See
[docs/architecture/decisions/0261-phase-260-nas-live-verify-phase-259.md](docs/architecture/decisions/0261-phase-260-nas-live-verify-phase-259.md).

#### Added

- ADR-0261: live verify logs ingest ``latest_trading_date`` (checklist item 124).

#### Explicitly out of scope

Inventing closes, default-on calibration, orders.

### Phase 259 - Ingest Run Latest Trading Date

Expose max trading date seen in an ingest fetch so operators can compare provider tip vs
store tip when ``stored=0``. See
[docs/architecture/decisions/0260-phase-259-ingest-run-latest-trading-date.md](docs/architecture/decisions/0260-phase-259-ingest-run-latest-trading-date.md).

#### Added

- ``latest_trading_date`` on ingest symbol results (domain + API + console).
- NAS verify logs provider tip beside store tip (checklist item 124).

#### Explicitly out of scope

New evidence-summary fields, inventing closes, default-on calibration, orders.

### Phase 258 - NAS Live Verification of Phase 257

Ops evidence gate after Phase 257 on-demand ingest tip refresh. Live verify passed
2026-07-31 (``c84524f``; AAPL ingest ``stored=0 skipped_existing=501``;
``pre_lag=2 post_lag=2`` tip ``2026-07-29`` unchanged OK). See
[docs/architecture/decisions/0259-phase-258-nas-live-verify-phase-257.md](docs/architecture/decisions/0259-phase-258-nas-live-verify-phase-257.md).

#### Added

- ADR-0259: live verify checklist item 124 for ingest tip refresh.

#### Explicitly out of scope

New evidence-summary fields, inventing closes, default-on calibration, orders.

### Phase 257 - On-Demand Ingest Tip Refresh

Exercise authenticated ingest so the stored tip / calendar lag can advance when providers
have newer closes. See
[docs/architecture/decisions/0258-phase-257-on-demand-ingest-tip-refresh.md](docs/architecture/decisions/0258-phase-257-on-demand-ingest-tip-refresh.md).

#### Added

- NAS verify checklist item 124: authenticated ``POST /market-data/ingest`` + re-read
  evidence-summary lag/tip (unchanged OK; never invent).
- Auth gate expects unauthenticated ingest POST → 401.

#### Explicitly out of scope

New evidence-summary fields, new providers, inventing closes, default-on calibration,
orders, UI modularization.

### Phase 256 - NAS Live Verification of Phase 255

Ops evidence gate after Phase 255 stored-bar calendar lag diagnostic. Live verify passed
2026-07-31 (``9259c16``; AAPL ``stored_bar_calendar_lag_trading_days=2``). See
[docs/architecture/decisions/0257-phase-256-nas-live-verify-phase-255.md](docs/architecture/decisions/0257-phase-256-nas-live-verify-phase-255.md).

#### Added

- ADR-0257: live verify requires backend+frontend recreate for Phase 255; checklist item 123.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 255 - Evidence Summary Stored Bar Calendar Lag

Exchange sessions the label-source bar tip lags behind the prior completed session
(ingest freshness vs calendar; not unlock shortfall). See
[docs/architecture/decisions/0256-phase-255-evidence-summary-stored-bar-calendar-lag.md](docs/architecture/decisions/0256-phase-255-evidence-summary-stored-bar-calendar-lag.md).

#### Added

- ``stored_bar_calendar_lag_trading_days`` on evidence summary (+ export).
- Domain ``stored_bar_calendar_lag_trading_days`` / ``snapshot_label_source_max_bar_date``.
- Console ``data-testid="evidence-stored-bar-calendar-lag-trading-days"``.
- NAS verify checklist item 123 for Phase 256.

#### Explicitly out of scope

UI modularization, inventing closes, default-on calibration, orders, redundant tip dates.

### Phase 254 - NAS Live Verification of Phase 253

Ops evidence gate after Phase 253 min-horizon required label end-date diagnostic. Live verify
passed 2026-07-31 (``c25e8b6``; AAPL
``latest_assessment_min_horizon_required_label_end_date=2026-08-05``). See
[docs/architecture/decisions/0255-phase-254-nas-live-verify-phase-253.md](docs/architecture/decisions/0255-phase-254-nas-live-verify-phase-253.md).

#### Added

- ADR-0255: live verify requires backend+frontend recreate for Phase 253; checklist item 122.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 253 - Evidence Summary Min-Horizon Required Label End Date

Calendar trading date that unlocks the earliest forward horizon (companion to min shortfall).
See
[docs/architecture/decisions/0254-phase-253-evidence-summary-min-horizon-required-label-end-date.md](docs/architecture/decisions/0254-phase-253-evidence-summary-min-horizon-required-label-end-date.md).

#### Added

- ``latest_assessment_min_horizon_required_label_end_date`` on evidence summary (+ export).
- Reuses ``snapshot_required_label_end_date`` with ``horizons=(min(...),)``.
- Console ``data-testid="evidence-latest-assessment-min-horizon-required-label-end-date"``.
- NAS verify checklist item 122 for Phase 254.

#### Explicitly out of scope

UI modularization, inventing closes, default-on calibration, orders, multi-horizon maps.

### Phase 252 - NAS Live Verification of Phase 251

Ops evidence gate after Phase 251 min-horizon forward-bar shortfall diagnostic. Live verify
passed 2026-07-31 (``6858194``; AAPL
``latest_assessment_min_horizon_forward_bar_shortfall=5``). See
[docs/architecture/decisions/0253-phase-252-nas-live-verify-phase-251.md](docs/architecture/decisions/0253-phase-252-nas-live-verify-phase-251.md).

#### Added

- ADR-0253: live verify requires backend+frontend recreate for Phase 251; checklist item 121.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 251 - Evidence Summary Min-Horizon Forward Bar Shortfall

Sessions still needed before the earliest forward horizon becomes labelable (partial unlock
ahead of max). See
[docs/architecture/decisions/0252-phase-251-evidence-summary-min-horizon-forward-bar-shortfall.md](docs/architecture/decisions/0252-phase-251-evidence-summary-min-horizon-forward-bar-shortfall.md).

#### Added

- ``latest_assessment_min_horizon_forward_bar_shortfall`` on evidence summary (+ export).
- Reuses ``snapshot_forward_bar_shortfall`` with ``horizons=(min(...),)``.
- Console ``data-testid="evidence-latest-assessment-min-horizon-forward-bar-shortfall"``.
- NAS verify checklist item 121 for Phase 252.

#### Explicitly out of scope

UI modularization, inventing closes, default-on calibration, orders, multi-horizon maps.

### Phase 250 - NAS Live Verification of Phase 249

Ops evidence gate after Phase 249 last-available label-bar date diagnostic. Live verify
passed 2026-07-31 (``8c35d1d``; AAPL
``latest_assessment_last_available_label_bar_date=2026-07-29``). See
[docs/architecture/decisions/0251-phase-250-nas-live-verify-phase-249.md](docs/architecture/decisions/0251-phase-250-nas-live-verify-phase-249.md).

#### Added

- ADR-0251: live verify requires backend+frontend recreate for Phase 249; checklist item 120.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 249 - Evidence Summary Latest Last Available Label Bar Date

How far stored label-source bars have advanced toward the required unlock end (progress
beside shortfall). See
[docs/architecture/decisions/0250-phase-249-evidence-summary-latest-last-available-label-bar-date.md](docs/architecture/decisions/0250-phase-249-evidence-summary-latest-last-available-label-bar-date.md).

#### Added

- ``latest_assessment_last_available_label_bar_date`` on evidence summary (+ export): max
  stored close on resolved label source with day >= as_of; null when N/A.
- Domain ``snapshot_last_available_label_bar_date``; console
  ``data-testid="evidence-latest-assessment-last-available-label-bar-date"``.
- NAS verify checklist item 120 for Phase 250.

#### Explicitly out of scope

UI modularization, inventing future closes, default-on calibration, orders.

### Phase 248 - NAS Live Verification of Phase 247

Ops evidence gate after Phase 247 required label end-date diagnostic. Live verify passed
2026-07-31 (``3fe7edf``; AAPL ``latest_assessment_required_label_end_date=2026-08-26``). See
[docs/architecture/decisions/0249-phase-248-nas-live-verify-phase-247.md](docs/architecture/decisions/0249-phase-248-nas-live-verify-phase-247.md).

#### Added

- ADR-0249: live verify requires backend+frontend recreate for Phase 247; checklist item 119.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 247 - Evidence Summary Latest Required Label End Date

Calendar trading date that unlocks max-horizon labeling (companion to shortfall). See
[docs/architecture/decisions/0248-phase-247-evidence-summary-latest-required-label-end-date.md](docs/architecture/decisions/0248-phase-247-evidence-summary-latest-required-label-end-date.md).

#### Added

- ``latest_assessment_required_label_end_date`` on evidence summary (+ export): calendar
  projection from as_of for max forward horizon; null when N/A.
- Domain ``snapshot_required_label_end_date``; console
  ``data-testid="evidence-latest-assessment-required-label-end-date"``.
- NAS verify checklist item 119 for Phase 248.

#### Explicitly out of scope

UI modularization, inventing future closes, default-on calibration, orders.

### Phase 246 - NAS Live Verification of Phase 245

Ops evidence gate after Phase 245 latest forward-bar shortfall diagnostic. Live verify passed
2026-07-31 (``cbe7032``; AAPL ``latest_assessment_forward_bar_shortfall=20``). See
[docs/architecture/decisions/0247-phase-246-nas-live-verify-phase-245.md](docs/architecture/decisions/0247-phase-246-nas-live-verify-phase-245.md).

#### Added

- ADR-0247: live verify requires backend+frontend recreate for Phase 245; checklist item 118.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 245 - Evidence Summary Latest Label Forward Bar Shortfall

How many additional forward trading sessions are needed before latest becomes label-ready
(backfill unlock signal). See
[docs/architecture/decisions/0246-phase-245-evidence-summary-latest-forward-bar-shortfall.md](docs/architecture/decisions/0246-phase-245-evidence-summary-latest-forward-bar-shortfall.md).

#### Added

- ``latest_assessment_forward_bar_shortfall`` on evidence summary (+ export): sessions still
  needed for max forward horizon; ``0`` when ready; null when N/A (no assessment /
  ``no_as_of_bar``).
- Domain ``snapshot_forward_bar_shortfall``; console
  ``data-testid="evidence-latest-assessment-forward-bar-shortfall"``.
- NAS verify checklist item 118 for Phase 246.

#### Explicitly out of scope

UI modularization, inventing ready targets, default-on calibration, orders.

### Phase 244 - NAS Live Verification of Phase 243

Ops evidence gate after Phase 243 most-recent-unlabeled as_of diagnostic. Live verify passed
2026-07-31 (``22a8339``; AAPL ``most_recent_unlabeled_as_of_trading_date=2026-07-29``). See
[docs/architecture/decisions/0245-phase-244-nas-live-verify-phase-243.md](docs/architecture/decisions/0245-phase-244-nas-live-verify-phase-243.md).

#### Added

- ADR-0245: live verify requires backend+frontend recreate for Phase 243; checklist item 117.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 243 - Evidence Summary Most Recent Unlabeled As-Of

as_of_trading_date of the newest unlabeled assessment (tip freshness beside tip id). See
[docs/architecture/decisions/0244-phase-243-evidence-summary-most-recent-unlabeled-as-of.md](docs/architecture/decisions/0244-phase-243-evidence-summary-most-recent-unlabeled-as-of.md).

#### Added

- ``most_recent_unlabeled_as_of_trading_date`` on evidence summary (+ export).
- Console ``data-testid="evidence-most-recent-unlabeled-as-of-trading-date"``.
- NAS verify checklist item 117 for Phase 244.

#### Explicitly out of scope

UI modularization, inventing label-ready targets, default-on calibration, orders.

### Phase 242 - NAS Live Verification of Phase 241

Ops evidence gate after Phase 241 most-recent-unlabeled assessment id diagnostic. Live verify
passed 2026-07-31 (``c7d5f7b``; AAPL ``most_recent_unlabeled_assessment_id=126``). See
[docs/architecture/decisions/0243-phase-242-nas-live-verify-phase-241.md](docs/architecture/decisions/0243-phase-242-nas-live-verify-phase-241.md).

#### Added

- ADR-0243: live verify requires backend+frontend recreate for Phase 241; checklist item 116.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 241 - Evidence Summary Most Recent Unlabeled Assessment Id

Newest unlabeled assessment snapshot id in the scan (drill-down target when ready count is
zero). See
[docs/architecture/decisions/0242-phase-241-evidence-summary-most-recent-unlabeled-assessment-id.md](docs/architecture/decisions/0242-phase-241-evidence-summary-most-recent-unlabeled-assessment-id.md).

#### Added

- ``most_recent_unlabeled_assessment_id`` on evidence summary (+ export).
- Console ``data-testid="evidence-most-recent-unlabeled-assessment-id"``.
- NAS verify checklist item 116 for Phase 242.

#### Explicitly out of scope

UI modularization, inventing label-ready targets, default-on calibration, orders.

### Phase 240 - NAS Live Verification of Phase 239

Ops evidence gate after Phase 239 unlabeled label-ready count diagnostic. Live verify passed
2026-07-31 (``b9e5033``; AAPL ``scan_unlabeled_label_ready_count=0`` with
``unlabeled_assessment_count=3``). See
[docs/architecture/decisions/0241-phase-240-nas-live-verify-phase-239.md](docs/architecture/decisions/0241-phase-240-nas-live-verify-phase-239.md).

#### Added

- ADR-0241: live verify requires backend+frontend recreate for Phase 239; checklist item 115.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 239 - Evidence Summary Scan Unlabeled Label-Ready Count

Count of unlabeled and label-ready assessments in the scan (explicit backfill-candidate
cardinality). See
[docs/architecture/decisions/0240-phase-239-evidence-summary-scan-unlabeled-label-ready-count.md](docs/architecture/decisions/0240-phase-239-evidence-summary-scan-unlabeled-label-ready-count.md).

#### Added

- ``scan_unlabeled_label_ready_count`` on evidence summary (+ export).
- ``OutcomeLabelService.scan_label_diagnostics`` returns unlabeled+ready count (one bar load).
- Console ``data-testid="evidence-scan-unlabeled-label-ready-count"``.
- NAS verify checklist item 115 for Phase 240.

#### Explicitly out of scope

UI modularization, redundant nested lifts, default-on calibration, orders.

### Phase 238 - NAS Live Verification of Phase 237

Ops evidence gate after Phase 237 unlabeled+labelable as_of diagnostic. Live verify passed
2026-07-31 (``c76b75c``; AAPL ``most_recent_unlabeled_labelable_as_of_trading_date=null`` with
``unlabeled_assessment_count=3``). See
[docs/architecture/decisions/0239-phase-238-nas-live-verify-phase-237.md](docs/architecture/decisions/0239-phase-238-nas-live-verify-phase-237.md).

#### Added

- ADR-0239: live verify requires backend+frontend recreate for Phase 237; checklist item 114.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 237 - Evidence Summary Most Recent Unlabeled Labelable As-Of

Newest as_of that is both unlabeled and label-ready (backfill next-target diagnostic). See
[docs/architecture/decisions/0238-phase-237-evidence-summary-most-recent-unlabeled-labelable-as-of.md](docs/architecture/decisions/0238-phase-237-evidence-summary-most-recent-unlabeled-labelable-as-of.md).

#### Added

- ``most_recent_unlabeled_labelable_as_of_trading_date`` on evidence summary (+ export).
- ``OutcomeLabelService.scan_label_diagnostics`` returns unlabeled+labelable as_of (one bar load).
- Console ``data-testid="evidence-most-recent-unlabeled-labelable-as-of-trading-date"``.
- NAS verify checklist item 114 for Phase 238.

#### Explicitly out of scope

UI modularization, redundant nested lifts, default-on calibration, orders.

### Phase 236 - NAS Live Verification of Phase 235

Ops evidence gate after Phase 235 most-recent-labelable as_of diagnostic. Live verify passed
2026-07-31 (``821aed1``; AAPL ``most_recent_labelable_as_of_trading_date=2026-02-05``). See
[docs/architecture/decisions/0237-phase-236-nas-live-verify-phase-235.md](docs/architecture/decisions/0237-phase-236-nas-live-verify-phase-235.md).

#### Added

- ADR-0237: live verify requires backend+frontend recreate for Phase 235; checklist item 113.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 235 - Evidence Summary Most Recent Labelable As-Of Trading Date

Newest assessment as_of that is label-ready with stored bars (backfill targeting diagnostic).
See
[docs/architecture/decisions/0236-phase-235-evidence-summary-most-recent-labelable-as-of-trading-date.md](docs/architecture/decisions/0236-phase-235-evidence-summary-most-recent-labelable-as-of-trading-date.md).

#### Added

- ``most_recent_labelable_as_of_trading_date`` on evidence summary (+ export).
- ``OutcomeLabelService.scan_label_diagnostics`` (one bar load for readiness + labelable as_of).
- Console ``data-testid="evidence-most-recent-labelable-as-of-trading-date"``.
- NAS verify checklist item 113 for Phase 236.

#### Explicitly out of scope

Companion assessment id, UI modularization, orders, new scoring math.

### Phase 234 - NAS Live Verification of Phase 233

Ops evidence gate after Phase 233 label block reason. Live verify passed 2026-07-31
(``bc554c7``; AAPL ``latest_assessment_label_block_reason=insufficient_forward_bars`` with
``latest_assessment_is_label_ready=False``, lag=119). See
[docs/architecture/decisions/0235-phase-234-nas-live-verify-phase-233.md](docs/architecture/decisions/0235-phase-234-nas-live-verify-phase-233.md).

#### Added

- ADR-0235: live verify requires backend+frontend recreate for Phase 233; checklist item 112.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 233 - Evidence Summary Latest Assessment Label Block Reason

Fail-closed reason code when latest assessment is not label-ready (aligned with
``OutcomeLabelReason``). See
[docs/architecture/decisions/0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md](docs/architecture/decisions/0234-phase-233-evidence-summary-latest-assessment-label-block-reason.md).

#### Added

- ``latest_assessment_label_block_reason`` on evidence summary (+ export).
- ``snapshot_label_block_reason`` + ``label_readiness_for_assessment`` domain helpers.
- Console ``data-testid="evidence-latest-assessment-label-block-reason"``.
- NAS verify checklist item 112 for Phase 234.

#### Explicitly out of scope

``already_labeled`` reason, new scoring math, orders, UI structural extracts.

### Phase 232 - NAS Live Verification of Phase 231

Ops evidence gate after Phase 231 latest-assessment label-ready diagnostic. Live verify passed
2026-07-31 (``d594387``; AAPL ``latest_assessment_is_label_ready=False`` with
``latest_assessment_id=126``, lag=119). See
[docs/architecture/decisions/0233-phase-232-nas-live-verify-phase-231.md](docs/architecture/decisions/0233-phase-232-nas-live-verify-phase-231.md).

#### Added

- ADR-0233: live verify requires backend+frontend recreate for Phase 231; checklist item 111.
- verify.ps1: print boolean ``False`` correctly (avoid PowerShell ``$false -eq ""`` trap).

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 231 - Evidence Summary Latest Assessment Is Label Ready

Boolean evidence diagnostic: whether the absolute latest assessment has stored forward bars
needed to label (reuse ``is_snapshot_label_ready``). See
[docs/architecture/decisions/0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md](docs/architecture/decisions/0232-phase-231-evidence-summary-latest-assessment-is-label-ready.md).

#### Added

- ``latest_assessment_is_label_ready`` on evidence summary (+ export); null when no assessment.
- ``OutcomeLabelService.is_assessment_label_ready`` wraps stored-bar ``is_snapshot_label_ready``.
- Console surfaces the field with ``data-testid="evidence-latest-assessment-is-label-ready"``.
- NAS verify checklist item 111 for Phase 232.

#### Explicitly out of scope

Label block reason string, new scoring math, orders, UI structural extracts.

### Phase 230 - NAS Live Verification of Phase 229

Ops evidence gate after Phase 229 scan-labeled freshness lag diagnostic. Live verify passed
2026-07-31 (``9154394``; AAPL ``scan_labeled_freshness_lag_trading_days=119`` with
``latest_as_of_trading_date=2026-07-29`` and
``most_recent_labeled_outcome_label_as_of_trading_date=2026-02-05``). See
[docs/architecture/decisions/0231-phase-230-nas-live-verify-phase-229.md](docs/architecture/decisions/0231-phase-230-nas-live-verify-phase-229.md).

#### Added

- ADR-0231: live verify requires backend+frontend recreate for Phase 229; checklist item 110.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 229 - Evidence Summary Scan-Labeled Freshness Lag

Derived evidence diagnostic: NYSE trading-day lag between latest assessment as_of and most
recent labeled outcome_label as_of. See
[docs/architecture/decisions/0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md](docs/architecture/decisions/0230-phase-229-evidence-summary-scan-labeled-freshness-lag.md).

#### Added

- ``scan_labeled_freshness_lag_trading_days`` on evidence summary (+ export); null when either
  as_of missing; exchange trading-day count via ``count_trading_days_strictly_between``.
- Console surfaces the field with ``data-testid="evidence-scan-labeled-freshness-lag-trading-days"``.
- NAS verify checklist item 110 for Phase 230.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts, redundant nested field lifts.

### Phase 228 - NAS Live Verification of Phase 227

Ops evidence gate after Phase 227 most recent labeled outcome label as-of trading date field.
Live verify passed 2026-07-31 (``285dafe``; AAPL
``most_recent_labeled_outcome_label_as_of_trading_date=2026-02-05`` with
``most_recent_labeled_outcome_label_id=82``). Closes the planned scan-labeled scalar
provenance series (Phases 213–228). See
[docs/architecture/decisions/0229-phase-228-nas-live-verify-phase-227.md](docs/architecture/decisions/0229-phase-228-nas-live-verify-phase-227.md).

#### Added

- ADR-0229: live verify requires backend+frontend recreate for Phase 227; checklist item 109.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 227 - Evidence Summary Most Recent Labeled Outcome Label As-Of Trading Date

Surface top-level ``most_recent_labeled_outcome_label_as_of_trading_date`` on evidence summary;
completes the planned scan-labeled scalar provenance series. See
[docs/architecture/decisions/0228-phase-227-evidence-summary-most-recent-labeled-outcome-label-as-of-trading-date.md](docs/architecture/decisions/0228-phase-227-evidence-summary-most-recent-labeled-outcome-label-as-of-trading-date.md).

#### Added

- ``most_recent_labeled_outcome_label_as_of_trading_date`` on evidence summary (+ export); from scan-labeled label.
- Console surfaces the field with ``data-testid="evidence-most-recent-labeled-outcome-label-as-of-trading-date"``.
- NAS verify checklist item 109 for Phase 228.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts, further redundant nested field lifts.

### Phase 226 - NAS Live Verification of Phase 225

Ops evidence gate after Phase 225 most recent labeled outcome label computed_at field. Live
verify passed 2026-07-31 (``1a4091f``; AAPL
``most_recent_labeled_outcome_label_computed_at=2026-07-30T21:25:15.962739Z`` with
``most_recent_labeled_outcome_label_id=82``). See
[docs/architecture/decisions/0227-phase-226-nas-live-verify-phase-225.md](docs/architecture/decisions/0227-phase-226-nas-live-verify-phase-225.md).

#### Added

- ADR-0227: live verify requires backend+frontend recreate for Phase 225; checklist item 108.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 225 - Evidence Summary Most Recent Labeled Outcome Label Computed At

Surface top-level ``most_recent_labeled_outcome_label_computed_at`` on evidence summary for
scan-labeled provenance. See
[docs/architecture/decisions/0226-phase-225-evidence-summary-most-recent-labeled-outcome-label-computed-at.md](docs/architecture/decisions/0226-phase-225-evidence-summary-most-recent-labeled-outcome-label-computed-at.md).

#### Added

- ``most_recent_labeled_outcome_label_computed_at`` on evidence summary (+ export); from scan-labeled label.
- Console surfaces the field with ``data-testid="evidence-most-recent-labeled-outcome-label-computed-at"``.
- NAS verify checklist item 108 for Phase 226.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 224 - NAS Live Verification of Phase 223

Ops evidence gate after Phase 223 most recent labeled outcome label bar source field. Live verify
passed 2026-07-31 (``7d73b42``; AAPL ``most_recent_labeled_outcome_label_bar_source=polygon``
with ``most_recent_labeled_outcome_label_id=82``). See
[docs/architecture/decisions/0225-phase-224-nas-live-verify-phase-223.md](docs/architecture/decisions/0225-phase-224-nas-live-verify-phase-223.md).

#### Added

- ADR-0225: live verify requires backend+frontend recreate for Phase 223; checklist item 107.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 223 - Evidence Summary Most Recent Labeled Outcome Label Bar Source

Surface top-level ``most_recent_labeled_outcome_label_bar_source`` on evidence summary for
scan-labeled provenance. See
[docs/architecture/decisions/0224-phase-223-evidence-summary-most-recent-labeled-outcome-label-bar-source.md](docs/architecture/decisions/0224-phase-223-evidence-summary-most-recent-labeled-outcome-label-bar-source.md).

#### Added

- ``most_recent_labeled_outcome_label_bar_source`` on evidence summary (+ export); from scan-labeled label.
- Console surfaces the field with ``data-testid="evidence-most-recent-labeled-outcome-label-bar-source"``.
- NAS verify checklist item 107 for Phase 224.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 222 - NAS Live Verification of Phase 221

Ops evidence gate after Phase 221 most recent labeled outcome label state field. Live verify
passed 2026-07-31 (``8a3f9a7``; AAPL ``most_recent_labeled_outcome_label_state=research_only``
with ``most_recent_labeled_outcome_label_id=82``). See
[docs/architecture/decisions/0223-phase-222-nas-live-verify-phase-221.md](docs/architecture/decisions/0223-phase-222-nas-live-verify-phase-221.md).

#### Added

- ADR-0223: live verify requires backend+frontend recreate for Phase 221; checklist item 106.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 221 - Evidence Summary Most Recent Labeled Outcome Label State

Surface top-level ``most_recent_labeled_outcome_label_state`` on evidence summary for
scan-labeled provenance. See
[docs/architecture/decisions/0222-phase-221-evidence-summary-most-recent-labeled-outcome-label-state.md](docs/architecture/decisions/0222-phase-221-evidence-summary-most-recent-labeled-outcome-label-state.md).

#### Added

- ``most_recent_labeled_outcome_label_state`` on evidence summary (+ export); from scan-labeled label.
- Console surfaces the field with ``data-testid="evidence-most-recent-labeled-outcome-label-state"``.
- NAS verify checklist item 106 for Phase 222.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 220 - NAS Live Verification of Phase 219

Ops evidence gate after Phase 219 most recent labeled outcome label schema version field. Live
verify passed 2026-07-31 (``a2b36b8``; AAPL ``most_recent_labeled_outcome_label_schema_version=1``
with ``most_recent_labeled_outcome_label_id=82``). See
[docs/architecture/decisions/0221-phase-220-nas-live-verify-phase-219.md](docs/architecture/decisions/0221-phase-220-nas-live-verify-phase-219.md).

#### Added

- ADR-0221: live verify requires backend+frontend recreate for Phase 219; checklist item 105.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 219 - Evidence Summary Most Recent Labeled Outcome Label Schema Version

Surface top-level ``most_recent_labeled_outcome_label_schema_version`` on evidence summary for
scan-labeled provenance. See
[docs/architecture/decisions/0220-phase-219-evidence-summary-most-recent-labeled-outcome-label-schema-version.md](docs/architecture/decisions/0220-phase-219-evidence-summary-most-recent-labeled-outcome-label-schema-version.md).

#### Added

- ``most_recent_labeled_outcome_label_schema_version`` on evidence summary (+ export); from scan-labeled label.
- Console surfaces the field with ``data-testid="evidence-most-recent-labeled-outcome-label-schema-version"``.
- NAS verify checklist item 105 for Phase 220.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 218 - NAS Live Verification of Phase 217

Ops evidence gate after Phase 217 most recent labeled outcome label method version field. Live
verify passed 2026-07-31 (``3219219``; AAPL ``most_recent_labeled_outcome_label_method_version=1``
with ``most_recent_labeled_outcome_label_method_id=forward_total_return_v1`` and
``most_recent_labeled_outcome_label_id=82``). See
[docs/architecture/decisions/0219-phase-218-nas-live-verify-phase-217.md](docs/architecture/decisions/0219-phase-218-nas-live-verify-phase-217.md).

#### Added

- ADR-0219: live verify requires backend+frontend recreate for Phase 217; checklist item 104.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 217 - Evidence Summary Most Recent Labeled Outcome Label Method Version

Surface top-level ``most_recent_labeled_outcome_label_method_version`` on evidence summary for
scan-labeled provenance. See
[docs/architecture/decisions/0218-phase-217-evidence-summary-most-recent-labeled-outcome-label-method-version.md](docs/architecture/decisions/0218-phase-217-evidence-summary-most-recent-labeled-outcome-label-method-version.md).

#### Added

- ``most_recent_labeled_outcome_label_method_version`` on evidence summary (+ export); from scan-labeled label.
- Console surfaces the field with ``data-testid="evidence-most-recent-labeled-outcome-label-method-version"``.
- NAS verify checklist item 104 for Phase 218.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 216 - NAS Live Verification of Phase 215

Ops evidence gate after Phase 215 most recent labeled outcome label method id field. Live verify
passed 2026-07-31 (``058f0c5``; AAPL ``most_recent_labeled_outcome_label_method_id=forward_total_return_v1``
with ``most_recent_labeled_outcome_label_id=82``). See
[docs/architecture/decisions/0217-phase-216-nas-live-verify-phase-215.md](docs/architecture/decisions/0217-phase-216-nas-live-verify-phase-215.md).

#### Added

- ADR-0217: live verify requires backend+frontend recreate for Phase 215; checklist item 103.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 215 - Evidence Summary Most Recent Labeled Outcome Label Method Id

Surface top-level ``most_recent_labeled_outcome_label_method_id`` on evidence summary for
scan-labeled provenance. See
[docs/architecture/decisions/0216-phase-215-evidence-summary-most-recent-labeled-outcome-label-method-id.md](docs/architecture/decisions/0216-phase-215-evidence-summary-most-recent-labeled-outcome-label-method-id.md).

#### Added

- ``most_recent_labeled_outcome_label_method_id`` on evidence summary (+ export); from scan-labeled label.
- Console surfaces the field with ``data-testid="evidence-most-recent-labeled-outcome-label-method-id"``.
- NAS verify checklist item 103 for Phase 216.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts, redundant nested-only access patterns.

### Phase 214 - NAS Live Verification of Phase 213

Ops evidence gate after Phase 213 most recent labeled outcome label id field. Live verify
passed 2026-07-31 (``a723fed``; AAPL ``most_recent_labeled_outcome_label_id=82`` with
``most_recent_labeled_assessment_id=125``; ``latest_outcome_label_id=null``). See
[docs/architecture/decisions/0215-phase-214-nas-live-verify-phase-213.md](docs/architecture/decisions/0215-phase-214-nas-live-verify-phase-213.md).

#### Added

- ADR-0215: live verify requires backend+frontend recreate for Phase 213; checklist item 102.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 213 - Evidence Summary Most Recent Labeled Outcome Label Id

Surface top-level ``most_recent_labeled_outcome_label_id`` on evidence summary after completing
the absolute-latest ``latest_outcome_label_*`` scalar series. See
[docs/architecture/decisions/0214-phase-213-evidence-summary-most-recent-labeled-outcome-label-id.md](docs/architecture/decisions/0214-phase-213-evidence-summary-most-recent-labeled-outcome-label-id.md).

#### Added

- ``most_recent_labeled_outcome_label_id`` on evidence summary (+ export); from scan-labeled label.
- Console surfaces the field with ``data-testid="evidence-most-recent-labeled-outcome-label-id"``.
- NAS verify checklist item 102 for Phase 214.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts, redundant ``latest_outcome_label_assessment_snapshot_id``.

### Phase 212 - NAS Live Verification of Phase 211

Ops evidence gate after Phase 211 latest outcome label as-of trading date field. Live verify
passed 2026-07-31 (``d0f8bb8``; AAPL ``latest_outcome_label_as_of_trading_date=null`` — latest
unlabeled). Closes absolute-latest outcome-label scalar provenance lift. See
[docs/architecture/decisions/0213-phase-212-nas-live-verify-phase-211.md](docs/architecture/decisions/0213-phase-212-nas-live-verify-phase-211.md).

#### Added

- ADR-0213: live verify requires backend+frontend recreate for Phase 211; checklist item 101.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 211 - Evidence Summary Latest Outcome Label As-Of Trading Date

Surface top-level ``latest_outcome_label_as_of_trading_date`` on evidence summary. See
[docs/architecture/decisions/0212-phase-211-evidence-summary-latest-outcome-label-as-of-trading-date.md](docs/architecture/decisions/0212-phase-211-evidence-summary-latest-outcome-label-as-of-trading-date.md).

#### Added

- ``latest_outcome_label_as_of_trading_date`` on evidence summary (+ export); from latest_outcome_label.
- Console surfaces the field with ``data-testid="evidence-latest-outcome-label-as-of-trading-date"``.
- NAS verify checklist item 101 for Phase 212.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 210 - NAS Live Verification of Phase 209

Ops evidence gate after Phase 209 latest outcome label bar source field. Live verify passed
2026-07-31 (``2ca0311``; AAPL ``latest_outcome_label_bar_source=null`` — latest unlabeled).
See
[docs/architecture/decisions/0211-phase-210-nas-live-verify-phase-209.md](docs/architecture/decisions/0211-phase-210-nas-live-verify-phase-209.md).

#### Added

- ADR-0211: live verify requires backend+frontend recreate for Phase 209; checklist item 100.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 209 - Evidence Summary Latest Outcome Label Bar Source

Surface top-level ``latest_outcome_label_bar_source`` on evidence summary. See
[docs/architecture/decisions/0210-phase-209-evidence-summary-latest-outcome-label-bar-source.md](docs/architecture/decisions/0210-phase-209-evidence-summary-latest-outcome-label-bar-source.md).

#### Added

- ``latest_outcome_label_bar_source`` on evidence summary (+ export); from latest_outcome_label.
- Console surfaces the field with ``data-testid="evidence-latest-outcome-label-bar-source"``.
- NAS verify checklist item 100 for Phase 210.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 208 - NAS Live Verification of Phase 207

Ops evidence gate after Phase 207 latest outcome label state field. Live verify passed
2026-07-31 (``5f5d8f5``; AAPL ``latest_outcome_label_state=null`` — latest unlabeled).
See
[docs/architecture/decisions/0209-phase-208-nas-live-verify-phase-207.md](docs/architecture/decisions/0209-phase-208-nas-live-verify-phase-207.md).

#### Added

- ADR-0209: live verify requires backend+frontend recreate for Phase 207; checklist item 99.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 207 - Evidence Summary Latest Outcome Label State

Surface top-level ``latest_outcome_label_state`` on evidence summary. See
[docs/architecture/decisions/0208-phase-207-evidence-summary-latest-outcome-label-state.md](docs/architecture/decisions/0208-phase-207-evidence-summary-latest-outcome-label-state.md).

#### Added

- ``latest_outcome_label_state`` on evidence summary (+ export); from latest_outcome_label.
- Console surfaces the field with ``data-testid="evidence-latest-outcome-label-state"``.
- NAS verify checklist item 99 for Phase 208.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 206 - NAS Live Verification of Phase 205

Ops evidence gate after Phase 205 latest outcome label schema version field. Live verify passed
2026-07-31 (``ef9aadc``; AAPL ``latest_outcome_label_schema_version=null`` — latest unlabeled).
See
[docs/architecture/decisions/0207-phase-206-nas-live-verify-phase-205.md](docs/architecture/decisions/0207-phase-206-nas-live-verify-phase-205.md).

#### Added

- ADR-0207: live verify requires backend+frontend recreate for Phase 205; checklist item 98.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 205 - Evidence Summary Latest Outcome Label Schema Version

Surface top-level ``latest_outcome_label_schema_version`` on evidence summary. See
[docs/architecture/decisions/0206-phase-205-evidence-summary-latest-outcome-label-schema-version.md](docs/architecture/decisions/0206-phase-205-evidence-summary-latest-outcome-label-schema-version.md).

#### Added

- ``latest_outcome_label_schema_version`` on evidence summary (+ export); from latest_outcome_label.
- Console surfaces the field with ``data-testid="evidence-latest-outcome-label-schema-version"``.
- NAS verify checklist item 98 for Phase 206.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 204 - NAS Live Verification of Phase 203

Ops evidence gate after Phase 203 latest outcome label method version field. Live verify passed
2026-07-31 (``32b2040``; AAPL ``latest_outcome_label_method_version=null`` — latest unlabeled).
See
[docs/architecture/decisions/0205-phase-204-nas-live-verify-phase-203.md](docs/architecture/decisions/0205-phase-204-nas-live-verify-phase-203.md).

#### Added

- ADR-0205: live verify requires backend+frontend recreate for Phase 203; checklist item 97.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 203 - Evidence Summary Latest Outcome Label Method Version

Surface top-level ``latest_outcome_label_method_version`` on evidence summary. See
[docs/architecture/decisions/0204-phase-203-evidence-summary-latest-outcome-label-method-version.md](docs/architecture/decisions/0204-phase-203-evidence-summary-latest-outcome-label-method-version.md).

#### Added

- ``latest_outcome_label_method_version`` on evidence summary (+ export); from latest_outcome_label.
- Console surfaces the field with ``data-testid="evidence-latest-outcome-label-method-version"``.
- NAS verify checklist item 97 for Phase 204.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 202 - NAS Live Verification of Phase 201

Ops evidence gate after Phase 201 latest outcome label method id field. Live verify passed
2026-07-31 (``fcbe338``; AAPL ``latest_outcome_label_method_id=null`` — latest unlabeled).
See
[docs/architecture/decisions/0203-phase-202-nas-live-verify-phase-201.md](docs/architecture/decisions/0203-phase-202-nas-live-verify-phase-201.md).

#### Added

- ADR-0203: live verify requires backend+frontend recreate for Phase 201; checklist item 96.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 201 - Evidence Summary Latest Outcome Label Method Id

Surface top-level ``latest_outcome_label_method_id`` on evidence summary. See
[docs/architecture/decisions/0202-phase-201-evidence-summary-latest-outcome-label-method-id.md](docs/architecture/decisions/0202-phase-201-evidence-summary-latest-outcome-label-method-id.md).

#### Added

- ``latest_outcome_label_method_id`` on evidence summary (+ export); from latest_outcome_label.
- Console surfaces the field with ``data-testid="evidence-latest-outcome-label-method-id"``.
- NAS verify checklist item 96 for Phase 202.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 200 - NAS Live Verification of Phase 199

Ops evidence gate after Phase 199 latest outcome label computed_at field. Live verify passed
2026-07-31 (``c15f605``; AAPL ``latest_outcome_label_computed_at=null`` — latest unlabeled).
See
[docs/architecture/decisions/0201-phase-200-nas-live-verify-phase-199.md](docs/architecture/decisions/0201-phase-200-nas-live-verify-phase-199.md).

#### Added

- ADR-0201: live verify requires backend+frontend recreate for Phase 199; checklist item 95.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 199 - Evidence Summary Latest Outcome Label Computed At

Surface top-level ``latest_outcome_label_computed_at`` on evidence summary. See
[docs/architecture/decisions/0200-phase-199-evidence-summary-latest-outcome-label-computed-at.md](docs/architecture/decisions/0200-phase-199-evidence-summary-latest-outcome-label-computed-at.md).

#### Added

- ``latest_outcome_label_computed_at`` on evidence summary (+ export); from latest_outcome_label.
- Console surfaces the field with ``data-testid="evidence-latest-outcome-label-computed-at"``.
- NAS verify checklist item 95 for Phase 200.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 198 - NAS Live Verification of Phase 197

Ops evidence gate after Phase 197 latest calibration assessment snapshot id field. Live verify
passed 2026-07-31 (``77b8901``; AAPL assessment_snapshot_id=126; probability_confidence=0.75).
See
[docs/architecture/decisions/0199-phase-198-nas-live-verify-phase-197.md](docs/architecture/decisions/0199-phase-198-nas-live-verify-phase-197.md).

#### Added

- ADR-0199: live verify requires backend+frontend recreate for Phase 197; checklist item 94.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 197 - Evidence Summary Latest Calibration Assessment Snapshot Id

Surface top-level ``latest_calibration_assessment_snapshot_id`` on evidence summary. See
[docs/architecture/decisions/0198-phase-197-evidence-summary-latest-calibration-assessment-snapshot-id.md](docs/architecture/decisions/0198-phase-197-evidence-summary-latest-calibration-assessment-snapshot-id.md).

#### Added

- ``latest_calibration_assessment_snapshot_id`` on evidence summary (+ export); from latest_calibration.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-assessment-snapshot-id"``.
- NAS verify checklist item 94 for Phase 198.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 196 - NAS Live Verification of Phase 195

Ops evidence gate after Phase 195 latest calibration probability confidence field. Live verify
passed 2026-07-31 (``3e8bf3c``; AAPL probability_confidence=0.75; state=research_only). See
[docs/architecture/decisions/0197-phase-196-nas-live-verify-phase-195.md](docs/architecture/decisions/0197-phase-196-nas-live-verify-phase-195.md).

#### Added

- ADR-0197: live verify requires backend+frontend recreate for Phase 195; checklist item 93.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 195 - Evidence Summary Latest Calibration Probability Confidence

Surface top-level ``latest_calibration_probability_confidence`` on evidence summary. See
[docs/architecture/decisions/0196-phase-195-evidence-summary-latest-calibration-probability-confidence.md](docs/architecture/decisions/0196-phase-195-evidence-summary-latest-calibration-probability-confidence.md).

#### Added

- ``latest_calibration_probability_confidence`` on evidence summary (+ export); from latest_calibration.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-probability-confidence"``.
- NAS verify checklist item 93 for Phase 196.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 194 - NAS Live Verification of Phase 193

Ops evidence gate after Phase 193 latest calibration state field. Live verify passed
2026-07-31 (``c72ec84``; AAPL state=research_only; schema_version=1). See
[docs/architecture/decisions/0195-phase-194-nas-live-verify-phase-193.md](docs/architecture/decisions/0195-phase-194-nas-live-verify-phase-193.md).

#### Added

- ADR-0195: live verify requires backend+frontend recreate for Phase 193; checklist item 92.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 193 - Evidence Summary Latest Calibration State

Surface top-level ``latest_calibration_state`` on evidence summary. See
[docs/architecture/decisions/0194-phase-193-evidence-summary-latest-calibration-state.md](docs/architecture/decisions/0194-phase-193-evidence-summary-latest-calibration-state.md).

#### Added

- ``latest_calibration_state`` on evidence summary (+ export); from latest_calibration.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-state"``.
- NAS verify checklist item 92 for Phase 194.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 192 - NAS Live Verification of Phase 191

Ops evidence gate after Phase 191 latest calibration schema version field. Live verify passed
2026-07-31 (``43353e3``; AAPL schema_version=1; method_version=2). See
[docs/architecture/decisions/0193-phase-192-nas-live-verify-phase-191.md](docs/architecture/decisions/0193-phase-192-nas-live-verify-phase-191.md).

#### Added

- ADR-0193: live verify requires backend+frontend recreate for Phase 191; checklist item 91.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 191 - Evidence Summary Latest Calibration Schema Version

Surface top-level ``latest_calibration_schema_version`` on evidence summary. See
[docs/architecture/decisions/0192-phase-191-evidence-summary-latest-calibration-schema-version.md](docs/architecture/decisions/0192-phase-191-evidence-summary-latest-calibration-schema-version.md).

#### Added

- ``latest_calibration_schema_version`` on evidence summary (+ export); from latest_calibration.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-schema-version"``.
- NAS verify checklist item 91 for Phase 192.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 190 - NAS Live Verification of Phase 189

Ops evidence gate after Phase 189 latest calibration method version field. Live verify passed
2026-07-31 (``346fcca``; AAPL method_version=2; method_id=research_calibration_v1). See
[docs/architecture/decisions/0191-phase-190-nas-live-verify-phase-189.md](docs/architecture/decisions/0191-phase-190-nas-live-verify-phase-189.md).

#### Added

- ADR-0191: live verify requires backend+frontend recreate for Phase 189; checklist item 90.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 189 - Evidence Summary Latest Calibration Method Version

Surface top-level ``latest_calibration_method_version`` on evidence summary. See
[docs/architecture/decisions/0190-phase-189-evidence-summary-latest-calibration-method-version.md](docs/architecture/decisions/0190-phase-189-evidence-summary-latest-calibration-method-version.md).

#### Added

- ``latest_calibration_method_version`` on evidence summary (+ export); from latest_calibration.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-method-version"``.
- NAS verify checklist item 90 for Phase 190.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 188 - NAS Live Verification of Phase 187

Ops evidence gate after Phase 187 latest calibration method id field. Live verify passed
2026-07-31 (``ac5cedc``; AAPL method_id=research_calibration_v1). See
[docs/architecture/decisions/0189-phase-188-nas-live-verify-phase-187.md](docs/architecture/decisions/0189-phase-188-nas-live-verify-phase-187.md).

#### Added

- ADR-0189: live verify requires backend+frontend recreate for Phase 187; checklist item 89.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 187 - Evidence Summary Latest Calibration Method Id

Surface top-level ``latest_calibration_method_id`` on evidence summary. See
[docs/architecture/decisions/0188-phase-187-evidence-summary-latest-calibration-method-id.md](docs/architecture/decisions/0188-phase-187-evidence-summary-latest-calibration-method-id.md).

#### Added

- ``latest_calibration_method_id`` on evidence summary (+ export); from latest_calibration.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-method-id"``.
- NAS verify checklist item 89 for Phase 188.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 186 - NAS Live Verification of Phase 185

Ops evidence gate after Phase 185 latest calibration bucket count field. Live verify passed
2026-07-31 (``8ee7b8f``; AAPL bucket_count=20; corpus_count=100). See
[docs/architecture/decisions/0187-phase-186-nas-live-verify-phase-185.md](docs/architecture/decisions/0187-phase-186-nas-live-verify-phase-185.md).

#### Added

- ADR-0187: live verify requires backend+frontend recreate for Phase 185; checklist item 88.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 185 - Evidence Summary Latest Calibration Bucket Count

Surface top-level ``latest_calibration_bucket_count`` on evidence summary. See
[docs/architecture/decisions/0186-phase-185-evidence-summary-latest-calibration-bucket-count.md](docs/architecture/decisions/0186-phase-185-evidence-summary-latest-calibration-bucket-count.md).

#### Added

- ``latest_calibration_bucket_count`` on evidence summary (+ export); from latest_calibration.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-bucket-count"``.
- NAS verify checklist item 88 for Phase 186.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 184 - NAS Live Verification of Phase 183

Ops evidence gate after Phase 183 latest calibration corpus count field. Live verify passed
2026-07-31 (``af08753``; AAPL corpus_count=100). See
[docs/architecture/decisions/0185-phase-184-nas-live-verify-phase-183.md](docs/architecture/decisions/0185-phase-184-nas-live-verify-phase-183.md).

#### Added

- ADR-0185: live verify requires backend+frontend recreate for Phase 183; checklist item 87.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 183 - Evidence Summary Latest Calibration Corpus Count

Surface top-level ``latest_calibration_corpus_count`` on evidence summary. See
[docs/architecture/decisions/0184-phase-183-evidence-summary-latest-calibration-corpus-count.md](docs/architecture/decisions/0184-phase-183-evidence-summary-latest-calibration-corpus-count.md).

#### Added

- ``latest_calibration_corpus_count`` on evidence summary (+ export); from latest_calibration.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-corpus-count"``.
- NAS verify checklist item 87 for Phase 184.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 182 - NAS Live Verification of Phase 181

Ops evidence gate after Phase 181 latest calibration computed_at field. Live verify passed
2026-07-31 (``b08c4ce``; AAPL computed_at=2026-07-31T05:25:31.947262Z; calibration_id=67). See
[docs/architecture/decisions/0183-phase-182-nas-live-verify-phase-181.md](docs/architecture/decisions/0183-phase-182-nas-live-verify-phase-181.md).

#### Added

- ADR-0183: live verify requires backend+frontend recreate for Phase 181; checklist item 86.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 181 - Evidence Summary Latest Calibration Computed At

Surface top-level ``latest_calibration_computed_at`` on evidence summary. See
[docs/architecture/decisions/0182-phase-181-evidence-summary-latest-calibration-computed-at.md](docs/architecture/decisions/0182-phase-181-evidence-summary-latest-calibration-computed-at.md).

#### Added

- ``latest_calibration_computed_at`` on evidence summary (+ export); from latest_calibration.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-computed-at"``.
- NAS verify checklist item 86 for Phase 182.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 180 - NAS Live Verification of Phase 179

Ops evidence gate after Phase 179 latest calibration horizon key field. Live verify passed
2026-07-31 (``dd3aaa5``; AAPL horizon_key=forward_return_5; calibration_id=66). See
[docs/architecture/decisions/0181-phase-180-nas-live-verify-phase-179.md](docs/architecture/decisions/0181-phase-180-nas-live-verify-phase-179.md).

#### Added

- ADR-0181: live verify requires backend+frontend recreate for Phase 179; checklist item 85.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 179 - Evidence Summary Latest Calibration Horizon Key

Surface top-level ``latest_calibration_horizon_key`` on evidence summary. See
[docs/architecture/decisions/0180-phase-179-evidence-summary-latest-calibration-horizon-key.md](docs/architecture/decisions/0180-phase-179-evidence-summary-latest-calibration-horizon-key.md).

#### Added

- ``latest_calibration_horizon_key`` on evidence summary (+ export); from latest_calibration.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-horizon-key"``.
- NAS verify checklist item 85 for Phase 180.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 178 - NAS Live Verification of Phase 177

Ops evidence gate after Phase 177 latest calibration id field. Live verify passed
2026-07-31 (``025958d``; AAPL calibration_id=65). See
[docs/architecture/decisions/0179-phase-178-nas-live-verify-phase-177.md](docs/architecture/decisions/0179-phase-178-nas-live-verify-phase-177.md).

#### Added

- ADR-0179: live verify requires backend+frontend recreate for Phase 177; checklist item 84.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 177 - Evidence Summary Latest Calibration Id

Surface top-level ``latest_calibration_id`` on evidence summary. See
[docs/architecture/decisions/0178-phase-177-evidence-summary-latest-calibration-id.md](docs/architecture/decisions/0178-phase-177-evidence-summary-latest-calibration-id.md).

#### Added

- ``latest_calibration_id`` on evidence summary (+ export); from latest_calibration when set.
- Console surfaces the field with ``data-testid="evidence-latest-calibration-id"``.
- NAS verify checklist item 84 for Phase 178.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 176 - NAS Live Verification of Phase 175

Ops evidence gate after Phase 175 latest outcome label id field. Live verify passed
2026-07-31 (``8836fd2``; AAPL outcome_label_id=null — latest assessment unlabeled). See
[docs/architecture/decisions/0177-phase-176-nas-live-verify-phase-175.md](docs/architecture/decisions/0177-phase-176-nas-live-verify-phase-175.md).

#### Added

- ADR-0177: live verify requires backend+frontend recreate for Phase 175; checklist item 83.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 175 - Evidence Summary Latest Outcome Label Id

Surface top-level ``latest_outcome_label_id`` on evidence summary. See
[docs/architecture/decisions/0176-phase-175-evidence-summary-latest-outcome-label-id.md](docs/architecture/decisions/0176-phase-175-evidence-summary-latest-outcome-label-id.md).

#### Added

- ``latest_outcome_label_id`` on evidence summary (+ export); from latest_outcome_label when set.
- Console surfaces the field with ``data-testid="evidence-latest-outcome-label-id"``.
- NAS verify checklist item 83 for Phase 176.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 174 - NAS Live Verification of Phase 173

Ops evidence gate after Phase 173 latest assessment id field. Live verify passed
2026-07-31 (``64fce25``; AAPL assessment_id=126, most_recent_labeled=125). See
[docs/architecture/decisions/0175-phase-174-nas-live-verify-phase-173.md](docs/architecture/decisions/0175-phase-174-nas-live-verify-phase-173.md).

#### Added

- ADR-0175: live verify requires backend+frontend recreate for Phase 173; checklist item 82.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 173 - Evidence Summary Latest Assessment Id

Surface top-level ``latest_assessment_id`` on evidence summary. See
[docs/architecture/decisions/0174-phase-173-evidence-summary-latest-assessment-id.md](docs/architecture/decisions/0174-phase-173-evidence-summary-latest-assessment-id.md).

#### Added

- ``latest_assessment_id`` on evidence summary (+ export); copied from latest assessment id.
- Console surfaces the field with ``data-testid="evidence-latest-assessment-id"``.
- NAS verify checklist item 82 for Phase 174.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 172 - NAS Live Verification of Phase 171

Ops evidence gate after Phase 171 latest probability confidence field. Live verify passed
2026-07-31 (``004d1f5``; AAPL probability_confidence=0.75). See
[docs/architecture/decisions/0173-phase-172-nas-live-verify-phase-171.md](docs/architecture/decisions/0173-phase-172-nas-live-verify-phase-171.md).

#### Added

- ADR-0173: live verify requires backend+frontend recreate for Phase 171; checklist item 81.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 171 - Evidence Summary Latest Probability Confidence

Surface top-level ``latest_probability_confidence`` on evidence summary. See
[docs/architecture/decisions/0172-phase-171-evidence-summary-latest-probability-confidence.md](docs/architecture/decisions/0172-phase-171-evidence-summary-latest-probability-confidence.md).

#### Added

- ``latest_probability_confidence`` on evidence summary (+ export); copied from latest
  assessment; null when unset; distinct from coverage confidence.
- Console surfaces the field with ``data-testid="evidence-latest-probability-confidence"``.
- NAS verify checklist item 81 for Phase 172.

#### Explicitly out of scope

New scoring math, default-on calibration, orders, UI structural extracts.

### Phase 170 - NAS Live Verification of Phase 169

Ops evidence gate after Phase 169 latest event_time field. Live verify passed
2026-07-31 (``fcf4123``; AAPL event_time=2026-07-29T23:59:59Z). See
[docs/architecture/decisions/0171-phase-170-nas-live-verify-phase-169.md](docs/architecture/decisions/0171-phase-170-nas-live-verify-phase-169.md).

#### Added

- ADR-0171: live verify requires backend+frontend recreate for Phase 169; checklist item 80.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 169 - Evidence Summary Latest Event Time

Surface top-level ``latest_event_time`` on evidence summary. See
[docs/architecture/decisions/0170-phase-169-evidence-summary-latest-event-time.md](docs/architecture/decisions/0170-phase-169-evidence-summary-latest-event-time.md).

#### Added

- ``latest_event_time`` on evidence summary (+ export); copied from latest assessment.
- Console surfaces the field with ``data-testid="evidence-latest-event-time"``.
- NAS verify checklist item 80 for Phase 170.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 168 - NAS Live Verification of Phase 167

Ops evidence gate after Phase 167 latest computed_at field. Live verify passed
2026-07-31 (``4fecc07``; AAPL computed_at=2026-07-30T22:00:01.230802Z). See
[docs/architecture/decisions/0169-phase-168-nas-live-verify-phase-167.md](docs/architecture/decisions/0169-phase-168-nas-live-verify-phase-167.md).

#### Added

- ADR-0169: live verify requires backend+frontend recreate for Phase 167; checklist item 79.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 167 - Evidence Summary Latest Computed At

Surface top-level ``latest_computed_at`` on evidence summary. See
[docs/architecture/decisions/0168-phase-167-evidence-summary-latest-computed-at.md](docs/architecture/decisions/0168-phase-167-evidence-summary-latest-computed-at.md).

#### Added

- ``latest_computed_at`` on evidence summary (+ export); copied from latest assessment.
- Console surfaces the field with ``data-testid="evidence-latest-computed-at"``.
- NAS verify checklist item 79 for Phase 168.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 166 - NAS Live Verification of Phase 165

Ops evidence gate after Phase 165 latest schema version field. Live verify passed
2026-07-31 (``41c359e``; AAPL schema_version=2). See
[docs/architecture/decisions/0167-phase-166-nas-live-verify-phase-165.md](docs/architecture/decisions/0167-phase-166-nas-live-verify-phase-165.md).

#### Added

- ADR-0167: live verify requires backend+frontend recreate for Phase 165; checklist item 78.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 165 - Evidence Summary Latest Schema Version

Surface top-level ``latest_schema_version`` on evidence summary. See
[docs/architecture/decisions/0166-phase-165-evidence-summary-latest-schema-version.md](docs/architecture/decisions/0166-phase-165-evidence-summary-latest-schema-version.md).

#### Added

- ``latest_schema_version`` on evidence summary (+ export); copied from latest assessment.
- Console surfaces the field with ``data-testid="evidence-latest-schema-version"``.
- NAS verify checklist item 78 for Phase 166.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 164 - NAS Live Verification of Phase 163

Ops evidence gate after Phase 163 latest lookback start date field. Live verify passed
2026-07-31 (``d120c76``; AAPL lookback_start=2026-07-01). See
[docs/architecture/decisions/0165-phase-164-nas-live-verify-phase-163.md](docs/architecture/decisions/0165-phase-164-nas-live-verify-phase-163.md).

#### Added

- ADR-0165: live verify requires backend+frontend recreate for Phase 163; checklist item 77.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 163 - Evidence Summary Latest Lookback Start Date

Surface top-level ``latest_lookback_start_date`` on evidence summary. See
[docs/architecture/decisions/0164-phase-163-evidence-summary-latest-lookback-start.md](docs/architecture/decisions/0164-phase-163-evidence-summary-latest-lookback-start.md).

#### Added

- ``latest_lookback_start_date`` on evidence summary (+ export); copied from latest assessment.
- Console surfaces the field with ``data-testid="evidence-latest-lookback-start-date"``.
- NAS verify checklist item 77 for Phase 164.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 162 - NAS Live Verification of Phase 161

Ops evidence gate after Phase 161 latest lookback end date field. Live verify passed
2026-07-31 (``eb6cfb8``; AAPL lookback_end=2026-07-29). See
[docs/architecture/decisions/0163-phase-162-nas-live-verify-phase-161.md](docs/architecture/decisions/0163-phase-162-nas-live-verify-phase-161.md).

#### Added

- ADR-0163: live verify requires backend+frontend recreate for Phase 161; checklist item 76.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 161 - Evidence Summary Latest Lookback End Date

Surface top-level ``latest_lookback_end_date`` on evidence summary. See
[docs/architecture/decisions/0162-phase-161-evidence-summary-latest-lookback-end.md](docs/architecture/decisions/0162-phase-161-evidence-summary-latest-lookback-end.md).

#### Added

- ``latest_lookback_end_date`` on evidence summary (+ export); copied from latest assessment.
- Console surfaces the field with ``data-testid="evidence-latest-lookback-end-date"``.
- NAS verify checklist item 76 for Phase 162.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts, ``lookback_start_date``.

### Phase 160 - NAS Live Verification of Phase 159

Ops evidence gate after Phase 159 latest method version field. Live verify passed 2026-07-31
(``f78c02b``; AAPL method_version=2). See
[docs/architecture/decisions/0161-phase-160-nas-live-verify-phase-159.md](docs/architecture/decisions/0161-phase-160-nas-live-verify-phase-159.md).

#### Added

- ADR-0161: live verify requires backend+frontend recreate for Phase 159; checklist item 75.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 159 - Evidence Summary Latest Method Version

Surface top-level ``latest_method_version`` on evidence summary. See
[docs/architecture/decisions/0160-phase-159-evidence-summary-latest-method-version.md](docs/architecture/decisions/0160-phase-159-evidence-summary-latest-method-version.md).

#### Added

- ``latest_method_version`` on evidence summary (+ export); copied from latest assessment.
- Console surfaces the field with ``data-testid="evidence-latest-method-version"``.
- NAS verify checklist item 75 for Phase 160.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 158 - NAS Live Verification of Phase 157

Ops evidence gate after Phase 157 latest method id field. Live verify passed 2026-07-31
(``1fbef07``; AAPL method_id=daily_bar_research_v1). See
[docs/architecture/decisions/0159-phase-158-nas-live-verify-phase-157.md](docs/architecture/decisions/0159-phase-158-nas-live-verify-phase-157.md).

#### Added

- ADR-0159: live verify requires backend+frontend recreate for Phase 157; checklist item 74.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 157 - Evidence Summary Latest Method Id

Surface top-level ``latest_method_id`` on evidence summary. See
[docs/architecture/decisions/0158-phase-157-evidence-summary-latest-method-id.md](docs/architecture/decisions/0158-phase-157-evidence-summary-latest-method-id.md).

#### Added

- ``latest_method_id`` on evidence summary (+ export); copied from latest assessment.
- Console surfaces the field with ``data-testid="evidence-latest-method-id"``.
- NAS verify checklist item 74 for Phase 158.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts, ``method_version``.

### Phase 156 - NAS Live Verification of Phase 155

Ops evidence gate after Phase 155 latest input source field. Live verify passed 2026-07-30
(``cecb8b4``; AAPL input_source=alpha_vantage). See
[docs/architecture/decisions/0157-phase-156-nas-live-verify-phase-155.md](docs/architecture/decisions/0157-phase-156-nas-live-verify-phase-155.md).

#### Added

- ADR-0157: live verify requires backend+frontend recreate for Phase 155; checklist item 73.
- ``verify.ps1`` Alembic SSH capture merges remote stderr so INFO logs do not abort Stop.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 155 - Evidence Summary Latest Input Source

Surface top-level ``latest_input_source`` on evidence summary (distinct from component
source). See
[docs/architecture/decisions/0156-phase-155-evidence-summary-latest-input-source.md](docs/architecture/decisions/0156-phase-155-evidence-summary-latest-input-source.md).

#### Added

- ``latest_input_source`` on evidence summary (+ export); copied from latest assessment.
- Console surfaces the field with ``data-testid="evidence-latest-input-source"``.
- NAS verify checklist item 73 for Phase 156.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 154 - NAS Live Verification of Phase 153

Ops evidence gate after Phase 153 latest bar count field. Live verify passed 2026-07-30
(``dda412e``; AAPL bar_count=20). See
[docs/architecture/decisions/0155-phase-154-nas-live-verify-phase-153.md](docs/architecture/decisions/0155-phase-154-nas-live-verify-phase-153.md).

#### Added

- ADR-0155: live verify requires backend+frontend recreate for Phase 153; checklist item 72.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 153 - Evidence Summary Latest Bar Count

Surface top-level ``latest_bar_count`` on evidence summary. See
[docs/architecture/decisions/0154-phase-153-evidence-summary-latest-bar-count.md](docs/architecture/decisions/0154-phase-153-evidence-summary-latest-bar-count.md).

#### Added

- ``latest_bar_count`` on evidence summary (+ export); copied from latest assessment.
- Console surfaces the field with ``data-testid="evidence-latest-bar-count"``.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 152 - NAS Live Verification of Phase 151

Ops evidence gate after Phase 151 as-of trading date field. Live verify passed 2026-07-30
(``3c44966``; AAPL as_of=2026-07-29). See
[docs/architecture/decisions/0153-phase-152-nas-live-verify-phase-151.md](docs/architecture/decisions/0153-phase-152-nas-live-verify-phase-151.md).

#### Added

- ADR-0153: live verify requires backend+frontend recreate for Phase 151; checklist item 71.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 151 - Evidence Summary Latest As-Of Trading Date

Surface top-level ``latest_as_of_trading_date`` on evidence summary. See
[docs/architecture/decisions/0152-phase-151-evidence-summary-latest-as-of-date.md](docs/architecture/decisions/0152-phase-151-evidence-summary-latest-as-of-date.md).

#### Added

- ``latest_as_of_trading_date`` on evidence summary (+ export); copied from latest assessment.
- Console surfaces the field with ``data-testid="evidence-latest-as-of-trading-date"``.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 150 - NAS Live Verification of Phase 149

Ops evidence gate after Phase 149 latest research index field. Live verify passed 2026-07-30
(``16ce17a``; AAPL research_index≈0.483). See
[docs/architecture/decisions/0151-phase-150-nas-live-verify-phase-149.md](docs/architecture/decisions/0151-phase-150-nas-live-verify-phase-149.md).

#### Added

- ADR-0151: live verify requires backend+frontend recreate for Phase 149; checklist item 70.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 149 - Evidence Summary Latest Research Index

Surface top-level ``latest_research_index`` on evidence summary. See
[docs/architecture/decisions/0150-phase-149-evidence-summary-latest-research-index.md](docs/architecture/decisions/0150-phase-149-evidence-summary-latest-research-index.md).

#### Added

- ``latest_research_index`` on evidence summary (+ export); numeric ``components.research_index`` only.
- Console surfaces the field with ``data-testid="evidence-latest-research-index"``.

#### Explicitly out of scope

New scoring math, orders, UI structural extracts.

### Phase 148 - NAS Live Verification of Phase 147

Ops evidence gate: redeploy backend+frontend under lab TLS after Phase 147 coverage-confidence
field. Live verify passed 2026-07-30 (``cab03a4``). See
[docs/architecture/decisions/0149-phase-148-nas-live-verify-phase-147.md](docs/architecture/decisions/0149-phase-148-nas-live-verify-phase-147.md).

#### Added

- ADR-0149: live verify requires backend+frontend recreate for Phase 147; checklist item 69.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 147 - Evidence Summary Latest Coverage Confidence

Surface top-level ``latest_coverage_confidence`` on evidence summary (keep coverage
separate from probability). See
[docs/architecture/decisions/0148-phase-147-evidence-summary-latest-coverage-confidence.md](docs/architecture/decisions/0148-phase-147-evidence-summary-latest-coverage-confidence.md).

#### Added

- ``latest_coverage_confidence`` on evidence summary (+ export); copied from latest assessment.
- Console shows the field next to latest probability_confidence with a distinctness note.

#### Explicitly out of scope

New scoring math, orders, further UI structural extracts.

### Phase 146 - NAS Live Verification of Phase 145

Ops evidence gate: redeploy backend+frontend under lab TLS after Phase 145 scan-wide
label counts. Live verify passed 2026-07-30 (``112dcef``). See
[docs/architecture/decisions/0147-phase-146-nas-live-verify-phase-145.md](docs/architecture/decisions/0147-phase-146-nas-live-verify-phase-145.md).

#### Added

- ADR-0147: live verify requires backend+frontend recreate for Phase 145; checklist item 68.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 145 - Evidence Summary Scan-Wide Label Counts

Add labeled/unlabeled assessment counts across the ≤100 evidence-summary scan (not only
mixed). See
[docs/architecture/decisions/0146-phase-145-evidence-summary-scan-label-counts.md](docs/architecture/decisions/0146-phase-145-evidence-summary-scan-label-counts.md).

#### Added

- ``labeled_assessment_count`` / ``unlabeled_assessment_count`` on evidence summary (+ export).
- Console surfaces both counts on ``ResearchEvidenceSummarySection``.

#### Explicitly out of scope

New calibration math, orders, further UI structural extracts.

### Phase 144 - NAS Live Verification of Phase 143

Ops evidence gate: redeploy frontend under lab TLS after Phase 143 error-alert extract. Live
verify passed 2026-07-30 (``434f471``). See
[docs/architecture/decisions/0145-phase-144-nas-live-verify-phase-143.md](docs/architecture/decisions/0145-phase-144-nas-live-verify-phase-143.md).

#### Added

- ADR-0145: live verify requires frontend recreate for Phase 143; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 143 - Extract Research Assessment Error Alert

Move panel error banner into a presentational component (no behavior change). See
[docs/architecture/decisions/0144-phase-143-extract-research-assessment-error-alert.md](docs/architecture/decisions/0144-phase-143-extract-research-assessment-error-alert.md).

#### Added

- ``ResearchAssessmentErrorAlert.tsx`` with ``data-testid="research-assessment-error"``.
- Panel UI modularization complete; next phases prefer product/evidence work.

#### Explicitly out of scope

New product math, orders.

### Phase 142 - NAS Live Verification of Phase 141

Ops evidence gate: redeploy frontend under lab TLS after Phase 141 panel-header extract.
Live verify passed 2026-07-30 (``1eea8ea``). See
[docs/architecture/decisions/0143-phase-142-nas-live-verify-phase-141.md](docs/architecture/decisions/0143-phase-142-nas-live-verify-phase-141.md).

#### Added

- ADR-0143: live verify requires frontend recreate for Phase 141; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 141 - Extract Research Assessment Panel Header

Move panel header chrome into a presentational component (no behavior change). See
[docs/architecture/decisions/0142-phase-141-extract-research-assessment-panel-header.md](docs/architecture/decisions/0142-phase-141-extract-research-assessment-panel-header.md).

#### Added

- ``ResearchAssessmentPanelHeader.tsx`` with ``data-testid="research-assessment-panel-header"``.

#### Explicitly out of scope

New product math, orders.

### Phase 140 - NAS Live Verification of Phase 139

Ops evidence gate: redeploy frontend under lab TLS after Phase 139 backfill-status section
extract. Live verify passed 2026-07-30 (``ae12b45``). See
[docs/architecture/decisions/0141-phase-140-nas-live-verify-phase-139.md](docs/architecture/decisions/0141-phase-140-nas-live-verify-phase-139.md).

#### Added

- ADR-0141: live verify requires frontend recreate for Phase 139; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 139 - Extract Backfill Status Banners

Move outcome-label and assessment backfill summary banners into a presentational section
(no behavior change). See
[docs/architecture/decisions/0140-phase-139-extract-backfill-status-section.md](docs/architecture/decisions/0140-phase-139-extract-backfill-status-section.md).

#### Added

- ``ResearchBackfillStatusSection.tsx`` with ``data-testid="backfill-status-section"``.
- Existing backfill summary test ids preserved.

#### Explicitly out of scope

New backfill math, orders.

### Phase 138 - NAS Live Verification of Phase 137

Ops evidence gate: redeploy frontend under lab TLS after Phase 137 latest-assessment section
extract. Live verify passed 2026-07-30 (``811730c``). See
[docs/architecture/decisions/0139-phase-138-nas-live-verify-phase-137.md](docs/architecture/decisions/0139-phase-138-nas-live-verify-phase-137.md).

#### Added

- ADR-0139: live verify requires frontend recreate for Phase 137; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 137 - Extract Latest Assessment Detail Panel Section

Move latest-assessment detail UI into a presentational section component (no behavior
change). See
[docs/architecture/decisions/0138-phase-137-extract-latest-assessment-section.md](docs/architecture/decisions/0138-phase-137-extract-latest-assessment-section.md).

#### Added

- ``ResearchLatestAssessmentSection.tsx`` with ``data-testid="latest-assessment-section"``.

#### Explicitly out of scope

New assessment math, orders.

### Phase 136 - NAS Live Verification of Phase 135

Ops evidence gate: redeploy frontend under lab TLS after Phase 135 evidence-summary section
extract. Live verify passed 2026-07-30 (``876c866``). See
[docs/architecture/decisions/0137-phase-136-nas-live-verify-phase-135.md](docs/architecture/decisions/0137-phase-136-nas-live-verify-phase-135.md).

#### Added

- ADR-0137: live verify requires frontend recreate for Phase 135; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 135 - Extract Evidence Summary Panel Section

Move evidence-summary diagnostics UI into a presentational section component (no behavior
change). See
[docs/architecture/decisions/0136-phase-135-extract-evidence-summary-section.md](docs/architecture/decisions/0136-phase-135-extract-evidence-summary-section.md).

#### Added

- ``ResearchEvidenceSummarySection.tsx`` with ``data-testid="evidence-summary-section"``.
- Horizon-expand UI state moved into the section (behavior-preserving).

#### Explicitly out of scope

New evidence-summary math, orders.

### Phase 134 - NAS Live Verification of Phase 133

Ops evidence gate: redeploy frontend under lab TLS after Phase 133 probability-calibration
section extract. Live verify passed 2026-07-30 (``c8d55cd``). See
[docs/architecture/decisions/0135-phase-134-nas-live-verify-phase-133.md](docs/architecture/decisions/0135-phase-134-nas-live-verify-phase-133.md).

#### Added

- ADR-0135: live verify requires frontend recreate for Phase 133; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 133 - Extract Probability Calibration Panel Section

Move probability calibration result UI into a presentational section component (no behavior
change). See
[docs/architecture/decisions/0134-phase-133-extract-probability-calibration-section.md](docs/architecture/decisions/0134-phase-133-extract-probability-calibration-section.md).

#### Added

- ``ResearchProbabilityCalibrationSection.tsx`` with
  ``data-testid="probability-calibration-section"``.

#### Explicitly out of scope

New calibration math, orders.

### Phase 132 - NAS Live Verification of Phase 131

Ops evidence gate: redeploy frontend under lab TLS after Phase 131 calibration-readiness
section extract. Live verify passed 2026-07-30 (``1169852``). See
[docs/architecture/decisions/0133-phase-132-nas-live-verify-phase-131.md](docs/architecture/decisions/0133-phase-132-nas-live-verify-phase-131.md).

#### Added

- ADR-0133: live verify requires frontend recreate for Phase 131; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 131 - Extract Calibration Readiness Panel Section

Move calibration readiness diagnostics UI into a presentational section component (no
behavior change). See
[docs/architecture/decisions/0132-phase-131-extract-calibration-readiness-section.md](docs/architecture/decisions/0132-phase-131-extract-calibration-readiness-section.md).

#### Added

- ``ResearchCalibrationReadinessSection.tsx`` with ``data-testid="calibration-readiness-section"``.

#### Explicitly out of scope

New calibration math, orders.

### Phase 130 - NAS Live Verification of Phase 129

Ops evidence gate: redeploy frontend under lab TLS after Phase 129 assessment-history
section extract. Live verify passed 2026-07-30 (``0ece4fb``). See
[docs/architecture/decisions/0131-phase-130-nas-live-verify-phase-129.md](docs/architecture/decisions/0131-phase-130-nas-live-verify-phase-129.md).

#### Added

- ADR-0131: live verify requires frontend recreate for Phase 129; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 129 - Extract Assessment History Panel Section

Move assessment history UI into a presentational section component (no behavior change).
See
[docs/architecture/decisions/0130-phase-129-extract-assessment-history-section.md](docs/architecture/decisions/0130-phase-129-extract-assessment-history-section.md).

#### Added

- ``ResearchAssessmentHistorySection.tsx`` with ``data-testid="assessment-history-section"``.
- Shared ``formatAssessmentHistoryRow`` / ``ASSESSMENT_SOURCE_FILTER_OPTIONS`` moved into
  ``research-assessment-panel-helpers.ts``.

#### Explicitly out of scope

New assessment math, orders.

### Phase 128 - NAS Live Verification of Phase 127

Ops evidence gate: redeploy frontend under lab TLS after Phase 127 outcome-label section
extract. Live verify passed 2026-07-30 (``9823e30``). See
[docs/architecture/decisions/0129-phase-128-nas-live-verify-phase-127.md](docs/architecture/decisions/0129-phase-128-nas-live-verify-phase-127.md).

#### Added

- ADR-0129: live verify requires frontend recreate for Phase 127; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 127 - Extract Outcome-Label History Panel Section

Move outcome-label history UI into a presentational section component (no behavior change).
See
[docs/architecture/decisions/0128-phase-127-extract-outcome-label-history-section.md](docs/architecture/decisions/0128-phase-127-extract-outcome-label-history-section.md).

#### Added

- ``ResearchOutcomeLabelHistorySection.tsx`` with ``data-testid="outcome-label-history-section"``.
- Shared label display helpers moved into ``research-assessment-panel-helpers.ts``.

#### Explicitly out of scope

New label math, orders.

### Phase 126 - NAS Live Verification of Phase 125

Ops evidence gate: redeploy frontend under lab TLS after Phase 125 toolbar grouping. Live
verify passed 2026-07-30 (``9a06fde``). See
[docs/architecture/decisions/0127-phase-126-nas-live-verify-phase-125.md](docs/architecture/decisions/0127-phase-126-nas-live-verify-phase-125.md).

#### Added

- ADR-0127: live verify requires frontend recreate for Phase 125; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 125 - Group Research Assessment Action Toolbar

Label toolbar button groups (Diagnostics / Assessments / Outcome labels / Calibration). See
[docs/architecture/decisions/0126-phase-125-group-research-assessment-action-toolbar.md](docs/architecture/decisions/0126-phase-125-group-research-assessment-action-toolbar.md).

#### Added

- Grouped toolbar sections with muted labels; existing action test ids preserved.

#### Explicitly out of scope

Changing action semantics, orders.

### Phase 124 - NAS Live Verification of Phase 123

Ops evidence gate: redeploy frontend under lab TLS after Phase 123 action toolbar extract.
Live verify passed 2026-07-30 (``5afa71e``). See
[docs/architecture/decisions/0125-phase-124-nas-live-verify-phase-123.md](docs/architecture/decisions/0125-phase-124-nas-live-verify-phase-123.md).

#### Added

- ADR-0125: live verify requires frontend recreate for Phase 123; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 123 - Extract Research Assessment Action Toolbar

Move header action buttons into ``ResearchAssessmentActionToolbar`` (no behavior change).
See
[docs/architecture/decisions/0124-phase-123-extract-research-assessment-action-toolbar.md](docs/architecture/decisions/0124-phase-123-extract-research-assessment-action-toolbar.md).

#### Added

- ``ResearchAssessmentActionToolbar.tsx`` with ``data-testid="research-assessment-action-toolbar"``.

#### Explicitly out of scope

UX regrouping beyond extraction, orders.

### Phase 122 - NAS Live Verification of Phase 121

Ops evidence gate: redeploy frontend under lab TLS after Phase 121 backfill refresh naming.
Live verify passed 2026-07-30 (``b0cf94d``). See
[docs/architecture/decisions/0123-phase-122-nas-live-verify-phase-121.md](docs/architecture/decisions/0123-phase-122-nas-live-verify-phase-121.md).

#### Added

- ADR-0123: live verify requires frontend recreate for Phase 121; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 121 - Outcome-Label Backfill Names Refresh Target

Show active assessment id chip + aria on **Backfill outcome labels** (refresh target only).
See
[docs/architecture/decisions/0122-phase-121-outcome-label-backfill-names-refresh-target.md](docs/architecture/decisions/0122-phase-121-outcome-label-backfill-names-refresh-target.md).

#### Added

- ``formatOutcomeLabelBackfillAriaLabel`` and id chip on backfill outcome labels.

#### Explicitly out of scope

Changing backfill API scope, orders.

### Phase 120 - NAS Live Verification of Phase 119

Ops evidence gate: redeploy frontend under lab TLS after Phase 119 calibration chip naming.
Live verify passed 2026-07-30 (``01cdb75``). See
[docs/architecture/decisions/0121-phase-120-nas-live-verify-phase-119.md](docs/architecture/decisions/0121-phase-120-nas-live-verify-phase-119.md).

#### Added

- ADR-0121: live verify requires frontend recreate for Phase 119; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 119 - Calibration Action Chips Name Latest Explicitly

Show ``({id} · latest)`` / aria ``(latest)`` on compute/download calibration controls. See
[docs/architecture/decisions/0120-phase-119-calibration-action-chips-name-latest.md](docs/architecture/decisions/0120-phase-119-calibration-action-chips-name-latest.md).

#### Added

- ``formatCalibrationActionAriaLabel`` / ``formatCalibrationActionIdChip`` for compute/download
  calibration controls.

#### Explicitly out of scope

Changing calibration target, default-on calibration, orders.

### Phase 118 - NAS Live Verification of Phase 117

Ops evidence gate: redeploy frontend under lab TLS after Phase 117 id-chip load-kind. Live
verify passed 2026-07-30 (``272e4b4``). See
[docs/architecture/decisions/0119-phase-118-nas-live-verify-phase-117.md](docs/architecture/decisions/0119-phase-118-nas-live-verify-phase-117.md).

#### Added

- ADR-0119: live verify requires frontend recreate for Phase 117; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 117 - Outcome-Label Action Id Chip Includes Load Kind

Show ``({id} · scan-labeled)`` / ``({id} · latest)`` on compute/download id chips when
load-kind is tracked. See
[docs/architecture/decisions/0118-phase-117-outcome-label-action-id-chip-load-kind.md](docs/architecture/decisions/0118-phase-117-outcome-label-action-id-chip-load-kind.md).

#### Added

- ``formatOutcomeLabelActionIdChip`` for visible compute/download chips.

#### Explicitly out of scope

Calibration chip changes, orders.

### Phase 116 - NAS Live Verification of Phase 115

Ops evidence gate: redeploy frontend under lab TLS after Phase 115 helpers module extract.
Live verify passed 2026-07-30 (``d902ff8``). See
[docs/architecture/decisions/0117-phase-116-nas-live-verify-phase-115.md](docs/architecture/decisions/0117-phase-116-nas-live-verify-phase-115.md).

#### Added

- ADR-0117: live verify requires frontend recreate for Phase 115; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 115 - Extract Outcome-Label Panel Helpers Module

Move pure outcome-label helpers out of ``ResearchAssessmentPanel.tsx`` (no behavior change).
See
[docs/architecture/decisions/0116-phase-115-extract-outcome-label-panel-helpers.md](docs/architecture/decisions/0116-phase-115-extract-outcome-label-panel-helpers.md).

#### Added

- ``research-assessment-panel-helpers.ts`` with load-kind + aria helpers; panel imports them.

#### Explicitly out of scope

Broader panel splits, UX copy changes, orders.

### Phase 114 - NAS Live Verification of Phase 113

Ops evidence gate: redeploy frontend under lab TLS after Phase 113 aria load-kind suffixes.
Live verify passed 2026-07-30 (``aba787e``). See
[docs/architecture/decisions/0115-phase-114-nas-live-verify-phase-113.md](docs/architecture/decisions/0115-phase-114-nas-live-verify-phase-113.md).

#### Added

- ADR-0115: live verify requires frontend recreate for Phase 113; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 113 - Outcome-Label Action Aria Includes Load Kind

Append ``(scan-labeled)`` / ``(latest)`` to compute/download outcome-label accessible names
when load-kind is tracked. See
[docs/architecture/decisions/0114-phase-113-outcome-label-action-aria-load-kind.md](docs/architecture/decisions/0114-phase-113-outcome-label-action-aria-load-kind.md).

#### Added

- ``formatOutcomeLabelActionAriaLabel`` for compute/download outcome-label buttons.

#### Explicitly out of scope

Visible button copy changes, calibration aria changes, orders.

### Phase 112 - NAS Live Verification of Phase 111

Ops evidence gate: redeploy frontend under lab TLS after Phase 111 load-kind helper. Live
verify passed 2026-07-30 (``b73512f``). See
[docs/architecture/decisions/0113-phase-112-nas-live-verify-phase-111.md](docs/architecture/decisions/0113-phase-112-nas-live-verify-phase-111.md).

#### Added

- ADR-0113: live verify requires frontend recreate for Phase 111; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 111 - Resolve Outcome-Label History Load Kind Helper

Extract shared load-kind resolution for outcome-label compute/backfill refresh (no behavior
change). See
[docs/architecture/decisions/0112-phase-111-resolve-outcome-label-history-load-kind.md](docs/architecture/decisions/0112-phase-111-resolve-outcome-label-history-load-kind.md).

#### Added

- ``resolveOutcomeLabelHistoryLoadKind`` used by compute, label-backfill refresh, and
  assessment-backfill label refresh.

#### Explicitly out of scope

UX copy changes, new API fields, orders.

### Phase 110 - NAS Live Verification of Phase 109

Ops evidence gate: redeploy frontend under lab TLS after Phase 109 handler single-source
cleanup. Live verify passed 2026-07-30 (``9a7abee``). See
[docs/architecture/decisions/0111-phase-110-nas-live-verify-phase-109.md](docs/architecture/decisions/0111-phase-110-nas-live-verify-phase-109.md).

#### Added

- ADR-0111: live verify requires frontend recreate for Phase 109; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 109 - Handlers Use Active Outcome-Label Assessment Id

Route compute/download/label-backfill refresh through ``activeOutcomeLabelAssessmentId``
(no behavior change). See
[docs/architecture/decisions/0110-phase-109-handlers-use-active-outcome-label-assessment-id.md](docs/architecture/decisions/0110-phase-109-handlers-use-active-outcome-label-assessment-id.md).

#### Added

- Shared helper used by outcome-label action handlers (single derivation).

#### Explicitly out of scope

UX copy changes, new API fields, changing assessment-backfill tracking, orders.

### Phase 108 - NAS Live Verification of Phase 107

Ops evidence gate: redeploy frontend under lab TLS after Phase 107 helper rename. Live
verify passed 2026-07-30 (``0979a9c``). See
[docs/architecture/decisions/0109-phase-108-nas-live-verify-phase-107.md](docs/architecture/decisions/0109-phase-108-nas-live-verify-phase-107.md).

#### Added

- ADR-0109: live verify requires frontend recreate for Phase 107; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 107 - Rename Active Outcome-Label Assessment Id Helper

Rename ``downloadOutcomeLabelsAssessmentId`` to ``activeOutcomeLabelAssessmentId`` (no
behavior change). See
[docs/architecture/decisions/0108-phase-107-rename-active-outcome-label-assessment-id.md](docs/architecture/decisions/0108-phase-107-rename-active-outcome-label-assessment-id.md).

#### Added

- Shared helper rename across compute/download bindings.

#### Explicitly out of scope

UX copy changes beyond rename, new API fields, orders.

### Phase 106 - NAS Live Verification of Phase 105

Ops evidence gate: redeploy frontend under lab TLS after Phase 105 load-latest labels
control. Live verify passed 2026-07-30 (``759bd25``). See
[docs/architecture/decisions/0107-phase-106-nas-live-verify-phase-105.md](docs/architecture/decisions/0107-phase-106-nas-live-verify-phase-105.md).

#### Added

- ADR-0107: live verify requires frontend recreate for Phase 105; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 105 - Load Labels for Latest Assessment

One-click return to outcome labels for ``latest`` when the panel is on another assessment.
See
[docs/architecture/decisions/0106-phase-105-load-labels-for-latest.md](docs/architecture/decisions/0106-phase-105-load-labels-for-latest.md).

#### Added

- ``Load labels for latest {id}`` control when loaded label assessment differs from latest.

#### Explicitly out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders.

### Phase 104 - NAS Live Verification of Phase 103

Ops evidence gate: redeploy frontend under lab TLS after Phase 103 calibration-controls
note. Live verify passed 2026-07-30 (``0bf44c2``). See
[docs/architecture/decisions/0105-phase-104-nas-live-verify-phase-103.md](docs/architecture/decisions/0105-phase-104-nas-live-verify-phase-103.md).

#### Added

- ADR-0105: live verify requires frontend recreate for Phase 103; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 103 - Calibration Controls Note When Scan-Labeled Differs

Clarify that calibration actions always use ``latest`` when the label panel is on another
assessment. See
[docs/architecture/decisions/0104-phase-103-calibration-controls-note-scan-labeled.md](docs/architecture/decisions/0104-phase-103-calibration-controls-note-scan-labeled.md).

#### Added

- Note near calibration controls when loaded label assessment id differs from ``latest.id``.

#### Explicitly out of scope

Binding calibration to scan-labeled assessments, new API fields, orders.

### Phase 102 - NAS Live Verification of Phase 101

Ops evidence gate: redeploy frontend under lab TLS after Phase 101 compute-calibration
naming. Live verify passed 2026-07-30 (``9916ae2``). See
[docs/architecture/decisions/0103-phase-102-nas-live-verify-phase-101.md](docs/architecture/decisions/0103-phase-102-nas-live-verify-phase-101.md).

#### Added

- ADR-0103: live verify requires frontend recreate for Phase 101; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 101 - Compute Calibration Names Latest Assessment Id

Show which assessment id compute-calibration targets (always ``latest``). See
[docs/architecture/decisions/0102-phase-101-compute-calibration-names-latest.md](docs/architecture/decisions/0102-phase-101-compute-calibration-names-latest.md).

#### Added

- Compute calibration button shows ``({latest.id})`` and accessible name includes the id.

#### Explicitly out of scope

Binding calibration to scan-labeled assessments, new API fields, orders.

### Phase 100 - NAS Live Verification of Phase 99

Ops evidence gate: redeploy frontend under lab TLS after Phase 99 calibrations download
naming. Live verify passed 2026-07-30 (``545c13e``). See
[docs/architecture/decisions/0101-phase-100-nas-live-verify-phase-99.md](docs/architecture/decisions/0101-phase-100-nas-live-verify-phase-99.md).

#### Added

- ADR-0101: live verify requires frontend recreate for Phase 99; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 99 - Calibrations Download Names Latest Assessment Id

Show which assessment id calibrations JSON download targets (always ``latest``). See
[docs/architecture/decisions/0100-phase-99-calibrations-download-names-latest.md](docs/architecture/decisions/0100-phase-99-calibrations-download-names-latest.md).

#### Added

- Calibrations download button shows ``({latest.id})`` and accessible name includes the id.

#### Explicitly out of scope

Binding calibrations to scan-labeled assessments, new API fields, orders.

### Phase 98 - NAS Live Verification of Phase 97

Ops evidence gate: redeploy frontend under lab TLS after Phase 97 assessment-backfill
label preserve. Live verify passed 2026-07-30 (``bce9be3``). See
[docs/architecture/decisions/0099-phase-98-nas-live-verify-phase-97.md](docs/architecture/decisions/0099-phase-98-nas-live-verify-phase-97.md).

#### Added

- ADR-0099: live verify requires frontend recreate for Phase 97; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 97 - Assessment Backfill Preserves Loaded Outcome Labels

After assessment backfill, keep outcome-label history on the loaded assessment id when
set. See
[docs/architecture/decisions/0098-phase-97-assessment-backfill-preserves-loaded-labels.md](docs/architecture/decisions/0098-phase-97-assessment-backfill-preserves-loaded-labels.md).

#### Added

- Assessment backfill refreshes labels for ``outcomeLabelHistoryAssessmentId ?? nextLatest.id``.

#### Explicitly out of scope

New API fields, default-on calibration, changing ``latest_assessment`` selection, orders.

### Phase 96 - NAS Live Verification of Phase 95

Ops evidence gate: redeploy frontend under lab TLS after Phase 95 backfill refresh binding.
Live verify passed 2026-07-30 (``2503fee``). See
[docs/architecture/decisions/0097-phase-96-nas-live-verify-phase-95.md](docs/architecture/decisions/0097-phase-96-nas-live-verify-phase-95.md).

#### Added

- ADR-0097: live verify requires frontend recreate for Phase 95; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 95 - Outcome-Label Backfill Refresh Uses Loaded Assessment Id

After backfill, refresh outcome-label history for the loaded assessment id (not always
latest). See
[docs/architecture/decisions/0096-phase-95-outcome-label-backfill-refresh-loaded-assessment.md](docs/architecture/decisions/0096-phase-95-outcome-label-backfill-refresh-loaded-assessment.md).

#### Added

- Backfill refresh uses ``outcomeLabelHistoryAssessmentId ?? latest.id`` (preserves load-kind).

#### Explicitly out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders.

### Phase 94 - NAS Live Verification of Phase 93

Ops evidence gate: redeploy frontend under lab TLS after Phase 93 compute binding.
Live verify passed 2026-07-30 (``41a3456``). See
[docs/architecture/decisions/0095-phase-94-nas-live-verify-phase-93.md](docs/architecture/decisions/0095-phase-94-nas-live-verify-phase-93.md).

#### Added

- ADR-0095: live verify requires frontend recreate for Phase 93; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 93 - Compute Outcome Labels Uses Loaded Assessment Id

Bind compute outcome labels to the assessment id shown in the panel (not always latest).
See
[docs/architecture/decisions/0094-phase-93-compute-outcome-labels-loaded-assessment.md](docs/architecture/decisions/0094-phase-93-compute-outcome-labels-loaded-assessment.md).

#### Added

- Compute uses ``outcomeLabelHistoryAssessmentId`` when set; button names the target id.

#### Explicitly out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders.

### Phase 92 - NAS Live Verification of Phase 91

Ops evidence gate: redeploy frontend under lab TLS after Phase 91 empty-state panel.
Live verify passed 2026-07-30 (``7bad1e9``). See
[docs/architecture/decisions/0093-phase-92-nas-live-verify-phase-91.md](docs/architecture/decisions/0093-phase-92-nas-live-verify-phase-91.md).

#### Added

- ADR-0093: live verify requires frontend recreate for Phase 91; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 91 - Outcome-Label Empty State for Loaded Assessment

Keep the outcome-label panel (and captions) visible when a loaded assessment has no
stored labels. See
[docs/architecture/decisions/0092-phase-91-outcome-label-empty-state-loaded-assessment.md](docs/architecture/decisions/0092-phase-91-outcome-label-empty-state-loaded-assessment.md).

#### Added

- Empty-state line when ``outcomeLabelHistoryAssessmentId`` is set and labels are empty.

#### Explicitly out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders.

### Phase 90 - NAS Live Verification of Phase 89

Ops evidence gate: redeploy frontend under lab TLS with Phase 89 download assessment-id
label. Live verify passed 2026-07-30 (``7eb4bdf``). See
[docs/architecture/decisions/0091-phase-90-nas-live-verify-phase-89.md](docs/architecture/decisions/0091-phase-90-nas-live-verify-phase-89.md).

#### Added

- ADR-0091: live verify requires frontend recreate for Phase 89; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 89 - Outcome-Label Download Names Assessment Id

Show which assessment id the outcome-label JSON download targets. See
[docs/architecture/decisions/0090-phase-89-outcome-label-download-names-assessment.md](docs/architecture/decisions/0090-phase-89-outcome-label-download-names-assessment.md).

#### Added

- Download button shows ``({id})`` and accessible name includes the assessment id.

#### Explicitly out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders.

### Phase 88 - NAS Live Verification of Phase 87

Ops evidence gate: redeploy frontend under lab TLS after Phase 87 download binding.
Live verify passed 2026-07-30 (``6cf4ae8``). See
[docs/architecture/decisions/0089-phase-88-nas-live-verify-phase-87.md](docs/architecture/decisions/0089-phase-88-nas-live-verify-phase-87.md).

#### Added

- ADR-0089: live verify requires frontend recreate for Phase 87; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 87 - Outcome-Label Download Uses Loaded Assessment Id

Bind outcome-label JSON download to the assessment id shown in the panel (not always
latest). See
[docs/architecture/decisions/0088-phase-87-outcome-label-download-loaded-assessment.md](docs/architecture/decisions/0088-phase-87-outcome-label-download-loaded-assessment.md).

#### Added

- Download uses ``outcomeLabelHistoryAssessmentId`` when set; else ``latest.id``.

#### Explicitly out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders.

### Phase 86 - NAS Live Verification of Phase 85

Ops evidence gate: redeploy frontend under lab TLS with Phase 85 load-kind caption.
Live verify passed 2026-07-30 (``b77591b``). See
[docs/architecture/decisions/0087-phase-86-nas-live-verify-phase-85.md](docs/architecture/decisions/0087-phase-86-nas-live-verify-phase-85.md).

#### Added

- ADR-0087: live verify requires frontend recreate for Phase 85; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 85 - Outcome-Label Load-Kind Caption

Caption whether the outcome-label panel was loaded from latest or scan-labeled (and note
when those ids differ). See
[docs/architecture/decisions/0086-phase-85-outcome-label-load-kind-caption.md](docs/architecture/decisions/0086-phase-85-outcome-label-load-kind-caption.md).

#### Added

- Outcome-label panel caption ``· latest`` / ``· scan-labeled`` (optional ``latest is {id}``).

#### Explicitly out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders.

### Phase 84 - NAS Live Verification of Phase 83

Ops evidence gate: redeploy frontend under lab TLS with Phase 83 assessment-id caption.
Live verify passed 2026-07-30 (``e244021``). See
[docs/architecture/decisions/0085-phase-84-nas-live-verify-phase-83.md](docs/architecture/decisions/0085-phase-84-nas-live-verify-phase-83.md).

#### Added

- ADR-0085: live verify requires frontend recreate for Phase 83; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 83 - Outcome-Label History Assessment Id Caption

Show which assessment id the loaded outcome-label panel belongs to (audits scan-labeled
loads). See
[docs/architecture/decisions/0084-phase-83-outcome-label-history-assessment-id.md](docs/architecture/decisions/0084-phase-83-outcome-label-history-assessment-id.md).

#### Added

- Outcome-label panel caption ``Assessment id {n}``.

#### Explicitly out of scope

New API fields, default-on calibration, changing ``latest_assessment``, orders.

### Phase 82 - NAS Live Verification of Phase 81

Ops evidence gate: redeploy frontend under lab TLS with Phase 81 load-scan-labeled control.
Live verify passed 2026-07-30. See
[docs/architecture/decisions/0083-phase-82-nas-live-verify-phase-81.md](docs/architecture/decisions/0083-phase-82-nas-live-verify-phase-81.md).

#### Added

- ADR-0083: live verify requires frontend recreate for Phase 81; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 81 - Load Scan-Labeled Outcome Labels

One-click load of outcome-label history for ``most_recent_labeled_assessment_id`` when it
differs from the absolute latest. See
[docs/architecture/decisions/0082-phase-81-load-scan-labeled-labels.md](docs/architecture/decisions/0082-phase-81-load-scan-labeled-labels.md).

#### Added

- Evidence-summary “Load labels for assessment {id}” control (existing list API).

#### Explicitly out of scope

New API endpoints, changing ``latest_assessment``, default-on calibration, orders.

### Phase 80 - NAS Live Verification of Phase 79

Ops evidence gate: redeploy backend+frontend under lab TLS and confirm
``most_recent_labeled_*`` on evidence-summary. Live verify passed 2026-07-30
(``most_recent_labeled_assessment_id=125`` while latest label keys were none). See
[docs/architecture/decisions/0081-phase-80-nas-live-verify-phase-79.md](docs/architecture/decisions/0081-phase-80-nas-live-verify-phase-79.md).

#### Added

- ADR-0081: live verify requires nested most-recent labeled fields; prior gates remain.
- Verify checklist item for ``most_recent_labeled_assessment_id`` /
  ``most_recent_labeled_outcome_label`` (+ export).

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 79 - Most-Recent Labeled Outcome on Evidence Summary

Surface the newest labeled assessment in the ≤100 scan when the absolute latest is still
unlabeled. See
[docs/architecture/decisions/0080-phase-79-most-recent-labeled-evidence-summary.md](docs/architecture/decisions/0080-phase-79-most-recent-labeled-evidence-summary.md).

#### Added

- Evidence-summary fields ``most_recent_labeled_assessment_id`` and
  ``most_recent_labeled_outcome_label``.
- Console “Scan-labeled …” rows when they differ from absolute latest.

#### Explicitly out of scope

Changing ``latest_assessment`` identity, default-on calibration, invented labels, orders.

### Phase 78 - NAS Live Verification of Phase 77

Ops evidence gate: redeploy frontend under lab TLS with Phase 77 horizon detail expand.
Live verify passed 2026-07-30. See
[docs/architecture/decisions/0079-phase-78-nas-live-verify-phase-77.md](docs/architecture/decisions/0079-phase-78-nas-live-verify-phase-77.md).

#### Added

- ADR-0079: live verify requires frontend recreate for Phase 77 expand UX; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 77 - Evidence-Summary Horizon Detail Expand

Clickable readiness-by-horizon mini-rows show nested ``by_horizon.detail`` when expanded.
See
[docs/architecture/decisions/0078-phase-77-horizon-detail-expand.md](docs/architecture/decisions/0078-phase-77-horizon-detail-expand.md).

#### Added

- Evidence-summary horizon mini-row toggle revealing nested readiness ``detail``.

#### Explicitly out of scope

New API fields, default-on calibration, gate changes, orders.

### Phase 76 - Evidence-Summary Nested Corpus/Bucket Verify Assertion

Ops hardening: assert nested ``corpus_count`` / ``min_corpus`` / ``bucket_count`` /
``min_bucket`` on authenticated evidence-summary (+ export). Live verify passed 2026-07-30
(``corpus=100/min 10``, ``bucket=20/min 5``). See
[docs/architecture/decisions/0077-phase-76-evidence-summary-corpus-bucket-verify.md](docs/architecture/decisions/0077-phase-76-evidence-summary-corpus-bucket-verify.md).

#### Added

- ADR-0077 and verify checklist item for Phase 71 corpus/bucket callout fields.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 75 - Evidence-Summary Nested by_horizon Verify Assertion

Ops hardening: assert authenticated evidence-summary (+ export) nested
``calibration_readiness.by_horizon`` includes ``forward_return_5`` and ``forward_return_20``.
Live verify passed 2026-07-30. See
[docs/architecture/decisions/0076-phase-75-evidence-summary-by-horizon-verify.md](docs/architecture/decisions/0076-phase-75-evidence-summary-by-horizon-verify.md).

#### Added

- ADR-0076 and verify checklist item for nested evidence-summary ``by_horizon`` keys.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 74 - NAS Live Verification of Phase 73

Ops evidence gate: redeploy frontend under lab TLS with Phase 73 by_horizon mini-rows.
Live verify passed 2026-07-30. See
[docs/architecture/decisions/0075-phase-74-nas-live-verify-phase-73.md](docs/architecture/decisions/0075-phase-74-nas-live-verify-phase-73.md).

#### Added

- ADR-0075: live verify requires frontend recreate for Phase 73 horizon rows; prior gates remain.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 73 - Per-Horizon Readiness Mini-Rows on Evidence Summary

Show nested ``by_horizon`` readiness status/corpus/bucket on the evidence summary after the
aggregate corpus callout. See
[docs/architecture/decisions/0074-phase-73-per-horizon-readiness-evidence-summary.md](docs/architecture/decisions/0074-phase-73-per-horizon-readiness-evidence-summary.md).

#### Added

- Evidence-summary “Readiness by horizon” mini-rows from nested ``calibration_readiness.by_horizon``.

#### Explicitly out of scope

New API fields, default-on calibration, gate changes, orders.

### Phase 72 - NAS Live Verification of Phase 71 (and pending 67–70)

Ops evidence gate: redeploy under lab TLS once SSH is restored; Phase 70 checks remain
mandatory. Live verify of ``94cf550`` passed on 2026-07-30 (closes Phases 70 and 72). See
[docs/architecture/decisions/0073-phase-72-nas-live-verify-phase-71.md](docs/architecture/decisions/0073-phase-72-nas-live-verify-phase-71.md).

#### Added

- ADR-0073: combined resume gate for Phases 67–71 when NAS SSH recovers.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 71 - Calibration Corpus Callout on Evidence Summary

Show readiness ``corpus_count`` / ``min_corpus`` and bucket counts on the evidence summary
next to mixed label coverage. See
[docs/architecture/decisions/0072-phase-71-calibration-corpus-callout-evidence-summary.md](docs/architecture/decisions/0072-phase-71-calibration-corpus-callout-evidence-summary.md).

#### Added

- Evidence-summary console rows for calibration corpus and bucket from nested readiness.

#### Explicitly out of scope

New API fields, Phase 70 NAS live verify (SSH-blocked), default-on calibration, orders.

### Phase 70 - NAS Live Verification of Phases 67–69

Ops evidence gate: redeploy under lab TLS and confirm mixed unlabeled/labeled coverage
fields (Phases 67–69). Live deploy remains blocked while NAS SSH is down; scripts and ADR
are committed for resume. See
[docs/architecture/decisions/0071-phase-70-nas-live-verify-phases-67-69.md](docs/architecture/decisions/0071-phase-70-nas-live-verify-phases-67-69.md).

#### Added

- ADR-0071: combined live verify for ``mixed_unlabeled_assessment_count``,
  ``mixed_labeled_assessment_count``, ``latest_mixed_label_bar_source``, and labeled+unlabeled
  == mixed count.
- Verify checklist item for Phase 70 mixed labeled count.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 69 - Explicit Mixed Labeled Count on Evidence Summary

Add ``mixed_labeled_assessment_count`` and console “N of M mixed” so labeled vs unlabeled
cross-source coverage is auditable at a glance. See
[docs/architecture/decisions/0070-phase-69-mixed-labeled-count-evidence-summary.md](docs/architecture/decisions/0070-phase-69-mixed-labeled-count-evidence-summary.md).

#### Added

- Evidence-summary field ``mixed_labeled_assessment_count`` (mixed − unlabeled).
- Console “Mixed labeled (scanned)” row with “of N mixed”.

#### Explicitly out of scope

Phase 68 NAS live verify (SSH-blocked), gate/math changes, default-on calibration, orders.

### Phase 68 - NAS Live Verification of Phase 67

Ops evidence gate: redeploy under lab TLS and confirm mixed label coverage fields on
evidence-summary. See
[docs/architecture/decisions/0069-phase-68-nas-live-verify-phase-67.md](docs/architecture/decisions/0069-phase-68-nas-live-verify-phase-67.md).

#### Added

- ADR-0069: live verify requires ``mixed_unlabeled_assessment_count`` and
  ``latest_mixed_label_bar_source`` on evidence-summary (+ export).
- Verify checklist item for Phase 68 mixed label coverage.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 67 - Mixed Label Coverage on Evidence Summary

Surface how many scanned mixed assessments still lack labels and the newest mixed label
``bar_source`` on the research evidence summary. See
[docs/architecture/decisions/0068-phase-67-mixed-label-coverage-evidence-summary.md](docs/architecture/decisions/0068-phase-67-mixed-label-coverage-evidence-summary.md).

#### Added

- Evidence-summary fields: ``mixed_unlabeled_assessment_count``,
  ``latest_mixed_label_bar_source``.
- Console rows for mixed unlabeled count and latest mixed label bar source.

#### Explicitly out of scope

Gate/math changes, default-on calibration, NAS live verify, actionable promotion, orders.

### Phase 66 - NAS Live Verification of Phase 65

Ops evidence gate: redeploy under lab TLS so prefer-mixed label backfill is live. See
[docs/architecture/decisions/0067-phase-66-nas-live-verify-phase-65.md](docs/architecture/decisions/0067-phase-66-nas-live-verify-phase-65.md).

#### Added

- ADR-0067: live verify requires backend recreate + ``outcome-labels/backfill?limit=100``.
- Verify checklist item for Phase 66 prefer-mixed backfill path.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 65 - Prefer Mixed Assessments in Outcome-Label Backfill

Prefer unlabeled label-ready ``component_source=mixed`` assessments when selecting backfill
candidates, and resolve true-mixed label bar sources from as-of provenance. See
[docs/architecture/decisions/0066-phase-65-prefer-mixed-label-backfill.md](docs/architecture/decisions/0066-phase-65-prefer-mixed-label-backfill.md).

#### Changed

- Backfill candidate order: mixed-first, then newest-first within each tier.
- ``resolve_label_bar_source`` accepts bars to pick a concrete source for true-mixed series.

#### Explicitly out of scope

Weakening gates, default-on calibration, NAS live verify, actionable promotion, orders.

### Phase 64 - NAS Live Verification of Phase 63

Ops evidence gate: redeploy under lab TLS so the one-click mixed history filter is live.
See
[docs/architecture/decisions/0065-phase-64-nas-live-verify-phase-63.md](docs/architecture/decisions/0065-phase-64-nas-live-verify-phase-63.md).

#### Added

- ADR-0065: live verify requires frontend recreate + full verify (Phase 62 mixed API retained;
  console one-click covered by Phase 63 unit tests).
- Verify checklist item for Phase 64 frontend redeploy.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 63 - One-Click Mixed Filter from Evidence Summary

Operator console: jump from evidence-summary mixed count to filtered assessment history.
See
[docs/architecture/decisions/0064-phase-63-one-click-mixed-filter.md](docs/architecture/decisions/0064-phase-63-one-click-mixed-filter.md).

#### Added

- Evidence-summary mixed-count control applies history ``component_source=mixed`` filter
  and scrolls to assessment history.

#### Explicitly out of scope

Gate/math changes, default-on calibration, NAS live verify, actionable promotion, orders.

### Phase 62 - NAS Live Verification of Phase 61

Ops evidence gate: redeploy under lab TLS and confirm assessment list/export
``component_source=mixed`` filtering. See
[docs/architecture/decisions/0063-phase-62-nas-live-verify-phase-61.md](docs/architecture/decisions/0063-phase-62-nas-live-verify-phase-61.md).

#### Added

- ADR-0063: live verify requires filtered assessments list+export for ``component_source=mixed``.
- Verify checklist item for Phase 62 mixed filter.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 61 - Assessment History Component-Source Filter

Operator filter/export of assessment history by ``component_source`` (including mixed-only)
so cross-source rows are auditable without scrolling. See
[docs/architecture/decisions/0062-phase-61-assessment-history-component-source-filter.md](docs/architecture/decisions/0062-phase-61-assessment-history-component-source-filter.md).

#### Added

- Optional ``component_source`` query param on ``GET .../assessments`` and
  ``GET .../assessments/export`` (scan ≤252 newest, return ≤``limit`` matches).
- Console history source filter and ``src=`` provenance on history rows; export honors filter.

#### Explicitly out of scope

Gate changes, default-on calibration, NAS live verify, actionable promotion, orders.

### Phase 60 - NAS Live Verification of Phase 59

Ops evidence gate: redeploy under lab TLS and confirm evidence-summary provenance fields.
See
[docs/architecture/decisions/0061-phase-60-nas-live-verify-phase-59.md](docs/architecture/decisions/0061-phase-60-nas-live-verify-phase-59.md).

#### Added

- ADR-0061: live verify requires ``latest_component_source``,
  ``latest_resolved_label_bar_source``, and ``mixed_component_source_assessment_count`` on
  evidence-summary (+ export).
- Verify checklist item for Phase 60 provenance fields.

#### Explicitly out of scope

New math, default-on calibration, ACME, actionable promotion, orders.

### Phase 59 - Cross-Source Provenance in Evidence Summary

Surface ``component_source=mixed`` and resolved label ``bar_source`` on the research evidence
summary for audit transparency when cross-source fill is used. See
[docs/architecture/decisions/0060-phase-59-cross-source-provenance-evidence-summary.md](docs/architecture/decisions/0060-phase-59-cross-source-provenance-evidence-summary.md).

#### Added

- Evidence-summary fields: ``latest_component_source``, ``latest_resolved_label_bar_source``,
  ``mixed_component_source_assessment_count``.
- Console evidence-summary provenance rows; annotate ``mixed`` as cross-source fill.

#### Explicitly out of scope

Changing assessment/label math, default-on calibration, NAS live verify, actionable promotion,
orders.

### Phase 58 - NAS Live Verification of Phase 57

Ops evidence gate: redeploy under lab TLS with source-aware label backfill and
``limit=100`` throughput path. See
[docs/architecture/decisions/0059-phase-58-nas-live-verify-phase-57.md](docs/architecture/decisions/0059-phase-58-nas-live-verify-phase-57.md).

#### Added

- ADR-0059: live verify requires ``outcome-labels/backfill?limit=100`` → 200 with persist
  when source-ready candidates exist; Phase 48/50 coupling retained at ``limit=20``.
- Verify checklist item for Phase 58 throughput backfill.

#### Explicitly out of scope

New label math, default-on calibration, ACME, actionable promotion, orders.

### Phase 57 - Source-Aware Label Backfill Throughput

Grow labeling of unlabeled assessments by matching readiness to compute bar sources and
raising scan/default limits. See
[docs/architecture/decisions/0058-phase-57-source-aware-label-backfill-throughput.md](docs/architecture/decisions/0058-phase-57-source-aware-label-backfill-throughput.md).

#### Changed

- Label-ready selection uses resolved assessment bar source + all forward horizons
  (omit false-ready rows that would fail closed at compute).
- ``BACKFILL_SCAN_LIMIT`` **252**; API default ``limit=100`` (max 252); console uses 100.

#### Explicitly out of scope

Weakening label gates, default-on calibration, NAS live verify, actionable promotion, orders.

### Phase 56 - NAS Live Verification of Phase 55

Ops evidence gate: redeploy under lab TLS with cross-source fill enabled and session-depth
research loads live. See
[docs/architecture/decisions/0057-phase-56-nas-live-verify-phase-55.md](docs/architecture/decisions/0057-phase-56-nas-live-verify-phase-55.md).

#### Added

- ADR-0057: live verify requires ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true``
  on ``.env.nas``, backend recreate, and prefer new assessment backfill persists when older
  secondary-filled as-of dates unlock.
- Verify checklist item for the cross-source fill flag.

#### Explicitly out of scope

New assessment math, default-on calibration, ACME, actionable promotion, orders.

### Phase 55 - Research Cross-Source Fill and Session-Depth Bar Load

Unlock older assessment as-of dates when primary compact history is shallow but secondary
(Polygon) history is deep. See
[docs/architecture/decisions/0056-phase-55-research-cross-source-session-depth.md](docs/architecture/decisions/0056-phase-55-research-cross-source-session-depth.md).

#### Changed

- Default ``AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL`` to ``true`` (still overridable).
- Research bar loads use ``list_recent_for_sessions`` so ``AEGIS_RESEARCH_BAR_LOAD_LIMIT``
  counts distinct trading dates, not dual-source observation rows.
- Compose pass-through for the cross-source fill flag (local + NAS).

#### Explicitly out of scope

NAS live verify, default-on calibration, actionable promotion, orders, ACME.

### Phase 54 - NAS Live Verification of Phase 53

Ops evidence gate: redeploy under lab TLS with ``AEGIS_DAILY_BAR_OUTPUT_SIZE=full``,
re-ingest, and verify deeper stored bars unlock backfill growth. See
[docs/architecture/decisions/0055-phase-54-nas-live-verify-phase-53.md](docs/architecture/decisions/0055-phase-54-nas-live-verify-phase-53.md).

#### Added

- ADR-0055: live verify requires ``full`` output size on ``.env.nas``, backend recreate,
  authenticated ingest, and retained Phase 48/50 coupling.
- Compose pass-through for daily-bar primary/secondary sources and Polygon API key so
  Alpha Vantage premium ``full`` gates can failover to Polygon.
- Verify checklist item for ``AEGIS_DAILY_BAR_OUTPUT_SIZE=full``.

#### Explicitly out of scope

New assessment math, default-on calibration, ACME, actionable promotion, orders.

### Phase 53 - Full Daily-Bar History for Research Corpus Growth

Default provider lookback to ``full`` so ``AEGIS_RESEARCH_BAR_LOAD_LIMIT=252`` can load
deeper stored series after re-ingest. See
[docs/architecture/decisions/0054-phase-53-full-daily-bar-history.md](docs/architecture/decisions/0054-phase-53-full-daily-bar-history.md).

#### Changed

- ``AEGIS_DAILY_BAR_OUTPUT_SIZE`` default ``full`` (``compact`` remains valid for light labs).
- Compose backend pass-through for ``AEGIS_DAILY_BAR_OUTPUT_SIZE`` (local + NAS overlay).
- Ops note: recreate backend and re-run ingest after switching an existing deploy to ``full``.
- Document that free Alpha Vantage rejects ``outputsize=full`` (premium); secondary Polygon
  failover is the research path when configured.

#### Explicitly out of scope

Automatic history rebuild jobs, guaranteeing readiness ``ready``, default-on calibration,
actionable promotion, orders, ACME.

### Phase 52 - NAS Live Verification of Phase 51

Ops evidence gate: redeploy under the lab TLS profile with
``AEGIS_RESEARCH_BAR_LOAD_LIMIT=252`` and verify assessment/label backfill on the live NAS.
See
[docs/architecture/decisions/0053-phase-52-nas-live-verify-phase-51.md](docs/architecture/decisions/0053-phase-52-nas-live-verify-phase-51.md).

#### Added

- ``AEGIS_RESEARCH_BAR_LOAD_LIMIT`` wired into Compose backend environment (local + NAS
  overlay) so ``.env.nas`` / ``.env`` values reach the container (default ``252``).
- ADR-0053: live verify requires bar-load setting on ``.env.nas`` and retains Phase 48/50
  coupling; new assessment persistence preferred when deeper stored bars unlock candidates.
- Checklist / docs updates for Phase 52.

#### Explicitly out of scope

Ingest ``outputsize`` / re-ingest, new assessment math, default-on calibration, ACME,
actionable promotion, orders.

### Phase 51 - Configurable Research Bar Load Limit

Configurable recent-bar depth for assessment and outcome-label paths so operators can grow
beyond a saturated 120-bar window. See
[docs/architecture/decisions/0052-phase-51-research-bar-load-limit.md](docs/architecture/decisions/0052-phase-51-research-bar-load-limit.md).

#### Added

- ``AEGIS_RESEARCH_BAR_LOAD_LIMIT`` (default ``252``) shared by on-demand assess, assessment
  backfill, and outcome-label / Phase 49 selection (ADR-0052).
- Assessment backfill existing as-of scan expands with the configured bar load.

#### Explicitly out of scope

Guaranteeing readiness ``ready``, ingest depth changes, auto-chaining backfills, default-on
calibration, actionable promotion, orders, ACME.

### Phase 50 - NAS Live Verification of Phase 49

Ops evidence gate: redeploy under the lab TLS profile and verify unlabeled label-ready
outcome-label backfill (``limit=20``) on the live NAS. See
[docs/architecture/decisions/0051-phase-50-nas-live-verify-phase-49.md](docs/architecture/decisions/0051-phase-50-nas-live-verify-phase-49.md).

#### Added

- ADR-0051: live verify confirms Phase 48 coupling still holds with outcome-label backfill
  ``limit=20`` after Phase 49 candidate selection.
- Checklist / docs updates for Phase 50.

#### Explicitly out of scope

New assessment/label math, default-on calibration, ACME, actionable promotion, orders.

### Phase 49 - Prefer Unlabeled Label-Ready Outcome-Label Backfill

Prefer unlabeled assessments with stored forward-horizon closes so default ``limit=20``
grows the labeled corpus without tip / already-labeled waste. See
[docs/architecture/decisions/0050-phase-49-prefer-unlabeled-label-backfill.md](docs/architecture/decisions/0050-phase-49-prefer-unlabeled-label-backfill.md).

#### Changed

- ``POST .../outcome-labels/backfill`` scans up to 100 assessments, omits rows that already
  have ``forward_total_return_v1`` labels or lack forward-horizon closes, then labels up to
  ``limit`` remaining candidates (ADR-0050).
- NAS verify outcome-label backfill uses ``limit=20`` again (Phase 48 coupling retained).

#### Explicitly out of scope

Raising ``BAR_LOAD_LIMIT``, auto-chaining assessment→label backfill, default-on calibration,
actionable promotion, orders, ACME.

### Phase 48 - NAS Live Verification of Phase 47

Ops evidence gate: redeploy under the lab TLS profile and verify label-ready assessment
backfill coupling on the live NAS. See
[docs/architecture/decisions/0049-phase-48-nas-live-verify-phase-47.md](docs/architecture/decisions/0049-phase-48-nas-live-verify-phase-47.md).

#### Added

- ADR-0049: live verify retains Phase 46 assessment-backfill checks and adds Phase 48
  coupling (when assessments ``persisted_count > 0``, outcome-label backfill must
  ``persisted_count >= 1``; label backfill uses ``limit=100``).
- `verify.ps1` / `verify.sh` Phase 48 gates.

#### Explicitly out of scope

New assessment/label math, default-on calibration, ACME, actionable promotion, orders.

### Phase 47 - Label-Ready Assessment Backfill Candidates

Prefer as-of dates that already have stored forward-horizon closes so Phase 43 labeling
can persist. See
[docs/architecture/decisions/0048-phase-47-label-ready-assessment-backfill.md](docs/architecture/decisions/0048-phase-47-label-ready-assessment-backfill.md).

#### Changed

- Assessment backfill candidate selection (ADR-0048): newest-first among primary dates
  with a close on the session ``max(FORWARD_HORIZON_SESSIONS)`` after ``as_of``; tip dates
  without forward coverage are omitted (``candidate_count=0`` when none qualify).

#### Explicitly out of scope

Default-on calibration, auto-label after assessment backfill, raising bar load limits,
actionable promotion, orders, ACME.

### Phase 46 - NAS Live Verification of Phase 45

Ops evidence gate: redeploy current revision under the lab TLS profile and verify
assessment backfill on the live NAS. See
[docs/architecture/decisions/0047-phase-46-nas-live-verify-phase-45.md](docs/architecture/decisions/0047-phase-46-nas-live-verify-phase-45.md).

#### Added

- ADR-0047: live verify includes unauth **401** and auth **200** summary for
  `POST .../assessments/backfill`.
- `verify.ps1` / `verify.sh` Phase 46 gates.

#### Explicitly out of scope

New assessment math, default-on calibration, ACME, actionable promotion, orders.

### Phase 45 - Historical Research Assessment Backfill

Research-only batch creation of point-in-time assessments for past primary bar dates so
operators can grow labeled corpus candidates. See
[docs/architecture/decisions/0046-phase-45-assessment-backfill.md](docs/architecture/decisions/0046-phase-45-assessment-backfill.md).

#### Added

- `POST /research/{symbol}/assessments/backfill?limit=` — truncate bars to each as-of,
  fail-closed per date, always 200 with summary counts.
- Operator console "Backfill assessments" control.
- ADR-0046.

#### Explicitly out of scope

Default-on calibration, auto-labeling during assessment backfill, rewriting history,
actionable promotion, orders, ACME/public TLS.

### Phase 44 - NAS Live Verification of Phase 43

Ops evidence gate: redeploy current revision under the lab TLS profile and verify
outcome-label backfill on the live NAS. See
[docs/architecture/decisions/0045-phase-44-nas-live-verify-phase-43.md](docs/architecture/decisions/0045-phase-44-nas-live-verify-phase-43.md).

#### Added

- ADR-0045: live verify includes unauth **401** and auth **200** summary for
  `POST .../outcome-labels/backfill`.
- `verify.ps1` / `verify.sh` Phase 44 gates.

#### Explicitly out of scope

New labeling math, default-on calibration, ACME, actionable promotion, orders.

### Phase 43 - Historical Outcome-Label Backfill

Research-only batch re-attempt of `forward_total_return_v1` labels over recent assessment
history so operators can grow the labeled corpus toward calibration readiness. See
[docs/architecture/decisions/0044-phase-43-outcome-label-backfill.md](docs/architecture/decisions/0044-phase-43-outcome-label-backfill.md).

#### Added

- `POST /research/{symbol}/outcome-labels/backfill?limit=` — fail-closed per assessment;
  always 200 with summary counts.
- Operator console "Backfill outcome labels" control.
- ADR-0044.

#### Explicitly out of scope

Default-on calibration, new horizons, guaranteeing readiness `ready`, actionable promotion,
orders, ACME/public TLS.

### Phase 42 - NAS Live Verification of Phase 41

Ops evidence gate: redeploy current revision under the lab TLS profile and verify
multi-horizon calibration readiness (`by_horizon`, alembic `0009`) on the live NAS. See
[docs/architecture/decisions/0043-phase-42-nas-live-verify-phase-41.md](docs/architecture/decisions/0043-phase-42-nas-live-verify-phase-41.md).

#### Added

- ADR-0043: live verify asserts readiness/`export` `by_horizon` for `forward_return_5` and
  `forward_return_20`; optional authenticated `POST .../calibrations?horizon=` (200 or
  fail-closed 422).
- `verify.ps1` / `verify.sh` Phase 42 gates (alembic `0009` already required).

#### Explicitly out of scope

ACME, new horizons, default-on calibration, actionable promotion, orders.

### Phase 41 - Multi-Horizon Probability Calibration

Horizon-specific research_calibration_v1 for `forward_return_5` and `forward_return_20`. See
[docs/architecture/decisions/0042-phase-41-multi-horizon-calibration.md](docs/architecture/decisions/0042-phase-41-multi-horizon-calibration.md).

#### Added

- Alembic `0009` `outcome_horizon_key` on calibration rows (backfill `forward_return_5`).
- `POST .../calibrations?horizon=`; readiness `by_horizon[]`; console horizon surfacing.
- ADR-0042.

#### Explicitly out of scope

New horizons beyond 5/20, default-on calibration, actionable promotion, orders, TLS changes.

### Phase 40 - NAS Lab TLS Live Cutover

Enable Phase 9 Caddy TLS on the live NAS with lab hosts, remapped ports, and self-signed
PEMs. See
[docs/architecture/decisions/0041-phase-40-nas-lab-tls-cutover.md](docs/architecture/decisions/0041-phase-40-nas-lab-tls-cutover.md)
and [docs/operations/nas-tls-cutover.md](docs/operations/nas-tls-cutover.md).

#### Added

- ADR-0041 lab profile (`aegis.local` / `api.aegis.local`, HTTPS `18443`, HTTP `18080`).
- Cutover/rollback runbook; `generate-lab-certs.ps1` / `.sh`.
- Caddy non-443 redirect via `AEGIS_TLS_HTTPS_PORT`; verify Caddy running + optional
  `AEGIS_NAS_VERIFY_CURL_RESOLVE`.

#### Explicitly out of scope

ACME, public DNS, multi-horizon calibration, default-on calibration, actionable promotion,
orders.

### Phase 39 - NAS Live Verification of Phase 38

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/assessments/export` on the live NAS. See
[docs/architecture/decisions/0040-phase-39-nas-live-verify-phase-38.md](docs/architecture/decisions/0040-phase-39-nas-live-verify-phase-38.md).

#### Added

- ADR-0040: live verify includes assessments export (401 unauth; attachment array when auth).
- `verify.ps1` / `verify.sh` assessments export auth gate + authenticated attachment check.

#### Explicitly out of scope

New assessment methods, default-on calibration, actionable promotion, orders, TLS cutover.

### Phase 38 - Assessment History JSON Export

Authenticated download of append-only research assessments for a symbol. See
[docs/architecture/decisions/0039-phase-38-assessments-export.md](docs/architecture/decisions/0039-phase-38-assessments-export.md).

#### Added

- `GET /research/{symbol}/assessments/export?limit=` — same JSON array as the list route
  with `Content-Disposition: attachment`.
- Operator console "Download assessments JSON" control.
- ADR-0039.

#### Explicitly out of scope

Default-on calibration, new methods, actionable promotion, orders, TLS cutover, CSV/PDF.

### Phase 37 - NAS Live Verification of Phase 36

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/assessments/{id}/calibrations/export` on the live NAS. See
[docs/architecture/decisions/0038-phase-37-nas-live-verify-phase-36.md](docs/architecture/decisions/0038-phase-37-nas-live-verify-phase-36.md).

#### Added

- ADR-0038: live verify includes calibrations export (401 unauth; attachment array when auth).
- `verify.ps1` / `verify.sh` calibrations export auth gate + authenticated attachment check.

#### Explicitly out of scope

New calibration methods, default-on calibration, actionable promotion, orders, TLS cutover.

### Phase 36 - Calibration History JSON Export

Authenticated download of append-only probability calibrations for an assessment. See
[docs/architecture/decisions/0037-phase-36-calibrations-export.md](docs/architecture/decisions/0037-phase-36-calibrations-export.md).

#### Added

- `GET /research/{symbol}/assessments/{id}/calibrations/export?limit=` — same JSON array
  as the list route with `Content-Disposition: attachment`.
- Operator console "Download calibrations JSON" control.
- ADR-0037.

#### Explicitly out of scope

Default-on calibration, new methods, actionable promotion, orders, TLS cutover, CSV/PDF.

### Phase 35 - NAS Live Verification of Phase 34

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/assessments/{id}/outcome-labels/export` on the live NAS. See
[docs/architecture/decisions/0036-phase-35-nas-live-verify-phase-34.md](docs/architecture/decisions/0036-phase-35-nas-live-verify-phase-34.md).

#### Added

- ADR-0036: live verify includes outcome-labels export (401 unauth; attachment array when auth).
- `verify.ps1` / `verify.sh` outcome-labels export auth gate + authenticated attachment check.

#### Explicitly out of scope

New label methods, default-on calibration, actionable promotion, orders, TLS cutover.

### Phase 34 - Outcome-Label History JSON Export

Authenticated download of append-only outcome labels for an assessment. See
[docs/architecture/decisions/0035-phase-34-outcome-labels-export.md](docs/architecture/decisions/0035-phase-34-outcome-labels-export.md).

#### Added

- `GET /research/{symbol}/assessments/{id}/outcome-labels/export?limit=` — same JSON array
  as the list route with `Content-Disposition: attachment`.
- Operator console "Download outcome labels JSON" control.
- ADR-0035.

#### Explicitly out of scope

New label methods, default-on calibration, actionable promotion, orders, TLS cutover,
CSV/PDF.

### Phase 33 - NAS Live Verification of Phase 32

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/calibration-readiness/export` on the live NAS. See
[docs/architecture/decisions/0034-phase-33-nas-live-verify-phase-32.md](docs/architecture/decisions/0034-phase-33-nas-live-verify-phase-32.md).

#### Added

- ADR-0034: live verify includes readiness export (401 unauth; attachment when auth).
- `verify.ps1` / `verify.sh` readiness export auth gate + authenticated attachment check.

#### Explicitly out of scope

Default-on calibration, horizon-specific methods, actionable promotion, orders, TLS cutover.

### Phase 32 - Calibration Readiness JSON Export

Authenticated download of calibration readiness diagnostics for offline audit. See
[docs/architecture/decisions/0033-phase-32-calibration-readiness-export.md](docs/architecture/decisions/0033-phase-32-calibration-readiness-export.md).

#### Added

- `GET /research/{symbol}/calibration-readiness/export` — same payload as readiness with
  `Content-Disposition: attachment`.
- Operator console "Download readiness JSON" control.
- ADR-0033.

#### Explicitly out of scope

Default-on calibration, horizon-specific methods, actionable promotion, orders, TLS cutover,
CSV/PDF.

### Phase 31 - NAS Live Verification of Phase 30

Ops evidence gate: redeploy current revision (Phase 30 end-date UI) and re-run live verify
on the NAS. See
[docs/architecture/decisions/0032-phase-31-nas-live-verify-phase-30.md](docs/architecture/decisions/0032-phase-31-nas-live-verify-phase-30.md).

#### Added

- ADR-0032: redeploy + verify; evidence-summary logs present `label_end_dates` keys only.
- `verify.ps1` / `verify.sh` log `end_date_keys` alongside label keys.

#### Explicitly out of scope

New methods, horizon-specific calibration, default-on calibration, actionable promotion,
orders, TLS cutover.

### Phase 30 - Outcome Label End-Date Surfacing

Operator console shows `label_end_dates` next to present horizon returns (API payload only).
See
[docs/architecture/decisions/0031-phase-30-label-end-date-surfacing.md](docs/architecture/decisions/0031-phase-30-label-end-date-surfacing.md).

#### Changed

- Outcome-label detail, history, and evidence summary include end trading dates when present.
- ADR-0031.

#### Explicitly out of scope

New horizons/methods, horizon-specific calibration, default-on calibration, actionable
promotion, orders, TLS cutover.

### Phase 29 - NAS Live Verification of Phase 28

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/assessments?limit=` on the live NAS. See
[docs/architecture/decisions/0030-phase-29-nas-live-verify-phase-28.md](docs/architecture/decisions/0030-phase-29-nas-live-verify-phase-28.md).

#### Added

- ADR-0030: live verify includes assessments list (401 unauth; 200 JSON array when auth).
- `verify.ps1` / `verify.sh` assessments list auth gate + authenticated check.

#### Explicitly out of scope

New methods, horizon-specific calibration, default-on calibration, actionable promotion,
orders, TLS cutover.

### Phase 28 - Research Assessment History in the Console

Operator console shows newest-first assessment history from the existing list API. See
[docs/architecture/decisions/0029-phase-28-assessment-history-console.md](docs/architecture/decisions/0029-phase-28-assessment-history-console.md).

#### Added

- Assessment history block (when more than one snapshot): computed_at, research_index,
  coverage_confidence, probability_confidence (null-safe).
- ADR-0029.

#### Explicitly out of scope

New assessment methods, horizon-specific calibration, default-on calibration, actionable
promotion, orders, TLS cutover.

### Phase 27 - NAS Live Verification of Phase 26

Ops evidence gate: redeploy current revision (Phase 26 multi-horizon UI) and re-run live
verify on the NAS. See
[docs/architecture/decisions/0028-phase-27-nas-live-verify-phase-26.md](docs/architecture/decisions/0028-phase-27-nas-live-verify-phase-26.md).

#### Added

- ADR-0028: redeploy + verify; evidence-summary logs present label keys only.
- `verify.ps1` / `verify.sh` log present `forward_return_*` keys when labels exist.

#### Explicitly out of scope

New horizons/methods, horizon-specific calibration, default-on calibration, actionable
promotion, orders, TLS cutover.

### Phase 26 - Multi-Horizon Outcome Label Surfacing

Operator console shows every horizon key present on outcome-label payloads (5 and 20
session returns already computed by Phase 13). See
[docs/architecture/decisions/0027-phase-26-multi-horizon-label-surfacing.md](docs/architecture/decisions/0027-phase-26-multi-horizon-label-surfacing.md).

#### Changed

- Evidence summary and outcome-label history render all API `labels` keys (sorted); no
  invented values.
- ADR-0027.

#### Explicitly out of scope

New horizons/methods, horizon-specific calibration, default-on calibration, actionable
promotion, orders, TLS cutover.

### Phase 25 - NAS Live Verification of Phase 24

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/evidence-summary/export` on the live NAS. See
[docs/architecture/decisions/0026-phase-25-nas-live-verify-phase-24.md](docs/architecture/decisions/0026-phase-25-nas-live-verify-phase-24.md).

#### Added

- ADR-0026: live verify includes evidence-summary export (401 unauth; attachment +
  `research_only` when authenticated).
- `verify.ps1` / `verify.sh` export auth gate + authenticated attachment check.

#### Explicitly out of scope

Default-on calibration, multi-horizon methods, actionable promotion, orders, TLS cutover.

### Phase 24 - Research Evidence Summary JSON Export

Authenticated download of the research-only evidence aggregate for offline audit. See
[docs/architecture/decisions/0025-phase-24-evidence-summary-export.md](docs/architecture/decisions/0025-phase-24-evidence-summary-export.md).

#### Added

- `GET /research/{symbol}/evidence-summary/export` — same payload as evidence-summary with
  `Content-Disposition: attachment`.
- Operator console "Download evidence JSON" control.
- ADR-0025.

#### Explicitly out of scope

Multi-horizon methods, default-on calibration, actionable promotion, orders, CSV/PDF.

### Phase 23 - NAS Live Verification of Phase 22

Ops evidence gate: redeploy current revision and verify
`GET /research/{symbol}/evidence-summary` on the live NAS. See
[docs/architecture/decisions/0024-phase-23-nas-live-verify-phase-22.md](docs/architecture/decisions/0024-phase-23-nas-live-verify-phase-22.md).

#### Added

- ADR-0024: live verify includes authenticated evidence-summary (state=`research_only`).
- `verify.ps1` / `verify.sh` evidence-summary auth gate + authenticated check.

#### Explicitly out of scope

Default-on calibration, multi-horizon methods, actionable promotion, orders.

### Phase 22 - Symbol Research Evidence Summary

Authenticated read-only aggregate of research evidence for one symbol (latest assessment,
readiness, latest label/calibration, history counts). See
[docs/architecture/decisions/0023-phase-22-research-evidence-summary.md](docs/architecture/decisions/0023-phase-22-research-evidence-summary.md).

#### Added

- ADR-0023: `GET /research/{symbol}/evidence-summary`; operator console evidence summary
  section. Missing fields are null/zero — never invented.

#### Explicitly out of scope

Multi-horizon methods, default-on calibration, actionable promotion, orders.

### Phase 21 - NAS Live Verification of Phases 18–20

Ops evidence gate: redeploy current revision to the UGREEN NAS and verify on-demand
calibration plus calibration/outcome-label history routes. See
[docs/architecture/decisions/0022-phase-21-nas-live-verify-phases-18-20.md](docs/architecture/decisions/0022-phase-21-nas-live-verify-phases-18-20.md).

#### Added

- ADR-0022: live verify includes authenticated `GET .../calibrations` and
  `GET .../outcome-labels` (JSON arrays; empty `[]` allowed).
- `verify.ps1` history list checks after login.

#### Explicitly out of scope

Default-on calibration, multi-horizon methods, actionable promotion, orders.

### Phase 20 - Outcome Label History

Authenticated list of append-only `forward_total_return_v1` rows for an assessment so
operators can audit repeated labeling. See
[docs/architecture/decisions/0021-phase-20-outcome-label-history.md](docs/architecture/decisions/0021-phase-20-outcome-label-history.md).

#### Added

- ADR-0021: `GET .../assessments/{id}/outcome-labels?limit=` (newest first; empty `[]` when
  none); operator console label history when more than one row exists.
- Mirrors Phase 19 calibration history; no new label method.

#### Explicitly out of scope

Multi-horizon method changes, default-on calibration, actionable promotion, orders.

### Phase 19 - Calibration History

Authenticated list of append-only `research_calibration_v1` rows for an assessment so
operators can audit repeated on-demand calibrations. See
[docs/architecture/decisions/0020-phase-19-calibration-history.md](docs/architecture/decisions/0020-phase-19-calibration-history.md).

#### Added

- ADR-0020: `GET .../assessments/{id}/calibrations?limit=` (newest first; empty `[]` when
  none); operator console calibration history when more than one row exists.
- Reuses Phase 15/18 persistence; no new method or automatic-calibration default change.

#### Explicitly out of scope

Multi-horizon methods, default-on calibration, actionable promotion, orders.

### Phase 18 - On-Demand Probability Calibration

Authenticated on-demand `research_calibration_v1` when readiness is `ready`, without enabling
global automatic calibration. See
[docs/architecture/decisions/0019-phase-18-on-demand-calibration.md](docs/architecture/decisions/0019-phase-18-on-demand-calibration.md).

#### Added

- ADR-0019: `POST` / `GET .../calibrations` and `.../calibrations/latest`; operator console
  “Compute calibration” when readiness status is `ready`.
- Reuses Phase 15 math and corpus gates; fail-closed HTTP 422; flag default remains `false`.

#### Explicitly out of scope

Default-on calibration, multi-horizon methods, actionable promotion, orders, and NAS live
deploy changes.

### Phase 17 - NAS Live Verification (Ops Evidence Gate)

Hardens the package/deploy/**verify** boundary for the current research-only stack: auth
gates include calibration-readiness, authenticated readiness checks, Alembic through `0008`,
and an explicit dry-run that is not acceptance evidence. See
[docs/architecture/decisions/0018-phase-17-nas-live-verification.md](docs/architecture/decisions/0018-phase-17-nas-live-verification.md)
and [docs/operations/nas-live-verification.md](docs/operations/nas-live-verification.md).

#### Added

- ADR-0018: live-verified definition; dry-run vs evidence.
- `verify.ps1` / `verify.sh`: calibration-readiness 401 gate, operator login + authenticated
  research/readiness checks, Alembic `0008|head`, `-DryRun` / `--dry-run`.
- Operator checklist and runbook updates; optional `AEGIS_NAS_VERIFY_SYMBOL`.

#### Explicitly out of scope

Default-on calibration, actionable promotion, orders, and NAS hardware provisioning.

### Phase 16 - Calibration Corpus Readiness & Operator Diagnostics

Read-only readiness diagnostics for Phase 15 corpus gates so operators can inspect whether
`research_calibration_v1` would pass before enabling calibration. See
[docs/architecture/decisions/0017-phase-16-calibration-readiness.md](docs/architecture/decisions/0017-phase-16-calibration-readiness.md).

#### Added

- ADR-0017: `GET /research/{symbol}/calibration-readiness`; domain
  `evaluate_calibration_readiness`; operator console readiness section.
- No new persistence; never invents `probability_confidence`.

#### Explicitly out of scope

Enabling calibration by default, actionable promotion, orders, and NAS live deployment.

### Phase 15 - Research Probability Calibration v1

First research-only `research_calibration_v1` empirical probability from stored labeled
historical corpus. Fail-closed when corpus gates fail; `state` remains `research_only`. See
[docs/architecture/decisions/0016-phase-15-research-probability-calibration.md](docs/architecture/decisions/0016-phase-15-research-probability-calibration.md).

#### Added

- ADR-0016: append-only `research_assessment_probability_calibrations` (migration `0008`);
  `AEGIS_RESEARCH_CALIBRATION_AFTER_LABEL_ENABLED` (default `false`); API overlay of latest
  calibration onto `probability_confidence`; scheduled/on-demand wiring after assessments.
- Operator console labels non-null probability as calibrated research-only.

#### Explicitly out of scope

Actionable promotion, orders, portfolio analytics, and NAS live deployment.

### Phase 14 - Scheduled Outcome Labels After Research Assessments

Automatic Phase 13 `forward_total_return_v1` labeling after successful research assessments
from post-ingest research and on-demand assessment creation. Fail-closed skips log and persist
nothing; `probability_confidence` remains null. See
[docs/architecture/decisions/0015-phase-14-scheduled-outcome-labels.md](docs/architecture/decisions/0015-phase-14-scheduled-outcome-labels.md).

#### Added

- ADR-0015: `AEGIS_RESEARCH_OUTCOME_LABEL_AFTER_ASSESSMENT_ENABLED` (local and NAS example
  default `true`); domain orchestration `scheduled_outcome_labels`; wiring in scheduled ingest
  lock, on-demand ingest, and on-demand assessment paths.
- Post-ingest research summary now carries persisted `assessment_snapshot_id` for labeling.

#### Explicitly out of scope

Probability calibration, actionable promotion, orders, and new label methods.

### Phase 13 - Research Outcome Labels (Calibration Evidence Prep)

Append-only forward-return outcome labels linked to research assessment snapshots.
`probability_confidence` remains null; labels are evidence only, not calibrated
probabilities. See
[docs/architecture/decisions/0014-phase-13-research-outcome-labels.md](docs/architecture/decisions/0014-phase-13-research-outcome-labels.md).

#### Added

- ADR-0014: `forward_total_return_v1` horizons 5 and 20 trading sessions; fail-closed;
  on-demand POST/GET under `/research/{symbol}/assessments/{id}/outcome-labels`.
- Table `research_assessment_outcome_labels` (migration `0007`).
- Operator console presentation of outcome labels when available.

#### Explicitly out of scope

Probability calibration, actionable promotion, orders. Automatic post-assessment labeling is
added in Phase 14 (ADR-0015).

### Phase 12 - Provider Historical Corrections (Append-Only)

When a provider revises a historical daily bar, AEGIS inserts a new `correction` observation
row with provenance instead of silently skipping or overwriting the prior row. Reads return
the latest `ingested_at` per `(source, symbol, trading_date)`. See
[docs/architecture/decisions/0013-phase-12-provider-historical-corrections.md](docs/architecture/decisions/0013-phase-12-provider-historical-corrections.md).

#### Added

- ADR-0013: material change detection, `observation_kind`, `supersedes_observation_id`,
  current-bar read policy, out of scope.
- Alembic `0006`: drop unique constraint on `(source, symbol, event_time)`; add correction
  columns and index for current-bar queries.
- Domain `bars_materially_differ`; ingestion inserts corrections with structured logging;
  `corrected_count` on ingest results.
- Setting `AEGIS_MARKET_DATA_CORRECTION_PRICE_EPSILON` (default `1e-6`).

#### Explicitly out of scope

Calibration, blended bars, actionable promotion, orders, correction history API, and live NAS
deploy from this phase.

### Phase 11 - Multi-Source Coverage Weighting (Research-Only)

Extends research assessment `coverage_confidence` with multi-source availability and
agreement factors when multiple daily-bar sources exist for a symbol's lookback window.
Component return/vol/index series stay single preferred source (no OHLCV blend).
`probability_confidence` remains null; `state` remains `research_only`. See
[docs/architecture/decisions/0012-phase-11-multi-source-coverage-weighting.md](docs/architecture/decisions/0012-phase-11-multi-source-coverage-weighting.md).

#### Added

- ADR-0012: method_version 2, preferred-source components, coverage formula, disagreement
  floor (`0.80`), feature flag, provenance fields, out of scope.
- Domain: multi-source factors on `daily_bar_research_v1`; optional cross-source component
  fill (default off); optional disagreement fail-closed; schema_version 2 components
  provenance.
- Settings / `.env.example` / `.env.nas.example`:
  `AEGIS_RESEARCH_MULTI_SOURCE_COVERAGE_ENABLED`,
  `AEGIS_RESEARCH_MULTI_SOURCE_CLOSE_TOLERANCE`,
  `AEGIS_RESEARCH_MULTI_SOURCE_DISAGREEMENT_FAIL_CLOSED`,
  `AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL`.
- Operator console: presentation-only factor / component-source fields when present.
- Tests for single-source agreement=1, soft disagreement penalty, hard reject, and fill.

#### Explicitly out of scope

Calibration, blended bars, corrections, actionable promotion, orders, and live NAS deploy
from this phase.

### Phase 10 - Second Daily-Bar Market-Data Provider (Polygon + failover)

Adds Polygon.io daily aggregates as a second typed `DailyBarProvider`, with configuration-
driven primary selection and optional per-symbol failover on rate-limit / unavailable
errors. Alpha Vantage remains selectable as primary or secondary. Research method
unchanged (`research_only`, `probability_confidence=null`). See
[docs/architecture/decisions/0011-phase-10-second-market-data-provider.md](docs/architecture/decisions/0011-phase-10-second-market-data-provider.md).

#### Added

- ADR-0011: provider pick, source ids (`alpha_vantage`, `polygon`), failover matrix, out of
  scope.
- `aegis.providers.polygon.PolygonProvider` (unadjusted daily aggs; Bearer auth; typed
  errors); `ProviderUnavailableError`; settings for primary/secondary and Polygon keys.
- Shared ingest wiring for on-demand and scheduled paths; successful writes use the producing
  adapter's `source` (no silent provenance swap).
- Tests: Polygon httpx mocks; failover orchestration; settings validation. No live network
  in CI.
- Docs / `.env.example` / `.env.nas.example` placeholders.

#### Explicitly out of scope

Calibration, actionable promotion, orders, corrections, intraday, multi-source consensus /
blended bars, auth changes, and live NAS deploy from this phase.

### Phase 9 - NAS Reverse-Proxy / TLS Packaging for Secure Cookies

Optional Caddy reverse-proxy + TLS termination for the UGREEN NAS Compose stack so operators
can use HTTPS with `AEGIS_SESSION_COOKIE_SECURE=true`. Packaging and ops only; application
session auth (Phase 4) remains the source of truth. Proxy is TLS + routing — not Basic Auth.
No product scoring expansion. See
[docs/architecture/decisions/0010-phase-9-nas-tls-reverse-proxy.md](docs/architecture/decisions/0010-phase-9-nas-tls-reverse-proxy.md).

#### Added

- ADR-0010: prefer Caddy; optional Compose overlay; operator PEMs and/or ACME; dual-host
  routing; cookie/CORS fail-closed alignment; forwarded headers documented.
- `docker/nas/docker-compose.nas.tls.yml` (unpublish API/frontend host ports; publish 443/80;
  Caddy service).
- Proxy templates under `docker/nas/proxy/` (`Caddyfile.files`, `Caddyfile.acme`); certs
  directory placeholders only (no committed PEMs).
- `.env.nas.example` TLS placeholders; package/deploy/verify/validate-local honor
  `AEGIS_NAS_TLS_ENABLED` and fail closed without required TLS material.
- Docs: NAS runbook, nas-deployment, configuration, overview, CI compose dry-run for TLS.

#### Explicitly out of scope

Live NAS deploy from CI, OAuth/MFA, calibration, actionable promotion, orders, second
provider, and application auth changes - each remains absent. Local dev stays HTTP +
Secure=false.

### Phase 8 - Scheduled Research Assessments After Ingest

After each successful locked scheduled ingest cycle (and after successful on-demand
`POST /market-data/ingest` when configured), automatically run Phase 6
`daily_bar_research_v1` for active watchlist symbols using stored bars only. Persist
append-only snapshots on success; skip with structured logs on fail-closed (no row). Keep
`state=research_only`, coverage set, `probability_confidence=null`. See
[docs/architecture/decisions/0009-phase-8-scheduled-research.md](docs/architecture/decisions/0009-phase-8-scheduled-research.md).

#### Added

- Backend: `domain.scheduled_research.run_research_after_ingest` (Protocol-based, per-symbol
  fail-closed); optional research inside `run_locked_ingestion_cycle` before lock release;
  scheduler and on-demand ingest wiring; setting
  `AEGIS_RESEARCH_SCHEDULE_AFTER_INGEST_ENABLED` (local and NAS example default `true`).
- Frontend: research panel copy notes post-ingest snapshots may appear after ingest
  (presentation only; RESEARCH ONLY labels unchanged).
- Docs: ADR-0009; overview and configuration updates; `.env.example` / `.env.nas.example`.

#### Explicitly out of scope

Calibration, actionable promotion, recommendations, chart signals, orders, TLS changes, and
NAS live verify - each remains absent.

### Phase 7 - UGREEN NAS Deployment Packaging

Packages the existing research-only authenticated stack for UGREEN NAS DXP-series hardware
(`linux/amd64`). Does not add actionable promotion, calibration, scheduled assessments, a
second provider, orders, OAuth, MFA, or RBAC. See
[docs/architecture/decisions/0008-phase-7-nas-deployment.md](docs/architecture/decisions/0008-phase-7-nas-deployment.md)
and [docker/nas/README.md](docker/nas/README.md).

#### Added

- Compose overlay `docker/nas/docker-compose.nas.yml` (extends root compose; no fork): amd64
  platform, always-restart, Postgres/Redis unpublished on the host, production-leaning
  defaults, image tags for save/load.
- `.env.nas.example` placeholders; `.env.nas` gitignored; frontend Dockerfile build-arg for
  `NEXT_PUBLIC_API_BASE_URL` (baked at package time).
- Scripts under `docker/nas/scripts/`: `package`, `deploy`, `verify`, `validate-local`
  (PowerShell + shell). Fail closed on missing env; reject default/template NAS passwords.
  Deploy applies Alembic through `0005`; verify checks health/ready/auth gate/key routes/
  frontend and documents log inspection. Upload ≠ verified deployment.
- Docs: ADR-0008; NAS runbook; `docs/operations/nas-deployment.md`; overview/README/CI notes.

#### Explicitly out of scope

Actionable promotion, calibration, scheduled assessments, second provider, order placement,
OAuth/MFA/RBAC, and committed hostnames/IPs/credentials - each remains absent.

### Phase 6 - Research-Only Scoring Foundations

On-demand research-only assessments over stored primary daily bars. Fail-closed when inputs
are incomplete; every success payload is `state=research_only` with non-null
`coverage_confidence` and null `probability_confidence`. No recommendations, actionable
promotion, calibration, or order placement; see
[docs/architecture/decisions/0007-phase-6-research-only-scoring.md](docs/architecture/decisions/0007-phase-6-research-only-scoring.md).

#### Added

- Backend: domain method `daily_bar_research_v1` (20-session return, annualized realized vol,
  `research_index`); append-only `research_assessment_snapshots` (Alembic `0005`);
  authenticated `POST/GET /research/{symbol}/assessments` and
  `GET /research/{symbol}/assessments/latest`; HTTP 422 structured `detail.reason` on gate
  failures with no persistence.
- Frontend: `ResearchAssessmentPanel` on `/symbols/[symbol]` with RESEARCH ONLY labeling;
  typed API client methods; presentation-only (no client-side research math).
- Docs: ADR-0007; architecture overview and data-model updates for research snapshots.

#### Explicitly out of scope

Actionable promotion, calibration / non-null probability confidence, scheduled assessments,
chart signal overlays, second provider, OAuth/MFA, order placement, and NAS deployment -
each is absent, not merely unimplemented, per the Phase 6 plan.

### Phase 5 - Daily Bar Charts

Candlestick OHLC + volume charts on the authenticated symbol page, using the existing
daily-bars API and TradingView Lightweight Charts. No scoring, recommendation, prediction,
indicators, signals, or order-placement logic exists in this phase; see
[docs/architecture/decisions/0006-phase-5-daily-bar-charts.md](docs/architecture/decisions/0006-phase-5-daily-bar-charts.md).

#### Added

- Frontend: `lightweight-charts` dependency; `DailyBarsChart` Client Component (candlestick +
  volume histogram, dispose on unmount, empty/error-safe); adapter mapping newest-first API
  bars to chronological series; chart above `DailyBarsTable` on `/symbols/[symbol]` with
  accessible name `{symbol} daily OHLC chart`.
- Docs: ADR-0006; architecture overview and frontend README updates for Phase 5.

#### Explicitly out of scope

Backend API/schema changes, technical indicators, scoring/recommendations/signals, auth
changes, order placement, and NAS deployment - each is absent, not merely unimplemented, per
the Phase 5 plan.

### Phase 4 - Operator Authentication

Cookie-based operator sessions protect watchlist and market-data HTTP routes. No scoring,
recommendation, prediction, chart libraries, OAuth/MFA, multi-role RBAC, or order-placement
logic exists in this phase; see
[docs/architecture/decisions/0005-phase-4-operator-auth.md](docs/architecture/decisions/0005-phase-4-operator-auth.md).

#### Added

- Backend auth: `operators` table (Alembic migration `0004`); Argon2 password hashes; Redis
  session store with httpOnly cookie (`AEGIS_SESSION_*`); `POST /auth/login`,
  `POST /auth/logout`, `GET /auth/me`; session dependency on `/watchlist*` and
  `/market-data*`; seed-once bootstrap from `AEGIS_OPERATOR_USERNAME` /
  `AEGIS_OPERATOR_PASSWORD` when the operators table is empty; CORS
  `allow_credentials=True` with the existing origin allow-list. `/health` and `/ready` remain
  public.
- Frontend: `/login` page; API client `credentials: "include"`; 401 redirects to login;
  `requireOperator` SSR gate on protected console routes; logout clears the session.
- Configuration and docs: operator/session settings in `.env.example` and
  [docs/operations/configuration.md](docs/operations/configuration.md); ADR-0005;
  local-development login and migration notes.

#### Explicitly out of scope

OAuth/SSO, MFA, password-reset email, multi-role authorization, charts/scoring/recommendations,
order placement, and NAS deployment - each is absent, not merely unimplemented, per the
Phase 4 plan.

### Phase 3 - Operator Console (Frontend)

A browser operator console for the existing Phase 1/2 APIs: manage the watchlist, trigger
on-demand ingest, and browse stored daily bars as a table. No scoring, recommendation,
prediction, chart libraries, authentication, or order-placement logic exists in this phase;
see
[docs/architecture/decisions/0004-phase-3-operator-console.md](docs/architecture/decisions/0004-phase-3-operator-console.md).

#### Added

- Frontend console (`frontend/`): `/` watchlist + ingest panels; `/symbols/[symbol]` daily-bar
  table; Source Sans 3 / IBM Plex Mono typography; typed API client extensions for watchlist,
  ingest, and daily bars; Vitest coverage for the client and key components.
- Backend CORS: `AEGIS_CORS_ORIGINS` setting and `CORSMiddleware` so the Next.js origin can call
  the API from the browser; Compose passes the setting through; unit tests cover allow-listed
  vs rejected preflight origins.

#### Explicitly out of scope

Authentication, chart libraries/indicators/scoring, schedule configuration UI, second
providers, corrections, and NAS deployment - each is absent, not merely unimplemented, per the
Phase 3 plan.

### Phase 2 - Scheduled Ingestion & Database-Backed Watchlist

Ingestion now runs automatically on a schedule, and the watchlist moves from a static
environment variable to a database-backed list manageable via the API while the service is
running. No scoring, recommendation, prediction, or order-placement logic exists anywhere in
this phase; see
[docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md](docs/architecture/decisions/0003-phase-2-scheduled-watchlist.md)
for the confirmed decisions (scheduler, coordination lock, watchlist storage, bootstrap,
validation, auth) and their accepted limitations.

#### Added

- Domain layer (`backend/src/aegis/domain/`): `watchlist.py` (`normalize_symbol`, a
  framework-free shape validator for user-submitted symbols) and `scheduled_ingestion.py`
  (`run_locked_ingestion_cycle`, a framework-free, `Protocol`-based lock-guarded ingestion
  cycle - independently unit-tested with fake Redis/watchlist/ingestion-service doubles, no
  real I/O).
- Persistence (`backend/src/aegis/persistence/`): `WatchlistSymbol` model and
  `WatchlistRepository` (`list_active`, `list_active_rows`, `add`, `deactivate`,
  `ensure_seeded`), plus an Alembic migration (`0003`) creating `watchlist_symbols` as a plain
  (non-hypertable) table with a unique constraint on `symbol`. Unlike
  `market_daily_bar_observations`, this table is a mutable, soft-deletable operational list,
  not an append-only observation (see ADR-0003).
- API (`backend/src/aegis/api/`): `GET /watchlist`, `POST /watchlist`, and
  `DELETE /watchlist/{symbol}` for watchlist management; `POST /market-data/ingest` now reads
  the active database-backed watchlist instead of `AEGIS_WATCHLIST_SYMBOLS` directly.
  `scheduler.py` wires an APScheduler `AsyncIOScheduler` into the application lifespan, running
  `run_locked_ingestion_cycle` on a cron schedule (`AEGIS_INGESTION_CRON`) guarded by a Redis
  lock (`AEGIS_INGESTION_SCHEDULE_LOCK_KEY`/`_TTL_SECONDS`) so multiple backend replicas can
  never run overlapping cycles; disabled entirely via `AEGIS_INGESTION_SCHEDULE_ENABLED=false`.
- Configuration: `AEGIS_INGESTION_SCHEDULE_ENABLED`, `AEGIS_INGESTION_CRON`,
  `AEGIS_INGESTION_SCHEDULE_LOCK_KEY`, `AEGIS_INGESTION_SCHEDULE_LOCK_TTL_SECONDS`, documented
  in `.env.example` and `docs/operations/configuration.md`. `AEGIS_WATCHLIST_SYMBOLS`'s role
  changes from "the watchlist" to "the one-time bootstrap seed" for the database table.
- Unit tests for symbol validation, the locked scheduled-ingestion cycle (fake doubles, no real
  I/O), the watchlist endpoints (dependency overrides), and scheduler lifespan wiring
  (enabled/disabled); a new cross-service integration test
  (`tests/integration/test_watchlist_repository_docker.py`) verifying the migration and the
  repository's add/deactivate/reactivate/seed behavior against the real Compose Postgres
  service.
- `apscheduler` added as a new main runtime dependency.

#### Explicitly out of scope

Any scoring/probability/confidence/recommendation computation, order placement/transmission,
frontend changes, authentication on any endpoint, a second data provider or intraday
granularity, and a separate worker process or multi-replica-aware scheduling beyond the Redis
lock - each is absent, not merely unimplemented, per the Phase 2 plan.

### Phase 1 - Market Data Ingestion (Alpha Vantage daily bars)

The first real external data integration: a typed Alpha Vantage provider adapter, validated
daily-bar rejection rules, an append-only TimescaleDB observation store, and on-demand
ingest/read API endpoints. No scoring, recommendation, prediction, or order-placement logic
exists anywhere in this phase; see
[docs/architecture/decisions/0002-phase-1-market-data-ingestion.md](docs/architecture/decisions/0002-phase-1-market-data-ingestion.md)
for the confirmed decisions (provider, granularity, trigger, watchlist, calendar, auth,
idempotency) and their accepted limitations.

#### Added

- Provider adapter (`backend/src/aegis/providers/`): `DailyBarProvider` protocol,
  `AlphaVantageProvider` (Alpha Vantage `TIME_SERIES_DAILY`, unadjusted daily OHLCV), and typed
  `ProviderError`/`ProviderRateLimitError` for both HTTP failures and Alpha Vantage's
  "200 OK with an error body" responses (invalid symbol, rate limit, premium-tier gate).
- Domain layer (`backend/src/aegis/domain/`): a swappable exchange-calendar wrapper
  (`calendars.py`, backed by `pandas-market-calendars`); daily-bar validation
  (`market_data_validation.py`) implementing every rejection rule from
  `docs/architecture/market-data-contracts.md` (invalid OHLC shape, non-positive values,
  closed-session/non-trading-day, and latest-bar staleness); and `MarketDataIngestionService`
  (`market_data_ingestion.py`) orchestrating fetch, validate, and idempotent persistence per
  watchlist symbol, isolating one symbol's provider failure from the rest of the run.
- Persistence (`backend/src/aegis/persistence/`): `MarketDailyBarObservation` model and
  `MarketDailyBarRepository`, plus an Alembic migration creating
  `market_daily_bar_observations` as a TimescaleDB hypertable (partitioned on `event_time`)
  with a unique constraint on `(source, symbol, event_time)` for idempotent re-ingestion.
- API (`backend/src/aegis/api/`): `POST /market-data/ingest` (runs one ingestion cycle over the
  configured watchlist) and `GET /market-data/{symbol}/daily-bars` (reads stored bars, 404 for
  an unknown symbol). No authentication in Phase 1 (self-hosted, local/trusted-network only;
  see ADR-0002).
- Configuration: `AEGIS_ALPHA_VANTAGE_API_KEY`, `AEGIS_ALPHA_VANTAGE_BASE_URL`,
  `AEGIS_ALPHA_VANTAGE_REQUEST_INTERVAL_SECONDS`, `AEGIS_WATCHLIST_SYMBOLS`,
  `AEGIS_DAILY_BAR_OUTPUT_SIZE`, `AEGIS_EXCHANGE_CALENDAR_NAME`, and
  `AEGIS_MAX_LATEST_BAR_STALENESS_TRADING_DAYS`, documented in `.env.example` and
  `docs/operations/configuration.md`.
- Unit tests for the provider adapter (`httpx.MockTransport`), calendar wrapper, validation
  rules, ingestion orchestration (fake provider/repository doubles, no real I/O), and both API
  endpoints (dependency overrides); a new cross-service integration test
  (`tests/integration/test_market_data_repository_docker.py`) verifying the migration,
  hypertable, and idempotent insert/read round trip against the real Compose Postgres/
  TimescaleDB service.
- `httpx` promoted from a test-only to a main runtime dependency; `pandas-market-calendars`
  added as a new main runtime dependency.

#### Explicitly out of scope

Order placement/transmission, any scoring/probability/confidence/recommendation computation,
background/scheduled ingestion, authentication on the new endpoints, a database-backed
watchlist, and any frontend change - each is absent, not merely unimplemented, per the Phase 1
plan.

### Phase 0 - Architecture & Repository Foundation

Repository and architecture foundation. No scoring, recommendation, prediction, or order-
placement logic exists anywhere in this phase; see
[docs/architecture/decisions/0001-phase-0-tooling.md](docs/architecture/decisions/0001-phase-0-tooling.md)
for the tooling decisions and
[docs/operations/](docs/operations/) for operational documentation.

#### Added

- Architecture documentation: system overview, data-model conventions (append-only,
  versioned, provenance-aware observations; coverage vs. probability confidence;
  research-only vs. actionable state), and market-data quote-rejection contracts.
- Backend service (`backend/`): FastAPI application on Python 3.12 managed with `uv`, exposing
  `/health` (liveness) and `/ready` (readiness against PostgreSQL/TimescaleDB and Redis), a
  baseline Alembic migration enabling the TimescaleDB extension, unit tests, and a scoped
  no-domain-logic structural check.
- Frontend service (`frontend/`): Next.js + TypeScript + Tailwind CSS application managed with
  pnpm, a single placeholder page, a typed API client for the backend health contract, and an
  equivalent no-domain-logic check.
- Local Docker Compose topology (`docker-compose.yml`) with health-checked `postgres`, `redis`,
  `backend`, and `frontend` services, plus pinned, non-root Dockerfiles for the backend and
  frontend and a build-only `linux/amd64` validation step for the UGREEN NAS target
  architecture (`docker/nas/README.md` documents the deployment boundary; no deployment occurs).
- Cross-service integration test (`tests/integration/`) verifying the readiness endpoint against
  the real Compose stack.
- CI workflow (`.github/workflows/ci.yml`) with backend, frontend, compose-validation,
  integration, and security-scanning jobs, and documentation of which gates are local-only vs.
  remote-dependent (`docs/operations/ci.md`).
- Security scanning documentation and local commands for dependency (`pip-audit`, `pnpm audit`),
  secret (`gitleaks`), and container-image (`trivy`) scans (`docs/operations/security-scanning.md`).
- Environment configuration reference (`.env.example`, `docs/operations/configuration.md`) and
  day-to-day developer workflow documentation (`docs/operations/local-development.md`).
- `.gitleaks.toml` allowlisting vendored/build directories for local secret scanning.

#### Fixed

- Backend: bumped `pytest`/`pytest-asyncio` to remediate a `pytest` CVE
  (`PYSEC-2026-1845`).
- Frontend: pinned `sharp` and `postcss` to patched versions via `pnpm-workspace.yaml`
  `overrides` (both are transitive `next` dependencies, not direct dependencies) to remediate
  `GHSA-f88m-g3jw-g9cj`, `GHSA-6g55-p6wh-862q`, `GHSA-r28c-9q8g-f849`, and
  `GHSA-qx2v-qp2m-jg93`.
- Docker images: both Dockerfiles now run `apt-get upgrade` in the final stage to pick up
  Debian security patches published after the pinned base image tag; the frontend image also
  removes the unused, bundled `npm`/`npx` CLI (this image only ever runs `node server.js`),
  eliminating scanner findings for code that is never executed. Both images scan clean at
  `trivy image --severity HIGH,CRITICAL --ignore-unfixed` as of this entry.
