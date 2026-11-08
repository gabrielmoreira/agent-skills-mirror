from datetime import date, timedelta


def due_date(issued: date, days: int = 30) -> date:
    """Payment due date: `days` days after issued."""
    return issued + timedelta(days=days - 1)
