"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "general"  # walk, feeding, meds, enrichment, grooming
    frequency: str = "daily"  # "daily" | "weekly"
    preferred_time: Optional[str] = None  # "HH:MM"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass

    def priority_value(self) -> int:
        """Return a numeric rank for priority (higher = more important)."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove a task by title."""
        pass

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed."""
        pass


@dataclass
class Owner:
    """The pet owner, their time budget, and their pets."""

    name: str
    available_minutes: int
    day_start: str = "08:00"  # "HH:MM"
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every pending task across all pets, paired with its pet."""
        pass


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.plan: list[tuple[str, Pet, Task]] = []  # (start_time, pet, task)
        self.skipped: list[tuple[Pet, Task]] = []

    def sort_tasks(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Order tasks by priority (high first), then by preferred time."""
        pass

    def filter_by_time(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Keep tasks that fit within the owner's available minutes."""
        pass

    def generate_plan(self) -> list[tuple[str, Pet, Task]]:
        """Sort, filter, and assign start times to build today's plan."""
        pass

    def explain_plan(self) -> str:
        """Describe why each task was scheduled or skipped."""
        pass
