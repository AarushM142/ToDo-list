import streamlit as st
from supabase import create_client
from supabase import Client
from dotenv import load_dotenv
import os

load_dotenv() 
#this loads the variables from the .env file so that sensetive credentials like API keys are loaded securely

url= os.getenv("SUPABASE_URL")
key= os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url,key)
#this enable supabase methods to be used with this variable supabase

def get_todos():
    response= supabase.table('todos').select('*').execute()
    return response.data

def add_todo(task):
    supabase.table('todos').insert({'task':task}).execute()
    #when this func is called, with insert function, it creates a dictionary(row) with every key called 'task' and the value for that is passed thru the argument varibale task

st.title("Supabase To-Do App")

task1=st.text_input("Add a new task:")

clicked = st.button("Add Task")

if clicked: #checks if button was clicked
    if task1: #checks if any character was input in the text box
        add_todo(task1)
        st.success("Task added!")
    else:
        st.error("Please enter a task")

st.write("### To-Do List:")
todos= get_todos()

if todos!=False: #if the todo list is empty, todos will return false hence this will check that
    for item in todos: #todos contains many dictionaries, item loops thru each dictionary and 'task' is the key for each dictionary so in the end you get the value of the 'task' key in each dictionary in the todos table 
        st.markdown(f"- {item['task']}")
else:
    st.write("No tasks available.")
