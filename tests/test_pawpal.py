from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def owner():
    """An owner with two pets and tasks added out of time order."""
    owner = Owner("Jordan", available_minutes=120)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Evening walk", 30, "medium", time="18:00"))
    mochi.add_task(Task("Morning walk", 30, "high", time="07:30", frequency="daily"))
    luna.add_task(Task("Feeding", 10, "high", time="08:00"))
    return owner


def titles(pairs):
    return [task.title for _, task in pairs]


# --- Phase 2 basics ---

def test_mark_complete_changes_status():
    task = Task("Feeding", 10)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", 30))
    assert len(pet.tasks) == 1


# --- Sorting ---

def test_sort_by_time_returns_chronological_order(owner):
    scheduler = Scheduler(owner)
    result = scheduler.sort_by_time(owner.get_all_tasks())
    assert titles(result) == ["Morning walk", "Feeding", "Evening walk"]


def test_sort_by_priority_puts_high_first_then_time(owner):
    scheduler = Scheduler(owner)
    result = scheduler.sort_by_priority(owner.get_all_tasks())
    assert titles(result) == ["Morning walk", "Feeding", "Evening walk"]
    assert [t.priority for _, t in result] == ["high", "high", "medium"]


# --- Filtering ---

def test_filter_by_pet_name(owner):
    scheduler = Scheduler(owner)
    assert titles(scheduler.filter_tasks(pet_name="Luna")) == ["Feeding"]


def test_filter_by_completion_status(owner):
    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Luna", "Feeding")
    assert titles(scheduler.filter_tasks(completed=True)) == ["Feeding"]
    assert "Feeding" not in titles(scheduler.filter_tasks(completed=False))


def test_time_budget_skips_lowest_priority(owner):
    owner.available_minutes = 45
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    assert titles(plan) == ["Morning walk", "Feeding"]
    assert titles(scheduler.skipped) == ["Evening walk"]


# --- Recurrence ---

def test_completing_daily_task_creates_next_day_task():
    pet = Pet("Mochi", "dog")
    today = date(2026, 10, 28)
    pet.add_task(Task("Morning walk", 30, frequency="daily", due_date=today))

    next_task = pet.complete_task("Morning walk")

    assert pet.tasks[0].completed is True
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert len(pet.tasks) == 2


def test_completing_weekly_task_creates_task_one_week_later():
    task = Task("Brushing", 15, frequency="weekly", due_date=date(2026, 10, 28))
    assert task.mark_complete().due_date == date(2026, 11, 4)


def test_completing_one_time_task_does_not_repeat():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Vet visit", 60))
    assert pet.complete_task("Vet visit") is None
    assert len(pet.tasks) == 1


def test_tomorrows_recurrence_not_in_todays_plan(owner):
    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Mochi", "Morning walk")
    assert "Morning walk" not in titles(scheduler.generate_plan())
    tomorrow = scheduler.generate_plan(date.today() + timedelta(days=1))
    assert titles(tomorrow) == ["Morning walk"]


# --- Conflict detection ---

def test_detect_conflicts_flags_duplicate_times(owner):
    owner.get_pet("Mochi").add_task(Task("Heartworm pill", 5, time="08:00"))
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Heartworm pill (Mochi)" in warnings[0] and "Feeding (Luna)" in warnings[0]


def test_no_conflicts_when_times_differ(owner):
    assert Scheduler(owner).detect_conflicts() == []


def test_completed_tasks_do_not_conflict(owner):
    owner.get_pet("Mochi").add_task(Task("Heartworm pill", 5, time="08:00"))
    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Luna", "Feeding")
    assert scheduler.detect_conflicts() == []


# --- Edge cases ---

def test_pet_with_no_tasks_gives_empty_plan():
    owner = Owner("Jordan", available_minutes=60)
    owner.add_pet(Pet("Mochi", "dog"))
    scheduler = Scheduler(owner)
    assert scheduler.generate_plan() == []
    assert scheduler.explain_plan() == "No tasks are due today."


def test_completing_missing_task_raises(owner):
    with pytest.raises(ValueError):
        Scheduler(owner).mark_task_complete("Mochi", "Swim")
