from sqlalchemy import (
Column,
Integer,
String,
Text,
TIMESTAMP,
ForeignKey,
text
)

from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="created")
    thread_id = Column(String(70), unique=True, nullable=False)

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP")
    )

    answers = relationship(
        "ProjectAnswer",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    specification = relationship(
        "Specification",
        uselist=False,
        back_populates="project",
        cascade="all, delete-orphan"
    )
class ProjectAnswer(Base):
    __tablename__ = "project_answers"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    iteration = Column(Integer, nullable=False, default=1)
    questions = Column(Text)
    answers = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    project = relationship(
        "Project",
        back_populates="answers",
    )

class Specification(Base):
    __tablename__ = "specifications"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    content = Column(Text, nullable=False)

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )

    project = relationship(
        "Project",
        back_populates="specification"
    )
