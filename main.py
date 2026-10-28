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
