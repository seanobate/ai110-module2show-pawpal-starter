# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. Enter basic owner and pet information (owner name, time available today, pet name and species).
2. Add or edit pet care tasks, each with a duration and a priority (and optionally a preferred time).
3. Generate today's care plan and see it in order, with an explanation of why each task was chosen or skipped.

**a. Initial design**

My UML (`diagrams/uml.mmd`) has four classes. An Owner has many Pets, each Pet has many Tasks, and a Scheduler works from the Owner.

- **Task** (dataclass): one care activity. It holds the title, duration in minutes, priority (low/medium/high), category, frequency, an optional preferred time, and whether it's completed. It can mark itself complete and turn its priority into a number for sorting.
- **Pet** (dataclass): holds the pet's name, species, age and its list of tasks. It's responsible for adding and removing its own tasks and for returning the ones still pending.
- **Owner** (dataclass): holds the owner's name, how many minutes they have today, when their day starts, their preferences, and their pets. It adds pets and collects every pending task across all of them.
- **Scheduler**: the "brain". Given an Owner, it sorts tasks (by priority, then preferred time), drops tasks that don't fit in the available time, assigns start times to build the plan, and explains the result.

**b. Design changes**

I asked the AI to review the skeleton, and it suggested two small changes, which I made:

- `Owner.get_all_tasks()` returns `(Pet, Task)` pairs instead of bare tasks. Tasks don't know which pet they belong to, so once the Scheduler collected them, the plan couldn't show "Walk (Mochi)". Keeping the pair fixes that without adding a back-reference on Task.
- I added a `skipped` list to `Scheduler`. `explain_plan()` is supposed to say why tasks were left out, but the original design threw away the filtered-out tasks, so there was nothing to explain from.

I also used `field(default_factory=list)` for the list attributes, so different Pets and Owners don't share the same list.

During implementation the design changed again (the final version is `diagrams/uml_final.mmd`):

- **Each task carries its own `time` and `due_date`.** The draft had the Scheduler working out start times from an `Owner.day_start`. That made sorting by time and conflict detection awkward, because a task had no time until a plan existed. Moving `time` onto `Task` (and dropping `day_start`) made plan entries simple `(Pet, Task)` pairs, and let sorting, filtering and conflict checks work on any list of tasks.
- **Recurrence lives on `Task`.** `mark_complete()` now returns the next occurrence, and `Pet.complete_task()` adds it to the pet. That kept the date math in one place, and `Scheduler.mark_task_complete()` is just a convenience wrapper around it.
- **New Scheduler methods** for Phase 4: `sort_by_priority`, `filter_tasks`, `detect_conflicts` and `mark_task_complete`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at four things:
- **Due date:** only pending tasks due today are considered.
- **Time budget:** the owner's available minutes for the day.
- **Priority:** high, medium or low.
- **Time of day:** each task's `HH:MM` time.

Priority mattered most because missing a high-priority task (meds, feeding) does real harm, while skipping brushing for a day doesn't. So when the budget is tight, tasks are picked in priority order and lower-priority ones are dropped first. Once the tasks are chosen, they're ordered by time so the plan reads like a real day.

**b. Tradeoffs**

- Conflict detection only flags tasks with the **exact same start time** (same date and the same `HH:MM`). It doesn't check whether durations overlap, so a 30-minute walk at 07:30 and a pill at 07:45 won't be flagged.
- The time-budget filter is **greedy**. It goes through tasks by priority and keeps each one that still fits, so it won't always find the combination that packs the most minutes into the day.

Both are reasonable for one owner with a handful of tasks. An exact-match check is easy to read and test, and it catches the most common mistake: putting two things at the same time. The greedy filter makes sure the important tasks always get in first, which matters more to a pet owner than squeezing in an extra low-priority task. If tasks got longer or more numerous, the next step would be to check for overlapping time windows using each task's start time plus its `duration_minutes`.

---

