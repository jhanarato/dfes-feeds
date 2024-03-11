from dataclasses import dataclass
from datetime import datetime

from dfes.bans import TotalFireBans, parse_bans


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
