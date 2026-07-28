# Market Data Quote Validation Contract

This contract defines what must happen at the boundary between an external market data
provider and the rest of AEGIS, before any derived metric is computed. Phase 0 introduced no
providers but established this contract so `providers/` adapters would be built against it
from the start. Phase 1 is the first concrete implementation: `aegis.providers.alpha_vantage`
detects and rejects malformed/error provider responses (see rule "Otherwise unusable" below),
and `aegis.domain.market_data_validation` implements every other rule below for daily bars.
See [decisions/0002-phase-1-market-data-ingestion.md](decisions/0002-phase-1-market-data-ingestion.md)
for how each rule maps to daily-bar granularity specifically.

## Rejection rules

A raw quote or observation MUST be rejected (not stored as valid, not used in any derived
computation) if any of the following hold:

- **Invalid**: fails basic type/shape/range validation (for example non-numeric price,
  missing required fields, malformed timestamp).
- **Stale**: the observation's age exceeds the maximum staleness threshold defined for its
  data class and market session (threshold is provider- and instrument-specific and must be
  configured explicitly, never assumed).
- **Zero or negative**: price, size, or other fields that are only meaningful as positive
  numbers are zero or negative, unless the field is explicitly documented as allowed to be
  zero/negative for that field (for example a signed change value).
- **Closed-session**: the quote is timestamped during a period when the relevant exchange
  calendar shows the market closed for that instrument, unless the record is explicitly
  labeled as an after-hours/extended-session observation and handled as such.
- **Otherwise unusable**: any other provider-specific condition that indicates the value does
  not reflect a real, tradable market state (for example an explicit provider error/warning
  flag on the payload).

## Handling of rejected data

- Rejected observations are not silently dropped without a trace: they are logged (structured
  logging, no secrets) with the rejection reason, so data-quality issues are diagnosable.
- Rejected observations are never used to compute derived metrics, coverage confidence, or any
  downstream value.
- A rejection does not retroactively alter previously stored valid observations.

## Labeling requirements

Any observation that is simulated, delayed, a fallback value, or otherwise incomplete must be
labeled as such in its stored record (see [data-model.md](data-model.md)) and must never be
presented to a user or to downstream logic as equivalent to a validated, real-time,
primary-source observation.

## Exchange calendars

Market-session determination (open/closed, regular/extended session) uses explicit,
per-exchange calendars rather than naive wall-clock heuristics. Calendars are configuration,
not hardcoded logic, so they can be corrected/updated without a code change. Calendar data
itself is versioned like any other input, so historical session determinations remain
reproducible.

## Scope note

Phase 0 did not implement any of the validation logic described here - there were no
providers yet. This document exists so the `providers/` module boundary (see
[overview.md](overview.md)) was designed against a single, agreed contract before its first
implementation. Phase 1 implements this contract for daily-bar granularity only; intraday/
real-time quotes (and therefore true intraday open/closed-session checks) remain deferred.
