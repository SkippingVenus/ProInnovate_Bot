from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FacebookPage(Base):
    """Página de Facebook conectada a un negocio."""

    __tablename__ = "facebook_pages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("negocios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fb_page_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    fb_page_name: Mapped[str] = mapped_column(String(200), nullable=False)
    fb_access_token: Mapped[str] = mapped_column(Text, nullable=False)  # Encrypted
    instagram_account_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relación inversa
    business: Mapped["Business"] = relationship("Business", back_populates="pages")

    def __repr__(self) -> str:
        return f"<FacebookPage(id={self.id}, fb_page_id={self.fb_page_id}, business_id={self.business_id})>"
