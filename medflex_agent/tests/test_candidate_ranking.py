"""
Tests for candidate_ranking.py.

Two tests are direct implementations of the D3 worked examples:
  - test_rule6_specialist_exact_match_overrides_urgency_weighting
  - test_high_urgency_non_specialist_proximity_dominates

These are the canonical evidence that the agentic design does what it claims:
the ranking inverts based on context in ways a fixed-weight sort cannot replicate.
"""

from datetime import date, timedelta
import pytest

from medflex_agent.models import (
    Candidate, NoShowRecord, PlacementRecord, EscalationType
)
from medflex_agent.candidate_ranking import rank_candidates

SPECIALIST_CONFIG = {"ICU", "NICU", "OR", "PICU", "ED", "CICU"}


def make_candidate(
    nurse_id: str,
    credentials: list[str],
    proximity_miles: float,
    response_rate: float | None = None,
    in_active_outreach: bool = False,
    no_show_history: list[NoShowRecord] | None = None,
) -> Candidate:
    return Candidate(
        nurse_id=nurse_id,
        credentials=credentials,
        proximity_miles=proximity_miles,
        in_active_outreach=in_active_outreach,
        response_rate=response_rate,
        no_show_history=no_show_history or [],
    )


# --- D3 worked examples ---

def test_rule6_specialist_exact_match_overrides_urgency_weighting():
    """
    D3 worked example (specialist variant): ICU shift, HIGH urgency.
    Without rule 6, Nurse B (close, high response rate) would win on raw score
    because HIGH urgency weights proximity heavily.
    Rule 6 forces exact specialist credential match above near-match regardless
    of urgency tier — Nurse A wins.
    """
    nurse_a = make_candidate("nurse_a", ["ICU"], proximity_miles=50, response_rate=0.70)
    nurse_b = make_candidate("nurse_b", [], proximity_miles=2, response_rate=0.95)

    result = rank_candidates(
        job_order_id="JO-001",
        facility_type="ICU",
        urgency_hours=2,  # HIGH tier — proximity dominant without rule 6
        required_credentials=["ICU"],
        eligible_candidates=[nurse_a, nurse_b],
        specialist_credential_config=SPECIALIST_CONFIG,
    )

    assert result.escalation_type is None
    assert result.ranked_candidates[0].nurse_id == "nurse_a"
    assert result.ranked_candidates[1].nurse_id == "nurse_b"
    assert "exact specialist credential match" in result.ranked_candidates[0].rationale


def test_high_urgency_non_specialist_proximity_dominates():
    """
    D3 worked example (urgent non-specialist fill): both nurses meet credentials;
    HIGH urgency weights proximity and response rate heavily.
    Nurse B (close, high response rate) ranks above Nurse A (far, lower response rate).
    A fixed-weight sort that treats all urgency tiers the same would rank them
    identically regardless of fill window.
    """
    nurse_a = make_candidate("nurse_a", ["RN", "BLS"], proximity_miles=50, response_rate=0.85)
    nurse_b = make_candidate("nurse_b", ["RN", "BLS"], proximity_miles=3, response_rate=0.95)

    result = rank_candidates(
        job_order_id="JO-002",
        facility_type="MED_SURG",
        urgency_hours=2,  # HIGH tier
        required_credentials=["RN", "BLS"],
        eligible_candidates=[nurse_a, nurse_b],
        specialist_credential_config=SPECIALIST_CONFIG,  # RN/BLS not specialist
    )

    assert result.escalation_type is None
    assert result.ranked_candidates[0].nurse_id == "nurse_b"
    assert "proximity dominant" in result.ranked_candidates[0].rationale
    assert "≤4h fill window" in result.ranked_candidates[0].rationale


def test_low_urgency_credential_specificity_dominates():
    """
    LOW urgency (>24h): credential specificity weight is 0.6.
    Nurse A (exact match, farther) ranks above Nurse B (partial match, closer).
    """
    nurse_a = make_candidate("nurse_a", ["ICU", "BLS"], proximity_miles=25, response_rate=0.85)
    nurse_b = make_candidate("nurse_b", ["BLS"], proximity_miles=3, response_rate=0.95)

    result = rank_candidates(
        job_order_id="JO-003",
        facility_type="ICU",
        urgency_hours=48,  # LOW tier
        required_credentials=["ICU", "BLS"],
        eligible_candidates=[nurse_a, nurse_b],
        specialist_credential_config=set(),  # rule 6 off — tests weights only
    )

    assert result.ranked_candidates[0].nurse_id == "nurse_a"
    assert "credential specificity dominant" in result.ranked_candidates[0].rationale


