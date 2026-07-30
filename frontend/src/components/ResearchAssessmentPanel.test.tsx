import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ResearchAssessmentPanel } from "./ResearchAssessmentPanel";

vi.mock("@/lib/api-client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api-client")>("@/lib/api-client");
  return {
    ...actual,
    getApiBaseUrl: () => "http://localhost:8000",
    createResearchAssessment: vi.fn(),
    getLatestResearchAssessment: vi.fn(),
    createOutcomeLabels: vi.fn(),
    getLatestOutcomeLabels: vi.fn(),
    getCalibrationReadiness: vi.fn(),
    createProbabilityCalibration: vi.fn(),
    listProbabilityCalibrations: vi.fn(),
  };
});

import {
  ApiClientError,
  createProbabilityCalibration,
  createResearchAssessment,
  getCalibrationReadiness,
  getLatestOutcomeLabels,
  getLatestResearchAssessment,
  listProbabilityCalibrations,
} from "@/lib/api-client";

const sampleAssessment = {
  id: 1,
  symbol: "AAPL",
  method_id: "daily_bar_research_v1",
  method_version: 1,
  state: "research_only",
  as_of_trading_date: "2024-01-26",
  event_time: "2024-01-26T23:59:59Z",
  computed_at: "2024-01-26T18:00:00Z",
  coverage_confidence: 0.95,
  probability_confidence: null,
  components: {
    total_return_20: 0.1,
    realized_vol_20: 0.2,
    research_index: 0.46,
  },
  schema_version: 1,
  input_source: "alpha_vantage",
  lookback_start_date: "2023-12-27",
  lookback_end_date: "2024-01-26",
  bar_count: 20,
};

const sampleCalibration = {
  id: 10,
  assessment_snapshot_id: 1,
  symbol: "AAPL",
  calibration_method_id: "research_calibration_v1",
  calibration_method_version: 1,
  state: "research_only",
  computed_at: "2024-01-26T19:00:00Z",
  probability_confidence: 0.62,
  corpus_count: 12,
  bucket_count: 6,
  schema_version: 1,
};

