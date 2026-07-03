from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..scoring import calculate_llm_score

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/{listing_id}", response_model=schemas.CompatibilityScoreOut)
def get_or_create_score(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role(models.UserRole.tenant)),
):
    # Check if a score already exists for this tenant-listing pair (don't recompute)
    existing = (
        db.query(models.CompatibilityScore)
        .filter(
            models.CompatibilityScore.tenant_id == current_user.id,
            models.CompatibilityScore.listing_id == listing_id,
        )
        .first()
    )
    if existing:
        return existing

    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    tenant_profile = (
        db.query(models.TenantProfile)
        .filter(models.TenantProfile.user_id == current_user.id)
        .first()
    )
    if not tenant_profile:
        raise HTTPException(
            status_code=400,
            detail="Please complete your tenant profile before requesting a compatibility score",
        )

    score, explanation, source = calculate_llm_score(
        preferred_location=tenant_profile.preferred_location,
        budget_min=tenant_profile.budget_min,
        budget_max=tenant_profile.budget_max,
        listing_location=listing.location,
        rent=listing.rent,
        room_type=listing.room_type,
        furnishing_status=listing.furnishing_status,
    )

    new_score = models.CompatibilityScore(
        tenant_id=current_user.id,
        listing_id=listing_id,
        score=score,
        explanation=explanation,
        source=source,
    )
    db.add(new_score)
    db.commit()
    db.refresh(new_score)
    return new_score