import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load credentials from secrets or .env
if st.secrets.get("SUPABASE_URL"):
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
else:
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase: Client = create_client(url, key)

# Authentication functions
def sign_up(email, password):
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Registration failed: {e}")

def sign_in(email, password):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Login Failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user_email = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout Failed: {e}")

# Main To-Do App
def main_app(user_email, user_id):
    st.title("Dashboard")
    st.success(f"Welcome, {user_email}!")

    if st.button("Logout"):
        sign_out()

    def get_todos():
        response = (
            supabase.table("todos")
            .select("*")
            .eq("user_id", user_id)
            .order("id", desc=False)
            .execute()
        )
        return response.data

    def add_todo(task):
        supabase.table("todos").insert({"task": task, "user_id": user_id}).execute()

    def del_todo(task_id):
        supabase.table("todos").delete().eq("id", task_id).eq("user_id", user_id).execute()

    st.subheader("Add a Task")
    task_input = st.text_input("New Task:")
    if st.button("Add Task"):
        if task_input:
            add_todo(task_input)
            st.success("Task added!")
            st.rerun()
        else:
            st.error("Please enter a task")

    st.subheader("Your To-Do List")
    todos = get_todos()

    if todos:
        for item in todos:
            edit_key = f"editing-{item['id']}"
            input_key = f"input-{item['id']}"

            if edit_key not in st.session_state:
                st.session_state[edit_key] = False
            if input_key not in st.session_state:
                st.session_state[input_key] = item["task"]

            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

            with col1:
                st.markdown(f"- {item['task']}")

            with col2:
                if st.button("Edit", key=f"edit-{item['id']}"):
                    st.session_state[edit_key] = True

                if st.session_state[edit_key]:
                    edited = st.text_input(
                        "Update Task:",
                        value=st.session_state[input_key],
                        key=input_key
                    )
                    if st.button("Save", key=f"save-{item['id']}"):
                        supabase.table("todos").update({"task": edited}).eq("id", item["id"]).eq("user_id", user_id).execute()
                        st.session_state[edit_key] = False
                        st.rerun()

            with col3:
                if st.button("Delete", key=f"del-{item['id']}"):
                    del_todo(item["id"])
                    st.rerun()
    else:
        st.info("No tasks available.")

# Authentication Screen
def auth_screen():
    st.title("Authentication")
    option = st.selectbox("Choose:", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Sign Up" and st.button("Register"):
        user = sign_up(email, password)
        if user and user.user:
            st.success("Registration successful. Please log in.")

    if option == "Login" and st.button("Login"):
        user = sign_in(email, password)
        if user and user.user:
            st.session_state.user_email = user.user.email
            st.session_state.user_id = user.user.id
            st.rerun()

# Session State Init
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Routing
if st.session_state.user_email:
    main_app(st.session_state.user_email, st.session_state.user_id)
else:
    auth_screen()
