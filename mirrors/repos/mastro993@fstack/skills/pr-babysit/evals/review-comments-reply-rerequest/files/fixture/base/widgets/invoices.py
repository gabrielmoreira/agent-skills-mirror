from dataclasses import dataclass


@dataclass
class Invoice:
    number: str
    customer: str
    amount: float
    status: str = "open"  # open | paid | void

    def __post_init__(self):
        # Amounts arrive as strings from the importer; float() also rejects None and blanks.
        self.amount = float(self.amount)
