from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from proyecto.extensions import db

class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
