from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, date

from dfes.bans import parse_bans


@dataclass
class Entry:
    published: datetime
    dfes_published: datetime
    summary: str
    bans: TotalFireBans | None = None

    def parse_summary(self):
        self.bans = parse_bans(self.summary)


@dataclass
class Feed:
    title: str
    published: datetime
    entries: list[Entry]


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
