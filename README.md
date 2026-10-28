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

## ✨ Features

- **Owners, pets and tasks:** one owner can have several pets, and each pet has its own care tasks (title, duration, priority, time, frequency).
- **Priority-aware daily plan:** `Scheduler.generate_plan()` picks today's pending tasks in priority order until the owner's available minutes run out, then shows them in time order.
- **Sorting by time:** `Scheduler.sort_by_time()` orders tasks by their `HH:MM` time, and `sort_by_priority()` orders them high → low.
- **Filtering:** `Scheduler.filter_tasks()` narrows the list by pet, by done/not done, and/or by date.
- **Conflict warnings:** `Scheduler.detect_conflicts()` flags two or more tasks set for the same date and time, across all pets, as a friendly warning rather than an error.
- **Daily and weekly recurrence:** completing a recurring task adds the next one automatically, 1 day or 7 days later (`Task.mark_complete()` using `timedelta`).
- **Plan explanations:** `Scheduler.explain_plan()` says why each task made it into the plan, and which tasks were skipped for lack of time.
- **Streamlit UI:** the `Owner` lives in `st.session_state`, so pets and tasks stay put as you click around.

Class design: [diagrams/uml_final.mmd](diagrams/uml_final.mmd) (the Phase 1 draft is [diagrams/uml.mmd](diagrams/uml.mmd)).

## 🖥️ Sample Output

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
python -m pytest
```

The suite in [tests/test_pawpal.py](tests/test_pawpal.py) has 16 tests covering:

- **Basics:** `mark_complete()` flips the status, and `add_task()` increases a pet's task count.
- **Sorting:** tasks entered out of order come back in time order, and priority sort puts high first and breaks ties by time.
- **Filtering:** by pet name, by done/not done, and the time budget dropping the lowest-priority task into `skipped`.
- **Recurrence:** a daily task creates a copy due the next day, a weekly task creates one due 7 days later, and a `once` task creates nothing. Tomorrow's copy shows up in tomorrow's plan, not today's.
- **Conflicts:** two tasks at the same time (on different pets) are flagged, tasks at different times aren't, and completed tasks are ignored.
- **Edge cases:** a pet with no tasks gives an empty plan with a friendly message, and completing a task that doesn't exist raises `ValueError`.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.3, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Seano\Documents\ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 16 items

tests\test_pawpal.py ................                                    [100%]

============================== warnings summary ===============================
..\..\AppData\Local\Programs\Python\Python313\Lib\site-packages\anyio\pytest_plugin.py:14
  PytestRemovedIn10Warning: _pytest.python.CallSpec2 has been renamed to CallSpec.

======================== 16 passed, 1 warning in 0.04s ========================
```

(The single warning comes from the third-party `anyio` pytest plugin, not from PawPal+ code.)

**Confidence level: ★★★★☆ (4/5).** Every core scheduling behavior is tested, including the edge cases. I held back one star because conflict detection only catches exact start-time matches (overlapping durations aren't checked), and the Streamlit UI is tested by hand rather than by automated tests.

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

Run the app with `streamlit run app.py`.

1. **Set up the owner.** In the *Owner* form, enter your name and how many minutes you have for pet care today (for example 90), then click **Save owner**.
2. **Add pets.** In the *Pets* form, add "Mochi" (dog) and then "Luna" (cat). A table lists each pet and how many tasks it has.
3. **Schedule tasks.** In the *Tasks* form, pick a pet and enter a title, time, duration, priority and frequency. For example: Mochi, "Morning walk", 07:30, 30 min, high, daily. Then Luna, "Feeding", 08:00, 10 min, high, daily. Then Mochi, "Heartworm pill", 08:00, 5 min, high, once.
4. **Browse tasks.** The task table is always sorted by date and time. Use **Show pet** and **Show status** to filter, for example to see only Luna's tasks or only the completed ones.
5. **Generate today's schedule.** Click **Generate schedule**. You'll see:
   - a green summary (how many tasks, and how many minutes used out of the budget)
   - a yellow **conflict warning**, because Mochi's pill and Luna's feeding are both at 08:00, with a suggestion to move one
   - the plan as a table in time order
   - a blue note listing any tasks skipped because time ran out (lowest priority goes first)
   - a **Why this plan?** expander with the scheduler's explanation
6. **Complete a recurring task.** In **Mark a task complete**, choose Mochi's Morning walk and click **Mark complete**. The app confirms that the next walk has been added for tomorrow. Switch **Show status** to *All* to see both the finished walk and tomorrow's.

The same behaviors run in the terminal with `python main.py`: tasks are added out of order, then the demo prints the plan, sorted and filtered lists, a conflict warning and a recurrence:

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

Tasks as entered:
  18:00  Mochi  Evening walk     medium 2026-10-28 [todo]
  07:30  Mochi  Morning walk     high   2026-10-28 [todo]
  08:00  Mochi  Heartworm pill   high   2026-10-28 [todo]
  08:00  Luna   Feeding          high   2026-10-28 [todo]
  19:00  Luna   Brushing         low    2026-10-28 [todo]

Sorted by time:
  07:30  Mochi  Morning walk     high   2026-10-28 [todo]
  08:00  Mochi  Heartworm pill   high   2026-10-28 [todo]
  08:00  Luna   Feeding          high   2026-10-28 [todo]
  18:00  Mochi  Evening walk     medium 2026-10-28 [todo]
  19:00  Luna   Brushing         low    2026-10-28 [todo]

Only Luna's tasks:
  08:00  Luna   Feeding          high   2026-10-28 [todo]
  19:00  Luna   Brushing         low    2026-10-28 [todo]

Conflict check:
  WARNING: Conflict on 2026-10-28 at 08:00: Heartworm pill (Mochi), Feeding (Luna)

Completed Mochi's Morning walk; next one queued for 2026-10-29.

Completed tasks:
  07:30  Mochi  Morning walk     high   2026-10-28 [done]

Mochi's pending tasks:
  18:00  Mochi  Evening walk     medium 2026-10-28 [todo]
  08:00  Mochi  Heartworm pill   high   2026-10-28 [todo]
  07:30  Mochi  Morning walk     high   2026-10-29 [todo]
```

**Screenshot or video** *(optional)*: not included. The walkthrough and CLI output above show every feature.
