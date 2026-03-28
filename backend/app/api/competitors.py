from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_active_subscription
from app.models.business import Business
from app.models.competitor import Competitor

router = APIRouter(prefix="/api/competitors", tags=["competitors"])


class CompetitorCreate(BaseModel):
    nombre: str
    fb_page_url: Optional[str] = None
    ig_username: Optional[str] = None
    gmb_place_id: Optional[str] = None


class CompetitorResponse(BaseModel):
    id: int
    nombre: str
    fb_page_url: Optional[str]
    ig_username: Optional[str]
    gmb_place_id: Optional[str]
    ultimo_analisis: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/", response_model=List[CompetitorResponse])
def list_competitors(
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Lista los competidores del negocio."""
    return db.query(Competitor).filter(Competitor.negocio_id == business.id).all()


@router.post("/", response_model=CompetitorResponse, status_code=201)
def create_competitor(
    payload: CompetitorCreate,
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Agrega un competidor para monitoreo."""
    competitor = Competitor(
        negocio_id=business.id,
        nombre=payload.nombre,
        fb_page_url=payload.fb_page_url,
        ig_username=payload.ig_username,
        gmb_place_id=payload.gmb_place_id,
    )
    db.add(competitor)
    db.commit()
    db.refresh(competitor)
    return competitor


@router.delete("/{competitor_id}")
def delete_competitor(
    competitor_id: int,
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Elimina un competidor del listado de monitoreo."""
    competitor = db.query(Competitor).filter(
        Competitor.id == competitor_id,
        Competitor.negocio_id == business.id,
    ).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competidor no encontrado.")
    db.delete(competitor)
    db.commit()
    return {"detail": "Competidor eliminado."}
