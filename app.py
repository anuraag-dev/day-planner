import streamlit as st
from datetime import date
from supabase import create_client

# ---------- SUPABASE ----------
SUPABASE_URL = "https://lxuttbhtsywsqosewogt.supabase.co"
SUPABASE_KEY = "sb_publishable_UUsaP-Hy9N-skV1CCp9hPQ_L8VbzQEG"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "calendar"

if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

# ---------- UI ----------
st.title("Day Planner")

# ---------- PAGE 1 : CALENDAR ----------
if st.session_state.page == "calendar":
    st.subheader("📅 Select a Day")

    picked_date = st.date_input(
        "Click a date",
        st.session_state.selected_date
    )

    if st.button("Open Day"):
        st.session_state.selected_date = picked_date
        st.session_state.page = "day"
        st.rerun()

# ---------- PAGE 2 : DAY PLAN ----------
elif st.session_state.page == "day":
    selected_date = st.session_state.selected_date

    st.subheader(f"📝 {selected_date}")

    # ---- Add task ----
    new_task = st.text_input("Add a task")

    if st.button("➕ Add"):
        if new_task.strip():
            supabase.table("tasks").insert({
                "task_date": str(selected_date),
                "text": new_task,
                "done": False
            }).execute()
            st.rerun()

    st.divider()

    # ---- Load tasks ----
    res = supabase.table("tasks") \
        .select("*") \
        .eq("task_date", str(selected_date)) \
        .order("created_at") \
        .execute()

    tasks = res.data or []

    # ---- Render tasks ----
    for task in tasks:
        checked = st.checkbox(
            "",
            task["done"],
            key=task["id"]
        )

        # Update done state if changed
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

    if st.button("⬅ Back to Calendar"):
        st.session_state.page = "calendar"
        st.rerun()
