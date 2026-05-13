from datetime import datetime, date, timedelta
from statistics import median
from typing import Optional

from .models import (
    Candidate, PlacementRecord, RankedCandidate, RankingResult, EscalationType
)

NO_SHOW_LOOKBACK_DAYS = 90
MAX_RANKED_CANDIDATES = 5
PREFERENCE_BOOST_THRESHOLD = 0.10  # within 10% of next-ranked candidate's score


# --- Urgency tier helpers ---

def _urgency_tier(urgency_hours: int) -> str:
    if urgency_hours <= 4:
        return "HIGH"
    elif urgency_hours <= 24:
        return "MEDIUM"
    return "LOW"


def _weights(urgency_tier: str) -> dict[str, float]:
    if urgency_tier == "HIGH":
        return {"credential": 0.2, "proximity": 0.5, "response_rate": 0.3}
    elif urgency_tier == "MEDIUM":
        return {"credential": 0.4, "proximity": 0.4, "response_rate": 0.2}
    return {"credential": 0.6, "proximity": 0.1, "response_rate": 0.3}


# --- Scoring helpers ---

def _credential_score(candidate_credentials: list[str], required_credentials: list[str]) -> float:
    if not required_credentials:
        return 1.0
    matched = sum(1 for c in required_credentials if c in candidate_credentials)
    return matched / len(required_credentials)


def _is_exact_match(candidate_credentials: list[str], required_credentials: list[str]) -> bool:
    return all(c in candidate_credentials for c in required_credentials)


def _proximity_score(proximity_miles: float) -> float:
    # Monotonically decreasing: closer = higher score; normalised over a 10-mile reference unit
    return 1.0 / (1.0 + proximity_miles / 10.0)


def _pool_median_response_rate(candidates: list[Candidate]) -> float:
    known = [c.response_rate for c in candidates if c.response_rate is not None]
    return median(known) if known else 0.5


def _has_recent_no_show(no_show_history, facility_type: str, as_of: date) -> bool:
    cutoff = as_of - timedelta(days=NO_SHOW_LOOKBACK_DAYS)
    return any(r.facility_type == facility_type and r.date >= cutoff for r in no_show_history)


# --- Rationale builder ---

def _build_rationale(
    cred_score: float,
    is_exact: bool,
    is_specialist_shift: bool,
    proximity_miles: float,
    response_rate: float,
    response_rate_imputed: bool,
    urgency_tier: str,
    preference_boosted: bool,
    no_show_demoted: bool,
) -> str:
    parts = []

    if is_exact and is_specialist_shift:
        parts.append("exact specialist credential match")
    elif is_exact:
        parts.append("exact credential match")
    elif cred_score > 0:
        parts.append(f"partial credential match ({cred_score:.0%})")
    else:
        parts.append("no credential match")

    if urgency_tier == "HIGH":
        parts.append(f"proximity dominant ({proximity_miles:.0f} mi) — urgency ≤4h fill window")
    elif urgency_tier == "MEDIUM":
        parts.append(f"credential and proximity equally weighted ({proximity_miles:.0f} mi)")
    else:
        parts.append(f"credential specificity dominant; proximity secondary given >24h urgency window ({proximity_miles:.0f} mi)")

    rr_note = f"{response_rate:.0%} response rate"
    if response_rate_imputed:
        rr_note += " (imputed — no historical data)"
    parts.append(rr_note)

    if preference_boosted:
        parts.append("facility preference record applied — moved up one rank position")

    if no_show_demoted:
        parts.append("demoted to bottom — no-show at this facility within 90 days")

    return "; ".join(parts)


# --- Main ranking function ---

