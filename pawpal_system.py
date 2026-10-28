"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "general"  # walk, feeding, meds, enrichment, grooming
    time: str = "08:00"  # "HH:MM", zero-padded so it sorts as a string
    frequency: str = "once"  # "once" | "daily" | "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_value(self) -> int:
        """Return a numeric rank for priority (higher = more important)."""
        return PRIORITY_RANK.get(self.priority, 0)


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove all tasks with the given title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """The pet owner, their time budget, and their pets."""

    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Look up a pet by name, or return None."""
        return next((p for p in self.pets if p.name == name), None)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all pets, paired with its pet."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.plan: list[tuple[Pet, Task]] = []
        self.skipped: list[tuple[Pet, Task]] = []

    def sort_by_time(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Return tasks ordered by their HH:MM time, earliest first."""
        return sorted(pairs, key=lambda p: p[1].time)

    def filter_by_time(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Keep the highest-priority tasks that fit in the owner's available minutes."""
        by_priority = sorted(pairs, key=lambda p: -p[1].priority_value())
        kept, used = [], 0
        self.skipped = []
        for pet, task in by_priority:
            if used + task.duration_minutes <= self.owner.available_minutes:
                kept.append((pet, task))
                used += task.duration_minutes
            else:
                self.skipped.append((pet, task))
        return kept

    def generate_plan(self, on_date: Optional[date] = None) -> list[tuple[Pet, Task]]:
        """Build the plan: pending tasks due on the date, trimmed to the time budget, sorted by time."""
        on_date = on_date or date.today()
        due = [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if not task.completed and task.due_date == on_date
        ]
        self.plan = self.sort_by_time(self.filter_by_time(due))
        return self.plan

    def explain_plan(self) -> str:
        """Describe why each task was scheduled or skipped."""
        if not self.plan and not self.skipped:
            return "No tasks are due today."
        used = sum(t.duration_minutes for _, t in self.plan)
        lines = [
            f"Scheduled {len(self.plan)} task(s) using {used} of "
            f"{self.owner.available_minutes} available minutes, highest priority first."
        ]
        for pet, task in self.plan:
            lines.append(
                f"- {task.time} {task.title} ({pet.name}): {task.priority} priority, "
                f"{task.duration_minutes} min fit in the budget."
            )
        for pet, task in self.skipped:
            lines.append(
                f"- Skipped {task.title} ({pet.name}): {task.priority} priority, "
                f"{task.duration_minutes} min did not fit in the remaining time."
            )
        return "\n".join(lines)
