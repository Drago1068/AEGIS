import { describe, expect, it } from "vitest";

import {
  distinctAsOfAssessments,
  formatAssessmentHistoryRow,
  formatCalibrationActionAriaLabel,
  formatCalibrationActionIdChip,
  formatLabelHorizonSummary,
  formatOutcomeLabelActionAriaLabel,
  formatOutcomeLabelActionIdChip,
  formatOutcomeLabelBackfillAriaLabel,
  resolveOutcomeLabelHistoryLoadKind,
  sortedLabelEntries,
} from "./research-assessment-panel-helpers";

describe("resolveOutcomeLabelHistoryLoadKind", () => {
  it("preserves an explicit tracked load kind", () => {
    expect(resolveOutcomeLabelHistoryLoadKind(3, "scan_labeled", 4)).toBe("scan_labeled");
    expect(resolveOutcomeLabelHistoryLoadKind(4, "latest", 4)).toBe("latest");
  });

  it("infers latest when assessment matches latest id", () => {
    expect(resolveOutcomeLabelHistoryLoadKind(4, null, 4)).toBe("latest");
  });

  it("infers scan_labeled when assessment differs or latest is missing", () => {
    expect(resolveOutcomeLabelHistoryLoadKind(3, null, 4)).toBe("scan_labeled");
    expect(resolveOutcomeLabelHistoryLoadKind(3, null, null)).toBe("scan_labeled");
    expect(resolveOutcomeLabelHistoryLoadKind(3, null, undefined)).toBe("scan_labeled");
  });
});

describe("formatOutcomeLabelActionAriaLabel", () => {
  it("omits kind suffix when load kind is unset", () => {
    expect(formatOutcomeLabelActionAriaLabel("Compute outcome labels", 1, null)).toBe(
      "Compute outcome labels for assessment 1",
    );
    expect(formatOutcomeLabelActionAriaLabel("Compute ready-horizon labels", 1, null)).toBe(
      "Compute ready-horizon labels for assessment 1",
    );
  });

  it("appends scan-labeled or latest when load kind is tracked", () => {
    expect(
      formatOutcomeLabelActionAriaLabel("Download outcome labels JSON", 3, "scan_labeled"),
    ).toBe("Download outcome labels JSON for assessment 3 (scan-labeled)");
    expect(formatOutcomeLabelActionAriaLabel("Compute outcome labels", 4, "latest")).toBe(
      "Compute outcome labels for assessment 4 (latest)",
    );
  });

  it("returns the bare action when assessment id is null", () => {
    expect(formatOutcomeLabelActionAriaLabel("Compute outcome labels", null, "latest")).toBe(
      "Compute outcome labels",
    );
  });
});

describe("formatOutcomeLabelActionIdChip", () => {
  it("shows id only when load kind is unset", () => {
    expect(formatOutcomeLabelActionIdChip(1, null)).toBe("(1)");
  });

  it("appends scan-labeled or latest when load kind is tracked", () => {
    expect(formatOutcomeLabelActionIdChip(3, "scan_labeled")).toBe("(3 · scan-labeled)");
    expect(formatOutcomeLabelActionIdChip(4, "latest")).toBe("(4 · latest)");
  });
});

describe("formatCalibrationActionAriaLabel", () => {
  it("appends latest when assessment id is set", () => {
    expect(formatCalibrationActionAriaLabel("Compute calibration", 1)).toBe(
      "Compute calibration for assessment 1 (latest)",
    );
    expect(formatCalibrationActionAriaLabel("Download calibrations JSON", 2)).toBe(
      "Download calibrations JSON for assessment 2 (latest)",
    );
  });

  it("returns the bare action when assessment id is null", () => {
    expect(formatCalibrationActionAriaLabel("Compute calibration", null)).toBe(
      "Compute calibration",
    );
  });
});

describe("formatCalibrationActionIdChip", () => {
  it("always includes latest", () => {
    expect(formatCalibrationActionIdChip(1)).toBe("(1 · latest)");
  });
});

describe("formatOutcomeLabelBackfillAriaLabel", () => {
  it("returns the bare action when assessment id is null", () => {
    expect(formatOutcomeLabelBackfillAriaLabel(null, null)).toBe("Backfill outcome labels");
  });

  it("names the refresh target assessment and load kind", () => {
    expect(formatOutcomeLabelBackfillAriaLabel(3, "scan_labeled")).toBe(
      "Backfill outcome labels then refresh assessment 3 (scan-labeled)",
    );
    expect(formatOutcomeLabelBackfillAriaLabel(4, "latest")).toBe(
      "Backfill outcome labels then refresh assessment 4 (latest)",
    );
    expect(formatOutcomeLabelBackfillAriaLabel(1, null)).toBe(
      "Backfill outcome labels then refresh assessment 1",
    );
  });
});

describe("sortedLabelEntries", () => {
  it("orders forward_return_N by horizon ascending then other keys", () => {
    expect(
      sortedLabelEntries({
        z_other: 1,
        forward_return_20: 0.2,
        forward_return_5: 0.05,
        a_other: 2,
      }).map(([k]) => k),
    ).toEqual(["forward_return_5", "forward_return_20", "a_other", "z_other"]);
  });
});

describe("formatLabelHorizonSummary", () => {
  it("formats compact horizon lines with optional end dates", () => {
    expect(formatLabelHorizonSummary({})).toBe("none");
    expect(
      formatLabelHorizonSummary(
        { forward_return_5: 0.05, forward_return_20: 0.1 },
        { forward_return_5: "2024-02-02", forward_return_20: "2024-02-23" },
      ),
    ).toBe("fwd5=0.0500 end=2024-02-02 · fwd20=0.1000 end=2024-02-23");
  });
});

describe("formatAssessmentHistoryRow", () => {
  it("formats compact assessment history lines from API fields only", () => {
    expect(
      formatAssessmentHistoryRow({
        computed_at: "2024-01-01T00:00:00Z",
        coverage_confidence: 0.5,
        probability_confidence: null,
        input_source: "alpha_vantage",
        components: { research_index: 0.1234, component_source: "mixed" },
      }),
    ).toBe(
      "2024-01-01T00:00:00Z · index=0.1234 · cov=0.5000 · p=null · src=mixed",
    );
  });
});

describe("distinctAsOfAssessments", () => {
  it("returns empty for empty input", () => {
    expect(distinctAsOfAssessments([])).toEqual([]);
  });

  it("keeps the newest row per as_of and skips invalid dates", () => {
    const rows = [
      { id: 3, as_of_trading_date: "2024-01-02", computed_at: "later" },
      { id: 2, as_of_trading_date: "2024-01-02", computed_at: "earlier" },
      { id: 1, as_of_trading_date: "2024-01-01", computed_at: "old" },
      { id: 0, as_of_trading_date: "bad", computed_at: "skip" },
    ];
    expect(distinctAsOfAssessments(rows)).toEqual([
      { id: 3, as_of_trading_date: "2024-01-02", computed_at: "later" },
      { id: 1, as_of_trading_date: "2024-01-01", computed_at: "old" },
    ]);
  });
});
