from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from proyecto.extensions import Base

question_tag = Table(
        "question_tag",
        Base.metadata,
        Column("question_id", ForeignKey("question.id")),
        Column("tag_id", ForeignKey("tag.id"))
        )
