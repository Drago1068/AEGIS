import { describe, expect, it } from "vitest";

import {
  formatOutcomeLabelActionAriaLabel,
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
