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
    backfillOutcomeLabels: vi.fn(),
    backfillResearchAssessments: vi.fn(),
    listOutcomeLabels: vi.fn(),
    getCalibrationReadiness: vi.fn(),
    createProbabilityCalibration: vi.fn(),
    listProbabilityCalibrations: vi.fn(),
    getResearchEvidenceSummary: vi.fn(),
    downloadResearchEvidenceSummary: vi.fn(),
    downloadCalibrationReadiness: vi.fn(),
    downloadOutcomeLabels: vi.fn(),
    downloadProbabilityCalibrations: vi.fn(),
    downloadResearchAssessments: vi.fn(),
    listResearchAssessments: vi.fn(),
  };
});

import {
  ApiClientError,
  backfillOutcomeLabels,
  backfillResearchAssessments,
  createProbabilityCalibration,
  createResearchAssessment,
  downloadCalibrationReadiness,
  downloadOutcomeLabels,
  downloadProbabilityCalibrations,
  downloadResearchAssessments,
  downloadResearchEvidenceSummary,
  createOutcomeLabels,
  getCalibrationReadiness,
  getLatestResearchAssessment,
  getResearchEvidenceSummary,
  listOutcomeLabels,
  listProbabilityCalibrations,
  listResearchAssessments,
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
    vi.mocked(listOutcomeLabels).mockResolvedValue([]);
    vi.mocked(listProbabilityCalibrations).mockResolvedValue([]);
    vi.mocked(listResearchAssessments).mockResolvedValue([]);
    vi.mocked(getResearchEvidenceSummary).mockResolvedValue({
      symbol: "AAPL",
      state: "research_only",
      latest_assessment: null,
      calibration_readiness: {
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
      },
      latest_outcome_label: null,
      latest_calibration: null,
      assessment_count: 0,
      outcome_label_count: 0,
      calibration_count: 0,
      latest_component_source: null,
      latest_resolved_label_bar_source: null,
      mixed_component_source_assessment_count: 0,
      mixed_unlabeled_assessment_count: 0,
      mixed_labeled_assessment_count: 0,
      latest_mixed_label_bar_source: null,
      most_recent_labeled_assessment_id: null,
      most_recent_labeled_outcome_label: null,
      detail: "Research-only evidence summary — not advice; missing fields are null or zero, never invented.",
    });
  });

  it("shows research-only labeling and empty state", () => {
    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={null} />);

    expect(screen.getAllByText(/research only/i).length).toBeGreaterThan(0);
    expect(screen.getByTestId("research-assessment-action-toolbar")).toBeInTheDocument();
    expect(screen.getByTestId("toolbar-group-diagnostics")).toBeInTheDocument();
    expect(screen.getByTestId("toolbar-group-assessments")).toBeInTheDocument();
    expect(screen.getByTestId("toolbar-group-outcome-labels")).toBeInTheDocument();
    expect(screen.getByTestId("toolbar-group-calibration")).toBeInTheDocument();
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
      expect(screen.getAllByText("insufficient_labeled_corpus").length).toBeGreaterThan(0);
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
    expect(screen.getByTestId("compute-calibration")).toHaveAccessibleName(
      /compute calibration for assessment 1 \(latest\)/i,
    );
    expect(screen.getByTestId("compute-calibration-id-chip")).toHaveTextContent("(1 · latest)");
    fireEvent.click(compute);

    await waitFor(() => {
      expect(createProbabilityCalibration).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        1,
        "forward_return_5",
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

  it("shows assessment history when more than one row exists", async () => {
    const older = {
      ...sampleAssessment,
      id: 2,
      computed_at: "2024-01-25T18:00:00Z",
      as_of_trading_date: "2024-01-25",
      coverage_confidence: 0.9,
      probability_confidence: null,
      components: {
        total_return_20: 0.05,
        realized_vol_20: 0.15,
        research_index: 0.4,
      },
    };
    const newer = {
      ...sampleAssessment,
      id: 3,
      computed_at: "2024-01-26T18:00:00Z",
      probability_confidence: 0.62,
    };
    vi.mocked(getLatestResearchAssessment).mockResolvedValue(newer);
    vi.mocked(listResearchAssessments).mockResolvedValue([newer, older]);

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh latest/i }));

    await waitFor(() => {
      expect(screen.getByText(/assessment history \(newest first\)/i)).toBeInTheDocument();
      expect(
        screen.getByText(/2024-01-26T18:00:00Z · index=0\.4600 · cov=0\.9500 · p=0\.6200 · src=alpha_vantage/),
      ).toBeInTheDocument();
      expect(
        screen.getByText(/2024-01-25T18:00:00Z · index=0\.4000 · cov=0\.9000 · p=null · src=alpha_vantage/),
      ).toBeInTheDocument();
      expect(listResearchAssessments).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        20,
        { componentSource: null },
      );
    });
  });

  it("shows outcome label history when more than one row exists", async () => {
    const newer = {
      id: 20,
      assessment_snapshot_id: 1,
      symbol: "AAPL",
      label_method_id: "forward_total_return_v1",
      label_method_version: 1,
      state: "research_only",
      as_of_trading_date: "2024-01-26",
      computed_at: "2024-01-26T20:00:00Z",
      labels: { forward_return_5: 0.05, forward_return_20: 0.1 },
      label_end_dates: {
        forward_return_5: "2024-02-02",
        forward_return_20: "2024-02-23",
      },
      schema_version: 1,
      bar_source: "alpha_vantage",
    };
    const older = {
      ...newer,
      id: 19,
      computed_at: "2024-01-26T18:00:00Z",
      labels: { forward_return_5: 0.03, forward_return_20: 0.08 },
    };
    vi.mocked(getLatestResearchAssessment).mockResolvedValue(sampleAssessment);
    vi.mocked(listOutcomeLabels).mockResolvedValue([newer, older]);

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh latest/i }));

    await waitFor(() => {
      expect(screen.getByTestId("outcome-label-history-section")).toBeInTheDocument();
      expect(screen.getByText(/outcome label history \(newest first\)/i)).toBeInTheDocument();
      expect(screen.getByTestId("outcome-label-history-assessment-id")).toHaveTextContent(
        /assessment id 1/i,
      );
      expect(screen.getByTestId("outcome-label-history-load-kind")).toHaveTextContent(/latest/i);
      expect(
        screen.getByText(
          /fwd5=0\.0500 end=2024-02-02 · fwd20=0\.1000 end=2024-02-23/,
        ),
      ).toBeInTheDocument();
      expect(
        screen.getByText(
          /fwd5=0\.0300 end=2024-02-02 · fwd20=0\.0800 end=2024-02-23/,
        ),
      ).toBeInTheDocument();
      expect(screen.getByText(/0\.050000 · end 2024-02-02/)).toBeInTheDocument();
      expect(screen.getByText(/0\.100000 · end 2024-02-23/)).toBeInTheDocument();
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

  it("shows evidence summary after refresh evidence summary", async () => {
    vi.mocked(getResearchEvidenceSummary).mockResolvedValue({
      symbol: "AAPL",
      state: "research_only",
      latest_assessment: sampleAssessment,
      calibration_readiness: {
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
        by_horizon: [
          {
            outcome_horizon_key: "forward_return_5",
            status: "ready",
            corpus_count: 12,
            bucket_count: 6,
            detail: "ok",
          },
          {
            outcome_horizon_key: "forward_return_20",
            status: "insufficient_bucket",
            corpus_count: 12,
            bucket_count: 2,
            detail: "need bucket",
          },
        ],
      },
      latest_outcome_label: {
        id: 20,
        assessment_snapshot_id: 1,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.05, forward_return_20: 0.1 },
        label_end_dates: {
          forward_return_5: "2024-02-02",
          forward_return_20: "2024-02-23",
        },
        schema_version: 1,
        bar_source: "alpha_vantage",
      },
      latest_calibration: sampleCalibration,
      assessment_count: 2,
      outcome_label_count: 1,
      calibration_count: 1,
      latest_component_source: "mixed",
      latest_resolved_label_bar_source: "alpha_vantage",
      mixed_component_source_assessment_count: 1,
      mixed_unlabeled_assessment_count: 0,
      mixed_labeled_assessment_count: 1,
      latest_mixed_label_bar_source: "alpha_vantage",
      most_recent_labeled_assessment_id: 1,
      most_recent_labeled_outcome_label: {
        id: 20,
        assessment_snapshot_id: 1,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.05, forward_return_20: 0.1 },
        label_end_dates: {
          forward_return_5: "2024-02-02",
          forward_return_20: "2024-02-23",
        },
        schema_version: 1,
        bar_source: "alpha_vantage",
      },
      detail: "Research-only evidence summary — not advice; missing fields are null or zero, never invented.",
    });

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh evidence summary/i }));

    await waitFor(() => {
      expect(screen.getByText(/evidence summary \(research-only/i)).toBeInTheDocument();
      expect(screen.getByText(/assessments \(≤100\)/i)).toBeInTheDocument();
      expect(screen.getByText(/calibration corpus \(readiness\)/i)).toBeInTheDocument();
      expect(screen.getByText(/12 \/ min 10/)).toBeInTheDocument();
      expect(screen.getByText(/calibration bucket \(readiness\)/i)).toBeInTheDocument();
      expect(screen.getByText(/6 \/ min 5/)).toBeInTheDocument();
      expect(screen.getByTestId("evidence-readiness-by-horizon")).toBeInTheDocument();
      expect(screen.getByText(/readiness by horizon/i)).toBeInTheDocument();
      expect(screen.getByTestId("evidence-horizon-forward_return_5")).toHaveTextContent(
        /forward_return_5: ready \(corpus=12, bucket=6\)/,
      );
      expect(screen.getByTestId("evidence-horizon-forward_return_20")).toHaveTextContent(
        /forward_return_20: insufficient_bucket \(corpus=12, bucket=2\)/,
      );
      expect(screen.queryByTestId("evidence-horizon-detail-forward_return_20")).toBeNull();
      expect(screen.getByText("1 / 1")).toBeInTheDocument();
      expect(screen.getByText(/latest component source/i)).toBeInTheDocument();
      expect(
        screen.getByText(/latest component source/i).closest("div"),
      ).toHaveTextContent(/mixed \(cross-source fill\)/);
      expect(screen.getByText(/resolved label bar source/i)).toBeInTheDocument();
      expect(screen.getByText(/mixed-source assessments \(scanned\)/i)).toBeInTheDocument();
      expect(screen.getByText(/mixed unlabeled \(scanned\)/i)).toBeInTheDocument();
      expect(screen.getByText(/mixed labeled \(scanned\)/i)).toBeInTheDocument();
      expect(screen.getByText(/of 1 mixed/i)).toBeInTheDocument();
      expect(screen.getByText(/latest mixed label bar source/i)).toBeInTheDocument();
      expect(screen.getByText(/latest forward_return_5/i)).toBeInTheDocument();
      expect(screen.getByText(/latest forward_return_20/i)).toBeInTheDocument();
      expect(screen.getByText(/0\.0500 · end 2024-02-02/)).toBeInTheDocument();
      expect(screen.getByText(/0\.1000 · end 2024-02-23/)).toBeInTheDocument();
      expect(getResearchEvidenceSummary).toHaveBeenCalledWith("http://localhost:8000", "AAPL");
    });

    fireEvent.click(screen.getByTestId("evidence-horizon-forward_return_20"));
    expect(screen.getByTestId("evidence-horizon-detail-forward_return_20")).toHaveTextContent(
      "need bucket",
    );
    fireEvent.click(screen.getByTestId("evidence-horizon-forward_return_20"));
    expect(screen.queryByTestId("evidence-horizon-detail-forward_return_20")).toBeNull();
  });

  it("downloads evidence summary JSON via export route", async () => {
    vi.mocked(downloadResearchEvidenceSummary).mockResolvedValue(
      "aegis-AAPL-evidence-summary.json",
    );

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /download evidence json/i }));

    await waitFor(() => {
      expect(downloadResearchEvidenceSummary).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
      );
    });
  });

  it("downloads calibration readiness JSON via export route", async () => {
    vi.mocked(downloadCalibrationReadiness).mockResolvedValue(
      "aegis-AAPL-calibration-readiness.json",
    );

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /download readiness json/i }));

    await waitFor(() => {
      expect(downloadCalibrationReadiness).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
      );
    });
  });

  it("downloads outcome labels JSON via export route", async () => {
    vi.mocked(downloadOutcomeLabels).mockResolvedValue(
      "aegis-AAPL-assessment-1-outcome-labels.json",
    );

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /download outcome labels json/i }));

    await waitFor(() => {
      expect(downloadOutcomeLabels).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        1,
        20,
      );
    });
    expect(screen.getByTestId("download-outcome-labels")).toHaveAccessibleName(
      /download outcome labels json for assessment 1/i,
    );
    expect(screen.getByTestId("download-outcome-labels-id-chip")).toHaveTextContent("(1)");
  });

  it("downloads outcome labels JSON for scan-labeled assessment id", async () => {
    vi.mocked(getResearchEvidenceSummary).mockResolvedValue({
      symbol: "AAPL",
      state: "research_only",
      latest_assessment: sampleAssessment,
      calibration_readiness: {
        symbol: "AAPL",
        status: "insufficient_corpus",
        assessment_snapshot_id: 1,
        research_index: 0.46,
        corpus_count: 0,
        bucket_count: 0,
        min_corpus: 10,
        min_bucket: 5,
        index_bucket_width: 0.15,
        calibration_method_id: "research_calibration_v1",
        detail: "research only",
      },
      latest_outcome_label: null,
      latest_calibration: null,
      assessment_count: 2,
      outcome_label_count: 1,
      calibration_count: 0,
      latest_component_source: "alpha_vantage",
      latest_resolved_label_bar_source: null,
      mixed_component_source_assessment_count: 0,
      mixed_unlabeled_assessment_count: 0,
      mixed_labeled_assessment_count: 0,
      latest_mixed_label_bar_source: null,
      most_recent_labeled_assessment_id: 3,
      most_recent_labeled_outcome_label: {
        id: 30,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.02 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
      detail: "Research-only evidence summary — not advice; missing fields are null or zero, never invented.",
    });
    vi.mocked(listOutcomeLabels).mockResolvedValue([
      {
        id: 30,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.02 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
    ]);
    vi.mocked(downloadOutcomeLabels).mockResolvedValue(
      "aegis-AAPL-assessment-3-outcome-labels.json",
    );

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh evidence summary/i }));
    const loadScan = await screen.findByTestId("load-scan-labeled-labels");
    await waitFor(() => {
      expect(loadScan).not.toBeDisabled();
    });
    fireEvent.click(loadScan);
    await waitFor(() => {
      expect(screen.getByTestId("outcome-label-history-assessment-id")).toHaveTextContent(
        /assessment id 3/i,
      );
    });
    vi.mocked(downloadOutcomeLabels).mockClear();
    const downloadBtn = screen.getByTestId("download-outcome-labels");
    await waitFor(() => {
      expect(downloadBtn).not.toBeDisabled();
    });
    fireEvent.click(downloadBtn);

    await waitFor(() => {
      expect(downloadOutcomeLabels).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        3,
        20,
      );
    });
    expect(screen.getByTestId("download-outcome-labels")).toHaveAccessibleName(
      /download outcome labels json for assessment 3 \(scan-labeled\)/i,
    );
    expect(screen.getByTestId("download-outcome-labels-id-chip")).toHaveTextContent(
      "(3 · scan-labeled)",
    );
  });

  it("shows empty-state when loaded assessment has no outcome labels", async () => {
    vi.mocked(getResearchEvidenceSummary).mockResolvedValue({
      symbol: "AAPL",
      state: "research_only",
      latest_assessment: sampleAssessment,
      calibration_readiness: {
        symbol: "AAPL",
        status: "insufficient_corpus",
        assessment_snapshot_id: 1,
        research_index: 0.46,
        corpus_count: 0,
        bucket_count: 0,
        min_corpus: 10,
        min_bucket: 5,
        index_bucket_width: 0.15,
        calibration_method_id: "research_calibration_v1",
        detail: "research only",
      },
      latest_outcome_label: null,
      latest_calibration: null,
      assessment_count: 2,
      outcome_label_count: 0,
      calibration_count: 0,
      latest_component_source: "alpha_vantage",
      latest_resolved_label_bar_source: null,
      mixed_component_source_assessment_count: 0,
      mixed_unlabeled_assessment_count: 0,
      mixed_labeled_assessment_count: 0,
      latest_mixed_label_bar_source: null,
      most_recent_labeled_assessment_id: 3,
      most_recent_labeled_outcome_label: {
        id: 30,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.02 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
      detail: "Research-only evidence summary — not advice; missing fields are null or zero, never invented.",
    });
    vi.mocked(listOutcomeLabels).mockResolvedValue([]);

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh evidence summary/i }));
    const loadScan = await screen.findByTestId("load-scan-labeled-labels");
    await waitFor(() => {
      expect(loadScan).not.toBeDisabled();
    });
    fireEvent.click(loadScan);

    await waitFor(() => {
      expect(screen.getByTestId("outcome-label-history-assessment-id")).toHaveTextContent(
        /assessment id 3/i,
      );
      expect(screen.getByTestId("outcome-label-history-load-kind")).toHaveTextContent(
        /scan-labeled \(latest is 1\)/i,
      );
      expect(screen.getByTestId("outcome-label-empty-state")).toHaveTextContent(
        /no outcome labels stored for assessment 3/i,
      );
      expect(screen.getByTestId("calibration-controls-latest-note")).toHaveTextContent(
        /calibration actions use latest assessment 1 \(panel labels are for 3\)/i,
      );
      expect(screen.getByTestId("load-latest-labels")).toHaveTextContent(
        /load labels for latest 1/i,
      );
    });

    vi.mocked(listOutcomeLabels).mockClear();
    vi.mocked(listOutcomeLabels).mockResolvedValue([]);
    const loadLatest = screen.getByTestId("load-latest-labels");
    await waitFor(() => {
      expect(loadLatest).not.toBeDisabled();
    });
    fireEvent.click(loadLatest);
    await waitFor(() => {
      expect(listOutcomeLabels).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        1,
        20,
      );
      expect(screen.getByTestId("outcome-label-history-assessment-id")).toHaveTextContent(
        /assessment id 1/i,
      );
      expect(screen.getByTestId("outcome-label-history-load-kind")).toHaveTextContent(
        /· latest/i,
      );
      expect(screen.queryByTestId("calibration-controls-latest-note")).not.toBeInTheDocument();
      expect(screen.queryByTestId("load-latest-labels")).not.toBeInTheDocument();
    });
  });

  it("computes outcome labels for scan-labeled assessment id", async () => {
    vi.mocked(getResearchEvidenceSummary).mockResolvedValue({
      symbol: "AAPL",
      state: "research_only",
      latest_assessment: sampleAssessment,
      calibration_readiness: {
        symbol: "AAPL",
        status: "insufficient_corpus",
        assessment_snapshot_id: 1,
        research_index: 0.46,
        corpus_count: 0,
        bucket_count: 0,
        min_corpus: 10,
        min_bucket: 5,
        index_bucket_width: 0.15,
        calibration_method_id: "research_calibration_v1",
        detail: "research only",
      },
      latest_outcome_label: null,
      latest_calibration: null,
      assessment_count: 2,
      outcome_label_count: 0,
      calibration_count: 0,
      latest_component_source: "alpha_vantage",
      latest_resolved_label_bar_source: null,
      mixed_component_source_assessment_count: 0,
      mixed_unlabeled_assessment_count: 0,
      mixed_labeled_assessment_count: 0,
      latest_mixed_label_bar_source: null,
      most_recent_labeled_assessment_id: 3,
      most_recent_labeled_outcome_label: {
        id: 30,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.02 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
      detail: "Research-only evidence summary — not advice; missing fields are null or zero, never invented.",
    });
    vi.mocked(listOutcomeLabels).mockResolvedValue([]);
    vi.mocked(createOutcomeLabels).mockResolvedValue({
      id: 31,
      assessment_snapshot_id: 3,
      symbol: "AAPL",
      label_method_id: "forward_total_return_v1",
      label_method_version: 1,
      state: "research_only",
      as_of_trading_date: "2024-01-26",
      computed_at: "2024-01-26T21:00:00Z",
      labels: { forward_return_5: 0.04 },
      label_end_dates: { forward_return_5: "2024-02-02" },
      schema_version: 1,
      bar_source: "polygon",
    } as never);

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh evidence summary/i }));
    const loadScan = await screen.findByTestId("load-scan-labeled-labels");
    await waitFor(() => {
      expect(loadScan).not.toBeDisabled();
    });
    fireEvent.click(loadScan);
    await waitFor(() => {
      expect(screen.getByTestId("outcome-label-empty-state")).toBeInTheDocument();
    });
    expect(screen.getByTestId("compute-outcome-labels")).toHaveAccessibleName(
      /compute outcome labels for assessment 3 \(scan-labeled\)/i,
    );
    expect(screen.getByTestId("compute-outcome-labels-id-chip")).toHaveTextContent(
      "(3 · scan-labeled)",
    );
    vi.mocked(listOutcomeLabels).mockResolvedValue([
      {
        id: 31,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T21:00:00Z",
        labels: { forward_return_5: 0.04 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
    ]);
    const computeBtn = screen.getByTestId("compute-outcome-labels");
    await waitFor(() => {
      expect(computeBtn).not.toBeDisabled();
    });
    fireEvent.click(computeBtn);

    await waitFor(() => {
      expect(createOutcomeLabels).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        3,
      );
      expect(screen.getByText(/0\.040000 · end 2024-02-02/)).toBeInTheDocument();
      expect(screen.getByTestId("outcome-label-history-load-kind")).toHaveTextContent(
        /scan-labeled \(latest is 1\)/i,
      );
    });
  });

  it("downloads calibrations JSON via export route", async () => {
    vi.mocked(downloadProbabilityCalibrations).mockResolvedValue(
      "aegis-AAPL-assessment-1-calibrations.json",
    );

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /download calibrations json/i }));

    await waitFor(() => {
      expect(downloadProbabilityCalibrations).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        1,
        20,
      );
    });
    expect(screen.getByTestId("download-calibrations")).toHaveAccessibleName(
      /download calibrations json for assessment 1 \(latest\)/i,
    );
    expect(screen.getByTestId("download-calibrations-id-chip")).toHaveTextContent("(1 · latest)");
    expect(screen.queryByTestId("calibration-controls-latest-note")).not.toBeInTheDocument();
  });

  it("downloads assessments JSON via export route", async () => {
    vi.mocked(downloadResearchAssessments).mockResolvedValue("aegis-AAPL-assessments.json");

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /download assessments json/i }));

    await waitFor(() => {
      expect(downloadResearchAssessments).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        20,
        { componentSource: null },
      );
    });
  });

  it("filters assessment history by component_source", async () => {
    const mixedRow = {
      ...sampleAssessment,
      id: 3,
      input_source: "mixed",
      components: {
        ...sampleAssessment.components,
        component_source: "mixed",
      },
    };
    vi.mocked(listResearchAssessments).mockResolvedValue([mixedRow]);

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.change(screen.getByLabelText(/history source filter/i), {
      target: { value: "mixed" },
    });

    await waitFor(() => {
      expect(listResearchAssessments).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        20,
        { componentSource: "mixed" },
      );
      expect(screen.getByText(/src=mixed/)).toBeInTheDocument();
    });
  });

  it("applies mixed history filter from evidence-summary mixed count", async () => {
    const mixedRow = {
      ...sampleAssessment,
      id: 3,
      input_source: "mixed",
      components: {
        ...sampleAssessment.components,
        component_source: "mixed",
      },
    };
    vi.mocked(getResearchEvidenceSummary).mockResolvedValue({
      symbol: "AAPL",
      state: "research_only",
      latest_assessment: sampleAssessment,
      calibration_readiness: {
        symbol: "AAPL",
        status: "insufficient_corpus",
        assessment_snapshot_id: 1,
        research_index: 0.46,
        corpus_count: 0,
        bucket_count: 0,
        min_corpus: 10,
        min_bucket: 5,
        index_bucket_width: 0.15,
        calibration_method_id: "research_calibration_v1",
        detail: "research only",
      },
      latest_outcome_label: null,
      latest_calibration: null,
      assessment_count: 2,
      outcome_label_count: 0,
      calibration_count: 0,
      latest_component_source: "mixed",
      latest_resolved_label_bar_source: null,
      mixed_component_source_assessment_count: 19,
      mixed_unlabeled_assessment_count: 0,
      mixed_labeled_assessment_count: 19,
      latest_mixed_label_bar_source: "polygon",
      most_recent_labeled_assessment_id: 3,
      most_recent_labeled_outcome_label: {
        id: 30,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.02 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
      detail: "Research-only evidence summary — not advice; missing fields are null or zero, never invented.",
    });
    vi.mocked(listResearchAssessments).mockResolvedValue([mixedRow]);

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh evidence summary/i }));

    const showMixed = await screen.findByRole("button", {
      name: /filter assessment history to mixed component source/i,
    });
    expect(showMixed).toHaveTextContent("19");
    await waitFor(() => {
      expect(showMixed).not.toBeDisabled();
    });
    vi.mocked(listResearchAssessments).mockClear();
    fireEvent.click(showMixed);

    await waitFor(() => {
      expect(listResearchAssessments).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        20,
        { componentSource: "mixed" },
      );
      expect(screen.getByLabelText(/history source filter/i)).toHaveValue("mixed");
      expect(screen.getByText(/src=mixed/)).toBeInTheDocument();
    });

    expect(screen.getByTestId("load-scan-labeled-labels")).toHaveTextContent(
      /load labels for assessment 3/i,
    );
    await waitFor(() => {
      expect(screen.getByTestId("load-scan-labeled-labels")).not.toBeDisabled();
    });
    vi.mocked(listOutcomeLabels).mockClear();
    vi.mocked(listOutcomeLabels).mockResolvedValue([
      {
        id: 30,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.02 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
    ]);
    fireEvent.click(screen.getByTestId("load-scan-labeled-labels"));
    await waitFor(() => {
      expect(listOutcomeLabels).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        3,
        20,
      );
      expect(screen.getByTestId("outcome-label-history-assessment-id")).toHaveTextContent(
        /assessment id 3/i,
      );
      expect(screen.getByTestId("outcome-label-history-load-kind")).toHaveTextContent(
        /scan-labeled \(latest is 1\)/i,
      );
    });
  });

  it("runs outcome-label backfill and shows research-only summary counts", async () => {
    vi.mocked(getLatestResearchAssessment).mockResolvedValue(sampleAssessment);
    vi.mocked(backfillOutcomeLabels).mockResolvedValue({
      symbol: "AAPL",
      assessment_count: 2,
      persisted_count: 1,
      skipped_count: 1,
      outcomes: [
        {
          symbol: "AAPL",
          assessment_snapshot_id: 2,
          persisted: true,
        },
        {
          symbol: "AAPL",
          assessment_snapshot_id: 1,
          persisted: false,
          reason: "insufficient_forward_bars",
          detail: "need more bars",
        },
      ],
      detail:
        "Research-only outcome-label backfill — not advice; skips are fail-closed, never invent confidence.",
    });

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /backfill outcome labels/i }));

    await waitFor(() => {
      expect(backfillOutcomeLabels).toHaveBeenCalledWith("http://localhost:8000", "AAPL", 100);
    });
    expect(await screen.findByTestId("outcome-label-backfill-summary")).toHaveTextContent(
      /attempted=2.*labeled=1.*skipped=1/,
    );
  });

  it("refreshes outcome labels for scan-labeled assessment after backfill", async () => {
    vi.mocked(getResearchEvidenceSummary).mockResolvedValue({
      symbol: "AAPL",
      state: "research_only",
      latest_assessment: sampleAssessment,
      calibration_readiness: {
        symbol: "AAPL",
        status: "insufficient_corpus",
        assessment_snapshot_id: 1,
        research_index: 0.46,
        corpus_count: 0,
        bucket_count: 0,
        min_corpus: 10,
        min_bucket: 5,
        index_bucket_width: 0.15,
        calibration_method_id: "research_calibration_v1",
        detail: "research only",
      },
      latest_outcome_label: null,
      latest_calibration: null,
      assessment_count: 2,
      outcome_label_count: 0,
      calibration_count: 0,
      latest_component_source: "alpha_vantage",
      latest_resolved_label_bar_source: null,
      mixed_component_source_assessment_count: 0,
      mixed_unlabeled_assessment_count: 0,
      mixed_labeled_assessment_count: 0,
      latest_mixed_label_bar_source: null,
      most_recent_labeled_assessment_id: 3,
      most_recent_labeled_outcome_label: {
        id: 30,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.02 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
      detail: "Research-only evidence summary — not advice; missing fields are null or zero, never invented.",
    });
    vi.mocked(listOutcomeLabels).mockResolvedValue([]);
    vi.mocked(backfillOutcomeLabels).mockResolvedValue({
      symbol: "AAPL",
      assessment_count: 1,
      persisted_count: 1,
      skipped_count: 0,
      outcomes: [{ symbol: "AAPL", assessment_snapshot_id: 3, persisted: true }],
      detail:
        "Research-only outcome-label backfill — not advice; skips are fail-closed, never invent confidence.",
    });

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh evidence summary/i }));
    const loadScan = await screen.findByTestId("load-scan-labeled-labels");
    await waitFor(() => {
      expect(loadScan).not.toBeDisabled();
    });
    fireEvent.click(loadScan);
    await waitFor(() => {
      expect(screen.getByTestId("outcome-label-history-assessment-id")).toHaveTextContent(
        /assessment id 3/i,
      );
    });

    vi.mocked(listOutcomeLabels).mockClear();
    vi.mocked(listOutcomeLabels).mockResolvedValue([
      {
        id: 40,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T22:00:00Z",
        labels: { forward_return_5: 0.06 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
    ]);
    const backfillLabels = screen.getByTestId("backfill-outcome-labels");
    await waitFor(() => {
      expect(backfillLabels).not.toBeDisabled();
    });
    expect(backfillLabels).toHaveAccessibleName(
      /backfill outcome labels then refresh assessment 3 \(scan-labeled\)/i,
    );
    expect(screen.getByTestId("backfill-outcome-labels-id-chip")).toHaveTextContent(
      "(3 · scan-labeled)",
    );
    vi.mocked(backfillOutcomeLabels).mockClear();
    fireEvent.click(backfillLabels);

    await waitFor(() => {
      expect(backfillOutcomeLabels).toHaveBeenCalledWith("http://localhost:8000", "AAPL", 100);
      expect(listOutcomeLabels).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        3,
        20,
      );
      expect(screen.getByTestId("outcome-label-history-assessment-id")).toHaveTextContent(
        /assessment id 3/i,
      );
      expect(screen.getByTestId("outcome-label-history-load-kind")).toHaveTextContent(
        /scan-labeled \(latest is 1\)/i,
      );
      expect(screen.getByText(/0\.060000 · end 2024-02-02/)).toBeInTheDocument();
    });
  });

  it("runs assessment backfill and shows research-only summary counts", async () => {
    vi.mocked(getLatestResearchAssessment).mockResolvedValue(sampleAssessment);
    vi.mocked(backfillResearchAssessments).mockResolvedValue({
      symbol: "AAPL",
      candidate_count: 3,
      persisted_count: 2,
      skipped_count: 1,
      outcomes: [],
      detail:
        "Research-only assessment backfill — not advice; skips are fail-closed, never invent confidence.",
    });

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /backfill assessments/i }));

    await waitFor(() => {
      expect(backfillResearchAssessments).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        20,
      );
    });
    expect(await screen.findByTestId("assessment-backfill-summary")).toHaveTextContent(
      /candidates=3.*persisted=2.*skipped=1/,
    );
  });

  it("keeps scan-labeled outcome labels after assessment backfill", async () => {
    vi.mocked(getResearchEvidenceSummary).mockResolvedValue({
      symbol: "AAPL",
      state: "research_only",
      latest_assessment: sampleAssessment,
      calibration_readiness: {
        symbol: "AAPL",
        status: "insufficient_corpus",
        assessment_snapshot_id: 1,
        research_index: 0.46,
        corpus_count: 0,
        bucket_count: 0,
        min_corpus: 10,
        min_bucket: 5,
        index_bucket_width: 0.15,
        calibration_method_id: "research_calibration_v1",
        detail: "research only",
      },
      latest_outcome_label: null,
      latest_calibration: null,
      assessment_count: 2,
      outcome_label_count: 1,
      calibration_count: 0,
      latest_component_source: "alpha_vantage",
      latest_resolved_label_bar_source: null,
      mixed_component_source_assessment_count: 0,
      mixed_unlabeled_assessment_count: 0,
      mixed_labeled_assessment_count: 0,
      latest_mixed_label_bar_source: null,
      most_recent_labeled_assessment_id: 3,
      most_recent_labeled_outcome_label: {
        id: 30,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.02 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
      detail: "Research-only evidence summary — not advice; missing fields are null or zero, never invented.",
    });
    vi.mocked(listOutcomeLabels).mockResolvedValue([
      {
        id: 30,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.02 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
    ]);
    vi.mocked(backfillResearchAssessments).mockResolvedValue({
      symbol: "AAPL",
      candidate_count: 1,
      persisted_count: 1,
      skipped_count: 0,
      outcomes: [],
      detail:
        "Research-only assessment backfill — not advice; skips are fail-closed, never invent confidence.",
    });
    const nextLatest = { ...sampleAssessment, id: 4 };
    vi.mocked(getLatestResearchAssessment).mockResolvedValue(nextLatest);

    render(<ResearchAssessmentPanel symbol="AAPL" initialLatest={sampleAssessment} />);
    fireEvent.click(screen.getByRole("button", { name: /refresh evidence summary/i }));
    const loadScan = await screen.findByTestId("load-scan-labeled-labels");
    await waitFor(() => {
      expect(loadScan).not.toBeDisabled();
    });
    fireEvent.click(loadScan);
    await waitFor(() => {
      expect(screen.getByTestId("outcome-label-history-assessment-id")).toHaveTextContent(
        /assessment id 3/i,
      );
    });

    vi.mocked(listOutcomeLabels).mockClear();
    vi.mocked(listOutcomeLabels).mockResolvedValue([
      {
        id: 30,
        assessment_snapshot_id: 3,
        symbol: "AAPL",
        label_method_id: "forward_total_return_v1",
        label_method_version: 1,
        state: "research_only",
        as_of_trading_date: "2024-01-26",
        computed_at: "2024-01-26T20:00:00Z",
        labels: { forward_return_5: 0.02 },
        label_end_dates: { forward_return_5: "2024-02-02" },
        schema_version: 1,
        bar_source: "polygon",
      },
    ]);
    const backfillAssessments = screen.getByRole("button", {
      name: /^backfill assessments$/i,
    });
    await waitFor(() => {
      expect(backfillAssessments).not.toBeDisabled();
    });
    vi.mocked(backfillResearchAssessments).mockClear();
    fireEvent.click(backfillAssessments);

    await waitFor(() => {
      expect(backfillResearchAssessments).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        20,
      );
      expect(listOutcomeLabels).toHaveBeenCalledWith(
        "http://localhost:8000",
        "AAPL",
        3,
        20,
      );
      expect(screen.getByTestId("outcome-label-history-assessment-id")).toHaveTextContent(
        /assessment id 3/i,
      );
      expect(screen.getByTestId("outcome-label-history-load-kind")).toHaveTextContent(
        /scan-labeled \(latest is 4\)/i,
      );
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
    expect(screen.getByText(/component source/i)).toBeInTheDocument();
    const componentSourceRow = screen.getByText(/component source/i).closest("div");
    expect(componentSourceRow).toHaveTextContent("alpha_vantage");
    expect(screen.getByText(/0\.9000 \(18\/20 comparable\)/)).toBeInTheDocument();
  });
});
