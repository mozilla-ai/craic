"""Review queue endpoints for the team API."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .auth import get_current_user
from .deps import get_store
from .knowledge_unit import KnowledgeUnit
from .store import TeamStore


class ReviewItem(BaseModel):
    """A KU with its review metadata."""

    knowledge_unit: KnowledgeUnit
    status: str
    reviewed_by: str | None
    reviewed_at: str | None


class ReviewQueueResponse(BaseModel):
    """Paginated review queue response."""

    items: list[ReviewItem]
    total: int
    offset: int
    limit: int


class ReviewDecisionResponse(BaseModel):
    """Response after approving or rejecting a KU."""

    unit_id: str
    status: str
    reviewed_by: str
    reviewed_at: str


class DailyCount(BaseModel):
    """Daily proposal count."""

    date: str
    proposed: int


class TrendsResponse(BaseModel):
    """Trend data for the dashboard chart."""

    daily: list[DailyCount]


class ReviewStatsResponse(BaseModel):
    """Dashboard metrics response."""

    counts: dict[str, int]
    domains: dict[str, int]
    confidence_distribution: dict[str, int]
    recent_activity: list[dict]
    trends: TrendsResponse


router = APIRouter(prefix="/review", tags=["review"])


@router.get("/queue")
def review_queue(
    limit: int = 20,
    offset: int = 0,
    _user: str = Depends(get_current_user),
    store: TeamStore = Depends(get_store),
) -> ReviewQueueResponse:
    """Return pending KUs for review.

    Args:
        limit: Maximum number of items to return.
        offset: Number of items to skip.
        _user: The authenticated user (unused, enforces auth).
        store: The team store dependency.

    Returns:
        A paginated list of pending knowledge units with review metadata.
    """
    items = store.pending_queue(limit=limit, offset=offset)
    total = store.pending_count()
    return ReviewQueueResponse(
        items=[
            ReviewItem(
                knowledge_unit=item["knowledge_unit"],
                status=item["status"],
                reviewed_by=item["reviewed_by"],
                reviewed_at=item["reviewed_at"],
            )
            for item in items
        ],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/{unit_id}/approve")
def approve_unit(
    unit_id: str,
    username: str = Depends(get_current_user),
    store: TeamStore = Depends(get_store),
) -> ReviewDecisionResponse:
    """Approve a pending KU.

    Args:
        unit_id: The knowledge unit identifier.
        username: The authenticated reviewer's username.
        store: The team store dependency.

    Returns:
        The updated review decision with status and reviewer details.

    Raises:
        HTTPException: With status 404 if the unit does not exist.
        HTTPException: With status 409 if the unit has already been reviewed.
    """
    status = store.get_review_status(unit_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Knowledge unit not found")
    if status["status"] != "pending":
        raise HTTPException(
            status_code=409, detail=f"Knowledge unit already {status['status']}"
        )
    store.set_review_status(unit_id, "approved", username)
    updated = store.get_review_status(unit_id)
    assert updated is not None  # Unit exists; we just wrote to it.
    return ReviewDecisionResponse(
        unit_id=unit_id,
        status=updated["status"],
        reviewed_by=updated["reviewed_by"],
        reviewed_at=updated["reviewed_at"],
    )


@router.post("/{unit_id}/reject")
def reject_unit(
    unit_id: str,
    username: str = Depends(get_current_user),
    store: TeamStore = Depends(get_store),
) -> ReviewDecisionResponse:
    """Reject a pending KU.

    Args:
        unit_id: The knowledge unit identifier.
        username: The authenticated reviewer's username.
        store: The team store dependency.

    Returns:
        The updated review decision with status and reviewer details.

    Raises:
        HTTPException: With status 404 if the unit does not exist.
        HTTPException: With status 409 if the unit has already been reviewed.
    """
    status = store.get_review_status(unit_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Knowledge unit not found")
    if status["status"] != "pending":
        raise HTTPException(
            status_code=409, detail=f"Knowledge unit already {status['status']}"
        )
    store.set_review_status(unit_id, "rejected", username)
    updated = store.get_review_status(unit_id)
    assert updated is not None  # Unit exists; we just wrote to it.
    return ReviewDecisionResponse(
        unit_id=unit_id,
        status=updated["status"],
        reviewed_by=updated["reviewed_by"],
        reviewed_at=updated["reviewed_at"],
    )


@router.get("/stats")
def review_stats(
    _user: str = Depends(get_current_user),
    store: TeamStore = Depends(get_store),
) -> ReviewStatsResponse:
    """Return dashboard metrics.

    Confidence distribution and recent activity are placeholder empty values
    in this task. They are wired to real store methods in Task 8.

    Args:
        _user: The authenticated user (unused, enforces auth).
        store: The team store dependency.

    Returns:
        Aggregated counts by status, domain distribution, and empty
        confidence/activity placeholders.
    """
    counts = store.counts_by_status()
    return ReviewStatsResponse(
        counts={
            "pending": counts.get("pending", 0),
            "approved": counts.get("approved", 0),
            "rejected": counts.get("rejected", 0),
        },
        domains=store.domain_counts(),
        confidence_distribution={},
        recent_activity=[],
        trends=TrendsResponse(daily=[]),
    )
