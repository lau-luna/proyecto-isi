from sqlalchemy import Column, ForeignKey, Table

from proyecto.extensions import Base

question_tag = Table(
    "question_tag",
    Base.metadata,
    Column("question_id", ForeignKey("question.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)
