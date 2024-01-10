import streamlit as st
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

api_secret = os.getenv('API_SECRET')

# Set up MongoDB connection
client = MongoClient(api_secret)
db = client["AI-Challenge-ScoreMaster"]
users = db["users"]
results = db["results"]

# Writing the session state
if 'users' and 'results' not in st.session_state:
    st.session_state.users = users
    st.session_state.results = results


def load_evaluations_from_mongodb():
    # Assuming you have a collection called "results" in your MongoDB
    evaluations = results.find({}, {"_id": 0})
    df = pd.DataFrame(evaluations)
    return df

# Load all evaluations from MongoDB and display them in a table
def display_evaluation_table():
    df = load_evaluations_from_mongodb()
    st.dataframe(df, use_container_width=True, hide_index=True)


display_evaluation_table()

# TODO: Don't forget to add a model counter or an uploaded am date to delete all of the models that are 2 weeks
# Automatically from the database