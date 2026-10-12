"""
Tests for edge-signal-aggregator aggregate_signals.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from aggregate_signals import (
    DEFAULT_CONFIG,
    _parse_timestamp,
    aggregate_signals,
    apply_contradiction_adjustments,
    are_signals_similar,
    as_ticker_list,
    calculate_composite_score,
    calculate_recency_factor,
    calculate_text_similarity,
    calculate_ticker_overlap,
    deduplicate_signals,
    detect_contradictions,
    extract_signals_from_concepts,
    extract_signals_from_edge_candidates,
    extract_signals_from_themes,
    generate_markdown_report,
    horizon_bucket,
    load_config,
    normalize_direction,
    normalize_score,
    parse_raw_score,
)


class TestNormalizeScore:
    """Tests for normalize_score function."""

    def test_numeric_score_in_range(self):
        """Test normalization of numeric score within range."""
        assert normalize_score(0.5) == 0.5
        assert normalize_score(0.0) == 0.0
        assert normalize_score(1.0) == 1.0

    def test_numeric_score_out_of_range(self):
        """Test normalization clamps values to [0, 1]."""
        assert normalize_score(1.5) == 1.0
        assert normalize_score(-0.5) == 0.0

    def test_letter_grades(self):
        """Test letter grade conversion."""
        assert normalize_score("A") == 1.0
        assert normalize_score("B") == 0.8
        assert normalize_score("C") == 0.6
        assert normalize_score("D") == 0.4
        assert normalize_score("F") == 0.2
        assert normalize_score("a") == 1.0  # Case insensitive

    def test_none_and_invalid(self):
        """Test handling of None and invalid values."""
        assert normalize_score(None) == 0.0
        assert normalize_score("invalid") == 0.0


class TestRecencyFactor:
    """Tests for calculate_recency_factor function."""

    def test_recent_timestamp(self):
        """Test recency factor for recent timestamps."""
        now = datetime.now(timezone.utc).isoformat()
        factor = calculate_recency_factor(now, DEFAULT_CONFIG["recency"])
        assert factor == 1.0

    def test_old_timestamp(self):
        """Test recency factor for old timestamps."""
        factor = calculate_recency_factor("2020-01-01", DEFAULT_CONFIG["recency"])
        assert factor == 0.85

    def test_none_timestamp(self):
        """Test recency factor for missing timestamp."""
        factor = calculate_recency_factor(None, DEFAULT_CONFIG["recency"])
        assert factor == 0.85


class TestTickerOverlap:
    """Tests for calculate_ticker_overlap function."""

    def test_full_overlap(self):
        """Test identical ticker lists."""
        assert calculate_ticker_overlap(["AAPL", "MSFT"], ["AAPL", "MSFT"]) == 1.0

    def test_partial_overlap(self):
        """Test partial ticker overlap."""
        overlap = calculate_ticker_overlap(["AAPL", "MSFT"], ["AAPL", "GOOGL"])
        assert overlap == pytest.approx(1 / 3)  # 1 overlap, 3 union

    def test_no_overlap(self):
        """Test no ticker overlap."""
        assert calculate_ticker_overlap(["AAPL"], ["MSFT"]) == 0.0

    def test_empty_lists(self):
        """Test empty ticker lists."""
        assert calculate_ticker_overlap([], []) == 0.0
        assert calculate_ticker_overlap(["AAPL"], []) == 0.0


class TestTextSimilarity:
    """Tests for calculate_text_similarity function."""

    def test_identical_text(self):
        """Test identical text strings."""
        assert calculate_text_similarity("AI Infrastructure", "AI Infrastructure") == 1.0

    def test_partial_similarity(self):
        """Test partial text overlap."""
        sim = calculate_text_similarity("AI Infrastructure Growth", "AI Compute Growth")
        assert 0 < sim < 1

    def test_no_similarity(self):
        """Test completely different text."""
        sim = calculate_text_similarity("Energy Sector", "Technology Growth")
        assert sim == 0.0

    def test_empty_strings(self):
        """Test empty strings."""
        assert calculate_text_similarity("", "") == 0.0
        assert calculate_text_similarity("test", "") == 0.0


class TestSignalSimilarity:
    """Tests for are_signals_similar function."""

    def test_similar_signals(self):
        """Test detection of similar signals."""
        sig_a = {"title": "AI Growth", "tickers": ["NVDA", "AMD"], "direction": "LONG"}
        sig_b = {"title": "AI Growth Thesis", "tickers": ["NVDA", "AVGO"], "direction": "LONG"}
        assert are_signals_similar(sig_a, sig_b, DEFAULT_CONFIG)

    def test_different_direction(self):
        """Test that different directions are not similar."""
        sig_a = {"title": "AI Growth", "tickers": ["NVDA"], "direction": "LONG"}
        sig_b = {"title": "AI Growth", "tickers": ["NVDA"], "direction": "SHORT"}
        assert not are_signals_similar(sig_a, sig_b, DEFAULT_CONFIG)

    def test_different_signals(self):
        """Test that truly different signals are not similar."""
        sig_a = {"title": "AI Growth", "tickers": ["NVDA"], "direction": "LONG"}
        sig_b = {"title": "Energy Decline", "tickers": ["XOM"], "direction": "LONG"}
        assert not are_signals_similar(sig_a, sig_b, DEFAULT_CONFIG)


class TestDeduplication:
    """Tests for deduplicate_signals function."""

    def test_no_duplicates(self):
        """Test deduplication with no duplicates."""
        signals = [
            {
                "skill": "theme_detector",
                "signal_ref": "t1",
                "title": "AI",
                "tickers": ["NVDA"],
                "direction": "LONG",
                "raw_score": 0.8,
            },
            {
                "skill": "sector_analyst",
                "signal_ref": "s1",
                "title": "Energy",
                "tickers": ["XOM"],
                "direction": "SHORT",
                "raw_score": 0.7,
            },
        ]
        deduped, log = deduplicate_signals(signals, DEFAULT_CONFIG)
        assert len(deduped) == 2
        assert len(log) == 0

    def test_with_duplicates(self):
        """Test deduplication merges similar signals."""
        signals = [
            {
                "skill": "theme_detector",
                "signal_ref": "t1",
                "title": "AI Infrastructure",
                "tickers": ["NVDA", "AMD"],
                "direction": "LONG",
                "raw_score": 0.9,
            },
            {
                "skill": "edge_candidate_agent",
                "signal_ref": "e1",
                "title": "AI Infrastructure Growth",
                "tickers": ["NVDA", "AVGO"],
                "direction": "LONG",
                "raw_score": 0.85,
            },
        ]
        deduped, log = deduplicate_signals(signals, DEFAULT_CONFIG)
        assert len(deduped) == 1
        assert len(log) == 1
        assert len(deduped[0]["contributing_skills"]) == 2


class TestContradictionDetection:
    """Tests for detect_contradictions function."""

    def test_no_contradictions(self):
        """Test with no contradictions."""
        signals = [
            {"skill": "a", "title": "AI", "tickers": ["NVDA"], "direction": "LONG"},
            {"skill": "b", "title": "Energy", "tickers": ["XOM"], "direction": "SHORT"},
        ]
        contradictions = detect_contradictions(signals)
        assert len(contradictions) == 0

    def test_detects_contradiction(self):
        """Test detection of opposing signals."""
        signals = [
            {
                "skill": "sector_analyst",
                "signal_ref": "s1",
                "title": "Energy Bearish",
                "tickers": ["XOM"],
                "direction": "SHORT",
            },
            {
                "skill": "institutional_flow_tracker",
                "signal_ref": "i1",
                "title": "XOM Buying",
                "tickers": ["XOM"],
                "direction": "LONG",
            },
        ]
        contradictions = detect_contradictions(signals)
        assert len(contradictions) == 1
        assert contradictions[0]["severity"] == "MEDIUM"
        assert contradictions[0]["ticker"] == "XOM"
        assert contradictions[0]["signal_a_ref"] == "institutional_flow_tracker:i1"
        assert contradictions[0]["signal_b_ref"] == "sector_analyst:s1"

    def test_same_skill_contradiction_is_high_severity(self):
        """Test that same-skill contradictions are HIGH severity."""
        signals = [
            {
                "skill": "theme_detector",
                "signal_ref": "t1",
                "title": "AI Bull",
                "tickers": ["NVDA"],
                "direction": "LONG",
            },
            {
                "skill": "theme_detector",
                "signal_ref": "t2",
                "title": "AI Bear",
                "tickers": ["NVDA"],
                "direction": "SHORT",
            },
        ]
        contradictions = detect_contradictions(signals)
        assert len(contradictions) == 1
        assert contradictions[0]["severity"] == "HIGH"

    def test_different_horizons_are_low_severity(self):
        """Test LOW severity when horizons are clearly different."""
        signals = [
            {
                "skill": "sector_analyst",
                "signal_ref": "s1",
                "title": "Short-term pullback",
                "tickers": ["AAPL"],
                "direction": "SHORT",
                "time_horizon": "1-2 weeks",
            },
            {
                "skill": "edge_concept_synthesizer",
                "signal_ref": "c1",
                "title": "Long-term trend intact",
                "tickers": ["AAPL"],
                "direction": "LONG",
                "time_horizon": "12 months",
            },
        ]
        contradictions = detect_contradictions(signals)
        assert len(contradictions) == 1
        assert contradictions[0]["severity"] == "LOW"


class TestCompositeScore:
    """Tests for calculate_composite_score function."""

    def test_single_skill_score(self):
        """Test composite score with single skill."""
        signal = {
            "skill": "edge_candidate_agent",
            "signal_ref": "test",
            "raw_score": 0.8,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        result = calculate_composite_score(signal, DEFAULT_CONFIG)
        assert 0 < result["composite_score"] <= 1.0
        assert "confidence_breakdown" in result

    def test_multi_skill_agreement_bonus(self):
        """Test that multi-skill agreement increases score."""
        signal_single = {
            "skill": "edge_candidate_agent",
            "signal_ref": "test",
            "raw_score": 0.8,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        signal_multi = {
            "skill": "edge_candidate_agent",
            "signal_ref": "test",
            "raw_score": 0.8,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contributing_skills": [
                {"skill": "edge_candidate_agent", "signal_ref": "e1", "raw_score": 0.8},
                {"skill": "theme_detector", "signal_ref": "t1", "raw_score": 0.8},
                {"skill": "sector_analyst", "signal_ref": "s1", "raw_score": 0.8},
            ],
        }
        single_result = calculate_composite_score(signal_single, DEFAULT_CONFIG)
        multi_result = calculate_composite_score(signal_multi, DEFAULT_CONFIG)
        assert multi_result["composite_score"] > single_result["composite_score"]


class TestContradictionAdjustments:
    """Tests for contradiction penalty / exclusion application."""

    def test_medium_contradiction_penalizes_both_signals(self):
        """Medium contradiction should reduce both signal scores."""
        scored_signals = [
            {"_source_ref": "a:s1", "composite_score": 0.8},
            {"_source_ref": "b:s2", "composite_score": 0.7},
        ]
        contradictions = [
            {
                "contradiction_id": "c1",
                "severity": "MEDIUM",
                "signal_a_ref": "a:s1",
                "signal_b_ref": "b:s2",
            }
        ]
        adjusted, log = apply_contradiction_adjustments(
            scored_signals,
            contradictions,
            DEFAULT_CONFIG,
        )
        assert adjusted[0]["composite_score"] == pytest.approx(0.72, abs=1e-4)
        assert adjusted[1]["composite_score"] == pytest.approx(0.63, abs=1e-4)
        assert len(log) == 2
        assert all(item["action"] == "penalty" for item in log)

    def test_high_contradiction_excludes_signals(self):
        """High contradiction should exclude signals by default."""
        scored_signals = [
            {"_source_ref": "a:s1", "composite_score": 0.8},
            {"_source_ref": "a:s2", "composite_score": 0.7},
        ]
        contradictions = [
            {
                "contradiction_id": "c2",
                "severity": "HIGH",
                "signal_a_ref": "a:s1",
                "signal_b_ref": "a:s2",
            }
        ]
        adjusted, log = apply_contradiction_adjustments(
            scored_signals,
            contradictions,
            DEFAULT_CONFIG,
        )
        assert adjusted[0]["_excluded"] is True
        assert adjusted[1]["_excluded"] is True
        assert len(log) == 2
        assert all(item["action"] == "exclude" for item in log)


class TestExtractSignals:
    """Tests for signal extraction functions."""

    def test_extract_from_edge_candidates(self):
        """Test extraction from edge-candidate-agent format."""
        data = [
            {
                "_source_file": "test.json",
                "tickets": [
                    {
                        "ticket_id": "T001",
                        "title": "Test Signal",
                        "score": 0.85,
                        "tickers": ["AAPL"],
                        "direction": "LONG",
                    }
                ],
            }
        ]
        signals, invalids = extract_signals_from_edge_candidates(data)
        assert len(signals) == 1
        assert signals[0]["skill"] == "edge_candidate_agent"
        assert signals[0]["signal_ref"] == "T001"
        assert signals[0]["raw_score"] == 0.85

    def test_extract_from_edge_candidates_priority_score_0_to_100(self):
        """Test extraction supports priority_score on 0-100 scale."""
        data = [
            {
                "_source_file": "candidate.json",
                "tickets": [
                    {
                        "ticket_id": "T002",
                        "title": "VWAP hold setup",
                        "priority_score": 78,
                        "observation": {"symbol": "nvda"},
                        "direction": "bullish",
                    }
                ],
            }
        ]
        signals, invalids = extract_signals_from_edge_candidates(data)
        assert len(signals) == 1
        assert signals[0]["raw_score"] == pytest.approx(0.78, abs=1e-6)
        assert signals[0]["tickers"] == ["NVDA"]
        assert signals[0]["direction"] == "LONG"

    def test_extract_from_concepts_support_fields(self):
        """Test concept extraction reads support.avg_priority_score and symbols."""
        data = [
            {
                "_source_file": "concept.yaml",
                "concepts": [
                    {
                        "concept_id": "C001",
                        "title": "AI infra breadth",
                        "support": {
                            "avg_priority_score": 64,
                            "symbols": ["NVDA", "AVGO"],
                        },
                    }
                ],
            }
        ]
        signals, invalids = extract_signals_from_concepts(data)
        assert len(signals) == 1
        assert signals[0]["signal_ref"] == "C001"
        assert signals[0]["raw_score"] == pytest.approx(0.64, abs=1e-6)
        assert signals[0]["tickers"] == ["AVGO", "NVDA"]

    def test_extract_from_themes(self):
        """Test extraction from theme-detector format."""
        data = [
            {
                "_source_file": "test.json",
                "themes": [
                    {
                        "theme_id": "ai_infra",
                        "theme_name": "AI Infrastructure",
                        "strength": 0.9,
                        "tickers": ["NVDA", "AMD"],
                    }
                ],
                "generated_at": "2026-03-01T10:00:00Z",
            }
        ]
        signals, invalids = extract_signals_from_themes(data)
        assert len(signals) == 1
        assert signals[0]["skill"] == "theme_detector"
        assert signals[0]["title"] == "AI Infrastructure"

    def test_extract_from_themes_dict_all_format(self):
        """Test extraction supports themes.all dict format and heat fields."""
        data = [
            {
                "_source_file": "theme.json",
                "themes": {
                    "all": [
                        {
                            "theme_id": "t-all-1",
                            "theme_name": "Earnings gap continuation",
                            "heat": 72,
                            "representative_stocks": ["aapl", "msft"],
                            "direction": "up",
                        }
                    ]
                },
                "generated_at": "2026-03-01T10:00:00Z",
            }
        ]
        signals, invalids = extract_signals_from_themes(data)
        assert len(signals) == 1
        assert signals[0]["raw_score"] == pytest.approx(0.72, abs=1e-6)
        assert signals[0]["tickers"] == ["AAPL", "MSFT"]
        assert signals[0]["direction"] == "LONG"


class TestAggregateSignals:
    """Tests for main aggregate_signals function."""

    def test_empty_inputs(self):
        """Test aggregation with empty inputs."""
        result = aggregate_signals([], [], [], [], [], [], DEFAULT_CONFIG)
        assert result["summary"]["total_input_signals"] == 0
        assert result["summary"]["unique_signals_after_dedup"] == 0

    def test_with_sample_data(self):
        """Test aggregation with sample data."""
        edge_candidates = [
            {
                "tickets": [
                    {
                        "ticket_id": "T1",
                        "title": "AI Capex",
                        "score": 0.9,
                        "tickers": ["NVDA"],
                        "direction": "LONG",
                    }
                ]
            }
        ]
        themes = [
            {
                "themes": [
                    {
                        "theme_id": "ai",
                        "theme_name": "AI Growth",
                        "strength": 0.85,
                        "tickers": ["NVDA", "AMD"],
                    }
                ]
            }
        ]

        result = aggregate_signals(
            edge_candidates=edge_candidates,
            edge_concepts=[],
            themes=themes,
            sectors=[],
            institutional=[],
            hints=[],
            config=DEFAULT_CONFIG,
        )

        assert result["summary"]["total_input_signals"] == 2
        assert len(result["ranked_signals"]) > 0
        assert result["ranked_signals"][0]["rank"] == 1

    def test_high_contradiction_excludes_from_ranking(self):
        """Same-skill opposite signals should be excluded from final ranking."""
        edge_candidates = [
            {
                "tickets": [
                    {
                        "ticket_id": "T-long",
                        "title": "AAPL breakout",
                        "score": 0.9,
                        "tickers": ["AAPL"],
                        "direction": "LONG",
                    },
                    {
                        "ticket_id": "T-short",
                        "title": "AAPL breakdown",
                        "score": 0.8,
                        "tickers": ["AAPL"],
                        "direction": "SHORT",
                    },
                ]
            }
        ]

        result = aggregate_signals(
            edge_candidates=edge_candidates,
            edge_concepts=[],
            themes=[],
            sectors=[],
            institutional=[],
            hints=[],
            config=DEFAULT_CONFIG,
        )

        assert result["summary"]["contradictions_found"] == 1
        assert result["summary"]["contradiction_adjustments_applied"] == 2
        assert result["ranked_signals"] == []


class TestMarkdownReport:
    """Tests for markdown report generation."""

    def test_generates_valid_markdown(self):
        """Test that markdown generation produces valid output."""
        result = {
            "generated_at": "2026-03-02T07:00:00Z",
            "config": {"min_conviction": 0.5},
            "summary": {
                "total_input_signals": 10,
                "unique_signals_after_dedup": 8,
                "contradictions_found": 1,
                "signals_above_threshold": 5,
            },
            "ranked_signals": [
                {
                    "rank": 1,
                    "signal_id": "sig_001",
                    "title": "Test Signal",
                    "composite_score": 0.85,
                    "contributing_skills": [
                        {"skill": "test", "signal_ref": "t1", "raw_score": 0.85}
                    ],
                    "tickers": ["AAPL"],
                    "direction": "LONG",
                    "time_horizon": "3 months",
                    "confidence_breakdown": {
                        "multi_skill_agreement": 0.3,
                        "signal_strength": 0.4,
                        "recency": 0.25,
                    },
                }
            ],
            "contradictions": [],
            "deduplication_log": [],
        }
        md = generate_markdown_report(result)
        assert "# Edge Signal Aggregator Dashboard" in md
        assert "Test Signal" in md
        assert "Score: 0.85" in md


class TestLoadConfig:
    """Tests for configuration loading."""

    def test_default_config(self):
        """Test loading default config when no file specified."""
        config = load_config(None)
        assert "weights" in config
        assert config["weights"]["edge_candidate_agent"] == 0.25

    def test_missing_config_file(self):
        """Test graceful handling of missing config file."""
        config = load_config("/nonexistent/path.yaml")
        assert "weights" in config  # Falls back to defaults


class TestIntegration:
    """Integration tests with file I/O."""

    def test_json_output(self, tmp_path: Path):
        """Test JSON file output."""
        import sys

        from aggregate_signals import main

        # Create sample input
        input_file = tmp_path / "edge_candidates.json"
        input_file.write_text(
            json.dumps(
                {
                    "tickets": [
                        {
                            "ticket_id": "T1",
                            "title": "Test",
                            "score": 0.8,
                            "tickers": ["AAPL"],
                            "direction": "LONG",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        # Run with captured output
        old_argv = sys.argv
        try:
            sys.argv = [
                "aggregate_signals.py",
                "--edge-candidates",
                str(input_file),
                "--output-dir",
                str(tmp_path),
            ]
            exit_code = main()
        finally:
            sys.argv = old_argv

        assert exit_code == 0

        # Check output files exist
        json_files = list(tmp_path.glob("edge_signal_aggregator_*.json"))
        md_files = list(tmp_path.glob("edge_signal_aggregator_*.md"))
        assert len(json_files) == 1
        assert len(md_files) == 1

        # Validate JSON structure
        with open(json_files[0]) as f:
            output = json.load(f)
        assert "schema_version" in output
        assert "ranked_signals" in output


class TestNormalizeDirection:
    """Tests for normalize_direction utility."""

    def test_long_variants(self):
        for label in ["long", "LONG", "bull", "bullish", "buy", "accumulation", "up"]:
            assert normalize_direction(label) == "LONG"

    def test_short_variants(self):
        for label in ["short", "SHORT", "bear", "bearish", "sell", "distribution", "down"]:
            assert normalize_direction(label) == "SHORT"

    def test_none_and_empty(self):
        assert normalize_direction(None) == "NEUTRAL"
        assert normalize_direction("") == "NEUTRAL"

    def test_custom_default(self):
        assert normalize_direction(None, default="LONG") == "LONG"


class TestAsTickerList:
    """Tests for as_ticker_list utility."""

    def test_string_list(self):
        assert as_ticker_list(["nvda", "AMD"]) == ["AMD", "NVDA"]

    def test_dict_list(self):
        assert as_ticker_list([{"symbol": "aapl"}, {"ticker": "msft"}]) == ["AAPL", "MSFT"]

    def test_comma_separated_string(self):
        assert as_ticker_list("NVDA, AMD, AAPL") == ["AAPL", "AMD", "NVDA"]

    def test_empty(self):
        assert as_ticker_list([]) == []
        assert as_ticker_list(None) == []


class TestParseRawScoreReplacements:
    """Replacements for former TestNormalizeScoreAuto cases (Issue #510)."""

    def test_zero_to_one_range(self):
        assert parse_raw_score(0.75, None) == (0.75, "valid", None)

    def test_zero_to_hundred_range_is_assumed(self):
        score, status, _ = parse_raw_score(85, None)
        assert score == 0.85
        assert status == "assumed_scale"

    def test_over_hundred_now_invalid(self):
        assert parse_raw_score(150, None) == (None, "invalid", "out_of_range")

    def test_negative_now_invalid(self):
        assert parse_raw_score(-5, None) == (None, "invalid", "negative")

    def test_none(self):
        assert parse_raw_score(None, None) == (0.0, "valid", None)

    def test_letter_grade(self):
        assert parse_raw_score("A", None) == (1.0, "valid", None)


class TestHorizonBucket:
    """Tests for horizon_bucket utility."""

    def test_numeric_day(self):
        assert horizon_bucket("20D") == "short"
        assert horizon_bucket("5d") == "short"

    def test_numeric_week(self):
        assert horizon_bucket("4W") == "short"
        assert horizon_bucket("16w") == "medium"

    def test_numeric_month(self):
        assert horizon_bucket("2M") == "short"
        assert horizon_bucket("6M") == "medium"
        assert horizon_bucket("12m") == "long"

    def test_text_horizons(self):
        assert horizon_bucket("1-3 months") == "short"
        assert horizon_bucket("3-6 months") == "medium"
        assert horizon_bucket("3 months") == "medium"
        assert horizon_bucket("6-12 months") == "long"

    def test_none_and_unknown(self):
        assert horizon_bucket(None) == "unknown"
        assert horizon_bucket("custom period") == "unknown"


class TestIndividualTicketYAML:
    """Test that individual ticket YAML files (no 'tickets' wrapper) are handled."""

    def test_single_ticket_dict_as_doc(self):
        """When a YAML file IS the ticket (not wrapped in tickets array)."""
        docs = [
            {
                "id": "ticket_001",
                "priority_score": 88.5,
                "observation": {"symbol": "NVDA"},
                "holding_horizon": "20D",
                "direction": "bullish",
                "title": "NVDA gap up",
                "_source_file": "tickets/exportable/ticket_001.yaml",
            }
        ]
        signals, invalids = extract_signals_from_edge_candidates(docs)
        assert len(signals) == 1
        assert signals[0]["tickers"] == ["NVDA"]
        assert signals[0]["raw_score"] == pytest.approx(0.885, rel=1e-2)
        assert signals[0]["direction"] == "LONG"


class TestParseRawScore:
    """T3/T4/T5/T10/T12: strict score parsing contract."""

    def test_t3_non_finite_rejected_declared_and_undeclared(self):
        for scale in (None, "0-1", "0-100"):
            for value in (float("nan"), float("inf"), float("-inf")):
                score, status, reason = parse_raw_score(value, scale)
                assert score is None
                assert status == "invalid"
                assert reason == "non_finite"

    def test_t3_undeclared_negative_rejected(self):
        score, status, reason = parse_raw_score(-5, None)
        assert score is None
        assert status == "invalid"
        assert reason == "negative"

    def test_t4_declared_0_100_boundary_1_0_and_1_1(self):
        assert parse_raw_score(1.0, "0-100") == (pytest.approx(0.01), "valid", None)
        assert parse_raw_score(1.1, "0-100") == (pytest.approx(0.011), "valid", None)

    def test_t4_declared_0_1_boundary_1_0_valid_1_1_rejected(self):
        assert parse_raw_score(1.0, "0-1") == (1.0, "valid", None)
        score, status, reason = parse_raw_score(1.1, "0-1")
        assert (score, status, reason) == (None, "invalid", "out_of_range")

    def test_t4_declared_negative_rejected(self):
        assert parse_raw_score(-1, "0-1") == (None, "invalid", "negative")
        assert parse_raw_score(-1, "0-100") == (None, "invalid", "negative")

    def test_t5_undeclared_above_one_is_assumed_scale(self):
        score, status, reason = parse_raw_score(1.1, None)
        assert status == "assumed_scale"
        assert reason is None
        assert score == pytest.approx(0.011)

    def test_t5_undeclared_at_or_below_one_is_plain_valid(self):
        assert parse_raw_score(1.0, None) == (1.0, "valid", None)
        assert parse_raw_score(0.75, None) == (0.75, "valid", None)

    def test_t5_undeclared_over_hundred_rejected(self):
        assert parse_raw_score(150, None) == (None, "invalid", "out_of_range")

    def test_t10_declared_scale_foo_is_missing_scale(self):
        score, status, reason = parse_raw_score(0.5, "foo")
        assert (score, status, reason) == (None, "invalid", "missing_scale")
        assert parse_raw_score(0.5, "") == (None, "invalid", "missing_scale")

    def test_t10_absent_scale_key_is_assumed_scale(self):
        status, reason = parse_raw_score(1.1, None)[1:]
        assert status == "assumed_scale"
        assert reason is None

    def test_t12_letter_grades_remain_valid(self):
        for grade, expected in (("A", 1.0), ("B", 0.8), ("C", 0.6), ("D", 0.4), ("F", 0.2)):
            score, status, reason = parse_raw_score(grade, None)
            assert (score, status, reason) == (expected, "valid", None)
        score, status, reason = parse_raw_score("a", "0-1")
        assert (score, status) == (1.0, "valid")

    def test_t12_unparsable_string_rejected(self):
        assert parse_raw_score("hot", None) == (None, "invalid", "unparsable")

    def test_none_stays_valid_zero_baseline(self):
        assert parse_raw_score(None, None) == (0.0, "valid", None)


# --- helpers for e2e idempotency / invalid plumbing tests ---


def _candidate_ticket(
    ticket_id="T001",
    title="AI Infrastructure Breakout",
    score=0.6,
    tickers=("NVDA",),
    direction="LONG",
):
    return {
        "ticket_id": ticket_id,
        "title": title,
        "score": score,
        "tickers": list(tickers),
        "direction": direction,
    }


def _candidate_doc(ticket, source_file, doc=None):
    doc = dict(doc or {})
    doc["_source_file"] = source_file
    doc["tickets"] = [ticket]
    return doc


def _theme_doc(doc=None, source_file="theme.json"):
    doc = dict(doc or {})
    doc["_source_file"] = source_file
    return doc


def _aggregate(*, edge_candidates=(), themes=()):
    return aggregate_signals(
        edge_candidates=list(edge_candidates),
        edge_concepts=[],
        themes=list(themes),
        sectors=[],
        institutional=[],
        hints=[],
        config=load_config(None),
    )


class TestIdempotency:
    """T1/T2/T9: re-ingestion must not inflate scores."""

    def test_t1_repeated_signal_from_two_files_is_idempotent(self, tmp_path):
        f1 = tmp_path / "run_a.json"
        f2 = tmp_path / "run_b.json"
        results = []
        copies_list = (1, 5, 10)
        for copies in copies_list:
            docs = []
            for i in range(copies):
                doc = _candidate_doc(_candidate_ticket(), "ingest.json")
                doc["_source_file"] = str(f1 if i % 2 == 0 else f2)
                docs.append(doc)
            result = _aggregate(edge_candidates=docs)
            results.append(result)
        base = results[0]
        for copies, r in zip(copies_list[1:], results[1:]):
            assert r["ranked_signals"][0]["composite_score"] == pytest.approx(
                base["ranked_signals"][0]["composite_score"]
            )
            check = r["summary"]["idempotency_check"]
            assert (
                check["unique_evidence_ids"]
                == base["summary"]["idempotency_check"]["unique_evidence_ids"]
            )
            assert check["total_input_signals"] == copies
            assert check["duplicate_copies_merged"] == copies - 1
            assert len(r["ranked_signals"]) == len(base["ranked_signals"])
        check = last_result = results[-1]["summary"]["idempotency_check"]
        assert last_result["unique_evidence_ids"] == 1
        assert last_result["duplicate_copies_merged"] == 9

    def test_t2_cross_skill_restatement_tier1_no_bonus(self, tmp_path):
        same_event_theme = {
            "themes": [
                {
                    "theme_id": "ai_infra",
                    "theme_name": "AI Infrastructure Breakout",
                    "strength": 0.6,
                    "tickers": ["NVDA"],
                    "direction": "up",
                }
            ]
        }
        composites = []
        for copies in (1, 5, 10):
            candidates = [
                _candidate_doc(_candidate_ticket(), "ingest.json", doc={"score_scale": "0-1"})
                for _ in range(copies)
            ]
            theme_doc = _theme_doc(same_event_theme, "theme.json")
            themes = [theme_doc] * copies
            result = _aggregate(edge_candidates=candidates, themes=themes)
            assert len(result["ranked_signals"]) == 1
            sig = result["ranked_signals"][0]
            assert sig["composite_score"] > 0
            composites.append(sig["composite_score"])
            assert sig["confidence_breakdown"]["multi_skill_agreement"] == 0
        assert len(set(composites)) == 1

    def test_t9_idempotency_check_shape(self):
        result = _aggregate(
            edge_candidates=[_candidate_doc(_candidate_ticket(), "a.json") for _ in range(3)]
        )
        check = result["summary"]["idempotency_check"]
        assert check == {
            "total_input_signals": 3,
            "unique_evidence_ids": 1,
            "duplicate_copies_merged": 2,
            "independent_units_total": 1,
        }
        assert result["schema_version"] == "1.1"


class TestAgreementTier:
    """T7/T7b/T8: documented agreement rule."""

    def _contributors(self, units):
        """units: list of (skill, ref, title, tickers)."""
        contribs = []
        for skill, ref, title, tickers in units:
            contribs.append(
                {
                    "skill": skill,
                    "signal_ref": ref,
                    "raw_score": 0.8,
                    "title": title,
                    "tickers": sorted(t.upper() for t in tickers),
                    "direction": "LONG",
                    "time_horizon": "1-3 months",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        return contribs

    def _merged_signal(self, units):
        from aggregate_signals import deduplicate_signals

        merged, _log = deduplicate_signals(self._contributors(units), load_config(None))
        return merged[0]

    def test_t7_same_event_two_skills_no_bonus(self):
        units = [
            ("theme_detector", "t1", "AI Infrastructure Breakout", ["NVDA"]),
            ("sector_analyst", "s1", "AI Infrastructure Breakout", ["NVDA"]),
        ]
        signal = self._merged_signal(units)
        result = calculate_composite_score(signal, load_config(None))
        assert result["confidence_breakdown"]["multi_skill_agreement"] == 0

    def test_t7b_paraphrase_restatement_is_known_limitation(self):
        units = [
            ("theme_detector", "t1", "NVDA surges on AI demand", ["NVDA"]),
            ("sector_analyst", "s1", "AI chip demand lifts Nvidia", ["NVDA"]),
        ]
        signal = self._merged_signal(units)
        result = calculate_composite_score(signal, load_config(None))
        assert result["confidence_breakdown"]["multi_skill_agreement"] > 0

    def test_t8_distinct_events_two_skills_bonus_fires(self):
        signal = {
            "skill": "theme_detector",
            "signal_ref": "merged",
            "raw_score": 0.8,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contributing_skills": [
                {
                    "skill": "theme_detector",
                    "signal_ref": "e1",
                    "raw_score": 0.8,
                    "title": "AI Infrastructure Breakout",
                    "tickers": ["NVDA"],
                    "direction": "LONG",
                },
                {
                    "skill": "sector_analyst",
                    "signal_ref": "e2",
                    "raw_score": 0.8,
                    "title": "Energy Sector Rotation",
                    "tickers": ["XOM"],
                    "direction": "LONG",
                },
            ],
        }
        result = calculate_composite_score(signal, load_config(None))
        assert result["confidence_breakdown"]["multi_skill_agreement"] > 0

    def test_t1b_three_evidence_ids_one_skill_no_bonus(self):
        signal = {
            "skill": "theme_detector",
            "signal_ref": "merged",
            "raw_score": 0.8,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contributing_skills": [
                {"skill": "theme_detector", "signal_ref": "e1", "raw_score": 0.8},
                {"skill": "theme_detector", "signal_ref": "e2", "raw_score": 0.8},
                {"skill": "theme_detector", "signal_ref": "e3", "raw_score": 0.8},
            ],
        }
        result = calculate_composite_score(signal, load_config(None))
        assert result["confidence_breakdown"]["multi_skill_agreement"] == 0


class TestInvalidSignalPlumbing:
    """T4/T5e2e/T6/T10e2e: invalid and assumed-scale reporting."""

    def test_t6_nan_item_reported_and_excluded(self):
        doc = {
            "tickets": [
                {
                    "ticket_id": "T-nan",
                    "title": "NaN Score Ticket",
                    "score": float("nan"),
                    "tickers": ["NVDA"],
                    "direction": "LONG",
                },
                _candidate_ticket(ticket_id="T-ok", title="OK Ticket", score=0.9),
            ]
        }
        result = _aggregate(edge_candidates=[doc])
        assert len(result["invalid_signals"]) == 1
        entry = result["invalid_signals"][0]
        assert entry["skill"] == "edge_candidate_agent"
        assert entry["signal_ref"] == "T-nan"
        assert entry["reason"] == "non_finite"
        assert entry["declared_scale"] is None
        assert "source_file" in entry
        titles = [s["title"] for s in result["ranked_signals"]]
        assert "NaN Score Ticket" not in titles
        assert "OK Ticket" in titles
        assert result["summary"]["signals_above_threshold"] == 1

    def test_t4_declared_0_1_ticket_above_range_e2e(self):
        doc = {
            "score_scale": "0-1",
            "tickets": [
                {
                    "ticket_id": "T-x",
                    "title": "Overscaled",
                    "priority_score": 1.1,
                    "tickers": ["NVDA"],
                    "direction": "LONG",
                }
            ],
        }
        result = _aggregate(edge_candidates=[doc])
        assert result["invalid_signals"][0]["reason"] == "out_of_range"
        assert result["invalid_signals"][0]["declared_scale"] == "0-1"
        assert result["ranked_signals"] == []

    def test_t4_declared_0_100_theme_scored_validly(self):
        doc = _theme_doc(
            {
                "score_scale": "0-100",
                "themes": [
                    {
                        "theme_id": "t1",
                        "theme_name": "AI Theme",
                        "heat": 72,
                        "tickers": ["NVDA"],
                        "direction": "up",
                        "score_scale": "0-100",
                    }
                ],
            }
        )
        result = _aggregate(edge_candidates=[], themes=[doc])
        assert result["invalid_signals"] == []
        assert result["ranked_signals"][0]["composite_score"] > 0
        assert result["ranked_signals"][0].get("evidence_id")

    def test_t5_assumed_scale_reported_e2e(self):
        doc = _theme_doc(
            {
                "themes": [
                    {
                        "theme_id": "t1",
                        "theme_name": "AI Theme",
                        "heat": 72,
                        "tickers": ["NVDA"],
                        "direction": "up",
                    }
                ]
            }
        )
        result = _aggregate(edge_candidates=[], themes=[doc])
        assert result["ranked_signals"][0]["score_scale_assumed"] is True
        assert len(result["scale_assumptions_report"]) == 1
        entry = result["scale_assumptions_report"][0]
        assert entry["assumed_scale"] == "0-100"
        assert entry["signal_ref"] == "t1"

    def test_t10_unparsable_scale_key_rejected_e2e(self):
        doc = _theme_doc(
            {
                "themes": [
                    {
                        "theme_id": "t1",
                        "theme_name": "AI Theme",
                        "strength": 0.8,
                        "score_scale": "foo",
                        "tickers": ["NVDA"],
                        "direction": "up",
                    }
                ]
            }
        )
        result = _aggregate(edge_candidates=[], themes=[doc])
        assert result["ranked_signals"] == []
        assert result["invalid_signals"][0]["reason"] == "missing_scale"

    def test_t6e2e_markdown_has_dropped_section(self):
        doc = {
            "tickets": [
                {
                    "ticket_id": "T-nan",
                    "title": "NaN Score Ticket",
                    "score": float("nan"),
                    "tickers": ["NVDA"],
                    "direction": "LONG",
                }
            ]
        }
        result = _aggregate(edge_candidates=[doc])
        md = generate_markdown_report(result)
        assert "Dropped by Score Validation" in md


class TestReviewFindingsFixes:
    """Regression tests for review round 1 findings (findings 1/2/4/6)."""

    def _docs_with_ts(self, records):
        return [
            _candidate_doc(
                {**_candidate_ticket(), "timestamp": ts},
                src,
            )
            for ts, src in records
        ]

    def test_t13_refreshed_timestamp_order_independent(self):
        old_ts, new_ts = "2026-01-01T00:00:00+00:00", "2026-10-10T00:00:00+00:00"
        # Order A: newest first; Order B: oldest first
        docs_a = self._docs_with_ts([(new_ts, "new.json"), (old_ts, "old.json")])
        docs_b = self._docs_with_ts([(old_ts, "old.json"), (new_ts, "new.json")])
        result_a = _aggregate(edge_candidates=docs_a)
        result_b = _aggregate(edge_candidates=docs_b)
        assert result_a["ranked_signals"][0]["composite_score"] == pytest.approx(
            result_b["ranked_signals"][0]["composite_score"]
        )
        # Merged primary carries the NEWEST timestamp (fresher, capped by recency)
        assert result_a["ranked_signals"][0]["composite_score"] > 0

    def test_t14_exact_log_survives_near_dup_consumption(self):
        # a1 unique + 4 identical re-ingests of b1, all similar to a1
        docs = [_candidate_doc(_candidate_ticket(ticket_id="a1"), "a.json")]
        docs += [
            _candidate_doc(
                _candidate_ticket(ticket_id="b1", title="Different Title Here"), "b.json"
            )
            for _ in range(4)
        ]
        result = _aggregate(edge_candidates=docs)
        exact_entries = [
            e for e in result["deduplication_log"] if e.get("reason") == "same evidence re-ingested"
        ]
        assert len(exact_entries) == 1
        assert len(exact_entries[0]["duplicates_removed"]) == 3
        assert result["summary"]["idempotency_check"]["duplicate_copies_merged"] == 3

    def test_t15_assumed_flag_or_across_exact_copies(self):
        declared = _candidate_doc(
            _candidate_ticket(score=72), "declared.json", doc={"score_scale": "0-100"}
        )
        undeclared = _candidate_doc(
            _candidate_ticket(ticket_id="T001", score=1.1), "undeclared.json"
        )
        result = _aggregate(edge_candidates=[declared, undeclared])
        assert result["ranked_signals"][0]["score_scale_assumed"] is True

    def test_t16_load_config_rejects_nan_weights(self, tmp_path):
        cfg = tmp_path / "nan_weights.yaml"
        cfg.write_text("weights:\n  theme_detector: .nan\n", encoding="utf-8")
        with pytest.raises(ValueError, match="non-finite"):
            load_config(str(cfg))


class TestReviewRound3Fixes:
    """Round-3 review fixes: strict-JSON safety + assumed-scale report dedupe."""

    def test_non_finite_contributor_is_strict_json_safe(self):
        signal = {
            "skill": "theme_detector",
            "signal_ref": "m",
            "raw_score": 0.8,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contributing_skills": [
                {"skill": "theme_detector", "signal_ref": "e1", "raw_score": float("nan")},
                {"skill": "sector_analyst", "signal_ref": "e2", "raw_score": None},
                {"skill": "edge_candidate_agent", "signal_ref": "e3", "raw_score": 0.8},
            ],
        }
        result = calculate_composite_score(signal, load_config(None))
        serialized = json.dumps(result, allow_nan=False)
        assert result["composite_score"] >= 0
        assert "NaN" not in serialized and "Infinity" not in serialized
        cleaned = [
            c["raw_score"] for c in result["contributing_skills"] if c["signal_ref"] in {"e1", "e2"}
        ]
        assert cleaned == [None, None]

    def test_assumed_scale_report_deduped_across_reingestions(self):
        docs = [
            _theme_doc(
                {
                    "themes": [
                        {
                            "theme_id": "t1",
                            "theme_name": "AI Theme",
                            "heat": 72,
                            "tickers": ["NVDA"],
                            "direction": "up",
                        }
                    ]
                },
                source_file=f"t{i}.json",
            )
            for i in range(5)
        ]
        result = _aggregate(themes=docs)
        assert len(result["scale_assumptions_report"]) == 1


