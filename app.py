from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day based on time, priority, and preferences.")

# Streamlit reruns this script on every click, so the Owner lives in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=90)
owner: Owner = st.session_state.owner

st.subheader("Owner")
with st.form("owner_form"):
    name = st.text_input("Owner name", value=owner.name)
    minutes = st.number_input(
        "Minutes available today", min_value=0, max_value=1440, value=owner.available_minutes
    )
    if st.form_submit_button("Save owner"):
        owner.name = name
        owner.available_minutes = int(minutes)
        st.success(f"Saved {owner.name} with {owner.available_minutes} minutes available.")

st.subheader("Pets")
with st.form("pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        elif owner.get_pet(pet_name.strip()):
            st.error(f"{pet_name} is already in your list.")
        else:
            owner.add_pet(Pet(name=pet_name.strip(), species=species, age=int(age)))
            st.success(f"Added {pet_name}.")

if owner.pets:
    st.table([{"Name": p.name, "Species": p.species, "Age": p.age, "Tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.subheader("Tasks")
if owner.pets:
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            task_pet = st.selectbox("Pet", [p.name for p in owner.pets])
            task_title = st.text_input("Task title", value="Morning walk")
            task_time = st.time_input("Time", value=time(8, 0))
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            owner.get_pet(task_pet).add_task(
                Task(
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=priority,
                    time=task_time.strftime("%H:%M"),
                    frequency=frequency,
                )
            )
            st.success(f"Added {task_title} for {task_pet}.")

    scheduler = Scheduler(owner)
    if owner.get_all_tasks():
        # Handle completion before drawing the table so the table shows the result.
        pending = scheduler.filter_tasks(completed=False)
        if pending:
            with st.form("complete_form"):
                choice = st.selectbox(
                    "Mark a task complete",
                    range(len(pending)),
                    format_func=lambda i: f"{pending[i][1].due_date} {pending[i][1].time} · "
                    f"{pending[i][1].title} ({pending[i][0].name})",
                )
                if st.form_submit_button("Mark complete"):
                    pet, task = pending[choice]
                    next_task = pet.complete_task(task.title)
                    if next_task:
                        st.success(f"Done! Next {task.title} for {pet.name} is on {next_task.due_date}.")
                    else:
                        st.success(f"Done! {task.title} for {pet.name} is complete.")

        col1, col2 = st.columns(2)
        with col1:
            pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
        with col2:
            status_filter = st.selectbox("Show status", ["Pending", "Completed", "All"])
        filtered = scheduler.filter_tasks(
            pet_name=None if pet_filter == "All pets" else pet_filter,
            completed={"Pending": False, "Completed": True, "All": None}[status_filter],
        )
        if filtered:
            st.table(
                [
                    {"Date": str(t.due_date), "Time": t.time, "Pet": pet.name, "Task": t.title,
                     "Minutes": t.duration_minutes, "Priority": t.priority,
                     "Frequency": t.frequency, "Done": "✅" if t.completed else ""}
                    # sorted() is stable, so date order keeps the time order within each day
                    for pet, t in sorted(scheduler.sort_by_time(filtered), key=lambda p: p[1].due_date)
                ]
            )
        else:
            st.info("No tasks match these filters.")
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet before adding tasks.")

st.divider()

st.subheader("Today's Schedule")
if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts(plan)
    if not plan and not scheduler.skipped:
        st.info("Nothing is due today. Add tasks or check back tomorrow.")
    else:
        used = sum(t.duration_minutes for _, t in plan)
        st.success(
            f"Planned {len(plan)} task(s) using {used} of {owner.available_minutes} minutes."
        )
        for warning in conflicts:
            st.warning(
                f"⚠️ {warning}. You can't do both at once, so consider moving one of them "
                "to a different time."
            )
        if plan:
            st.table(
                [{"Time": t.time, "Pet": pet.name, "Task": t.title, "Minutes": t.duration_minutes,
                  "Priority": t.priority} for pet, t in plan]
            )
        if scheduler.skipped:
            st.info(
                "Skipped (not enough time): "
                + ", ".join(f"{t.title} ({pet.name}, {t.priority})" for pet, t in scheduler.skipped)
            )
        with st.expander("Why this plan?"):
            st.text(scheduler.explain_plan())
