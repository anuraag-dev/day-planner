import streamlit as st
from datetime import date
from supabase import create_client

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Day Planner", page_icon="🗓️", layout="centered")

# -------------------- SUPABASE --------------------
# These MUST be set in Streamlit Cloud Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------- SESSION STATE --------------------
if "page" not in st.session_state:
    st.session_state.page = "calendar"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

# -------------------- UI --------------------
st.title("🗓️ Day Planner")

# ======================================================
# PAGE 1: CALENDAR
# ======================================================
if st.session_state.page == "calendar":
    st.subheader("Select a day")

    picked_date = st.date_input(
        "Choose a date",
        st.session_state.selected_date
    )

    if st.button("Open day"):
        st.session_state.selected_date = picked_date
        st.session_state.page = "day"
        st.rerun()

# ======================================================
# PAGE 2: DAY VIEW
# ======================================================
elif st.session_state.page == "day":
    selected_date = st.session_state.selected_date
    st.subheader(f"Tasks for {selected_date}")

    # ---------- ADD TASK ----------
    new_task = st.text_input("Add a task")

    if st.button("➕ Add task"):
        if new_task.strip():
            supabase.table("tasks").insert({
                "task_date": str(selected_date),
                "text": new_task.strip(),
                "done": False
            }).execute()
            st.rerun()

    st.divider()

    # ---------- LOAD TASKS ----------
    response = (
        supabase
        .table("tasks")
        .select("*")
        .eq("task_date", str(selected_date))
        .order("created_at")
        .execute()
    )

    tasks = response.data or []

    # ---------- DISPLAY TASKS ----------
    for task in tasks:
        checked = st.checkbox(
            "",
            value=task["done"],
            key=task["id"]
        )

        if checked != task["done"]:
            supabase.table("tasks") \
                .update({"done": checked}) \
                .eq("id", task["id"]) \
                .execute()

        if checked:
            st.markdown(f"~~{task['text']}~~")
        else:
            st.write(task["text"])

    st.divider()

    if st.button("⬅ Back to calendar"):
        st.session_state.page = "calendar"
        st.rerun()
