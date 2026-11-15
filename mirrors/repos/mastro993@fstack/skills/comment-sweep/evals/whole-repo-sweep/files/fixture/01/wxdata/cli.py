"""Command-line entry point, installed as `wx`."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import click

from wxdata import db
from wxdata.aggregate import daily_stats
from wxdata.client import SkyFeedClient
from wxdata.config import DEFAULT_CONFIG_PATH, Settings, load_settings
from wxdata.export import to_parquet
from wxdata.ingest import ingest_day
from wxdata.models import all_station_ids, readings_between
from wxdata.reports import write_daily_report

DAY = click.DateTime(formats=["%Y-%m-%d"])


def _day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime(day.year, day.month, day.day, tzinfo=UTC)
    return start, start + timedelta(days=1)


@click.group()
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_PATH,
    show_default=True,
    help="Path to wxdata.yaml.",
)
@click.pass_context
def main(ctx: click.Context, config_path: Path) -> None:
    """Weather station data tools: ingest SkyFeed readings, build reports, export data."""
    settings = load_settings(config_path)
    db.init_engine(settings.database_url)
    ctx.obj = settings
    ctx.call_on_close(db.dispose)


@main.command()
@click.option("--day", "day_dt", type=DAY, required=True, help="UTC day, YYYY-MM-DD.")
@click.option(
    "--station",
    "stations",
    multiple=True,
    help="Station ID; repeat for several. Defaults to the configured stations.",
)
@click.pass_obj
def ingest(settings: Settings, day_dt: datetime, stations: tuple[str, ...]) -> None:
    """Fetch, clean, and store every SkyFeed reading for DAY."""
    # Parse the date
    day = day_dt.date()
    with SkyFeedClient(settings.skyfeed_api_key) as client, db.session_scope() as session:
        station_ids = stations or settings.stations or tuple(all_station_ids(session))
        result = ingest_day(client, session, station_ids, day)
    click.echo(
        f"{day}: fetched {result.fetched}, stored {result.stored}, "
        f"dropped {result.duplicates} duplicates and {result.outliers} outliers"
    )


@main.command()
@click.option("--day", "day_dt", type=DAY, required=True, help="UTC day, YYYY-MM-DD.")
@click.option("--out", type=click.Path(path_type=Path, dir_okay=False), required=True)
@click.pass_obj
def report(settings: Settings, day_dt: datetime, out: Path) -> None:
    """Render the daily HTML station report for DAY to OUT."""
    day = day_dt.date()
    start, end = _day_bounds(day)
    with db.session_scope() as session:
        stats = daily_stats(readings_between(session, start, end, settings.stations), day)
    write_daily_report(stats, day, out)
    click.echo(f"wrote {out}")


@main.command()
@click.option("--start", "start_dt", type=DAY, required=True, help="First UTC day, YYYY-MM-DD.")
@click.option("--end", "end_dt", type=DAY, required=True, help="Day after the last one.")
@click.option("--out", type=click.Path(path_type=Path, dir_okay=False), required=True)
@click.pass_obj
def export(settings: Settings, start_dt: datetime, end_dt: datetime, out: Path) -> None:
    """Write the readings from START up to, but not including, END to a Parquet file."""
    start = start_dt.replace(tzinfo=UTC)
    end = end_dt.replace(tzinfo=UTC)
    if end <= start:
        raise click.BadParameter("--end must be after --start")
    with db.session_scope() as session:
        written = to_parquet(readings_between(session, start, end, settings.stations), out)
    click.echo(f"wrote {written} readings to {out}")


if __name__ == "__main__":  # pragma: no cover
    main()