def rank_candidates(
    job_order_id: str,
    facility_type: str,
    urgency_hours: int,
    required_credentials: list[str],
    eligible_candidates: list[Candidate],
    hospital_preference_history: Optional[list[PlacementRecord]] = None,
    specialist_credential_config: Optional[set[str]] = None,
    as_of: Optional[date] = None,
) -> RankingResult:
    """
    Rank eligible nurse candidates for a shift.

    Inputs match the D4 capability spec exactly. Returns a RankingResult with
    up to 5 ranked candidates and a stated rationale per candidate, or a
    pool_exhausted escalation if no candidates are available.

    specialist_credential_config: set of credential strings classified as
    specialist-tier by the compliance team (Linda). If not provided, rule 6
    (exact-match priority for specialist credentials) does not apply.
    """
    as_of = as_of or date.today()
    hospital_preference_history = hospital_preference_history or []
    specialist_credential_config = specialist_credential_config or set()

    # Rule 1: exclude candidates in active outreach on any concurrent fill cycle
    available = [c for c in eligible_candidates if not c.in_active_outreach]

    if not available:
        return RankingResult(
            job_order_id=job_order_id,
            ranked_candidates=[],
            ranking_timestamp=datetime.now(),
            escalation_type=EscalationType.POOL_EXHAUSTED,
        )

    # Rule 2: identify no-show candidates — demote to bottom, do not exclude
    no_show_ids = {
        c.nurse_id for c in available
        if _has_recent_no_show(c.no_show_history, facility_type, as_of)
    }
    rankable = [c for c in available if c.nurse_id not in no_show_ids]
    no_show_pool = [c for c in available if c.nurse_id in no_show_ids]

    tier = _urgency_tier(urgency_hours)
    w = _weights(tier)
    pool_median_rr = _pool_median_response_rate(eligible_candidates)

    is_specialist_shift = any(c in specialist_credential_config for c in required_credentials)
    preferred_nurse_ids = {
        r.nurse_id for r in hospital_preference_history if r.facility_type == facility_type
    }

    def score_candidate(c: Candidate, demoted: bool = False) -> dict:
        rr = c.response_rate if c.response_rate is not None else pool_median_rr
        rr_imputed = c.response_rate is None
        cred_score = _credential_score(c.credentials, required_credentials)
        is_exact = _is_exact_match(c.credentials, required_credentials)
        raw_score = (
            w["credential"] * cred_score
            + w["proximity"] * _proximity_score(c.proximity_miles)
            + w["response_rate"] * rr
        )
        return {
            "candidate": c,
            "raw_score": raw_score,
            "cred_score": cred_score,
            "is_exact": is_exact,
            "rr": rr,
            "rr_imputed": rr_imputed,
            "preferred": c.nurse_id in preferred_nurse_ids,
            "no_show_demoted": demoted,
            "boosted": False,
        }

    scored = [score_candidate(c) for c in rankable]

    # Rule 6: for specialist shifts, hard-split exact-match above near-match
    # regardless of urgency tier — exact group sorted internally by raw score,
    # then near-match group sorted internally by raw score
    if is_specialist_shift:
        exact_group = sorted([s for s in scored if s["is_exact"]], key=lambda s: s["raw_score"], reverse=True)
        near_group = sorted([s for s in scored if not s["is_exact"]], key=lambda s: s["raw_score"], reverse=True)
        sorted_scored = exact_group + near_group
    else:
        sorted_scored = sorted(scored, key=lambda s: s["raw_score"], reverse=True)

    # Rule 7: apply preference boost — move preferred nurse up one rank if within
    # PREFERENCE_BOOST_THRESHOLD of the next-ranked candidate; never cross the
    # specialist exact/near-match boundary
    for i in range(1, len(sorted_scored)):
        entry = sorted_scored[i]
        if not entry["preferred"]:
            continue
        prev = sorted_scored[i - 1]
        if is_specialist_shift and entry["is_exact"] != prev["is_exact"]:
            continue  # do not boost across the specialist boundary
        if prev["raw_score"] > 0:
            gap = (prev["raw_score"] - entry["raw_score"]) / prev["raw_score"]
            if gap <= PREFERENCE_BOOST_THRESHOLD:
                sorted_scored[i]["boosted"] = True
                sorted_scored[i], sorted_scored[i - 1] = sorted_scored[i - 1], sorted_scored[i]

    # Append no-show candidates at the bottom (rule 2)
    sorted_scored.extend(score_candidate(c, demoted=True) for c in no_show_pool)

    # Build output — cap at MAX_RANKED_CANDIDATES
    ranked = []
    for rank_position, entry in enumerate(sorted_scored[:MAX_RANKED_CANDIDATES], start=1):
        c = entry["candidate"]
        rationale = _build_rationale(
            cred_score=entry["cred_score"],
            is_exact=entry["is_exact"],
            is_specialist_shift=is_specialist_shift,
            proximity_miles=c.proximity_miles,
            response_rate=entry["rr"],
            response_rate_imputed=entry["rr_imputed"],
            urgency_tier=tier,
            preference_boosted=entry["boosted"],
            no_show_demoted=entry["no_show_demoted"],
        )
        ranked.append(RankedCandidate(
            nurse_id=c.nurse_id,
            rank=rank_position,
            rationale=rationale,
            in_active_outreach=False,
        ))

    return RankingResult(
        job_order_id=job_order_id,
        ranked_candidates=ranked,
        ranking_timestamp=datetime.now(),
        escalation_type=None,
    )