describe("ResearchAssessmentPanel", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getCalibrationReadiness).mockResolvedValue({
      symbol: "AAPL",
      status: "insufficient_labeled_corpus",
      assessment_snapshot_id: 1,
      research_index: 0.46,
      corpus_count: 3,
      bucket_count: 2,
      min_corpus: 10,
      min_bucket: 5,
      index_bucket_width: 0.15,
      calibration_method_id: "research_calibration_v1",
      detail: "need at least 10 labeled historical examples, found 3",
    });
    vi.mocked(getLatestOutcomeLabels).mockRejectedValue(
      new ApiClientError("missing labels", 404, null),
    );
    vi.mocked(listProbabilityCalibrations).mockResolvedValue([]);
  });

  it("shows research-only labeling and empty state", () => {
    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={null} />);

    expect(screen.getAllByText(/research only/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/no research assessment stored yet/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /compute calibration/i })).toBeDisabled();
  });

  it("renders an initial latest assessment from the API payload", () => {
    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);

    expect(screen.getByText(/state: research only/i)).toBeInTheDocument();
    expect(screen.getByText("0.9500")).toBeInTheDocument();
    expect(screen.getByText(/null \(not calibrated\)/i)).toBeInTheDocument();
    expect(screen.getByText("0.46")).toBeInTheDocument();
  });

  it("runs an assessment through the API and displays the result", async () => {
    vi.mocked(createResearchAssessment).mockResolvedValue(sampleAssessment);

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={null} />);
    fireEvent.click(screen.getByRole("button", { name: /run assessment/i }));

    await waitFor(() => {
      expect(createResearchAssessment).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
      );
    });
    await waitFor(() => {
      expect(screen.getByText(/state: research only/i)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText(/calibration readiness/i)).toBeInTheDocument();
      expect(screen.getByText("insufficient_labeled_corpus")).toBeInTheDocument();
    });
    expect(screen.getByRole("button", { name: /compute calibration/i })).toBeDisabled();
  });

  it("computes calibration when readiness is ready", async () => {
    vi.mocked(getCalibrationReadiness)
      .mockResolvedValueOnce({
        symbol: "AAPL",
        status: "ready",
        assessment_snapshot_id: 1,
        research_index: 0.46,
        corpus_count: 12,
        bucket_count: 6,
        min_corpus: 10,
        min_bucket: 5,
        index_bucket_width: 0.15,
        calibration_method_id: "research_calibration_v1",
        detail: "corpus and bucket gates pass",
      })
      .mockResolvedValue({
        symbol: "AAPL",
        status: "ready",
        assessment_snapshot_id: 1,
        research_index: 0.46,
        corpus_count: 12,
        bucket_count: 6,
        min_corpus: 10,
        min_bucket: 5,
        index_bucket_width: 0.15,
        calibration_method_id: "research_calibration_v1",
        detail: "corpus and bucket gates pass",
      });
    vi.mocked(createProbabilityCalibration).mockResolvedValue(sampleCalibration);
    vi.mocked(listProbabilityCalibrations).mockResolvedValue([sampleCalibration]);

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh readiness/i }));

    const compute = screen.getByRole("button", { name: /compute calibration/i });
    await waitFor(() => {
      expect(screen.getByText("ready")).toBeInTheDocument();
      expect(compute).not.toBeDisabled();
    });
    fireEvent.click(compute);

    await waitFor(() => {
      expect(createProbabilityCalibration).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        1,
      );
    });
    await waitFor(() => {
      expect(listProbabilityCalibrations).toHaveBeenCalled();
      expect(screen.getByText(/probability calibration \(research-only/i)).toBeInTheDocument();
      expect(screen.getByText(/0\.6200 \(calibrated research-only\)/)).toBeInTheDocument();
    });
  });

  it("shows calibration history when more than one row exists", async () => {
    const older = {
      ...sampleCalibration,
      id: 9,
      computed_at: "2024-01-26T18:00:00Z",
      probability_confidence: 0.5,
    };
    vi.mocked(getLatestResearchAssessment).mockResolvedValue(sampleAssessment);
    vi.mocked(listProbabilityCalibrations).mockResolvedValue([sampleCalibration, older]);

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh latest/i }));

    await waitFor(() => {
      expect(screen.getByText(/calibration history \(newest first\)/i)).toBeInTheDocument();
      expect(screen.getByText(/p=0\.6200/)).toBeInTheDocument();
      expect(screen.getByText(/p=0\.5000/)).toBeInTheDocument();
    });
  });

  it("surfaces structured fail-closed errors without inventing numbers", async () => {
    vi.mocked(createResearchAssessment).mockRejectedValue(
      new ApiClientError("gate failed", 422, {
        detail: {
          reason: "insufficient_primary_bars",
          message: "need 20 usable primary bars, found 5",
        },
      }),
    );

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={null} />);
    fireEvent.click(screen.getByRole("button", { name: /run assessment/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(/insufficient_primary_bars/i);
    });
    expect(screen.queryByText(/state: research only/i)).not.toBeInTheDocument();
  });

  it("refresh latest clears when the API returns 404", async () => {
    vi.mocked(getLatestResearchAssessment).mockRejectedValue(
      new ApiClientError("missing", 404, null),
    );

    render(
      <ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />,
    );
    fireEvent.click(screen.getByRole("button", { name: /refresh latest/i }));

    await waitFor(() => {
      expect(screen.getByText(/no research assessment stored yet/i)).toBeInTheDocument();
    });
  });

  it("renders Phase 11 multi-source provenance fields from the API payload", () => {
    const v2 = {
      ...sampleAssessment,
      method_version: 2,
      schema_version: 2,
      components: {
        ...sampleAssessment.components,
        component_source: "alpha_vantage",
        coverage_sources: ["alpha_vantage", "polygon"],
        comparable_dates: 20,
        agreeing_dates: 18,
        source_availability_factor: 1,
        source_agreement_factor: 0.9,
        bar_count_factor: 1,
        freshness_factor: 1,
        primary_fraction: 1,
      },
    };
    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={v2} />);

    expect(screen.getByText("daily_bar_research_v1 v2")).toBeInTheDocument();
    expect(screen.getByText("alpha_vantage")).toBeInTheDocument();
    expect(screen.getByText(/0\.9000 \(18\/20 comparable\)/)).toBeInTheDocument();
  });
});