# --- Rule 1: in_active_outreach exclusion ---

def test_in_active_outreach_candidates_excluded_from_output():
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=5, in_active_outreach=True)
    nurse_b = make_candidate("nurse_b", ["RN"], proximity_miles=10, in_active_outreach=False)

    result = rank_candidates(
        job_order_id="JO-004",
        facility_type="MED_SURG",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a, nurse_b],
    )

    nurse_ids = [rc.nurse_id for rc in result.ranked_candidates]
    assert "nurse_a" not in nurse_ids
    assert "nurse_b" in nurse_ids


def test_pool_exhausted_when_all_candidates_in_active_outreach():
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=5, in_active_outreach=True)
    nurse_b = make_candidate("nurse_b", ["RN"], proximity_miles=10, in_active_outreach=True)

    result = rank_candidates(
        job_order_id="JO-005",
        facility_type="MED_SURG",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a, nurse_b],
    )

    assert result.escalation_type == EscalationType.POOL_EXHAUSTED
    assert result.ranked_candidates == []


def test_pool_exhausted_when_eligible_candidates_empty():
    result = rank_candidates(
        job_order_id="JO-006",
        facility_type="MED_SURG",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[],
    )

    assert result.escalation_type == EscalationType.POOL_EXHAUSTED


# --- Rule 2: no-show demotion ---

def test_no_show_candidate_ranked_last():
    recent_no_show = NoShowRecord(facility_type="ICU", date=date.today() - timedelta(days=30))
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=5, response_rate=0.90,
                             no_show_history=[recent_no_show])
    nurse_b = make_candidate("nurse_b", ["RN"], proximity_miles=50, response_rate=0.60)

    result = rank_candidates(
        job_order_id="JO-007",
        facility_type="ICU",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a, nurse_b],
    )

    ranked_ids = [rc.nurse_id for rc in result.ranked_candidates]
    assert ranked_ids[-1] == "nurse_a"
    assert "demoted to bottom" in result.ranked_candidates[-1].rationale


def test_old_no_show_beyond_lookback_does_not_demote():
    old_no_show = NoShowRecord(facility_type="ICU", date=date.today() - timedelta(days=120))
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=5, response_rate=0.90,
                             no_show_history=[old_no_show])
    nurse_b = make_candidate("nurse_b", ["RN"], proximity_miles=50, response_rate=0.60)

    result = rank_candidates(
        job_order_id="JO-008",
        facility_type="ICU",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a, nurse_b],
    )

    # nurse_a should rank first (closer, higher response rate) — old no-show ignored
    assert result.ranked_candidates[0].nurse_id == "nurse_a"
    assert "demoted" not in result.ranked_candidates[0].rationale


def test_no_show_at_different_facility_does_not_demote():
    other_facility_no_show = NoShowRecord(facility_type="MED_SURG", date=date.today() - timedelta(days=10))
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=5, response_rate=0.90,
                             no_show_history=[other_facility_no_show])

    result = rank_candidates(
        job_order_id="JO-009",
        facility_type="ICU",  # different facility from the no-show record
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a],
    )

    assert result.ranked_candidates[0].nurse_id == "nurse_a"
    assert "demoted" not in result.ranked_candidates[0].rationale


# --- Rule 8: response rate imputation ---

def test_missing_response_rate_imputed_from_pool_median():
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=10, response_rate=None)
    nurse_b = make_candidate("nurse_b", ["RN"], proximity_miles=20, response_rate=0.80)
    nurse_c = make_candidate("nurse_c", ["RN"], proximity_miles=30, response_rate=0.60)

    result = rank_candidates(
        job_order_id="JO-010",
        facility_type="MED_SURG",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a, nurse_b, nurse_c],
    )

    nurse_a_result = next(rc for rc in result.ranked_candidates if rc.nurse_id == "nurse_a")
    assert "imputed" in nurse_a_result.rationale


def test_no_response_rate_data_at_all_uses_neutral_default():
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=5, response_rate=None)
    nurse_b = make_candidate("nurse_b", ["RN"], proximity_miles=10, response_rate=None)

    result = rank_candidates(
        job_order_id="JO-011",
        facility_type="MED_SURG",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a, nurse_b],
    )

    assert result.escalation_type is None
    assert len(result.ranked_candidates) == 2
    for rc in result.ranked_candidates:
        assert "imputed" in rc.rationale


# --- Rule 7: preference boost ---

