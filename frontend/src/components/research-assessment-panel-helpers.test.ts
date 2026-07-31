import { describe, expect, it } from "vitest";

import {
  formatCalibrationActionAriaLabel,
  formatCalibrationActionIdChip,
  formatOutcomeLabelActionAriaLabel,
  formatOutcomeLabelActionIdChip,
  resolveOutcomeLabelHistoryLoadKind,
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
