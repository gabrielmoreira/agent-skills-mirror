"""SQLAlchemy models for stations and their readings."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, UniqueConstraint, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Station(Base):
    __tablename__ = "stations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")

    readings: Mapped[list[Reading]] = relationship(back_populates="station")


class Reading(Base):
    __tablename__ = "readings"
    __table_args__ = (
        UniqueConstraint("station_id", "observed_at", name="uq_readings_station_time"),
        Index("ix_readings_observed_at", "observed_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[str] = mapped_column(ForeignKey("stations.id"))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    temperature_c: Mapped[float | None] = mapped_column(Float)
    pressure_hpa: Mapped[float | None] = mapped_column(Float)
    humidity_pct: Mapped[float | None] = mapped_column(Float)

    station: Mapped[Station] = relationship(back_populates="readings")


def station_by_id(session: Session, station_id: str) -> Station | None:
    """Returns the station."""
    return session.get(Station, station_id)


def all_station_ids(session: Session) -> list[str]:
    return list(session.scalars(select(Station.id).order_by(Station.id)))


def readings_between(
    session: Session,
    start: datetime,
    end: datetime,
    station_ids: Sequence[str] | None = None,
) -> list[Reading]:
    """Readings with start <= observed_at < end, oldest first."""
    query = select(Reading).where(Reading.observed_at >= start, Reading.observed_at < end)
    if station_ids:
        query = query.where(Reading.station_id.in_(station_ids))
    return list(session.scalars(query.order_by(Reading.observed_at, Reading.station_id)))
