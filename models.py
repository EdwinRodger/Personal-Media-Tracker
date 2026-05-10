"""Domain types and allowed values for media entries.

This module defines the core data structures and constant lists used throughout
the application to ensure consistency between the UI, validation, and database.
"""

from dataclasses import dataclass
from typing import Optional

MEDIA_TYPES = ("Movie", "TV Show")
STATUSES = ("Plan to watch", "Watching", "Watched", "Dropped")


@dataclass
class MediaRow:
    """
    Represents a single media entry record.

    Attributes:
        id (Optional[int]): The database primary key. None for new entries.
        title (str): The title of the movie or show.
        media_type (str): The type of media (from MEDIA_TYPES).
        status (str): The current watch status (from STATUSES).
        year (Optional[int]): The release year of the media.
        rating (Optional[float]): The user rating (0-10).
        notes (str): Additional comments or details.
    """
    id: Optional[int]
    title: str
    media_type: str
    status: str
    year: Optional[int]
    rating: Optional[float]
    notes: str
