import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def new_id() -> str:
    return str(uuid.uuid4())


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("name", name="uq_teams_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(40), nullable=False)

    home_matches: Mapped[list["Match"]] = relationship(
        back_populates="home_team",
        foreign_keys="Match.home_team_id",
    )
    away_matches: Mapped[list["Match"]] = relationship(
        back_populates="away_team",
        foreign_keys="Match.away_team_id",
    )


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    home_team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id"), nullable=False
    )
    away_team_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("teams.id"), nullable=False
    )
    home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    home_team: Mapped[Team] = relationship(foreign_keys=[home_team_id], back_populates="home_matches")
    away_team: Mapped[Team] = relationship(foreign_keys=[away_team_id], back_populates="away_matches")
