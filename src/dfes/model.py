from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class AffectedAreas:
    pairs: list[tuple[str, str]]

    def to_dict(self) -> dict:
        result = defaultdict(list)
        for pair in self.pairs:
            result[pair[0]].append(pair[1])

        return result


@dataclass
class TotalFireBans:
    revoked: bool
    issued: datetime
    declared_for: date
    locations: AffectedAreas


