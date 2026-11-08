from typing import Optional, List
from sqlalchemy import Integer, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.persistence.models import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.shared.persistence.models import AgentModel


# Tabella associativa (meglio come Table, non come classe Model)
team_workers = Table(
    'team_workers',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True),
    Column('agent_id', Integer, ForeignKey('agents.id', ondelete='RESTRICT'), primary_key=True)
)


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Foreign key per il supervisor
    supervisor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("agents.id", ondelete="RESTRICT"),
        nullable=False
    )
    # Relationship per ottenere il supervisor (one to one)    (Come mai? perchè così ho un campo "team.supervisor.name" mi dà già il nome del supervisor, pur avendo solo id nella tabella)
    supervisor: Mapped["AgentModel"] = relationship(
        "AgentModel",
        foreign_keys=[supervisor_id],      # avendo nella table la foreign key la uso nella relationship (forse è opzionale e ORM lo aggiungerebbe da solo)
        back_populates="managed_teams"      # crea relazione bidirezionale: in AgentModel il campo "managed_teams" si riempie automaticamente
    )

    # Relationship per i workers (one to many)
    workers: Mapped[List["AgentModel"]] = relationship(
        "AgentModel",
        secondary="team_workers",       # uso campo secondary perchè non ho una foreign key diretta da Team a Agent
        back_populates="worker_teams"
    )