## 3. AI Collaboration

> _Draft written with Claude Code from what happened in this session. Edit it so it matches your own experience._

**a. How you used AI**

I used Claude Code inside VS Code for the whole project:
- brainstorming the four classes and drawing the Mermaid UML
- generating the dataclass skeleton
- implementing the logic
- writing `main.py` and the tests
- wiring up the Streamlit UI

The most effective feature was **plan mode**. Before touching any files, the assistant read the repo and wrote a plan that I could review and approve (the class design, the exact commit messages, how it would check its work). Agent-style editing across several files was also useful for the recurrence change, which touched `Task`, `Pet`, `Scheduler`, `main.py` and the UI together.

The most helpful prompts were specific and grounded in my own files. For example: "based on my skeletons, how should the Scheduler get all tasks from the Owner's pets?", or "why is this test failing, and is the bug in the test or in `pawpal_system.py`?" Generic prompts gave generic answers.

Keeping each phase separate (design, then core logic, then UI, then algorithms, then tests, then docs), each with its own commit, kept every conversation focused on one goal. It also made it easy to see what changed at each step in `git log`.

**b. Judgment and verification**

- **Start times.** The first design had the Scheduler compute start times from `Owner.day_start`. When it came to sorting by time and detecting conflicts, I moved `time` onto `Task` instead. It's less "clever", but much easier to read and test.
- **The UI order bug.** The first UI version put the "Mark complete" form *below* the task table, so the table didn't update after you clicked. I caught that while reviewing and moved the form above the table.
- **Conflict detection.** I kept it to exact time matches rather than overlapping-duration checks, because the simpler version is easier to explain and was enough for this scenario.

I checked every AI change three ways: running `python main.py` to see real output, running `python -m pytest` after each phase, and running a headless Streamlit test that adds pets and tasks, generates a schedule and marks a task complete.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 16 pytest tests:
- task completion and adding tasks
- sorting by time and by priority
- filtering by pet and by done/not done
- the time budget skipping the lowest-priority task
- daily, weekly and one-time recurrence, including that tomorrow's copy doesn't appear in today's plan
- conflict detection (flagged when times match, not flagged when they differ or the task is already done)
- edge cases: a pet with no tasks, and completing a task that doesn't exist

These matter because the scheduler's whole job is to decide *what* happens and *when*. A sorting or recurrence bug would quietly give the owner a wrong plan, for example a daily walk that never comes back, or meds dropped in favor of brushing.

**b. Confidence**

About 4 out of 5. All the core behaviors pass, including the edge cases. With more time I would test:
- overlapping durations, such as a 07:30 walk lasting 30 minutes and an 07:45 pill
- times that aren't zero-padded (like "7:30"), which would break string sorting
- two pets with the same name
- invalid priority or frequency values
- a zero-minute budget
- automated tests for the Streamlit UI using `streamlit.testing.AppTest`

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how small and testable the Scheduler ended up. Every method takes a list of `(Pet, Task)` pairs and returns a new list. Because of that, sorting, filtering and conflict detection each take only a few lines, and the 16 tests were easy to write. The CLI-first approach also meant that by the time I wired up the UI, the logic was already proven.

**b. What you would improve**

- Detect conflicts from overlapping time windows (start time plus duration) instead of only exact time matches.
- Use a better selection method than greedy, so the plan packs the time budget more fully.
- Validate input: priority and frequency values, and zero-padded times.
- Save owners, pets and tasks to a file so they survive a browser refresh.
- Use the `preferences` dictionary, which is stored but not used yet.

**c. Key takeaway**

Being the "lead architect" means the AI can write code faster than I can, but I'm the one who decides what the system *should* be. The UML and the plan-approval step were where I had the most control: catching a design problem there cost one sentence, while catching it after the code was written meant rewriting several files. Asking for small, reviewable steps and checking each one with real output and tests is what kept the AI's speed from turning into a mess.
