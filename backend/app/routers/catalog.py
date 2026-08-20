from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DeliveryArea, DeliverySlot, FlowerType, Occasion
from ..schemas import DeliveryAreaOut, DeliverySlotOut, FlowerTypeOut, OccasionOut, SameDayOut
from ..timeutil import same_day_status

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/occasions", response_model=list[OccasionOut])
def list_occasions(db: Session = Depends(get_db)):
    return db.query(Occasion).order_by(Occasion.sort_order).all()


@router.get("/flower-types", response_model=list[FlowerTypeOut])
def list_flower_types(db: Session = Depends(get_db)):
    return db.query(FlowerType).order_by(FlowerType.name).all()


@router.get("/delivery-areas", response_model=list[DeliveryAreaOut])
def list_areas(db: Session = Depends(get_db)):
    return db.query(DeliveryArea).order_by(DeliveryArea.name).all()


@router.get("/delivery-slots", response_model=list[DeliverySlotOut])
def list_slots(db: Session = Depends(get_db)):
    return db.query(DeliverySlot).order_by(DeliverySlot.sort_order).all()


@router.get("/same-day", response_model=SameDayOut)
def same_day():
    return same_day_status()
