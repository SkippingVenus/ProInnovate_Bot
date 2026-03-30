from datetime import date, datetime, timedelta
from typing import Optional, List

from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import require_active_subscription
from app.models.business import Business
from app.models.message import Message
from app.models.metric import Metric

router = APIRouter(prefix="/api/reports", tags=["reports"])


class DashboardMetrics(BaseModel):
    mensajes_hoy: int
    tasa_respuesta: float  # porcentaje
    tiempo_promedio_respuesta_horas: Optional[float]
    rating_google: Optional[float]
    seguidores_total: int
    alcance_organico_semana: int
    mensajes_urgentes_pendientes: int


class MetricEntry(BaseModel):
    fecha: date
    plataforma: str
    seguidores: Optional[int]
    alcance_organico: Optional[int]
    mensajes_recibidos: Optional[int]
    mensajes_respondidos: Optional[int]
    rating_promedio: Optional[float]

    model_config = {"from_attributes": True}


@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard(
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Devuelve las métricas del dashboard para el negocio autenticado."""
    hoy = date.today()
    inicio_semana = datetime.utcnow() - timedelta(days=7)

    # Mensajes recibidos hoy
    mensajes_hoy = db.query(func.count(Message.id)).filter(
        Message.negocio_id == business.id,
        func.date(Message.created_at) == hoy,
    ).scalar() or 0

    # Tasa de respuesta (últimos 30 días)
    total_30 = db.query(func.count(Message.id)).filter(
        Message.negocio_id == business.id,
        Message.created_at >= datetime.utcnow() - timedelta(days=30),
    ).scalar() or 0

    respondidos_30 = db.query(func.count(Message.id)).filter(
        Message.negocio_id == business.id,
        Message.estado.in_(["aprobado", "enviado"]),
        Message.created_at >= datetime.utcnow() - timedelta(days=30),
    ).scalar() or 0

    tasa_respuesta = (respondidos_30 / total_30 * 100) if total_30 > 0 else 0.0

    # Tiempo promedio de respuesta
    tiempo_promedio = None
    respondidos_con_tiempo = db.query(Message).filter(
        Message.negocio_id == business.id,
        Message.respondido_at.isnot(None),
        Message.created_at >= datetime.utcnow() - timedelta(days=30),
    ).all()
    if respondidos_con_tiempo:
        tiempos = [
            (m.respondido_at - m.created_at).total_seconds() / 3600
            for m in respondidos_con_tiempo
            if m.respondido_at and m.created_at
        ]
        tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else None

    # Rating promedio de Google (últimas métricas)
    ultima_metrica_google = db.query(Metric).filter(
        Metric.negocio_id == business.id,
        Metric.plataforma == "google",
    ).order_by(Metric.fecha.desc()).first()
    rating_google = ultima_metrica_google.rating_promedio if ultima_metrica_google else None

    # Seguidores totales (FB + IG)
    seguidores_fb = db.query(Metric).filter(
        Metric.negocio_id == business.id,
        Metric.plataforma == "facebook",
    ).order_by(Metric.fecha.desc()).first()
    seguidores_ig = db.query(Metric).filter(
        Metric.negocio_id == business.id,
        Metric.plataforma == "instagram",
    ).order_by(Metric.fecha.desc()).first()

    seguidores_total = (seguidores_fb.seguidores or 0 if seguidores_fb else 0) + (
        seguidores_ig.seguidores or 0 if seguidores_ig else 0
    )

    # Alcance orgánico de la semana
    alcance_semana = db.query(func.sum(Metric.alcance_organico)).filter(
        Metric.negocio_id == business.id,
        Metric.fecha >= inicio_semana.date(),
    ).scalar() or 0

    # Mensajes urgentes pendientes
    urgentes_pendientes = db.query(func.count(Message.id)).filter(
        Message.negocio_id == business.id,
        Message.urgente == True,
        Message.estado == "pendiente",
    ).scalar() or 0

    return DashboardMetrics(
        mensajes_hoy=mensajes_hoy,
        tasa_respuesta=round(tasa_respuesta, 1),
        tiempo_promedio_respuesta_horas=round(tiempo_promedio, 2) if tiempo_promedio else None,
        rating_google=rating_google,
        seguidores_total=seguidores_total,
        alcance_organico_semana=alcance_semana,
        mensajes_urgentes_pendientes=urgentes_pendientes,
    )


@router.get("/metrics", response_model=List[MetricEntry])
def get_metrics(
    plataforma: Optional[str] = Query(None),
    days: int = Query(30, le=90),
    db: Session = Depends(get_db),
    business: Business = Depends(require_active_subscription),
):
    """Devuelve métricas históricas del negocio."""
    desde = date.today() - timedelta(days=days)
    query = db.query(Metric).filter(
        Metric.negocio_id == business.id,
        Metric.fecha >= desde,
    )
    if plataforma:
        query = query.filter(Metric.plataforma == plataforma)
    return query.order_by(Metric.fecha.desc()).all()