def test_preference_boost_applied_within_threshold():
    """
    Nurse B is preferred by the facility and scores within 10% of Nurse A.
    Nurse B should be moved up one rank position.
    """
    # Nurse A scores slightly higher on raw; Nurse B is preferred and within 10%
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=5, response_rate=0.90)
    nurse_b = make_candidate("nurse_b", ["RN"], proximity_miles=7, response_rate=0.88)

    preference = [PlacementRecord(facility_type="MED_SURG", nurse_id="nurse_b")]

    result = rank_candidates(
        job_order_id="JO-012",
        facility_type="MED_SURG",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a, nurse_b],
        hospital_preference_history=preference,
    )

    assert result.ranked_candidates[0].nurse_id == "nurse_b"
    assert "preference record applied" in result.ranked_candidates[0].rationale


def test_preference_boost_not_applied_beyond_threshold():
    """
    Nurse B is preferred but scores more than 10% below Nurse A — no boost.
    """
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=2, response_rate=0.95)
    nurse_b = make_candidate("nurse_b", ["RN"], proximity_miles=40, response_rate=0.50)

    preference = [PlacementRecord(facility_type="MED_SURG", nurse_id="nurse_b")]

    result = rank_candidates(
        job_order_id="JO-013",
        facility_type="MED_SURG",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a, nurse_b],
        hospital_preference_history=preference,
    )

    assert result.ranked_candidates[0].nurse_id == "nurse_a"
    assert "preference record applied" not in result.ranked_candidates[0].rationale


def test_preference_boost_does_not_cross_specialist_boundary():
    """
    Nurse B is preferred and a near-match. Nurse A is an exact specialist match.
    Even if Nurse B is within 10% on raw score, rule 6 boundary is not crossed.
    """
    nurse_a = make_candidate("nurse_a", ["ICU"], proximity_miles=20, response_rate=0.80)
    nurse_b = make_candidate("nurse_b", [], proximity_miles=2, response_rate=0.95)

    preference = [PlacementRecord(facility_type="ICU", nurse_id="nurse_b")]

    result = rank_candidates(
        job_order_id="JO-014",
        facility_type="ICU",
        urgency_hours=48,
        required_credentials=["ICU"],
        eligible_candidates=[nurse_a, nurse_b],
        hospital_preference_history=preference,
        specialist_credential_config=SPECIALIST_CONFIG,
    )

    assert result.ranked_candidates[0].nurse_id == "nurse_a"


# --- Rule 9: max 5 candidates ---

def test_max_five_candidates_returned():
    candidates = [
        make_candidate(f"nurse_{i}", ["RN"], proximity_miles=float(i * 5), response_rate=0.80)
        for i in range(1, 8)
    ]

    result = rank_candidates(
        job_order_id="JO-015",
        facility_type="MED_SURG",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=candidates,
    )

    assert len(result.ranked_candidates) == 5


# --- Rank positions ---

def test_rank_positions_are_sequential_from_one():
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=5, response_rate=0.90)
    nurse_b = make_candidate("nurse_b", ["RN"], proximity_miles=10, response_rate=0.80)
    nurse_c = make_candidate("nurse_c", ["RN"], proximity_miles=15, response_rate=0.70)

    result = rank_candidates(
        job_order_id="JO-016",
        facility_type="MED_SURG",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a, nurse_b, nurse_c],
    )

    ranks = [rc.rank for rc in result.ranked_candidates]
    assert ranks == [1, 2, 3]


# --- Shared entity: in_active_outreach always False in output ---

def test_ranked_candidates_in_active_outreach_is_false():
    """
    Parallel outreach sets in_active_outreach to True on send.
    At ranking time it is always False — parallel outreach owns that state write.
    """
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=5)

    result = rank_candidates(
        job_order_id="JO-017",
        facility_type="MED_SURG",
        urgency_hours=6,
        required_credentials=["RN"],
        eligible_candidates=[nurse_a],
    )

    assert all(rc.in_active_outreach is False for rc in result.ranked_candidates)


# --- Rationale content ---

def test_rationale_includes_job_order_context():
    nurse_a = make_candidate("nurse_a", ["RN"], proximity_miles=5, response_rate=0.85)

    result = rank_candidates(
        job_order_id="JO-018",
        facility_type="MED_SURG",
        urgency_hours=30,  # LOW tier
        required_credentials=["RN"],
        eligible_candidates=[nurse_a],
    )

    rationale = result.ranked_candidates[0].rationale
    assert ">24h urgency window" in rationale
    assert "5 mi" in rationale
    assert "85%" in rationale
