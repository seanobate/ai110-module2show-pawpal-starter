# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Output of `python main.py`:

```
Today's Schedule for Jordan
====================================================
Time   Pet    Task                Min  Priority
----------------------------------------------------
07:30  Mochi  Morning walk         30  high
08:00  Mochi  Heartworm pill        5  high
08:00  Luna   Feeding              10  high
18:00  Mochi  Evening walk         30  medium
----------------------------------------------------
Scheduled 4 task(s) using 75 of 75 available minutes, highest priority first.
- 07:30 Morning walk (Mochi): high priority, 30 min fit in the budget.
- 08:00 Heartworm pill (Mochi): high priority, 5 min fit in the budget.
- 08:00 Feeding (Luna): high priority, 10 min fit in the budget.
- 18:00 Evening walk (Mochi): medium priority, 30 min fit in the budget.
- Skipped Brushing (Luna): low priority, 15 min did not fit in the remaining time.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

All scheduling logic lives in [pawpal_system.py](pawpal_system.py).

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Time sort uses `sorted()` with a `lambda` key on the zero-padded `"HH:MM"` string, which sorts correctly as text. Priority sort puts high before low and breaks ties by time. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed, on_date)`, `Scheduler.filter_by_time()` | `filter_tasks` combines any of the filters (by pet, by done/not done, by date). `filter_by_time` picks tasks in priority order while they still fit in the owner's available minutes; whatever doesn't fit goes into `Scheduler.skipped`. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups pending tasks by `(due_date, time)` and returns a warning string for each slot that holds more than one task, whether for the same pet or different pets. It warns and never raises an error. |
| Recurring tasks | `Task.mark_complete()`, `Pet.complete_task()`, `Scheduler.mark_task_complete()` | When a `daily` or `weekly` task is completed, a copy is created with `due_date + timedelta(days=1 or 7)` and added back to the pet. `once` tasks just end. |
| Daily plan | `Scheduler.generate_plan()`, `Scheduler.explain_plan()` | Takes the pending tasks due today, applies the time budget, sorts the result by time, and explains why each task was scheduled or skipped. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
