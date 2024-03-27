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
    issued: datetime
    declared_for: date
    locations: AffectedAreas
    revoked: bool = False


@dataclass
class Item:
    published: datetime
    description: str
    bans: TotalFireBans | None = None


@dataclass
class Feed:
    title: str
    published: datetime
    items: list[Item]
