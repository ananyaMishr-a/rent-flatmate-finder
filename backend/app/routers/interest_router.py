from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..email_utils import send_email

router = APIRouter(prefix="/interests", tags=["interests"])


@router.post("/", response_model=schemas.InterestRequestOut)
def express_interest(
    payload: schemas.InterestRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role(models.UserRole.tenant)),
):
    listing = db.query(models.Listing).filter(models.Listing.id == payload.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.is_filled:
        raise HTTPException(status_code=400, detail="This listing is already filled")

    existing = (
        db.query(models.InterestRequest)
        .filter(
            models.InterestRequest.tenant_id == current_user.id,
            models.InterestRequest.listing_id == payload.listing_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="You already expressed interest in this listing")

    new_interest = models.InterestRequest(
        tenant_id=current_user.id,
        listing_id=payload.listing_id,
    )
    db.add(new_interest)
    db.commit()
    db.refresh(new_interest)

    score_entry = (
        db.query(models.CompatibilityScore)
        .filter(
            models.CompatibilityScore.tenant_id == current_user.id,
            models.CompatibilityScore.listing_id == payload.listing_id,
        )
        .first()
    )
    if score_entry and score_entry.score > 80:
        owner = db.query(models.User).filter(models.User.id == listing.owner_id).first()
        send_email(
            to=owner.email,
            subject="High-compatibility tenant interested in your listing!",
            body=f"{current_user.name} (compatibility score: {score_entry.score}) has expressed interest in your listing at {listing.location}.",
        )

    return new_interest


@router.patch("/{interest_id}", response_model=schemas.InterestRequestOut)
def update_interest_status(
    interest_id: int,
    payload: schemas.InterestStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role(models.UserRole.owner)),
):
    interest = db.query(models.InterestRequest).filter(models.InterestRequest.id == interest_id).first()
    if not interest:
        raise HTTPException(status_code=404, detail="Interest request not found")

    listing = db.query(models.Listing).filter(models.Listing.id == interest.listing_id).first()
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this listing")

    interest.status = payload.status
    db.commit()
    db.refresh(interest)

    tenant = db.query(models.User).filter(models.User.id == interest.tenant_id).first()
    send_email(
        to=tenant.email,
        subject=f"Your interest request was {payload.status.value}",
        body=f"The owner has {payload.status.value} your interest in the listing at {listing.location}.",
    )

    return interest