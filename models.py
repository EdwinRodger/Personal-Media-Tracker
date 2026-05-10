"""Domain types and allowed values for media entries."""

from dataclasses import dataclass
from typing import Optional

MEDIA_TYPES = ("Movie", "TV Show")
STATUSES = ("Plan to watch", "Watching", "Watched", "Dropped")


@dataclass
class MediaRow:
    id: Optional[int]
    title: str
    media_type: str
    status: str
    year: Optional[int]
    rating: Optional[float]
    notes: str
