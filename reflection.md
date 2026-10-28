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

**a. How you used AI**

I used Claude Code in VS Code as an agent for the whole project. I gave it the instructions for each phase, and it handled:
- the UML diagram
- the class skeleton
- the scheduling logic
- the `main.py` demo
- the tests
- the Streamlit UI
- the documentation

My job was to steer it and check the results.

The feature that helped most was **plan mode**. Before changing any files, Claude read the repo and wrote out a plan for me to approve: the class design, which files it would change, the commit message for each phase, and how it would test its work. It also asked me about decisions that were mine to make, like which name to put on my Git commits and whether to push after every phase. Approving a plan before any code got written made it much easier to follow what was happening.

The most useful prompts were the actual phase instructions, pasted in with their concrete requirements (e.g., "sort tasks by time," "a daily task should come back the next day," "conflicts should give a warning, not crash"). Clear requirements gave clear results.

I didn't use separate chat sessions. Everything happened in one long conversation. What kept it organized instead was doing **one phase at a time with its own commit**:
- `chore: add class skeletons from UML`
- `feat: implement PawPal+ core classes…`
- `feat: connect Streamlit UI…`
- `feat: implement sorting, filtering, and conflict detection`
- `test: add automated test suite…`
- `docs: finalize UML, README, and reflection`

Each phase had a clear goal, and `git log` shows how the project grew step by step. Next time, I'd try a fresh session for testing, so the AI looks at the code with "fresh eyes" instead of testing code it remembers writing.

**b. Judgment and verification**

- **Simplifying the design.** The first UML had the Scheduler working out start times from an `Owner.day_start` value. In Phase 2 the design changed so each `Task` stores its own `time` and `due_date`. That's less clever, but it made sorting, filtering and conflict checks simple and easy to test, so I kept the simpler version.
- **Keeping conflict detection simple.** Conflicts are only flagged when two tasks have the exact same start time; overlapping durations aren't checked. I accepted this because it's easy to understand and catches the most common mistake. It's noted as a known limitation.
- **A UI bug caught in review.** In the first version of the polished UI, the "Mark complete" form was *below* the task table, so the table didn't update after a click. This was caught during review and fixed by moving the form above the table.

To check the work, I didn't just trust that the code was right. After each phase, `python main.py` was run to see real output, `python -m pytest` was run (16 tests, all passing), and the Streamlit app was tested by adding pets and tasks, generating a schedule and marking a task complete. I also recorded myself using the app (`assets/pawpal_demo.mp4`) to confirm it works in the browser.

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
