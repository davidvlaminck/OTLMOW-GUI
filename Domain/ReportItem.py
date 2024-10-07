from dataclasses import dataclass

from Domain.enums import ReportAction


@dataclass
class ReportItem:
    id: str
    actie: ReportAction
    attribute: str
    original_value: str
    new_value: str
