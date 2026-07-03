from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/listings", tags=["listings"])

@router.post("/", response_model=schemas.ListingOut)
def create_listing(
    listing: schemas.ListingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role(models.UserRole.owner)),
):
    new_listing = models.Listing(
        owner_id=current_user.id,
        location=listing.location,
        rent=listing.rent,
        available_from=listing.available_from,
        room_type=listing.room_type,
        furnishing_status=listing.furnishing_status,
        photo_url=listing.photo_url,
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return new_listing

@router.get("/", response_model=List[schemas.ListingOut])
def browse_listings(
    location: Optional[str] = None,
    min_rent: Optional[float] = None,
    max_rent: Optional[float] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Listing).filter(models.Listing.is_filled == False)

    if location:
        query = query.filter(models.Listing.location.ilike(f"%{location}%"))
    if min_rent is not None:
        query = query.filter(models.Listing.rent >= min_rent)
    if max_rent is not None:
        query = query.filter(models.Listing.rent <= max_rent)

    return query.all()

@router.patch("/{listing_id}/mark-filled", response_model=schemas.ListingOut)
def mark_filled(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role(models.UserRole.owner)),
):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this listing")

    listing.is_filled = True
    db.commit()
    db.refresh(listing)
    return listing