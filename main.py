import streamlit as st
import requests

st.markdown("""
    <style>
        .title {
            font = "sans-serif";
            font-size:60px !important;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="title">COE-AI Chatbot</div>', unsafe_allow_html=True)

st.write("xxxxx")

response = requests.get("http://localhost:8000/api")

if response.status_code == 200:
    st.write("FastAPI says:", response.json()["message"])
else:
    st.write("Failed to fetch data from FastAPI")
