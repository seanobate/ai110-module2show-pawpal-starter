"""CLI demo for PawPal+: builds an owner with two pets and prints today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(scheduler: Scheduler) -> None:
    """Print the generated plan as an aligned table."""
    print(f"Today's Schedule for {scheduler.owner.name}")
    print("=" * 52)
    print(f"{'Time':<6} {'Pet':<6} {'Task':<18} {'Min':>4}  Priority")
    print("-" * 52)
    for pet, task in scheduler.plan:
        print(f"{task.time:<6} {pet.name:<6} {task.title:<18} {task.duration_minutes:>4}  {task.priority}")
    print("-" * 52)
    print(scheduler.explain_plan())


def print_tasks(heading: str, pairs) -> None:
    """Print a short list of (pet, task) pairs under a heading."""
    print(f"\n{heading}")
    for pet, task in pairs:
        status = "done" if task.completed else "todo"
        print(f"  {task.time}  {pet.name:<6} {task.title:<16} {task.priority:<6} {task.due_date} [{status}]")


def build_demo_owner() -> Owner:
    """Create the sample owner, pets, and tasks (added out of time order on purpose)."""
    owner = Owner(name="Jordan", available_minutes=75)
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Evening walk", 30, "medium", "walk", time="18:00", frequency="daily"))
    mochi.add_task(Task("Morning walk", 30, "high", "walk", time="07:30", frequency="daily"))
    luna.add_task(Task("Feeding", 10, "high", "feeding", time="08:00", frequency="daily"))
    luna.add_task(Task("Brushing", 15, "low", "grooming", time="19:00", frequency="weekly"))
    mochi.add_task(Task("Heartworm pill", 5, "high", "meds", time="08:00"))
    return owner


if __name__ == "__main__":
    scheduler = Scheduler(build_demo_owner())
    scheduler.generate_plan()
    print_schedule(scheduler)

    all_tasks = scheduler.owner.get_all_tasks()
    print_tasks("Tasks as entered:", all_tasks)
    print_tasks("Sorted by time:", scheduler.sort_by_time(all_tasks))
    print_tasks("Only Luna's tasks:", scheduler.filter_tasks(pet_name="Luna"))

    print("\nConflict check:")
    conflicts = scheduler.detect_conflicts()
    for warning in conflicts:
        print(f"  WARNING: {warning}")
    if not conflicts:
        print("  No conflicts.")

    next_walk = scheduler.mark_task_complete("Mochi", "Morning walk")
    print(f"\nCompleted Mochi's Morning walk; next one queued for {next_walk.due_date}.")
    print_tasks("Completed tasks:", scheduler.filter_tasks(completed=True))
    print_tasks("Mochi's pending tasks:", scheduler.filter_tasks(pet_name="Mochi", completed=False))