def _stamped(score, timestamp, source_file, ticket_id="T001", evidence_id="ev-1"):
    ticket = _candidate_ticket(ticket_id=ticket_id, score=score)
    ticket["evidence_id"] = evidence_id
    if timestamp is not None:
        ticket["timestamp"] = timestamp
    return _candidate_doc(ticket, source_file, doc={"score_scale": "0-1"})


class TestNewestObservationWins:
    """PR #528 review: the newest re-ingested observation determines the score."""

    def _score(self, *docs):
        result = _aggregate(edge_candidates=list(docs))
        assert len(result["ranked_signals"]) == 1
        return result

    def test_newer_lower_score_wins_in_either_order(self):
        old = _stamped(0.9, "2026-10-09T00:00:00Z", "a.json")
        new = _stamped(0.5, "2026-10-10T00:00:00Z", "b.json")
        fwd = self._score(old, new)
        rev = self._score(new, old)
        newest_only = self._score(new)
        want = newest_only["ranked_signals"][0]["composite_score"]
        assert fwd["ranked_signals"][0]["composite_score"] == pytest.approx(want)
        assert rev["ranked_signals"][0]["composite_score"] == pytest.approx(want)
        contrib = fwd["ranked_signals"][0]["contributing_skills"][0]
        assert contrib["raw_score"] == 0.5

    def test_log_records_discarded_copy_scores_and_timestamps(self):
        old = _stamped(0.9, "2026-10-09T00:00:00Z", "a.json")
        new = _stamped(0.5, "2026-10-10T00:00:00Z", "b.json")
        log = self._score(old, new)["deduplication_log"][0]
        assert log["retained_copy"]["raw_score"] == 0.5
        assert log["discarded_copies"] == [
            {
                "signal_ref": "T001",
                "source_file": "a.json",
                "raw_score": 0.9,
                "timestamp": "2026-10-09T00:00:00Z",
            }
        ]
        assert "newest timestamp wins" in log["selection_rule"]

    def test_identical_reingestion_unchanged(self):
        one = self._score(_stamped(0.7, "2026-10-09T00:00:00Z", "a.json"))
        many = self._score(*[_stamped(0.7, "2026-10-09T00:00:00Z", f"f{i}.json") for i in range(5)])
        assert many["ranked_signals"][0]["composite_score"] == pytest.approx(
            one["ranked_signals"][0]["composite_score"]
        )

    def test_mixed_timezone_offsets_compared_as_instants(self):
        # 2026-10-10T00:30:00-05:00 is 05:30Z, later than 2026-10-10T04:00:00Z even
        # though it is lexicographically smaller.
        later = _stamped(0.5, "2026-10-10T00:30:00-05:00", "a.json")
        earlier = _stamped(0.9, "2026-10-10T04:00:00Z", "b.json")
        for docs in ((later, earlier), (earlier, later)):
            sig = self._score(*docs)["ranked_signals"][0]
            assert sig["contributing_skills"][0]["raw_score"] == 0.5

    def test_equal_timestamp_tie_keeps_highest_score_in_either_order(self):
        a = _stamped(0.4, "2026-10-10T00:00:00Z", "a.json")
        b = _stamped(0.8, "2026-10-10T00:00:00Z", "b.json")
        for docs in ((a, b), (b, a)):
            sig = self._score(*docs)["ranked_signals"][0]
            assert sig["contributing_skills"][0]["raw_score"] == 0.8

    def test_missing_or_unparsable_timestamp_loses_to_dated_copy(self):
        dated = _stamped(0.3, "2026-10-01", "a.json")
        for other_ts in (None, "not-a-date"):
            other = _stamped(0.9, other_ts, "b.json")
            for docs in ((dated, other), (other, dated)):
                sig = self._score(*docs)["ranked_signals"][0]
                assert sig["contributing_skills"][0]["raw_score"] == 0.3

    def test_all_missing_timestamps_keep_highest_score(self):
        a = _stamped(0.3, None, "a.json")
        b = _stamped(0.6, None, "b.json")
        for docs in ((a, b), (b, a)):
            sig = self._score(*docs)["ranked_signals"][0]
            assert sig["contributing_skills"][0]["raw_score"] == 0.6


