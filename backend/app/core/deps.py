from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.business import Business

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_business(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Business:
    """Dependencia: devuelve el negocio autenticado o lanza 401."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    business_id: str = payload.get("sub")
    if business_id is None:
        raise credentials_exception

    business = db.query(Business).filter(Business.id == int(business_id)).first()
    if business is None:
        raise credentials_exception

    return business


def require_active_subscription(
    business: Business = Depends(get_current_business),
) -> Business:
    """Dependencia: verifica suscripción activa."""
    from datetime import datetime, timezone

    if business.suscripcion_vence and business.suscripcion_vence < datetime.now(
        timezone.utc
    ).replace(tzinfo=None):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Tu suscripción ha vencido. Por favor renueva tu plan para continuar.",
        )
    return business
