"""HTML and plain-text reports rendered from Jinja templates."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape

from wxdata.aggregate import DailyStats, hottest, low_coverage
from wxdata.client import SKYFEED_TERMS_URL
from wxdata.textutil import slugify

HEAT_ALERT_C = 35.0
REPORT_URL = "https://reports.wxdata.northwind.example/daily/{day}.html"

_env = Environment(
    loader=PackageLoader("wxdata", "templates"),
    autoescape=select_autoescape(["html", "html.j2"]),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)
_env.filters["slug"] = slugify


# ===== Rendering =====


def render_daily_report(stats: list[DailyStats], day: date) -> str:
    template = _env.get_template("daily_report.html.j2")
    return template.render(
        day=day,
        stats=stats,
        hottest=hottest(stats, 3),
        low_coverage=low_coverage(stats),
        terms_url=SKYFEED_TERMS_URL,
    )


def write_daily_report(stats: list[DailyStats], day: date, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_daily_report(stats, day), encoding="utf-8")
    return out


def render_alert(stats: list[DailyStats], day: date) -> str | None:
    hot = [s for s in stats if s.max_c >= HEAT_ALERT_C]
    if not hot:
        return None
    template = _env.get_template("alert_email.txt.j2")
    return template.render(
        day=day,
        stations=sorted(hot, key=lambda s: s.max_c, reverse=True),
        threshold=HEAT_ALERT_C,
        report_url=REPORT_URL.format(day=day.isoformat()),
    )