class TestReviewPr528Reporting:
    def test_scale_assumption_report_keeps_original_value(self):
        doc = _theme_doc(
            {
                "themes": [
                    {
                        "theme_id": "t1",
                        "theme_name": "AI Theme",
                        "heat": 7.2,
                        "tickers": ["NVDA"],
                        "direction": "up",
                    }
                ]
            }
        )
        entry = _aggregate(themes=[doc])["scale_assumptions_report"][0]
        assert entry["value"] == 7.2
        assert entry["normalized_value"] == pytest.approx(0.072)
        assert entry["assumed_scale"] == "0-100"

    def test_markdown_renders_none_contributor_score_as_na(self):
        signal = {
            "skill": "theme_detector",
            "signal_ref": "m",
            "raw_score": 0.8,
            "title": "T",
            "contributing_skills": [
                {"skill": "sector_analyst", "signal_ref": "e2", "raw_score": None},
                {"skill": "edge_candidate_agent", "signal_ref": "e3", "raw_score": 0.8},
            ],
        }
        scored = calculate_composite_score(signal, load_config(None))
        result = _aggregate()
        result["ranked_signals"] = [
            {
                "rank": 1,
                "title": "T",
                "composite_score": 0.9,
                "tickers": [],
                "direction": "LONG",
                "time_horizon": "x",
                "contributing_skills": scored["contributing_skills"],
                "confidence_breakdown": scored["confidence_breakdown"],
            }
        ]
        md = generate_markdown_report(result)
        assert "sector_analyst: n/a (e2)" in md

    def test_markdown_high_conviction_label_uses_inclusive_threshold(self):
        md = generate_markdown_report(_aggregate())
        assert "High Conviction (>=0.5)" in md


