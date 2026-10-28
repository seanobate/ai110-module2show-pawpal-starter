"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import Optional

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


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

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as done and return its next occurrence if it recurs."""
        self.completed = True
        days = RECURRENCE_DAYS.get(self.frequency)
        if days is None:
            return None
        return replace(self, due_date=self.due_date + timedelta(days=days), completed=False)

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

    def complete_task(self, title: str) -> Optional[Task]:
        """Complete the earliest pending task with this title; queue and return its next occurrence."""
        pending = sorted(
            (t for t in self.tasks if t.title == title and not t.completed),
            key=lambda t: t.due_date,
        )
        if not pending:
            raise ValueError(f"{self.name} has no pending task named {title!r}")
        next_task = pending[0].mark_complete()
        if next_task:
            self.add_task(next_task)
        return next_task


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

    def sort_by_priority(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Return tasks ordered high to low priority, breaking ties by time."""
        return sorted(pairs, key=lambda p: (-p[1].priority_value(), p[1].time))

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        on_date: Optional[date] = None,
    ) -> list[tuple[Pet, Task]]:
        """Return the owner's tasks matching every filter that is given (None means any)."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if (pet_name is None or pet.name == pet_name)
            and (completed is None or task.completed == completed)
            and (on_date is None or task.due_date == on_date)
        ]

    def filter_by_time(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Keep the highest-priority tasks that fit in the owner's available minutes."""
        by_priority = self.sort_by_priority(pairs)
        kept, used = [], 0
        self.skipped = []
        for pet, task in by_priority:
            if used + task.duration_minutes <= self.owner.available_minutes:
                kept.append((pet, task))
                used += task.duration_minutes
            else:
                self.skipped.append((pet, task))
        return kept

    def detect_conflicts(self, pairs: Optional[list[tuple[Pet, Task]]] = None) -> list[str]:
        """Return a warning for each date/time slot that has two or more pending tasks."""
        if pairs is None:
            pairs = self.filter_tasks(completed=False)
        slots = defaultdict(list)
        for pet, task in pairs:
            slots[(task.due_date, task.time)].append(f"{task.title} ({pet.name})")
        return [
            f"Conflict on {day} at {time}: " + ", ".join(names)
            for (day, time), names in sorted(slots.items())
            if len(names) > 1
        ]

    def mark_task_complete(self, pet_name: str, title: str) -> Optional[Task]:
        """Complete a pet's task by name and return the next occurrence, if any."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"No pet named {pet_name!r}")
        return pet.complete_task(title)

    def generate_plan(self, on_date: Optional[date] = None) -> list[tuple[Pet, Task]]:
        """Build the plan: pending tasks due on the date, trimmed to the time budget, sorted by time."""
        due = self.filter_tasks(completed=False, on_date=on_date or date.today())
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
