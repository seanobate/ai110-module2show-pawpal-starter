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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
