from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from proyecto.extensions import Base

class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r})"