class TestReviewRound2Determinism:
    def test_scale_report_source_file_is_order_independent(self):
        def doc(name):
            return _theme_doc(
                {
                    "themes": [
                        {
                            "theme_id": "t1",
                            "theme_name": "AI Theme",
                            "heat": 7.2,
                            "tickers": ["NVDA"],
                            "direction": "up",
                        }
                    ]
                },
                source_file=name,
            )

        a, b = doc("a.json"), doc("b.json")
        fwd = _aggregate(themes=[a, b])["scale_assumptions_report"]
        rev = _aggregate(themes=[b, a])["scale_assumptions_report"]
        assert fwd == rev
        assert len(fwd) == 1

    @pytest.mark.parametrize(
        "ts",
        [
            "2026-10-10T12:00:00+0000",
            "2026-10-10T12:00:00.123456789Z",
            "2026-10-10T12:00:00+00",
        ],
    )
    def test_parse_timestamp_normalizes_py310_hostile_forms(self, ts):
        parsed = _parse_timestamp(ts)
        assert parsed is not None
        assert parsed.utcoffset().total_seconds() == 0
        assert (parsed.year, parsed.month, parsed.day, parsed.hour) == (2026, 10, 10, 12)

    def test_parse_timestamp_nanosecond_fraction_truncated(self):
        parsed = _parse_timestamp("2026-10-10T12:00:00.123456789Z")
        assert parsed.microsecond == 123456

    def test_non_iso_timestamps_are_not_ordered(self):
        assert _parse_timestamp(1760097600) is None
        assert _parse_timestamp("20261010") is None
        assert _parse_timestamp("1760097600") is None

    def test_full_tie_with_different_title_is_order_independent(self):
        def sig(title):
            return {
                "skill": "edge_candidate_agent",
                "signal_ref": "T1",
                "source_file": "a.json",
                "evidence_id": "ev",
                "raw_score": 0.5,
                "timestamp": "2026-10-10T00:00:00Z",
                "title": title,
                "direction": "LONG",
                "tickers": ["NVDA"],
            }

        config = load_config(None)
        one, _ = deduplicate_signals([sig("Alpha"), sig("Beta")], config)
        two, _ = deduplicate_signals([sig("Beta"), sig("Alpha")], config)
        assert one[0]["title"] == two[0]["title"]

    def test_recency_naive_t_timestamp_treated_as_utc(self):
        cfg = {"within_24h": 1.0, "days_1_to_3": 0.95, "days_3_to_7": 0.9, "days_7_plus": 0.85}
        naive = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        assert calculate_recency_factor(naive, cfg) == 1.0
        assert calculate_recency_factor(naive.replace("T", "T", 1) + "+0000", cfg) == 1.0
